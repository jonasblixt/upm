"""Helpers for the scripts that draw into a .kicad_pcb (KiCad 10 format).

Each script builds a list of top-level items with a Drawing, then replace()
swaps them in as one named group: a previous copy of the group, with every
item in it, is removed first, so the scripts can be re-run. Close the board
in KiCad before running them.
"""
import re
import uuid


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def num(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


class Drawing:
    def __init__(self, layer):
        self.layer = layer
        self.items = []         # (uuid, s-expression)

    def _add(self, body):
        u = str(uuid.uuid4())
        self.items.append((u, body.replace("@UUID@", u)))

    def text(self, s, x, y, size=1.2, th=0.15, just="left", bold=False, angle=0, layer=None):
        j = f"\n\t\t\t(justify {just})" if just else ""
        b = "\n\t\t\t\t(bold yes)" if bold else ""
        self._add(f"""\t(gr_text "{esc(s)}"
\t\t(at {num(x)} {num(y)} {num(angle)})
\t\t(layer "{layer or self.layer}")
\t\t(uuid "@UUID@")
\t\t(effects
\t\t\t(font
\t\t\t\t(size {size} {size})
\t\t\t\t(thickness {th}){b}
\t\t\t){j}
\t\t)
\t)""")

    def _shape(self, kind, pts, w, layer, fill=None):
        f = "" if fill is None else f"\n\t\t(fill {'yes' if fill else 'no'})"
        p = "\n".join(f"\t\t({k} {num(x)} {num(y)})" for k, (x, y) in pts)
        self._add(f"""\t({kind}
{p}
\t\t(stroke
\t\t\t(width {w})
\t\t\t(type solid)
\t\t){f}
\t\t(layer "{layer or self.layer}")
\t\t(uuid "@UUID@")
\t)""")

    def line(self, x1, y1, x2, y2, w=0.1, layer=None):
        self._shape("gr_line", [("start", (x1, y1)), ("end", (x2, y2))], w, layer)

    def rect(self, x1, y1, x2, y2, w=0.1, fill=False, layer=None):
        self._shape("gr_rect", [("start", (x1, y1)), ("end", (x2, y2))], w, layer, fill)

    def circle(self, cx, cy, r, w=0.1, layer=None):
        self._shape("gr_circle", [("center", (cx, cy)), ("end", (cx + r, cy))], w, layer, False)

    def arc(self, start, mid, end, w=0.1, layer=None):
        self._shape("gr_arc", [("start", start), ("mid", mid), ("end", end)], w, layer)

    def hatch(self, x1, y1, x2, y2, pitch=1.0, w=0.05):
        """45-degree hatch clipped to the rectangle."""
        h = y2 - y1
        k = x1 - h
        while k < x2:
            xa, ya, xb, yb = k, y2, k + h, y1
            if xa < x1:
                ya -= x1 - xa
                xa = x1
            if xb > x2:
                yb += xb - x2
                xb = x2
            if xb > xa:
                self.line(xa, ya, xb, yb, w)
            k += pitch

    def dimension(self, x1, y1, x2, y2, height, vertical=False, layer=None):
        """Orthogonal dimension between two points, in mm; the text is its length."""
        lay = layer or self.layer
        value = abs(y2 - y1) if vertical else abs(x2 - x1)
        if vertical:
            tx, ty, ta = x1 + height - 1.15, (y1 + y2) / 2, 90
        else:
            tx, ty, ta = (x1 + x2) / 2, y1 + height - 1.15, 0
        self._add(f"""\t(dimension
\t\t(type orthogonal)
\t\t(layer "{lay}")
\t\t(uuid "@UUID@")
\t\t(pts
\t\t\t(xy {num(x1)} {num(y1)}) (xy {num(x2)} {num(y2)})
\t\t)
\t\t(height {num(height)})
\t\t(orientation {1 if vertical else 0})
\t\t(format
\t\t\t(prefix "")
\t\t\t(suffix "")
\t\t\t(units 3)
\t\t\t(units_format 0)
\t\t\t(precision 4)
\t\t\t(suppress_zeroes yes)
\t\t)
\t\t(style
\t\t\t(thickness 0.1)
\t\t\t(arrow_length 1.27)
\t\t\t(text_position_mode 0)
\t\t\t(arrow_direction outward)
\t\t\t(extension_height 0.58642)
\t\t\t(extension_offset 0.5)
\t\t\t(keep_text_aligned yes)
\t\t)
\t\t(gr_text "{num(value)}"
\t\t\t(at {num(tx)} {num(ty)} {ta})
\t\t\t(layer "{lay}")
\t\t\t(uuid "@UUID@")
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1 1)
\t\t\t\t\t(thickness 0.15)
\t\t\t\t)
\t\t\t)
\t\t)
\t)""")

    def keepout(self, name, layers, pts):
        """Rule area that allows nothing: no tracks, vias, pads, pours or footprints."""
        lay = " ".join(f'"{n}"' for n in layers)
        xy = " ".join(f"(xy {num(x)} {num(y)})" for x, y in pts)
        self._add(f"""\t(zone
\t\t(layers {lay})
\t\t(uuid "@UUID@")
\t\t(name "{esc(name)}")
\t\t(hatch edge 0.5)
\t\t(connect_pads
\t\t\t(clearance 0)
\t\t)
\t\t(min_thickness 0.25)
\t\t(keepout
\t\t\t(tracks not_allowed)
\t\t\t(vias not_allowed)
\t\t\t(pads not_allowed)
\t\t\t(copperpour not_allowed)
\t\t\t(footprints not_allowed)
\t\t)
\t\t(placement
\t\t\t(enabled no)
\t\t\t(sheetname "")
\t\t)
\t\t(fill
\t\t\t(thermal_gap 0.5)
\t\t\t(thermal_bridge_width 0.5)
\t\t)
\t\t(polygon
\t\t\t(pts
\t\t\t\t{xy}
\t\t\t)
\t\t)
\t)""")


def blocks(s):
    """Split a board into its top-level items: [(text, is_item)], in order."""
    out, block = [], None
    for ln in s.split("\n"):
        if block is None:
            if re.match(r"^\t\(\w+", ln) and ln.count("(") != ln.count(")"):
                block = [ln]
            else:
                out.append((ln, False))
        else:
            block.append(ln)
            if ln == "\t)":
                out.append(("\n".join(block), True))
                block = None
    return out


def remove_group(s, name):
    """Drop a previous copy of the group and every top-level item in it."""
    members, kept, n = set(), [], 0
    parts = blocks(s)
    for text, is_item in parts:
        if is_item and text.startswith(f'\t(group "{esc(name)}"\n'):
            members = set(re.findall(r'"([0-9a-f-]{36})"', text))
    for text, is_item in parts:
        if is_item:
            if text.startswith(f'\t(group "{esc(name)}"\n'):
                continue
            u = re.search(r'^\t\t\(uuid "([^"]+)"\)', text, re.M)
            if u and u.group(1) in members:
                n += 1
                continue
        kept.append(text)
    return "\n".join(kept), n


def replace(src, dst, name, drawings):
    """Write the drawings' items into the board as the group `name`."""
    raw = open(src, encoding="utf-8", newline="").read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    s, removed = remove_group(raw.replace("\r\n", "\n"), name)
    items = [it for d in drawings for it in d.items]
    members = " ".join(f'"{u}"' for u, _ in items)
    group = (f'\t(group "{esc(name)}"\n\t\t(uuid "{uuid.uuid4()}")\n\t\t(locked yes)\n'
             f'\t\t(members {members}\n\t\t)\n\t)')
    body = "\n".join(t for _, t in items)
    ei = s.index("\n\t(embedded_fonts")
    s = s[:ei] + "\n" + body + "\n" + group + s[ei:]
    open(dst, "w", encoding="utf-8", newline="").write(s.replace("\n", eol))
    print(f"{name}: removed {removed} old items, wrote {len(items)}")
