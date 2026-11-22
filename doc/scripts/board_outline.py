#!/usr/bin/env python3
"""Board outline and enclosure drawing for the Hammond 1455A802.

Draws, as one locked group "Outline 1455A802":
  Edge.Cuts        the outline, with cut-outs for the mid-mount USB-C
                   receptacles (two in bezel A's end, one in bezel B's), a
                   notch for the light pipe and one for the output header
  F.Cu, B.Cu       a rule area over each rail strip: no tracks, vias, pads,
                   pours or footprints where the card guides hold the board
  F.Mask, B.Mask   an opening over each rail strip: bare laminate is about
                   0.06 mm thinner in the 1.63 mm guides than with mask on it
  User.Enclosure   (User.1) the rail strips, bezel sides, an end view of each
                   bezel with the board and the openings in it, and the
                   mechanical notes
  User.Dimensions  (User.4) the outline dimensions

A previous copy of the group is removed first, so the script can be re-run
after changing the values below. It replaces the whole outline: cut-outs
added by hand in KiCad are not in the group and stay, but check them. Close
the board in KiCad before running it.

    python doc/scripts/board_outline.py hw/v2/upm-v2.kicad_pcb

J1, J2, J3, J4 and D1 sit in these cut-outs. Their positions are in
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
PANEL_W = 55.5          # the bezel's panel area (label recess), centred
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
# USB-C: Wurth 632723130112. J2 (to the DUT) in the middle of bezel B; J1 (host)
# and J4 (PD power input) on bezel A, equally spaced across its panel: centres a
# third of the panel apart, PANEL_W / 6 either side of the middle (2026-11-20).
# Seen from outside bezel A with the top side up, J1 is on the left (towards the
# board's top edge, y0) and J4 on the right. From its data sheet: cut-out 9.5
# wide; the board edge is drawn 5.25 beyond the lower through-hole row, the
# cut-out's inner edge 0.55.
USB_Y = BOARD_W / 2     # J2, across the board, from the top edge
J1_Y = USB_Y - PANEL_W / 6      # 20.75: 9.25 left of the middle seen from outside bezel A
J4_Y = USB_Y + PANEL_W / 6      # 39.25: 9.25 right of it
USB_CUT_W = 9.5
USB_CUT_D = 4.70
USB_RELIEF = 0.5        # radius of the relief at the cut-out's inner corners
USB_REACH = 2.51        # mating face beyond the board end
# The shell's mouth, from Wurth's STEP: 9.20 x 3.42, its ends arcs of radius
# 1.48 centred 3.12 either side of the middle and 0.23 above and below the
# centre line, joined by short straight flanks. The bezel opening follows it
# at USB_CLEAR all round: 9.80 x 4.02 with the same arc centres.
USB_SHELL = (9.20, 3.42)
USB_SHELL_R = 1.48
USB_CLEAR = 0.3
USB_ABOVE = 0.29        # shell centre above the board's top face (data sheet detail B, Wurth's STEP)
# Open-drain outputs, bezel B: Samtec HTSW-104-08-L-S laid flat in a notch in
# the board end (footprint Jonas:Samtec_HTSW-104-08-L-S_EdgeMount, which holds
# the same numbers). The post tips end USB_REACH beyond the board end, like
# J2's mating face, so the bezel opening is the shroud: a Dupont housing goes
# through it and into the notch. The insulator (10.16 x 2.49 seen from
# outside, 2.54 long) sits against the notch's inner wall; its pin row is about
# 0.35 above the board's top face (0.32 to the pin centre plus the solder).
HDR_Y = USB_Y + 15.0    # 15 mm to the left of J2, seen from outside
HDR_POST = 5.84         # lead style -08
# A Harwin M20-1060400 crimp housing (drawing M20-106XX00) is 10.36 +-0.30 wide and
# 2.50 (+-0.20) thick. The notch moves with the board and passes the largest with 0.27
# per side. The bezel opening has to allow for the board as well: it can shift sideways
# in the card guides until J2's shell meets its opening, 0.30 either way, which leaves
# 0.22 per side at worst (checked in mech/upm-v2-assembly.sc).
HDR_CUT_W = 11.2
HDR_CUT_D = HDR_POST + 2.54 - USB_REACH     # to the insulator's rear face, 5.87
HDR_RELIEF = 0.5
HDR_OPENING = (11.7, 3.3)   # bezel opening: 10.66 + 2 x 0.30 + 2 x 0.22; 2.70 + 2 x 0.30
HDR_ABOVE = 0.35
# Light pipe: Dialight 515-1351-0188F in bezel B, lit by D1 (Wurth
# 155124M173200, side view) through a notch in the board end. Its 5.0 mm head rests
# on the 0.53 mm label; the pipe is 4.77 long below the head, press fit by four ribs
# (4.11) in the hole, and 3.56 wide where it reaches behind the bezel.
PIPE_Y = USB_Y - 12.0   # 12 mm to the right of the connector, seen from outside
PIPE_HOLE = 3.96        # 0.156" +-0.002, straight (Dialight 515 VPM 5 mm data sheet)
PIPE_HEAD = 5.0
PIPE_TIP = 3.56         # its diameter behind the bezel
LABEL_T = 0.53          # 0.4 PET + 0.13 3M 468MP, fills the recess
PIPE_BEHIND = 4.77 - 2.5 - LABEL_T  # 1.74 behind the bezel
# The notch is as deep as the pipe reaches when the board touches bezel B, plus 0.26:
# D1's lens is at the bottom of the notch, so the gap to the pipe is 0.26 to 0.76 mm
# over the board's 0.5 mm end play (Dialight's drawing shows 0.26 to 0.50). As wide
# as the pipe plus the board's 0.30 sideways play plus 0.32 a side.
NOTCH_W, NOTCH_D, NOTCH_R = 4.8, 2.0, 0.5
LED_LENS = 1.25         # D1's origin (middle of its base) to the tip of its lens

edge = Drawing("Edge.Cuts")
mech = Drawing("User.1")
dims = Drawing("User.4")
rule = Drawing("F.Cu")
mask = Drawing("F.Mask")

# ------------------------------------------------------------ outline
x0, y0, x1, y1, c = OX, OY, OX + BOARD_L, OY + BOARD_W, CHAMFER
Q = math.sqrt(0.5)


def cutout(xe, sgn, ya, yb, depth=USB_CUT_D, r=USB_RELIEF):
    """Path of a connector cut-out in the end at x = xe, from wall ya to wall yb.
    sgn is +1 where the board lies towards +x of that end. The inner corners
    are relieved with a half circle on each wall, so a square body fits."""
    xi = xe + sgn * depth
    d = 1 if yb > ya else -1
    return [("L", (xe, ya), (xi - sgn * 2 * r, ya)),
            ("A", (xi - sgn * 2 * r, ya), (xi - sgn * r, ya - d * r), (xi, ya)),
            ("L", (xi, ya), (xi, yb)),
            ("A", (xi, yb), (xi - sgn * r, yb + d * r), (xi - sgn * 2 * r, yb)),
            ("L", (xi - sgn * 2 * r, yb), (xe, yb))]


yu, yp, r = OY + USB_Y, OY + PIPE_Y, NOTCH_R
ua, ub = yu - USB_CUT_W / 2, yu + USB_CUT_W / 2
ha, hb = OY + HDR_Y - HDR_CUT_W / 2, OY + HDR_Y + HDR_CUT_W / 2
na, nb, xn = yp - NOTCH_W / 2, yp + NOTCH_W / 2, x1 - NOTCH_D
path = [("L", (x0 + c, y0), (x1 - c, y0)), ("L", (x1 - c, y0), (x1, y0 + c)),
        # bezel B end, top to bottom: light pipe notch, J2, then J3
        ("L", (x1, y0 + c), (x1, na)), ("L", (x1, na), (xn + r, na)),
        ("A", (xn + r, na), (xn + r - r * Q, na + r - r * Q), (xn, na + r)),
        ("L", (xn, na + r), (xn, nb - r)),
        ("A", (xn, nb - r), (xn + r - r * Q, nb - r + r * Q), (xn + r, nb)),
        ("L", (xn + r, nb), (x1, nb)), ("L", (x1, nb), (x1, ua))]
path += cutout(x1, -1, ua, ub)
path += [("L", (x1, ub), (x1, ha))]     # then J3's notch
path += cutout(x1, -1, ha, hb, HDR_CUT_D, HDR_RELIEF)
path += [("L", (x1, hb), (x1, y1 - c)), ("L", (x1, y1 - c), (x1 - c, y1)),
         ("L", (x1 - c, y1), (x0 + c, y1)), ("L", (x0 + c, y1), (x0, y1 - c))]
# bezel A end, bottom to top: J4, then J1
ya = y1 - c
for yc in (OY + J4_Y, OY + J1_Y):
    path += [("L", (x0, ya), (x0, yc + USB_CUT_W / 2))]
    path += cutout(x0, 1, yc + USB_CUT_W / 2, yc - USB_CUT_W / 2)
    ya = yc - USB_CUT_W / 2
path += [("L", (x0, ya), (x0, y0 + c)), ("L", (x0, y0 + c), (x0 + c, y0))]
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
mech.text("BEZEL A  J1 host, J4 power in", x0 - 5.5, (y0 + y1) / 2, size=1.2, th=0.2, just=None, angle=90, bold=True)
mech.text("BEZEL B  USB out, light pipe, outputs", x1 + 11.5, (y0 + y1) / 2, size=1.2, th=0.2, just=None,
          angle=90, bold=True)
# the light pipe, where it ends when the board touches bezel B
mech.rect(x1 - PIPE_BEHIND, yp - PIPE_TIP / 2, x1 + 2.5 + LABEL_T, yp + PIPE_TIP / 2, w=0.05)

dims.dimension(x0, y1, x1, y1, 4.0)
dims.dimension(x1, y0, x1, y1, 7.0, vertical=True)

# ------------------------------------------------------------ end views
r_out, r_in = OUTER_H / 2, CAVITY_H / 2
flat = OUTER_W / 2 - r_out
aw, ah = USB_SHELL[0] + 2 * USB_CLEAR, USB_SHELL[1] + 2 * USB_CLEAR
ar = USB_SHELL_R + USB_CLEAR
ex, ez = aw / 2 - ar, ah / 2 - ar           # arc centres, from the middle of the opening
hw_, hh = HDR_OPENING


def end_view(cx, cy, title, side):
    """The enclosure seen from outside one bezel, 1:1, with the board in it.
    side is +1 for bezel B, where the board's top edge (y0) is to the right,
    and -1 for bezel A, where it is to the left. Returns the board's top face."""
    def vx(y):                              # across the board -> across the view
        return cx + side * (BOARD_W / 2 - y)

    mech.text(title, cx - OUTER_W / 2, cy - OUTER_H / 2 - 2.5, size=1.2, th=0.2, bold=True)
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
    mech.text(f"{CLEAR_TOP:.2f} above", cx + 21.0, top - 1.5, size=1.0, just=None)
    mech.text(f"{CLEAR_BOT:.2f} below", cx + 21.0, top + BOARD_T + CLEAR_BOT / 2, size=1.0, just=None)
    for sgn in (-1, 1):                     # where the guide lips end
        xl = cx + sgn * (GUIDE_SPAN / 2 - GUIDE_DEPTH)
        mech.line(xl, cy - r_in, xl, cy + r_in, w=0.05)
    mech.text("guide lips end here", cx + GUIDE_SPAN / 2 - GUIDE_DEPTH - 1.0, cy - r_in + 1.0,
              size=0.8, th=0.12, just="right")
    return vx, top


def usb_opening(ux, uy, label, cy):
    for s in (-1, 1):
        mech.line(ux - ex, uy + s * ah / 2, ux + ex, uy + s * ah / 2, w=0.15)     # top, bottom
        mech.line(ux + s * aw / 2, uy - ez, ux + s * aw / 2, uy + ez, w=0.15)     # flanks
        for t in (-1, 1):                                                          # four arcs
            a0 = (ux + s * ex, uy + t * ah / 2)
            a1 = (ux + s * aw / 2, uy + t * ez)
            mid = (ux + s * (ex + ar * Q), uy + t * (ez + ar * Q))
            mech.arc(a0, mid, a1, w=0.15)
    mech.text(label, ux, cy + r_out + 1.3, size=0.8, th=0.12, just=None)


# bezel B: J2, the light pipe and the outputs
cx, cy = (x0 + x1) / 2, y1 + 22.0
vx, top = end_view(cx, cy, "BEZEL B FROM OUTSIDE  1:1, simplified", 1)
usb_opening(vx(USB_Y), top - USB_ABOVE, "USB-C J2, to the DUT", cy)
hx, hy = vx(HDR_Y), top - HDR_ABOVE
mech.rect(hx - hw_ / 2, hy - hh / 2, hx + hw_ / 2, hy + hh / 2, w=0.15)
px = vx(PIPE_Y)
mech.circle(px, cy, PIPE_HOLE / 2, w=0.15)
mech.circle(px, cy, PIPE_HEAD / 2, w=0.05)     # the pipe's head, on the label
mech.text("light pipe", px, cy + r_out + 1.3, size=0.8, th=0.12, just=None)
mech.text("outputs, pin 1 left", hx, cy + r_out + 1.3, size=0.8, th=0.12, just=None)

# bezel A: J1 and J4
cya = cy + OUTER_H + 10.0
vxa, topa = end_view(cx, cya, "BEZEL A FROM OUTSIDE  1:1, simplified", -1)
usb_opening(vxa(J1_Y), topa - USB_ABOVE, "USB-C J1, host", cya)
usb_opening(vxa(J4_Y), topa - USB_ABOVE, "USB-C J4, PD power in", cya)

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
    f"7. USB-C, J1 and J4 on bezel A, J2 on bezel B: Wurth 632723130112 in a {USB_CUT_W:.1f} x {USB_CUT_D:.1f} mm cut-out,",
    f"   mating face {USB_REACH:.1f} mm past the board end. The bezel opening follows the shell ({USB_SHELL[0]:.2f} x {USB_SHELL[1]:.2f}, ends",
    f"   R {USB_SHELL_R:.2f}) {USB_CLEAR:.1f} mm all round: {aw:.2f} x {ah:.2f} mm, ends R {ar:.2f} with straight flanks {2 * ez:.2f} mm long.",
    f"   Its centre {USB_ABOVE:.2f} mm above the board's top face. J2 in the middle of bezel B. J1 and J4 equally spaced",
    f"   on bezel A's {PANEL_W:.1f} mm panel, {PANEL_W / 6:.2f} mm either side of the middle: J1 (host) on the left",
    "   seen from outside, J4 (PD power in) on the right.",
    f"8. Light pipe, bezel B: Dialight 515-1351-0188F, its {PIPE_HEAD:.1f} mm head on the label. Hole {PIPE_HOLE:.2f} mm,",
    f"   straight, on the bezel's centre line, {USB_Y - PIPE_Y:.1f} mm right of the connector seen from outside.",
    f"   It ends {PIPE_BEHIND:.2f} mm behind the bezel, in the {NOTCH_W:.1f} x {NOTCH_D:.1f} mm notch in front of D1.",
    f"9. Outputs, bezel B: Samtec HTSW-104-08-L-S laid flat on the top side in a {HDR_CUT_W:.1f} x {HDR_CUT_D:.2f} mm notch,",
    f"   post tips {USB_REACH:.2f} mm past the board end like the USB-C face: the opening is the shroud, a Dupont housing",
    f"   goes in. Opening {hw_:.2f} x {hh:.2f} mm (corners up to R 0.5), {HDR_Y - USB_Y:.1f} mm left of the connector",
    f"   seen from outside, its centre {HDR_ABOVE:.2f} mm above the board's top face. Pin 1 on the left.",
]
yn = cya + OUTER_H / 2 + 8.0
for i, n in enumerate(NOTES):
    mech.text(n, x0, yn + i * 2.4, size=1.3 if i == 0 else 1.1, th=0.2 if i == 0 else 0.15, bold=(i == 0))

if __name__ == "__main__":
    src = sys.argv[1]
    replace(src, sys.argv[2] if len(sys.argv) > 2 else src, GROUP, [edge, rule, mask, mech, dims])
