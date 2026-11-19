#!/usr/bin/env python3
"""Stackup drawing, impedance table, fabrication notes and drill table on User.3.

Draws the JLC04161H-2116 cross-section, the controlled-impedance table and
the fabrication notes of doc/v2-pcb.md onto the User.3 layer (named
User.Stackup): the stackup right of the board, the fab notes below it, the
drill table to the far right. Everything goes in one locked group,
"Stackup JLC04161H-2116", so it moves as a unit. A previous copy of that
group is removed first, so the script can be re-run after changing the
values below. Close the board in KiCad before running it.

    python doc/scripts/stackup_drawing.py hw/v2/upm-v2.kicad_pcb

Keep STACK, IMP and FAB_NOTES in step with doc/v2-pcb.md. The drill table is
read from the board's vias and pads, so re-run the script whenever holes
change. Adapted from the PoEtato project's script of the same name.
"""
import re
import sys

from kicad_draw import Drawing, blocks, replace

GROUP = "Stackup JLC04161H-2116"

X0, Y0 = 125.0, 30.0          # top-left of the stackup block
SCALE = 24.0                   # cross-section vertical scale (mm per mm)
SEC_W = 22.0                   # cross-section width
ROW = 3.4                      # label row pitch
FX, FY = 30.0, 172.0           # fabrication notes
DX, DY = 232.0, 30.0           # drill table

d = Drawing("User.3")
text, line, rect = d.text, d.line, d.rect

# ---------------------------------------------------------------- data
# (name, kind, function, material, thickness mm, Dk)
STACK = [
    ("F.Cu",   "cu",   "L1 SIG", "Copper 1 oz",   0.035,  None),
    ("",       "pp",   "",       "Prepreg 2116",  0.1164, 4.16),
    ("In1.Cu", "cu",   "L2 GND", "Copper 0.5 oz", 0.0152, None),
    ("",       "core", "",       "Core",          1.265,  4.6),
    ("In2.Cu", "cu",   "L3 PWR", "Copper 0.5 oz", 0.0152, None),
    ("",       "pp",   "",       "Prepreg 2116",  0.1164, 4.16),
    ("B.Cu",   "cu",   "L4 SIG", "Copper 1 oz",   0.035,  None),
]
TOTAL = sum(r[4] for r in STACK)

# (target, signals, layer, width, gap, reference)
IMP = [
    ("90 Ω diff", "USB pairs, *USB*_D_P / _N", "L1", "0.16", "0.15", "L2 GND"),
    ("",          "",                          "L4", "0.16", "0.15", "L3, over GND only"),
    ("50 Ω SE",   "Default track width",       "L1", "0.18", "-",    "L2 GND"),
    ("",          "",                          "L4", "0.18", "-",    "L3, over GND only"),
]

# ---------------------------------------------------------------- title
text("PCB STACKUP  JLCPCB JLC04161H-2116", X0, Y0, size=2.0, th=0.3, bold=True)
text(f"4 layers, 1.6 mm finished ({TOTAL:.3f} mm laminate + mask), "
     "outer 1 oz, inner 0.5 oz, FR-4", X0, Y0 + 3.6, size=1.1, th=0.15)

# ---------------------------------------------------------------- stackup
ytab = Y0 + 9.0                 # header row
ysec = ytab + 2.6               # top of cross-section / first label row
cx = {"layer": X0 + SEC_W + 9.0}
cx["func"] = cx["layer"] + 12.5
cx["mat"] = cx["func"] + 12.0
cx["th"] = cx["mat"] + 24.0
cx["dk"] = cx["th"] + 13.0
xend = cx["dk"] + 8.0

for key, label in (("layer", "Layer"), ("func", "Use"), ("mat", "Material"),
                   ("th", "Thickness"), ("dk", "Dk")):
    text(label, cx[key], ytab, size=1.2, th=0.2, bold=True)
text(f"Cross-section (vertical x{SCALE:.0f})", X0, ytab, size=1.0, th=0.15)
line(cx["layer"] - 1.0, ytab + 1.3, xend, ytab + 1.3, 0.15)

sec_h = TOTAL * SCALE
row0 = ysec + (sec_h - ROW * len(STACK)) / 2      # label rows centred on the section
y = ysec
for i, (name, kind, func, mat, t, dk) in enumerate(STACK):
    h = t * SCALE
    y1, y2 = y, y + h
    if kind == "cu":
        rect(X0, y1, X0 + SEC_W, y2, w=0.05, fill=True)
    else:
        rect(X0, y1, X0 + SEC_W, y2, w=0.1)
        if kind == "core":
            d.hatch(X0, y1, X0 + SEC_W, y2)
    ymid = (y1 + y2) / 2
    yrow = row0 + ROW * (i + 0.5)
    # leader: section edge -> elbow -> label row
    line(X0 + SEC_W, ymid, X0 + SEC_W + 2.5, ymid, 0.08)
    line(X0 + SEC_W + 2.5, ymid, X0 + SEC_W + 6.0, yrow, 0.08)
    line(X0 + SEC_W + 6.0, yrow, cx["layer"] - 1.0, yrow, 0.08)
    bold = kind == "cu"
    if name:
        text(name, cx["layer"], yrow, size=1.2, th=0.2 if bold else 0.15, bold=bold)
    if func:
        text(func, cx["func"], yrow, size=1.2, th=0.2, bold=True)
    text(mat, cx["mat"], yrow, size=1.2)
    text(f"{t:.4f} mm" if t < 0.2 else f"{t:.3f} mm", cx["th"], yrow, size=1.2)
    text("-" if dk is None else f"{dk:.2f}", cx["dk"], yrow, size=1.2)
    y = y2

ybot = ysec + sec_h + 1.0
line(cx["layer"] - 1.0, ybot, xend, ybot, 0.15)
text(f"Total {TOTAL:.3f} mm (+ solder mask, Dk 3.8)", cx["mat"], ybot + 2.0, size=1.2, th=0.2, bold=True)

# ---------------------------------------------------------------- impedance table
yi = ybot + 7.0
text("CONTROLLED IMPEDANCE  (order with impedance control)", X0, yi, size=1.5, th=0.25, bold=True)
ih = yi + 3.5
icol = [X0, X0 + 15.0, X0 + 46.0, X0 + 55.0, X0 + 65.0, X0 + 75.0, xend]
heads = ["Target", "Signals", "Layer", "W mm", "S mm", "Reference"]
IROW = 3.0
rows = len(IMP) + 1
rect(icol[0], ih, icol[-1], ih + IROW * rows, w=0.15)
for c in icol[1:-1]:
    line(c, ih, c, ih + IROW * rows, 0.08)
for r in range(1, rows):
    yy = ih + IROW * r
    # group the L1 + L4 rows of one class visually
    line(icol[0] if r % 2 == 1 else icol[2], yy, icol[-1], yy, 0.15 if r == 1 else 0.08)
for c, hd in zip(icol, heads):
    text(hd, c + 1.0, ih + IROW / 2, size=1.1, th=0.2, bold=True)
for r, row in enumerate(IMP, start=1):
    yy = ih + IROW * (r + 0.5)
    for k, (c, val) in enumerate(zip(icol, row)):
        if not val:
            continue
        # target and signals span the L1 + L4 row pair
        text(val, c + 1.0, yy + (IROW / 2 if k < 2 else 0), size=1.1, bold=(k == 0), th=0.2 if k == 0 else 0.15)

# W/S/H geometry sketch
ys = ih + IROW * rows + 4.0
text("Geometry", X0, ys, size=1.1, th=0.2, bold=True)
sx = X0
pw = 44.0
yp = ys + 9.0                       # reference plane
gh = 1.4                            # trace height
yt = yp - 4.0                       # trace bottom
rect(sx, yp, sx + pw, yp + 1.0, w=0.05, fill=True)
text("Reference plane (GND)", sx + pw + 1.5, yp + 0.5, size=1.0)
line(sx, yt, sx + pw, yt, 0.05)     # laminate surface
tw, ts = 9.0, 7.0
t1 = sx + 8.0
t2 = t1 + tw + ts
rect(t1, yt - gh, t1 + tw, yt, w=0.05, fill=True)
rect(t2, yt - gh, t2 + tw, yt, w=0.05, fill=True)
yd = yt - gh - 1.5
line(t1, yd, t1 + tw, yd, 0.08)
line(t1 + tw, yd, t2, yd, 0.08)
for xx in (t1, t1 + tw, t2):
    line(xx, yd - 0.6, xx, yd + 0.6, 0.08)
text("W", t1 + tw / 2 - 0.5, yd - 1.2, size=1.0)
text("S", t1 + tw + ts / 2 - 0.4, yd - 1.2, size=1.0)
xh = t2 + tw + 3.0
line(xh, yt, xh, yp, 0.08)
for yy in (yt, yp):
    line(xh - 0.6, yy, xh + 0.6, yy, 0.08)
text("H = dielectric to reference", xh + 1.0, (yt + yp) / 2, size=1.0)
text("SE: one trace of width W", sx + pw + 1.5, yt - gh, size=1.0)

# ---------------------------------------------------------------- notes
yn = yp + 5.0
notes = [
    "Notes",
    "1. Widths from a 2D field solve: solder mask Dk 3.8, 30 µm over laminate, 15 µm over Cu;",
    "   rectangular trace profile. Expect about ±5 %. Confirm in the JLCPCB impedance",
    "   calculator for JLC04161H-2116 before ordering.",
    "2. L1 references L2 GND (0.1164 mm). L2 is unbroken under every controlled trace.",
    "   L4 references L3: route controlled traces there only over GND copper on L3.",
    "   Pours keep 0.3 mm from controlled traces.",
    "3. Dk per JLCPCB: prepreg 2116 4.16, core 4.6 (test frequency not stated).",
]
for i, n in enumerate(notes):
    text(n, X0, yn + i * 2.4, size=1.1 if i else 1.3, th=0.2 if i == 0 else 0.15, bold=(i == 0))

# ---------------------------------------------------------------- fabrication notes
# below the board, vendor-neutral (doc/v2-pcb.md section 6)
FAB_NOTES = [
    "1. Build to IPC-6012 Class 2. 4-layer rigid FR-4, Tg >= 150 °C, rated for lead-free assembly.",
    "   Reference build: JLCPCB stackup JLC04161H-2116, Tg 155 option.",
    "2. Finished board thickness 1.60 mm ±10 %.",
    "3. Finished copper: outer layers 1 oz (35 µm), inner layers 0.5 oz.",
    "4. Layer order and use per the stackup table. Dielectric thicknesses are nominal; other",
    "   materials and constructions are acceptable if the impedance targets and the finished",
    "   thickness are met and L1-L2 and L3-L4 each stay <= 0.15 mm.",
    "5. Controlled impedance per the table, ±10 %. The fab may change the width of controlled",
    "   traces by up to ±0.025 mm (keeping the pair pitch) to meet the targets. No TDR report needed.",
    "6. Surface finish ENIG. LPI solder mask both sides, Dk about 3.8.",
    "7. Vias are plated through-holes, smallest finished hole 0.3 mm, tented both sides.",
    "8. Outline routed, ±0.2 mm or better. The two 79.5 mm edges slide in card guides: no V-cut,",
    "   and no break-off tabs or tab remains on any edge. The solder mask is open along those",
    "   two edges on purpose: 3 mm strips of bare laminate, both sides.",
    "9. J1 and J2 need plated slots of 0.4 x 0.9, 0.5 x 1.1 and 0.5 x 1.5 mm and a non-plated slot",
    "   of 0.65 x 0.95 mm, see the drill table. Do not enlarge or round them without asking.",
]
text("FABRICATION NOTES", FX, FY, size=1.5, th=0.25, bold=True)
for i, n in enumerate(FAB_NOTES):
    text(n, FX, FY + 3.0 + i * 2.4, size=1.1)


# ---------------------------------------------------------------- drill table
DROW = 3.0


def holes(s):
    """{(plated, x, y): [count, refs]} from the board's vias and pads; y is None for a round hole."""
    tab = {}

    def add(key, ref):
        e = tab.setdefault(key, [0, set()])
        e[0] += 1
        if ref:
            e[1].add(ref)

    for item, is_item in blocks(s):
        if not is_item:
            continue
        if item.startswith("\t(via\n"):
            add((True, float(re.search(r"\(drill ([\d.]+)", item).group(1)), None), None)
        elif item.startswith("\t(footprint "):
            ref = re.search(r'\(property "Reference" "([^"]+)"', item).group(1)
            for p in re.finditer(r'^\t\t\(pad "[^"]*" (thru_hole|np_thru_hole) .*?^\t\t\)$', item, re.S | re.M):
                m = re.search(r"\(drill (?:oval )?([\d.]+)(?: ([\d.]+))?", p.group(0))
                x = float(m.group(1))
                y = float(m.group(2)) if m.group(2) and float(m.group(2)) != x else None
                add((p.group(1) == "thru_hole", x, y), ref)
    return tab


def natural(ref):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", ref)]


def drill_table(s):
    tab = holes(s)
    rows = sorted(tab.items(), key=lambda kv: (not kv[0][0], kv[0][1], kv[0][2] or 0))
    n_pth = sum(c for (pl, _, _), (c, _) in tab.items() if pl)
    n_npth = sum(c for (pl, _, _), (c, _) in tab.items() if not pl)
    text(f"DRILL TABLE  {n_pth} PTH, {n_npth} NPTH", DX, DY, size=1.5, th=0.25, bold=True)
    dcol = [DX, DX + 13.0, DX + 23.0, DX + 31.0, DX + 46.0]
    top = DY + 1.5
    bottom = top + DROW * (len(rows) + 1)
    rect(dcol[0], top, dcol[-1], bottom, w=0.15)
    for c in dcol[1:-1]:
        line(c, top, c, bottom, 0.08)
    for r in range(1, len(rows) + 1):
        line(dcol[0], top + DROW * r, dcol[-1], top + DROW * r, 0.15 if r == 1 else 0.08)
    for c, hd in zip(dcol, ["Hole Ø mm", "Type", "Qty", "Used by"]):
        text(hd, c + 1.0, top + DROW / 2, size=1.1, th=0.2, bold=True)
    for r, ((plated, x, y), (count, refs)) in enumerate(rows, start=1):
        size = f"{x:.2f} × {y:.2f}" if y else f"{x:.2f}"
        kind = ("PTH" if plated else "NPTH") + (" slot" if y else "")
        used = ", ".join(sorted(refs, key=natural)) if refs else "Vias"
        yy = top + DROW * (r + 0.5)
        for c, val in zip(dcol, (size, kind, str(count), used)):
            text(val, c + 1.0, yy, size=1.1)


if __name__ == "__main__":
    src = sys.argv[1]
    drill_table(open(src, encoding="utf-8").read().replace("\r\n", "\n"))
    replace(src, sys.argv[2] if len(sys.argv) > 2 else src, GROUP, [d])
    print(f"laminate {TOTAL:.4f} mm")
