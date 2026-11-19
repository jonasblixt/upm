#!/usr/bin/env python3
"""Board outline and enclosure drawing for the Hammond 1455A802.

Draws, as one locked group "Outline 1455A802":
  Edge.Cuts        the outline, with a cut-out in each end for the mid-mount
                   USB-C receptacles and a notch for the light pipe
  F.Cu, B.Cu       a rule area over each rail strip: no tracks, vias, pads,
                   pours or footprints where the card guides hold the board
  F.Mask, B.Mask   an opening over each rail strip: bare laminate is about
                   0.06 mm thinner in the 1.63 mm guides than with mask on it
  User.Enclosure   (User.1) the rail strips, bezel sides, an end view of the
                   enclosure with the board and the bezel openings in it,
                   and the mechanical notes
  User.Dimensions  (User.4) the outline dimensions

A previous copy of the group is removed first, so the script can be re-run
after changing the values below. It replaces the whole outline: cut-outs
added by hand in KiCad are not in the group and stay, but check them. Close
the board in KiCad before running it.

    python doc/scripts/board_outline.py hw/v2/upm-v2.kicad_pcb

J1, J2 and D1 sit in these cut-outs. Their positions are in
place_fixed_parts.py, which imports the constants below: run it after this
script when they change.

The numbers are from Hammond's drawing (datasheets/1455A802.pdf) and their
STEP model; doc/v2-pcb.md section 1 has the reasoning.
"""
import math
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

# ------------------------------------------------------------ bezel parts
# USB-C: Wurth 632723130112, one in the middle of each end (J1 bezel A, J2
# bezel B). From its data sheet: cut-out 9.5 wide; the board edge is drawn
# 5.25 beyond the lower through-hole row, the cut-out's inner edge 0.55.
USB_Y = BOARD_W / 2     # across the board, from the top edge
USB_CUT_W = 9.5
USB_CUT_D = 4.70
USB_RELIEF = 0.5        # radius of the relief at the cut-out's inner corners
USB_REACH = 2.51        # mating face beyond the board end
USB_APERTURE = (10.2, 4.0)   # bezel opening: shell 9.65 x 3.42 at the mouth
USB_ABOVE = 0.29        # shell centre above the board's top face (data sheet detail B, Wurth's STEP)
# Light pipe: Dialight 515-1313-0125F in bezel B, lit by D1 (Wurth
# 155124M173200, side view) through a notch in the board end.
PIPE_Y = USB_Y - 12.0   # 12 mm to the right of the connector, seen from outside
PIPE_HOLE = 3.05        # 60 degree countersink to 3.25
PIPE_BEHIND = 0.7       # the 3.2 mm pipe reaches this far behind the 2.5 mm bezel
NOTCH_W, NOTCH_D, NOTCH_R = 3.6, 1.3, 0.5
LED_LENS = 1.25         # D1's origin (middle of its base) to the tip of its lens

edge = Drawing("Edge.Cuts")
mech = Drawing("User.1")
dims = Drawing("User.4")
rule = Drawing("F.Cu")
mask = Drawing("F.Mask")

# ------------------------------------------------------------ outline
x0, y0, x1, y1, c = OX, OY, OX + BOARD_L, OY + BOARD_W, CHAMFER
Q = math.sqrt(0.5)


def usb_cutout(xe, sgn, ya, yb):
    """Path of a connector cut-out in the end at x = xe, from wall ya to wall yb.
    sgn is +1 where the board lies towards +x of that end. The inner corners
    are relieved with a half circle on each wall, so the square shell fits."""
    xi, r = xe + sgn * USB_CUT_D, USB_RELIEF
    d = 1 if yb > ya else -1
    return [("L", (xe, ya), (xi - sgn * 2 * r, ya)),
            ("A", (xi - sgn * 2 * r, ya), (xi - sgn * r, ya - d * r), (xi, ya)),
            ("L", (xi, ya), (xi, yb)),
            ("A", (xi, yb), (xi - sgn * r, yb + d * r), (xi - sgn * 2 * r, yb)),
            ("L", (xi - sgn * 2 * r, yb), (xe, yb))]


yu, yp, r = OY + USB_Y, OY + PIPE_Y, NOTCH_R
ua, ub = yu - USB_CUT_W / 2, yu + USB_CUT_W / 2
na, nb, xn = yp - NOTCH_W / 2, yp + NOTCH_W / 2, x1 - NOTCH_D
path = [("L", (x0 + c, y0), (x1 - c, y0)), ("L", (x1 - c, y0), (x1, y0 + c)),
        # bezel B end, top to bottom: light pipe notch, then J2
        ("L", (x1, y0 + c), (x1, na)), ("L", (x1, na), (xn + r, na)),
        ("A", (xn + r, na), (xn + r - r * Q, na + r - r * Q), (xn, na + r)),
        ("L", (xn, na + r), (xn, nb - r)),
        ("A", (xn, nb - r), (xn + r - r * Q, nb - r + r * Q), (xn + r, nb)),
        ("L", (xn + r, nb), (x1, nb)), ("L", (x1, nb), (x1, ua))]
path += usb_cutout(x1, -1, ua, ub)
path += [("L", (x1, ub), (x1, y1 - c)), ("L", (x1, y1 - c), (x1 - c, y1)),
         ("L", (x1 - c, y1), (x0 + c, y1)), ("L", (x0 + c, y1), (x0, y1 - c)),
         # bezel A end, bottom to top: J1
         ("L", (x0, y1 - c), (x0, ub))]
path += usb_cutout(x0, 1, ub, ua)
path += [("L", (x0, ua), (x0, y0 + c)), ("L", (x0, y0 + c), (x0 + c, y0))]
for seg in path:
    if seg[0] == "L":
        edge.line(*seg[1], *seg[2], w=0.05)
    else:
        edge.arc(seg[1], seg[2], seg[3], w=0.05)

# ------------------------------------------------------------ rail strips
for name, ya, yb in (("RAIL_TOP", y0, y0 + RAIL), ("RAIL_BOTTOM", y1 - RAIL, y1)):
    rule.keepout(name, ["F.Cu", "B.Cu"], [(x0, ya), (x1, ya), (x1, yb), (x0, yb)])
    for layer in ("F.Mask", "B.Mask"):
        mask.rect(x0, ya, x1, yb, w=0, fill=True, layer=layer)
    yl = yb if ya == y0 else ya
    mech.line(x0, yl, x1, yl, w=0.1)
    mech.text(f"RAIL {RAIL:.1f} mm: in the card guide. No parts, no copper on L1 / L4, no mask",
              (x0 + x1) / 2, (ya + yb) / 2, size=1.0, just=None)
mech.text("BEZEL A  USB in", x0 - 5.5, (y0 + y1) / 2, size=1.2, th=0.2, just=None, angle=90, bold=True)
mech.text("BEZEL B  USB out, light pipe", x1 + 11.5, (y0 + y1) / 2, size=1.2, th=0.2, just=None,
          angle=90, bold=True)
# the light pipe, where it ends when the board touches bezel B
mech.rect(x1 - PIPE_BEHIND, yp - 2.87 / 2, x1 + 2.5, yp + 2.87 / 2, w=0.05)

dims.dimension(x0, y1, x1, y1, 4.0)
dims.dimension(x1, y0, x1, y1, 7.0, vertical=True)

# ------------------------------------------------------------ end view
cx, cy = (x0 + x1) / 2, y1 + 22.0
mech.text("BEZEL B FROM OUTSIDE  1:1, simplified", cx - OUTER_W / 2, cy - OUTER_H / 2 - 2.5,
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
mech.text(f"{CLEAR_TOP:.2f} above", cx - 17.0, top - CLEAR_TOP / 2, size=1.0, just=None)
mech.text(f"{CLEAR_BOT:.2f} below", cx - 17.0, top + BOARD_T + CLEAR_BOT / 2, size=1.0, just=None)
# bezel openings. Seen from outside bezel B the board's top edge (y0) is to the right.
aw, ah = USB_APERTURE
ux, uy = cx + (BOARD_W / 2 - USB_Y), top - USB_ABOVE
mech.rect(ux - aw / 2, uy - ah / 2, ux + aw / 2, uy + ah / 2, w=0.15)
px = cx + (BOARD_W / 2 - PIPE_Y)
mech.circle(px, cy, PIPE_HOLE / 2, w=0.15)
mech.text("USB-C", ux, cy + r_out + 1.3, size=0.8, th=0.12, just=None)
mech.text("light pipe", px, cy + r_out + 1.3, size=0.8, th=0.12, just=None)
for sgn in (-1, 1):                     # where the guide lips end
    xl = cx + sgn * (GUIDE_SPAN / 2 - GUIDE_DEPTH)
    mech.line(xl, cy - r_in, xl, cy + r_in, w=0.05)
mech.text("guide lips end here", cx + GUIDE_SPAN / 2 - GUIDE_DEPTH - 1.0, cy - r_in + 1.0,
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
    f"7. USB-C, both bezels: Wurth 632723130112 in a {USB_CUT_W:.1f} x {USB_CUT_D:.1f} mm cut-out, mating face",
    f"   {USB_REACH:.1f} mm past the board end. Bezel opening {aw:.1f} x {ah:.1f} mm, in the middle of the bezel's",
    f"   width, its centre {USB_ABOVE:.2f} mm above the board's top face (the shell is 2.00 above, 1.42 below).",
    f"8. Light pipe, bezel B: Dialight 515-1313-0125F. Hole {PIPE_HOLE:.2f} mm, 60° countersink to 3.25 mm,",
    f"   on the bezel's centre line, {USB_Y - PIPE_Y:.1f} mm right of the connector seen from outside.",
    f"   It ends {PIPE_BEHIND:.1f} mm behind the bezel, in the {NOTCH_W:.1f} x {NOTCH_D:.1f} mm notch in front of D1.",
]
yn = cy + OUTER_H / 2 + 8.0
for i, n in enumerate(NOTES):
    mech.text(n, x0, yn + i * 2.4, size=1.3 if i == 0 else 1.1, th=0.2 if i == 0 else 0.15, bold=(i == 0))

if __name__ == "__main__":
    src = sys.argv[1]
    replace(src, sys.argv[2] if len(sys.argv) > 2 else src, GROUP, [edge, rule, mask, mech, dims])
