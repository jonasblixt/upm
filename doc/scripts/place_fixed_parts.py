#!/usr/bin/env python3
"""Places the parts whose position the enclosure fixes: J1, J2 and D1.

J1 and J2 (USB-C, Wurth 632723130112) go in the cut-outs in the middle of
the two board ends, D1 (side-view LED) behind the light pipe notch at
bezel B. The positions come from board_outline.py. Each footprint is taken
from the library, linked to its schematic symbol, given the nets of the
netlist and locked. An existing J1, J2 or D1 is replaced, tracks are left
alone.

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
# Both footprints have +Y towards the bezel; a pad's footprint (px, py) lands at
# (x + dir * py, y - dir * px).
PARTS = {
    "J1": (X0, Y0 + bo.USB_Y, -1, "A1", (-2.75, -7.06)),
    "J2": (X1, Y0 + bo.USB_Y, 1, "A1", (-2.75, -7.06)),
    "D1": (X1 - bo.NOTCH_D - bo.LED_LENS, Y0 + bo.PIPE_Y, 1, "1", (-1.4, 0.0)),
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
            fields[find(p, "name")[0][1]] = find(p, "value")[0][1]
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


def main(board_path, net_path):
    lib = os.path.join(os.environ["JONAS_KICADLIB"], "footprints", "Jonas.pretty")
    comps, nets = netlist(net_path)
    board = pcbnew.LoadBoard(board_path)
    for ref, (x, y, direction, check_pad, (px, py)) in PARTS.items():
        comp = comps[ref]
        nick, name = comp["footprint"].split(":")
        old = board.FindFootprintByReference(ref)
        if old:
            board.Remove(old)
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
