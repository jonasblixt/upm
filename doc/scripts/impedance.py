#!/usr/bin/env python3
"""Trace widths for the controlled-impedance classes (doc/pcb-stackup.md).

A 2D electrostatic field solver: finite differences on a nonuniform grid,
cell-centred permittivity, the energy of the solved potential gives the
capacitance per unit length. Z0 = 1 / (c0 * sqrt(C * C_air)); differential
impedance is twice the odd-mode impedance. The solver is the one from the
PoEtato project (doc/scripts/impedance.py there), cut down to the outer-layer
case, which is all a 4-layer board has.

Model:
  - trace on the laminate (L1, or L4 seen from below: the stackups are
    symmetric), reference plane under the prepreg, solder mask (MASK_DK;
    MASK_SUB over laminate, MASK_TOP over copper), air
  - optional copper pour on the same layer, at the plane's potential, a
    given distance from the outer trace edges (--pour)
  - rectangular trace cross-section (real traces are trapezoidal), grounded
    box 3 mm to the sides and 5 mm above, far enough not to matter

Expect about +-5 % against the fab. JLCPCB's impedance calculator is the
reference for the order; this script is for comparing stackups and for the
starting widths.

    python doc/scripts/impedance.py                 # the chosen stackup
    python doc/scripts/impedance.py --stackup all   # every 4-layer candidate
    python doc/scripts/impedance.py --detail        # sensitivity of the chosen geometry
    python doc/scripts/impedance.py --check         # analytic sanity check

Needs numpy and scipy (pip install numpy scipy).
"""
import argparse

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.optimize import brentq

C0 = 299792458.0
EPS0 = 8.8541878128e-12
MM = 1e-3

MASK_DK = 3.8
MASK_SUB = 0.030 * MM
MASK_TOP = 0.015 * MM
CU_OUTER = 0.035 * MM

# JLCPCB 4-layer, 1.6 mm, 1 oz outer / 0.5 oz inner (jlcpcb.com/impedance).
# name: (prepreg, L1-L2 and L3-L4 thickness mm, Dk)
STACKUPS = {
    "7628": ("7628", 0.2104, 4.4),
    "2116": ("2116", 0.1164, 4.16),
    "3313": ("3313", 0.0994, 4.1),
    "1080": ("1080", 0.0764, 3.91),
}
CHOSEN = "2116"

# (label, ohms, gap mm or None for single-ended)
CLASSES = [
    ("50 ohm SE", 50, None),
    ("90 ohm diff", 90, 0.15),
]

# The geometry on the board (doc/pcb-stackup.md section 3): width, gap in mm
USB_W, USB_S = 0.16, 0.15


def axis(keys, lo, hi, fine, coarse, grow=1.25):
    """Grid lines through every key point, fine at the keys, growing between."""
    keys = sorted(set([lo, hi] + [k for k in keys if lo <= k <= hi]))
    pts = [lo]
    for a, b in zip(keys[:-1], keys[1:]):
        length = b - a
        left, x, d = [], 0.0, fine
        while x + d < length / 2:
            x += d
            left.append(x)
            d = min(d * grow, coarse)
        right = [length - v for v in reversed(left)]
        seg = left + ([length / 2] if length > 2 * fine else []) + right
        pts += [a + v for v in sorted(set(round(v, 12) for v in seg)) if 0 < v < length] + [b]
    return np.array(sorted(set(round(p, 12) for p in pts)))


def energy(conductors, x, y, eps_fn):
    """Field energy per unit length for conductors [(x0, x1, y0, y1, V)]."""
    nx, ny = len(x), len(y)
    dx, dy = np.diff(x), np.diff(y)
    xc, yc = (x[:-1] + x[1:]) / 2, (y[:-1] + y[1:]) / 2
    XC, YC = np.meshgrid(xc, yc, indexing="ij")
    E = eps_fn(XC, YC)

    idx = np.arange(nx * ny).reshape(nx, ny)
    fixed = np.zeros((nx, ny), bool)
    vfix = np.zeros((nx, ny))
    fixed[0, :] = fixed[-1, :] = fixed[:, 0] = fixed[:, -1] = True
    X, Y = np.meshgrid(x, y, indexing="ij")
    tol = 1e-12
    for x0, x1, y0, y1, v in conductors:
        m = (X >= x0 - tol) & (X <= x1 + tol) & (Y >= y0 - tol) & (Y <= y1 + tol)
        fixed |= m
        vfix[m] = v

    # edge conductances from the permittivity of the cells either side
    ex = np.zeros((nx - 1, ny))
    ex[:, 1:] += E * dy[None, :] / 2
    ex[:, :-1] += E * dy[None, :] / 2
    ey = np.zeros((nx, ny - 1))
    ey[1:, :] += E * dx[:, None] / 2
    ey[:-1, :] += E * dx[:, None] / 2
    a = np.concatenate([idx[:-1, :].ravel(), idx[:, :-1].ravel()])
    b = np.concatenate([idx[1:, :].ravel(), idx[:, 1:].ravel()])
    g = np.concatenate([(ex / dx[:, None]).ravel(), (ey / dy[None, :]).ravel()])

    n = nx * ny
    lap = sp.coo_matrix((np.concatenate([-g, -g, g, g]),
                         (np.concatenate([a, b, a, b]), np.concatenate([b, a, a, b]))),
                        shape=(n, n)).tocsr()
    f = fixed.ravel()
    v = vfix.ravel().copy()
    v[~f] = spla.spsolve(lap[~f][:, ~f].tocsc(), -lap[~f][:, f] @ v[f])
    return 0.5 * np.sum(g * (v[a] - v[b]) ** 2) * EPS0


class Microstrip:
    """Outer-layer trace or pair: h/er is the prepreg to the plane below.
    pour: distance from the outer trace edges to a grounded pour on the same
    layer, or None for no pour."""

    def __init__(self, h, er, t=CU_OUTER, pour=None, mask=True, fine=2e-6, coarse=60e-6,
                 lid=5 * MM, side=3 * MM):
        self.h, self.er, self.t, self.pour, self.mask = h, er, t, pour, mask
        self.fine, self.coarse, self.lid, self.side = fine, coarse, lid, side

    def _cap(self, w, s, air):
        h, t = self.h, self.t
        sub, top = (MASK_SUB, MASK_TOP) if self.mask else (0.0, 0.0)
        traces = [(-w / 2, w / 2)] if s is None else [(-s / 2 - w, -s / 2), (s / 2, s / 2 + w)]
        half = w / 2 if s is None else w + s / 2
        xl = half + self.side
        copper = list(traces)
        if self.pour is not None:
            copper += [(-xl, -half - self.pour), (half + self.pour, xl)]
        x = axis([p for c in copper for p in c] + [0.0], -xl, xl, self.fine, self.coarse)
        y = axis([0, h, h + t, h + sub, h + t + top],
                 -10e-6, h + t + self.lid, self.fine, self.coarse)
        cond = [(-xl, xl, -10e-6, 0.0, 0.0)]
        cond += [(x0, x1, h, h + t, 0.0) for x0, x1 in copper[len(traces):]]

        def eps(X, Y):
            e = np.ones_like(X)
            if air:
                return e
            e[Y < h] = self.er
            if sub or top:
                m = (Y >= h) & (Y < h + sub)
                for x0, x1 in copper:
                    m |= (X > x0 - top) & (X < x1 + top) & (Y >= h) & (Y < h + t + top)
                e[m] = MASK_DK
            return e

        if s is None:
            cond.append((traces[0][0], traces[0][1], h, h + t, 1.0))
            return 2 * energy(cond, x, y, eps)          # W = C V^2 / 2
        cond += [(traces[0][0], traces[0][1], h, h + t, 1.0),
                 (traces[1][0], traces[1][1], h, h + t, -1.0)]
        return energy(cond, x, y, eps)                  # +-1 V: W = C_odd

    def impedance(self, w, s=None):
        z = 1 / (C0 * np.sqrt(self._cap(w, s, False) * self._cap(w, s, True)))
        return z if s is None else 2 * z

    def width_for(self, z, s=None):
        return brentq(lambda w: self.impedance(w, s) - z, 0.04 * MM, 0.8 * MM, xtol=1e-7)


def layer(name, **kw):
    _, h, er = STACKUPS[name]
    return Microstrip(h * MM, er, **kw)


def check():
    # microstrip without mask: Hammerstad-Jensen with thickness correction
    h, w, t, er = 0.2 * MM, 0.36 * MM, 35e-6, 4.4
    ms = Microstrip(h, er, t=t, mask=False)
    dw = t / np.pi * np.log(1 + 4 * np.e / (t / h * (1 / np.tanh(np.sqrt(6.517 * w / h))) ** 2))
    u = (w + dw * (1 + 1 / np.cosh(np.sqrt(er - 1))) / 2) / h
    f = 6 + (2 * np.pi - 6) * np.exp(-(30.666 / u) ** 0.7528)
    a = 1 + np.log((u ** 4 + (u / 52) ** 2) / (u ** 4 + 0.432)) / 49 + np.log(1 + (u / 18.1) ** 3) / 18.7
    bb = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    ee = (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u) ** (-a * bb)
    hj = 60 * np.log(f / u + np.sqrt(1 + 4 / u ** 2)) / np.sqrt(ee)
    print(f"microstrip  FD {ms.impedance(w):6.2f}  Hammerstad-Jensen {hj:6.2f}")


def detail(name):
    """How far the chosen USB geometry moves with etch, gap, pours and uncoupling."""
    w, s = USB_W * MM, USB_S * MM
    ms = layer(name)
    print(f"JLC04161H-{name}, 90 ohm pair {USB_W:.2f} / {USB_S:.2f} mm")
    print(f"  nominal                         {ms.impedance(w, s):6.1f} ohm", flush=True)
    for dw in (-0.02, 0.02):
        # etch moves the edges: the pitch stays, the gap changes the other way
        print(f"  width {dw:+.2f} mm (pitch kept)      {ms.impedance(w + dw * MM, s - dw * MM):6.1f} ohm",
              flush=True)
    print(f"  uncoupled, 2 x Z0 of one trace  {2 * ms.impedance(w):6.1f} ohm", flush=True)
    for p in (0.15, 0.3):
        print(f"  pour at {p:.2f} mm                 {layer(name, pour=p * MM).impedance(w, s):6.1f} ohm",
              flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stackup", default=CHOSEN, choices=list(STACKUPS) + ["all"])
    ap.add_argument("--check", action="store_true", help="run the analytic sanity check")
    ap.add_argument("--detail", action="store_true", help="sensitivity of the board's USB geometry")
    args = ap.parse_args()
    if args.check:
        check()
        return
    names = list(STACKUPS) if args.stackup == "all" else [args.stackup]
    if args.detail:
        for name in names:
            detail(name)
        return
    print(f"{'stackup':15} {'layer':6} {'class':13} {'W mm':>6} {'S mm':>6} {'uncoupled':>10}")
    for name in names:
        ms = layer(name)
        for label, z, s in CLASSES:
            w = ms.width_for(z, None if s is None else s * MM)
            gap = "-" if s is None else f"{s:.2f}"
            unc = "" if s is None else f"{2 * ms.impedance(w):6.1f} ohm"
            print(f"JLC04161H-{name:5} L1/L4  {label:13} {w / MM:6.3f} {gap:>6} {unc:>10}", flush=True)


if __name__ == "__main__":
    main()
