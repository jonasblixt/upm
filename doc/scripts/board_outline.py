#!/usr/bin/env python3
"""Board outline and enclosure drawing for the Hammond 1455A802.

Draws, as one locked group "Outline 1455A802":
  Edge.Cuts        the outline
  F.Cu, B.Cu       a rule area over each rail strip: no tracks, vias, pads,
                   pours or footprints where the card guides hold the board
  F.Mask, B.Mask   an opening over each rail strip: bare laminate is about
                   0.06 mm thinner in the 1.63 mm guides than with mask on it
  User.Enclosure   (User.1) the rail strips, bezel sides, an end view of the
                   enclosure with the board in it, and the mechanical notes
  User.Dimensions  (User.4) the outline dimensions

A previous copy of the group is removed first, so the script can be re-run
after changing the values below. It replaces the whole outline: cut-outs
added by hand in KiCad are not in the group and stay, but check them. Close
the board in KiCad before running it.

    python doc/scripts/board_outline.py hw/v2/upm-v2.kicad_pcb

The numbers are from Hammond's drawing (datasheets/1455A802.pdf) and their
STEP model; doc/v2-pcb.md section 1 has the reasoning.
"""
import sys

from kicad_draw import Drawing, replace

GROUP = "Outline 1455A802"

# ------------------------------------------------------------ enclosure
EXTRUSION_L = 81.0      # +-0.5
BEZEL_STEP = 0.5        # each bezel reaches this far into the extrusion
GUIDE_SPAN = 61.88      # +-0.51, bottom of one card guide to the other
GUIDE_DEPTH = 2.29      # how far the lips reach in over the board
GUIDE_GAP = 1.63        # card guide opening
CLEAR_TOP = 4.45        # board top to the inside of the extrusion
CLEAR_BOT = 2.92        # board bottom to the inside of the extrusion
OUTER_W, OUTER_H = 70.0, 12.0
CAVITY_H = 9.0
SCREW_SPAN = 63.5       # between the two screw channels
BOSS_R, SCREW_R = 3.07, 1.5

# ------------------------------------------------------------ board
BOARD_L = 79.5          # along the rails: fits the shortest extrusion (80.5 - 2 x 0.5)
BOARD_W = 60.0          # across the rails
BOARD_T = 1.6
CHAMFER = 1.0           # corner lead-in for the card guides
RAIL = 3.0              # strip along each long edge kept free of parts and outer copper

OX, OY = 30.0, 30.0     # top-left corner of the board on the sheet

edge = Drawing("Edge.Cuts")
mech = Drawing("User.1")
dims = Drawing("User.4")
rule = Drawing("F.Cu")
mask = Drawing("F.Mask")

# ------------------------------------------------------------ outline
x0, y0, x1, y1, c = OX, OY, OX + BOARD_L, OY + BOARD_W, CHAMFER
pts = [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c),
       (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]
for a, b in zip(pts, pts[1:] + pts[:1]):
    edge.line(a[0], a[1], b[0], b[1], w=0.05)

# ------------------------------------------------------------ rail strips
for name, ya, yb in (("RAIL_TOP", y0, y0 + RAIL), ("RAIL_BOTTOM", y1 - RAIL, y1)):
    rule.keepout(name, ["F.Cu", "B.Cu"], [(x0, ya), (x1, ya), (x1, yb), (x0, yb)])
    for layer in ("F.Mask", "B.Mask"):
        mask.rect(x0, ya, x1, yb, w=0, fill=True, layer=layer)
    yl = yb if ya == y0 else ya
    mech.line(x0, yl, x1, yl, w=0.1)
    mech.text(f"RAIL {RAIL:.1f} mm: in the card guide. No parts, no copper on L1 / L4, no mask",
              (x0 + x1) / 2, (ya + yb) / 2, size=1.0, just=None)
mech.text("BEZEL A", x0 - 2.0, (y0 + y1) / 2, size=1.2, th=0.2, just=None, angle=90, bold=True)
mech.text("BEZEL B", x1 + 9.0, (y0 + y1) / 2, size=1.2, th=0.2, just=None, angle=90, bold=True)

dims.dimension(x0, y1, x1, y1, 4.0)
dims.dimension(x1, y0, x1, y1, 4.0, vertical=True)

# ------------------------------------------------------------ end view
cx, cy = (x0 + x1) / 2, y1 + 22.0
mech.text("END VIEW  1:1, simplified", cx - OUTER_W / 2, cy - OUTER_H / 2 - 2.5,
          size=1.2, th=0.2, bold=True)
r_out, r_in = OUTER_H / 2, CAVITY_H / 2
flat = OUTER_W / 2 - r_out
for r in (r_out, r_in):
    mech.line(cx - flat, cy - r, cx + flat, cy - r)
    mech.line(cx - flat, cy + r, cx + flat, cy + r)
    for sgn in (-1, 1):
        mech.arc((cx + sgn * flat, cy - r), (cx + sgn * (flat + r), cy), (cx + sgn * flat, cy + r))
for sgn in (-1, 1):
    mech.circle(cx + sgn * SCREW_SPAN / 2, cy, BOSS_R)
    mech.circle(cx + sgn * SCREW_SPAN / 2, cy, SCREW_R)
# the board: its top face sits at the middle of the cavity, CLEAR_TOP below the roof
top = cy - r_in + CLEAR_TOP
mech.rect(cx - BOARD_W / 2, top, cx + BOARD_W / 2, top + BOARD_T, w=0.05, fill=True)
mech.text(f"{CLEAR_TOP:.2f} above", cx, top - CLEAR_TOP / 2, size=1.0, just=None)
mech.text(f"{CLEAR_BOT:.2f} below", cx, top + BOARD_T + CLEAR_BOT / 2, size=1.0, just=None)
for sgn in (-1, 1):                     # where the guide lips end
    xl = cx + sgn * (GUIDE_SPAN / 2 - GUIDE_DEPTH)
    mech.line(xl, cy - r_in, xl, cy + r_in, w=0.05)
mech.text("guide lips end here", cx + GUIDE_SPAN / 2 - GUIDE_DEPTH - 1.0, cy - r_in + 1.2,
          size=0.8, th=0.12, just="right")

# ------------------------------------------------------------ notes
between = EXTRUSION_L - 2 * BEZEL_STEP
NOTES = [
    "ENCLOSURE  Hammond 1455A802 (datasheets/1455A802.pdf)",
    f"1. Board {BOARD_L:.1f} x {BOARD_W:.1f} x {BOARD_T:.1f} mm. It slides into the extrusion's card guides along",
    f"   the {BOARD_L:.1f} mm edges and is held by the two bezels. No mounting holes.",
    f"2. Length: the extrusion is {EXTRUSION_L:.1f} ±0.5 and each bezel reaches {BEZEL_STEP:.1f} into it, which leaves",
    f"   {between - 0.5:.1f} to {between + 0.5:.1f} mm between the bezels. {BOARD_L:.1f} fits the shortest.",
    f"3. Width: the guides are {GUIDE_SPAN:.2f} ±0.51 apart at their bottoms and {GUIDE_DEPTH:.2f} deep, {GUIDE_GAP:.2f} high.",
    f"4. Rail strips, {RAIL:.1f} mm along both long edges, both sides: no parts, no copper on L1 / L4,",
    "   no solder mask. Bare, they are about 1.53 mm thick on a nominal board.",
    f"5. Clear height {CLEAR_TOP:.2f} mm above the top side and {CLEAR_BOT:.2f} mm below the bottom side.",
    "   Design to 4.0 and 2.5 mm.",
    "6. Bezels: 2.5 mm thick over a 55.5 x 8.86 mm panel area, centred. The board's top face",
    "   is on the centre line of the bezel.",
]
yn = cy + OUTER_H / 2 + 6.0
for i, n in enumerate(NOTES):
    mech.text(n, x0, yn + i * 2.4, size=1.3 if i == 0 else 1.1, th=0.2 if i == 0 else 0.15, bold=(i == 0))

if __name__ == "__main__":
    src = sys.argv[1]
    replace(src, sys.argv[2] if len(sys.argv) > 2 else src, GROUP, [edge, rule, mask, mech, dims])
