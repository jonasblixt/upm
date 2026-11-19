# UPM V2 — PCB outline, stackup and design rules

The V2 board is 4 layers on JLCPCB's **JLC04161H-2116** stackup, 79.5 × 60.0 mm, for the
Hammond 1455A802 enclosure. The USB pairs are 90 Ω controlled impedance. Decided 2026-11-19.

The KiCad project is `hw/v2/upm-v2.kicad_pro` (KiCad 10). So far it holds the outline, the
physical stackup, the net classes and the design rules: there is no V2 schematic yet, and
the root sheet is empty. What V2 is to contain is in [`v2-plan.md`](v2-plan.md).

| File | Holds |
|---|---|
| `hw/v2/upm-v2.kicad_pcb` | Outline, rail keep-outs and mask openings, Board Setup → Physical Stackup, |
| | and the drawings: |
| | enclosure on `User.Enclosure` (User.1), stackup and fab notes on `User.Stackup` |
| | (User.3), dimensions on `User.Dimensions` (User.4) |
| `hw/v2/upm-v2.kicad_pro` | Board-wide rules, net classes, track, via and pair presets |
| `hw/v2/upm-v2.kicad_dru` | Custom rules (§7) |
| `doc/scripts/board_outline.py` | Draws the outline, keep-outs and enclosure drawing (§1) |
| `doc/scripts/stackup_drawing.py` | Draws the stackup, impedance table, fab notes and drill table |
| `doc/scripts/impedance.py` | Field solver the widths come from (§4) |

---

## 1. Enclosure and outline

Hammond 1455A802: extruded aluminium body, 70 × 12 mm outside, 81 mm long, with a
polycarbonate bezel screwed on each end. The board slides into card guides in the
extrusion and the bezels hold it lengthwise. There are no mounting holes.

The numbers are from Hammond's current drawing (`datasheets/1455A802.pdf`) and their STEP
model (`Hammond_1455A802.stp` in the library, 2013).

| | Value | Source |
|---|---|---|
| Extrusion length | 81.00 ±0.50 mm | drawing |
| Bezel step into the extrusion | 0.50 mm each end | drawing, STEP |
| Card guides, bottom to bottom | 61.88 ±0.51 mm | drawing |
| Card guide depth (the lips over the board edge) | 2.29 mm | drawing |
| Card guide opening | 1.63 mm | drawing (1.61 in the STEP) |
| Clear height above the board | 4.45 mm | drawing |
| Clear height below the board | 2.92 mm | drawing |
| Bezel panel area | 55.5 × 8.86 mm, 2.5 mm thick, centred | drawing, STEP |

**Outline: 79.5 × 60.0 mm**, 1.0 mm corner chamfers as lead-in for the guides.

- **Length 79.5, not Hammond's nominal 80.** The step on each bezel is a 54.5 × 8.8 mm
  plateau that butts against the board ends (STEP), so the board has 81.0 − 2 × 0.5 =
  80.0 mm at nominal and 79.5 mm in the shortest extrusion the drawing allows. At 79.5 the
  bezels always close. The cost is end play: 0.5 mm in a nominal enclosure, up to 1.2 mm in
  the longest one with the board routed 0.2 mm short. It is `BOARD_L` in
  `board_outline.py` if 80.0 is preferred.
- **Width 60.0.** The guides' lips end 57.3 mm apart, so a centred board is held by
  1.35 mm on each side.
- **Older enclosures are tighter across the width.** Hammond's 2010 drawing
  (`inkapsling_1455A802.pdf` in the library) and the 2013 STEP model give about 60.1 to
  60.45 mm between the guide bottoms, not 61.88. A 60.0 mm board fits both; a wider one
  would only fit the current extrusion.

**Rail strips.** 3.0 mm along both 79.5 mm edges, on both sides, is kept free of parts and
of copper on L1 and L4. The lips cover up to 2.29 mm of an edge when the board sits
against one side, and the anodising they slide on is no insulation once it is scratched.
Two rule areas, `RAIL_TOP` and `RAIL_BOTTOM`, enforce it in DRC. Inner layers may run to
the usual 0.5 mm from the edge. That leaves 54.0 mm of usable width.

**The rail strips have no solder mask either** (added 2026-11-19): a filled rectangle on
F.Mask and B.Mask over each strip. The guides are 1.63 mm high (1.61 mm in the STEP) and
the board is 1.6 mm ±10 %, so the strips are made as thin as the stackup allows:

| At the rail strips | Nominal board | Fits while the board overall is under |
|---|---|---|
| Outer copper and mask, as on the rest of the board | 1.63 mm | 1.63 mm, +2 % |
| No outer copper, mask | 1.59 mm | 1.67 mm, +4 % |
| **No outer copper, no mask** | 1.53 mm | 1.73 mm, +8 % |

"Overall" is the thickness over copper and mask, which is what the ±10 % applies to. The
top of that band, 1.73 to 1.76 mm, still does not fit; see §8.

**Height.** 4.45 mm above the top side and 2.92 mm below the bottom side. Design to 4.0 and
2.5 mm. This decides the connectors, see §8.

**Bezels.** The board's top face is on the centre line of the bezel (0.03 mm above it in
the STEP), so a connector whose centre is *h* above the board comes out *h* above the
middle of the bezel. A connector has to reach 2.5 mm past the board end to sit flush with
the bezel's panel face.

`board_outline.py` draws all of this as one locked group, `Outline 1455A802`, and replaces
it when re-run:

```sh
python doc/scripts/board_outline.py hw/v2/upm-v2.kicad_pcb
```

## 2. Stackup

1.6 mm finished, 1 oz outer copper, 0.5 oz inner copper (both finished weights), FR-4.
Thicknesses and Dk are from JLCPCB's impedance page (jlcpcb.com/impedance), read
2026-11-19. JLCPCB does not state the frequency the Dk applies at.

| Layer | Use | Material | Thickness | Dk |
|---|---|---|---|---|
| F.Cu | **L1 signal**, parts, USB pairs | Copper 1 oz | 0.035 mm | |
| | | Prepreg 2116 | 0.1164 mm | 4.16 |
| In1.Cu | **L2 GND**, unbroken | Copper 0.5 oz | 0.0152 mm | |
| | | Core | 1.265 mm | 4.6 |
| In2.Cu | **L3 PWR**, GND fill between the rails | Copper 0.5 oz | 0.0152 mm | |
| | | Prepreg 2116 | 0.1164 mm | 4.16 |
| B.Cu | **L4 signal**, GND pour | Copper 1 oz | 0.035 mm | |

Laminate total 1.598 mm, plus solder mask (Dk 3.8).

JLCPCB's user guide gives Dk 4.43 for cores this thick where the impedance page says 4.6.
It makes no difference here: nothing is routed against the core.

## 3. Why this stackup

JLCPCB lists 18 four-layer stackups at 1.6 mm. Four have a single prepreg ply between the
outer layer and the plane; the rest stack plies to 0.16–0.65 mm, which only makes the
traces wider than the default.

| Stackup | L1–L2 | 90 Ω pair, W / S | 50 Ω | Pair uncoupled | Note |
|---|---|---|---|---|---|
| JLC04161H-7628 | 0.2104 mm | 0.23 / 0.15 mm | 0.35 mm | 121 Ω, +34 % | JLCPCB's default |
| **JLC04161H-2116** | 0.1164 mm | 0.16 / 0.15 mm | 0.18 mm | 107 Ω, +20 % | chosen |
| JLC04161H-3313 | 0.0994 mm | 0.14 / 0.15 mm | 0.15 mm | 104 Ω, +17 % | fallback |
| JLC04161H-1080 | 0.0764 mm | 0.11 / 0.15 mm | 0.12 mm | 102 Ω, +13 % | too narrow |

"Pair uncoupled" is the differential impedance where the two traces split apart, twice the
single-ended impedance of one of them.

- **The plane sets the impedance, not the gap.** A USB pair cannot stay coupled
  everywhere. It splits at the Type-C connector, where A6/B6 and A7/B7 have to be joined,
  at the ESD array, at the data switch and at the hub's pins. On 7628 each split is a step
  from 90 to about 120 Ω. On 2116 it is a step to about 107 Ω.
- **The geometry fits the parts.** 0.16 / 0.15 mm has a 0.31 mm pitch, which runs straight
  out of 0.5 mm-pitch pads. On 7628 the 50 Ω width is 0.35 mm, wider than those pads.
- **Close planes.** L1 is 0.12 mm from GND instead of 0.21 mm, which lowers crosstalk and
  loop area for everything on the board, and power pours on L4 get the same from L3.
- **Same geometry as PoEtato.** Its outer layers are 2116 prepreg over GND as well, so the
  widths, presets and rules are the ones already in use there.
- **1080 is rejected** for width: at 0.11 mm the ±20 % etch tolerance is a larger share of
  the trace, for no gain.

**Cost and lead time are not confirmed.** JLCPCB advertises impedance control at no extra
charge. The data behind their impedance page lists 2116 with no fee, like 7628 and 3313,
but unlike those two it is not flagged for expedited builds. Check the quote. If 2116 costs more
or takes longer than it is worth, **JLC04161H-3313 is the fallback**: 0.14 / 0.15 mm for
90 Ω and 0.15 mm for 50 Ω, everything else in this document unchanged.

## 4. Impedance and net classes

| Class | Nets | Track / pair | Why |
|---|---|---|---|
| `90Ohm-diff_USB` | every USB D+/D− pair | 0.16 mm, gap 0.15 mm | 90 Ω differential, |
| | | | L1 over L2 GND |
| `Default` | everything else | 0.18 mm | 50 Ω on L1, so plain signals |
| | | | get it for free |
| `Power_3A` | DUT power: 5 V input → switch | 1.5 mm, 1.0 mm minimum, | 3 A on 1 oz outer copper, |
| | → shunt → DUT connector | clearance 0.2 mm | 10 K rise |
| `Power_0A5` | upstream VBUS, 5 V and 3.3 V | 0.4 mm | the UPM's own supply, |
| | branch tracks | | under 0.5 A |
| `Kelvin_SENSE` | shunt sense pairs to the monitor | 0.15 mm, gap 0.15 mm | routed as a pair from |
| | | | the shunt pads |

Solved impedances for the widths on the board: 88.9 Ω for the USB pair, 50.4 Ω for the
default track.

- **USB pairs get their class from their name.** Two patterns in the project,
  `*USB*_D_P` and `*USB*_D_N`, assign `90Ohm-diff_USB`. Name the pairs that way, for
  example `USB_UP_D_P/N`, `USB_DUT_D_P/N`, `USB_MCU_D_P/N`. KiCad only pairs nets whose
  names end in P/N or +/−. Each segment between two parts (connector, ESD array, switch,
  hub) is its own net and needs its own name.
- **The other three classes have no nets yet.** Assign them in the schematic with rule
  areas, as in PoEtato, once the nets exist. `Kelvin_SENSE` nets also need to end in P/N
  to route as a pair.
- **The MCU's pair is full speed only** (SAMD21, 12 Mbit/s) and would work at any
  impedance. It gets the class anyway, because the pattern matches it and it costs nothing.
- **`Power_3A` assumes the 3 A the plan recommends**, which is still an open question
  there. 1.5 mm is the narrowest neck, not the target: use pours, and double them on
  another layer where there is room. 1.5 mm of 1 oz copper is 0.33 mΩ per mm, so 40 mm of
  it drops 39 mV at 3 A. Inner copper is 0.5 oz and needs about 8 mm for the same current,
  so a track on L3 does not carry it. Use at least 4 vias of 0.3 mm where the path
  changes layer.
- **Not controlled:** I²C, SWD, the crystals, the aux inputs and outputs.

## 5. How the widths were computed

`doc/scripts/impedance.py` is the 2D field solver from PoEtato, cut down to outer layers.
It solves the cross-section on a nonuniform grid and computes Z0 from the capacitance with
and without the dielectric. `--check` compares it with an analytic microstrip formula; they
agree within 1 %.

```sh
pip install numpy scipy
python doc/scripts/impedance.py                 # JLC04161H-2116
python doc/scripts/impedance.py --stackup all   # the four candidates of §3
python doc/scripts/impedance.py --detail        # how far 0.16 / 0.15 moves
python doc/scripts/impedance.py --check
```

Assumptions: 35 µm finished outer copper; solder mask Dk 3.8, 30 µm over laminate and
15 µm over copper, which is what JLCPCB states; rectangular trace cross-section. Real
traces are trapezoidal, which raises the impedance by a few ohms.

What moves the USB pair, from `--detail`:

| Case | Differential impedance |
|---|---|
| Nominal, 0.16 / 0.15 mm | 88.9 Ω |
| Etched 0.02 mm narrow or wide, pitch kept | 96.3 Ω / 82.0 Ω |
| Pour 0.15 mm from the pair | 86.8 Ω |
| Pour 0.3 mm from the pair | 88.6 Ω |

Expect the results to be within about ±5 % of the fab. **JLCPCB's impedance calculator is
the reference for the order.** It has not been run for this board: it needs a browser.
Confirm 90 Ω for JLC04161H-2116 there, and update §4, the project's presets and
`stackup_drawing.py` if its widths differ.

## 6. Fabrication requirements

This is what goes to the fab. It is written to work for any vendor: §2 is the reference
build at JLCPCB, but another fab can build to its own materials as long as it meets these
requirements. The same notes are on the board drawing.

1. **Build to IPC-6012 Class 2.** 4-layer rigid FR-4, Tg ≥ 150 °C, rated for lead-free
   assembly. Reference build: JLCPCB stackup JLC04161H-2116, Tg 155 option.
2. **Finished board thickness** 1.60 mm ±10 %.
3. **Finished copper:** outer layers 1 oz (35 µm), inner layers 0.5 oz.
4. **Layer order and use** as in §2. The dielectric thicknesses are nominal. Other
   materials and constructions are acceptable if the impedance targets and the finished
   thickness are met, and L1–L2 and L3–L4 each stay ≤ 0.15 mm.
5. **Controlled impedance** per §4, ±10 %. The fab may change the width of controlled
   traces by up to ±0.025 mm, keeping the pair pitch, to meet the targets. No TDR report
   is needed: the pairs are USB 2.0 and a few centimetres long.
6. **Surface finish** ENIG. LPI solder mask on both sides, Dk about 3.8.
7. **Vias** are plated through-holes, smallest finished hole 0.3 mm, tented on both sides.
8. **Outline** routed, ±0.2 mm or better. The two 79.5 mm edges slide in card guides: no
   V-cut, and no break-off tabs or tab remains on any edge. The solder mask is open along
   those two edges on purpose: 3 mm strips of bare laminate, both sides.

**Keeping things in step.** The drawing comes from `doc/scripts/stackup_drawing.py`. When
the stackup, the widths or these notes change, update this document, Board Setup →
Physical Stackup and the script's `STACK`, `IMP` and `FAB_NOTES`. Then close the board in
KiCad and re-run the script; it replaces the previous drawing, and it reads the drill
table from the board's vias and pads:

```sh
python doc/scripts/stackup_drawing.py hw/v2/upm-v2.kicad_pcb
```

## 7. Design rules

The board-wide rules and net classes are in `hw/v2/upm-v2.kicad_pro` (Board Setup), the
custom rules in `hw/v2/upm-v2.kicad_dru`. The values are PoEtato's where nothing differs.
JLCPCB's limits are from their capabilities page (multilayer, 1 oz), read 2026-11-19.

| Rule | UPM V2 | JLCPCB limit | Note |
|---|---|---|---|
| Track width, default | 0.18 mm | | 50 Ω on L1 |
| Track width, minimum | 0.15 mm | 0.09 mm, ±20 % | The narrowest class |
| Clearance | 0.15 mm | 0.09 mm trace/space | Equals the USB pair gap. Leaves |
| | | | 0.2 mm between 0.5 mm-pitch pads |
| Pour to USB pair | 0.3 mm | | Keeps a pour from acting as a |
| | | | coplanar ground (§5). Tracks only |
| Via, default | 0.3 / 0.6 mm | min 0.15 / 0.25 mm; | Hole / diameter |
| | | no extra cost from 0.3 mm | |
| Via, small | 0.25 / 0.45 mm | no extra cost at ≥ 0.45 mm | For tight fanout only |
| Via annular ring, minimum | 0.1 mm | diameter ≥ hole + 0.1 mm | |
| Hole to copper | 0.3 mm | via 0.2; PTH 0.28 | Covers the inner layers too |
| Hole to hole | 0.3 mm | via 0.2; pad holes 0.45 | Keep component holes ≥ 0.45 mm |
| | | | apart by footprint |
| Copper to board edge | 0.5 mm | routed 0.2 mm | 3.0 mm on L1 / L4 along the |
| | | | rails, by rule area (§1) |
| Solder mask | 1:1, web ≥ 0.1 mm | bridge 0.10 mm | |
| Silkscreen | text ≥ 1.0 mm, | the same | |
| | stroke ≥ 0.15 mm | | |

**Presets.** Tracks 0.15, 0.16, 0.18, 0.25, 0.4, 0.5, 1.0 and 1.5 mm. Pairs 0.16 / 0.15 mm
(USB) and 0.15 / 0.15 mm (sense), via gap 0.25 mm.

**Custom rules.** Saving Board Setup → Custom Rules rewrites the file and drops comments,
so the reasons are here. Every number needs a unit, or KiCad ignores the whole file.

| Rule | Constraint | Why |
|---|---|---|
| Pour clearance to controlled impedance | zones keep 0.3 mm from | §5 |
| | `90Ohm-diff_USB` tracks | |
| USB pairs | skew ≤ 0.127 mm within a pair | PoEtato's limit, under 1 ps |
| | uncoupled ≤ 10 mm | Room for the connector, ESD |
| | | and switch fan-outs |
| | ≤ 2 vias per net | The pairs stay on L1. Two allow |
| | | the Type-C A6/B6 cross-over |
| DUT power path | `Power_3A` tracks ≥ 1.0 mm | §4 |

Each rule was checked in KiCad 10.0.8 with a deliberate violation: a track in a rail
strip, a 0.5 mm `Power_3A` track, a 0.12 mm track and a USB pair with 5 mm skew were all
reported.

**Routing rules that DRC does not check:**

- Route the USB pairs on L1 over unbroken L2 GND. No splits or slots in L2 under them.
  R1's DUT pair ran on the bottom layer over the 3.3 V plane and crossed a slot in it
  (R1 review, item 8).
- If a pair must use L4, the L3 copper under it has to be GND, with a GND via next to each
  signal via.
- Keep the hub next to the DUT connector so that the DUT pair is short.
- Sense pairs leave from the shunt's pads and stay clear of the DUT power pour's edges.

## 8. Open items

| # | Item |
|---|---|
| 1 | Confirm the 90 Ω width in JLCPCB's calculator for JLC04161H-2116 (§5) |
| 2 | Check the price and lead time of JLC04161H-2116 against 3313 at quote (§3) |
| 3 | **Connectors must fit 4.45 mm.** A standard USB-A receptacle is about 7 mm tall and |
| | does not fit. The DUT port needs a mid-mount USB-A in a board cut-out, which changes |
| | the outline, or USB-C. A barrel jack and an upright 2.54 mm header do not fit either |
| 4 | Board length 79.5 or 80.0 mm (§1) |
| 5 | Board thickness against the 1.63 mm guides (§1). The bare rail strips fit while the |
| | board is under about 1.73 mm; ±10 % allows 1.76 mm. Measure the first boards. The |
| | strips can be sanded, and JLC04161H-3313 is 0.034 mm thinner |
| 6 | Bezel cut-outs, once the connectors are chosen. The apertures have to clear the |
| | plug overmoulds if the connectors sit behind the panel face |
| 7 | Assign `Power_3A`, `Power_0A5` and `Kelvin_SENSE` in the schematic (§4) |
| 8 | Production jobsets, as in PoEtato (`pcb_outputs.kicad_jobset`), when there is |
| | something to release |
