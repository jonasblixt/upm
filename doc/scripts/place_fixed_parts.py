#!/usr/bin/env python3
"""Places the parts whose position the enclosure fixes: J1, J2, J3, J4, D1 and E1.

J1, J2 and J4 (USB-C, Wurth 632723130112) go in their cut-outs: J2 in the
middle of bezel B's end, J1 (host) and J4 (PD power in) equally spaced on
bezel A's, D1 (side-view LED) behind the light pipe notch at
bezel B, J3 (the outputs, a Samtec HTSW-104-08-L-S laid flat) in the notch
at bezel B, 15 mm from J2. The positions come from board_outline.py. Each footprint is taken
from the library, linked to its schematic symbol, given the nets of the
netlist and locked. An existing J1, J2, J3, J4, D1 or E1 is replaced, tracks are left
alone.

E1 (the enclosure bond, a Wurth 331246501860 contact finger) goes on the top
side between J1 and J4, on the board's centre line, its pad SPRING_X from the
bezel A end, its foot end towards that end and the loop of its arm inboard. It
presses on the extrusion's roof, which has to be stripped of its anodising
there (doc/v2-pcb.md). R16, its 0603 to GND, is put next to it if it is not on
that side of the board yet; it is not locked and a later run leaves it where it
is. Nothing is on the bottom side: the board is assembled from one side.

It needs KiCad's own Python (pcbnew) and the Jonas footprint library:

    kicad-cli sch export netlist --format kicadsexpr -o upm-v2.net hw/v2/upm-v2.kicad_sch
    JONAS_KICADLIB=<kicadlib> python doc/scripts/place_fixed_parts.py hw/v2/upm-v2.kicad_pcb upm-v2.net

Close the board in KiCad first. Everything else on the board comes in
through Update PCB from Schematic as usual.
"""
import os
import re
import sys

import pcbnew

import board_outline as bo

X0, Y0, X1 = bo.OX, bo.OY, bo.OX + bo.BOARD_L
# ref: (x, y, direction the footprint's +Y points: +1 = +x, -1 = -x, check pad, where it must land)
# All five footprints have +Y towards the bezel; a pad's footprint (px, py) lands at
# (x + dir * py, y - dir * px).
PARTS = {
    "J1": (X0, Y0 + bo.J1_Y, -1, "A1", (-2.75, -7.06)),
    "J4": (X0, Y0 + bo.J4_Y, -1, "A1", (-2.75, -7.06)),
    "J2": (X1, Y0 + bo.USB_Y, 1, "A1", (-2.75, -7.06)),
    "D1": (X1 - bo.NOTCH_D - bo.LED_LENS, Y0 + bo.PIPE_Y, 1, "1", (-1.4, 0.0)),
    "J3": (X1, Y0 + bo.HDR_Y, 1, "1", (-3.81, -8.67)),
}

# The enclosure bond. ref: (x, y, angle, top side, lock and replace, check)
# E1's footprint has its origin at the pad, its foot end 1.65 towards +X and the
# loop of its arm 3.35 towards -X; the arm rises from the loop as a ramp and its
# flat top, which is what touches, is above the pad. The loop goes inboard: the
# board is pushed in bezel B end first, so the mouth of the extrusion meets the
# ramp and its roof then slides along the arm from the loop towards the tip. The
# check is where the foot end must land, 1.65 from the pad centre towards the
# bezel A end: it stops the script if the angle does not put it there.
SPRING_X = 6.5          # E1's pad centre from the bezel A end
SPRING_FOOT = 1.65
BOND = {
    "E1": (X0 + SPRING_X, Y0 + bo.BOARD_W / 2, 180.0, True, True, X0 + SPRING_X - SPRING_FOOT),
    "R16": (X0 + SPRING_X + 5.5, Y0 + bo.BOARD_W / 2, 0.0, True, False, None),
}


def sexpr(text):
    """Minimal s-expression reader: nested lists of strings."""
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    pos = 0

    def read():
        nonlocal pos
        t = tok[pos]
        pos += 1
        if t != "(":
            return t[1:-1].replace('\\"', '"') if t.startswith('"') else t
        out = []
        while tok[pos] != ")":
            out.append(read())
        pos += 1
        return out

    return read()


def find(node, key):
    return [n for n in node if isinstance(n, list) and n and n[0] == key]


def netlist(path):
    root = sexpr(open(path, encoding="utf-8").read())
    comps, nets = {}, {}
    for c in find(find(root, "components")[0], "comp"):
        ref = find(c, "ref")[0][1]
        sheet = find(find(c, "sheetpath")[0], "tstamps")[0][1]
        fields = {}
        for p in find(c, "property"):
            # flags such as exclude_from_bom have no value
            fields[find(p, "name")[0][1]] = (find(p, "value") or [[None, ""]])[0][1]
        for f in find(find(c, "fields")[0], "field") if find(c, "fields") else []:
            fields[find(f, "name")[0][1]] = f[2] if len(f) > 2 else ""
        comps[ref] = dict(value=find(c, "value")[0][1], footprint=find(c, "footprint")[0][1],
                          path=sheet.rstrip("/") + "/" + find(c, "tstamps")[0][1],
                          datasheet=(find(c, "datasheet") or [[None, ""]])[0][1],
                          description=(find(c, "description") or [[None, ""]])[0][1], fields=fields)
    for n in find(find(root, "nets")[0], "net"):
        name = find(n, "name")[0][1]
        for node in find(n, "node"):
            nets[(find(node, "ref")[0][1], find(node, "pin")[0][1])] = name
    return comps, nets


def library(nick):
    """Folder of a footprint library: Jonas from JONAS_KICADLIB, the rest are KiCad's own."""
    if nick == "Jonas":
        return os.path.join(os.environ["JONAS_KICADLIB"], "footprints", "Jonas.pretty")
    stock = os.environ.get("KICAD10_FOOTPRINT_DIR") or os.path.join(
        os.path.dirname(sys.executable), "..", "share", "kicad", "footprints")
    return os.path.join(stock, nick + ".pretty")


def load(board, board_path, ref, comp, nets):
    """The footprint of a component, linked to its symbol and with its nets, added to the board."""
    nick, name = comp["footprint"].split(":")
    fp = pcbnew.FootprintLoad(library(nick), name)
    fp.SetFPID(pcbnew.LIB_ID(nick, name))
    fp.SetReference(ref)
    fp.SetValue(comp["value"])
    fp.SetPath(pcbnew.KIID_PATH(comp["path"]))
    fp.SetSheetname("/")
    fp.SetSheetfile(os.path.basename(board_path).replace(".kicad_pcb", ".kicad_sch"))
    fields = dict(Datasheet=comp["datasheet"], Description=comp["description"])
    fields.update((k, v) for k, v in comp["fields"].items() if k in ("Manufacturer", "Part Number", "Color"))
    for key, value in fields.items():
        fp.SetField(key, value)
        for field in fp.GetFields():
            if field.GetName() == key:
                field.SetVisible(False)
    board.Add(fp)
    for pad in fp.Pads():
        net_name = nets.get((ref, pad.GetNumber()))
        if net_name:
            net = board.FindNet(net_name)
            if net is None:
                net = pcbnew.NETINFO_ITEM(board, net_name)
                board.Add(net)
            pad.SetNet(net)
    return fp, name


def main(board_path, net_path):
    comps, nets = netlist(net_path)
    board = pcbnew.LoadBoard(board_path)
    for ref, (x, y, angle, top, fixed, check) in BOND.items():
        old = board.FindFootprintByReference(ref)
        if old and not fixed and old.IsFlipped() != top:
            print(f"{ref}: already on the board, left where it is")
            continue
        if old:
            board.Remove(old)
        fp, name = load(board, board_path, ref, comps[ref], nets)
        pos = pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
        fp.SetPosition(pos)
        if not top:
            fp.Flip(pos, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(angle)
        if check is not None:
            layer = pcbnew.F_Fab if top else pcbnew.B_Fab
            fab = [g.GetBoundingBox() for g in fp.GraphicalItems() if g.GetLayer() == layer
                   and g.GetClass() == "PCB_SHAPE"]
            got = pcbnew.ToMM(min(b.GetLeft() for b in fab))
            if abs(got - check) > 0.06:
                raise SystemExit(f"{ref}: its outline starts at x {got:.3f}, expected {check:.3f}")
        fp.SetLocked(fixed)
        print(f"{ref}: {name} at ({x:.2f}, {y:.2f}) on the {'top' if top else 'bottom'} side, {angle:+.0f} deg")
    for ref, (x, y, direction, check_pad, (px, py)) in PARTS.items():
        comp = comps[ref]
        nick, name = comp["footprint"].split(":")
        old = board.FindFootprintByReference(ref)
        if old:
            board.Remove(old)
        lib = library(nick)
        fp = pcbnew.FootprintLoad(lib, name)
        fp.SetFPID(pcbnew.LIB_ID(nick, name))
        fp.SetReference(ref)
        fp.SetValue(comp["value"])
        fp.SetPath(pcbnew.KIID_PATH(comp["path"]))
        fp.SetSheetname("/")
        fp.SetSheetfile(os.path.basename(board_path).replace(".kicad_pcb", ".kicad_sch"))
        fields = dict(Datasheet=comp["datasheet"], Description=comp["description"])
        fields.update((k, v) for k, v in comp["fields"].items() if k in ("Manufacturer", "Part Number", "Color"))
        for key, value in fields.items():
            fp.SetField(key, value)
            for field in fp.GetFields():
                if field.GetName() == key:
                    field.SetVisible(False)
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        want = (x + direction * py, y - direction * px)
        for angle in (90.0, -90.0):
            fp.SetOrientationDegrees(angle)
            pad = fp.FindPadByNumber(check_pad)
            got = (pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y))
            if abs(got[0] - want[0]) < 1e-3 and abs(got[1] - want[1]) < 1e-3:
                break
        else:
            raise SystemExit(f"{ref}: pad {check_pad} lands at {got}, expected {want}")
        for pad in fp.Pads():
            net_name = nets.get((ref, pad.GetNumber()))
            if net_name:
                net = board.FindNet(net_name)
                if net is None:
                    net = pcbnew.NETINFO_ITEM(board, net_name)
                    board.Add(net)
                pad.SetNet(net)
        fp.SetLocked(True)
        print(f"{ref}: {name} at ({x:.2f}, {y:.2f}), {angle:+.0f} deg, pad {check_pad} at "
              f"({got[0]:.3f}, {got[1]:.3f})")
    pcbnew.SaveBoard(board_path, board)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
