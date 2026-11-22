# UPM V2 — PCB outline, stackup and design rules

The V2 board is 4 layers on JLCPCB's **JLC04161H-2116** stackup, 79.5 × 60.0 mm, for the
Hammond 1455A802 enclosure. The USB pairs are 90 Ω controlled impedance. Decided 2026-11-19.

The KiCad project is `hw/v2/upm-v2.kicad_pro` (KiCad 10). So far it holds the outline, the
physical stackup, the net classes, the design rules and the parts the enclosure fixes: the
three USB-C connectors, the status LED, the output header and, since 2026-11-22, the spring
that bonds the enclosure to GND (§1). Since 2026-11-20 the
schematic also has the two TPS25751D PD controllers (`pd.kicad_sch`) and the SAMD21E18A MCU
(`mcu.kicad_sch`) with their passives. Global labels connect them to the USB-C connectors'
VBUS and CC pins on the root sheet. Their footprints are on the board, parked below the outline
and not yet placed. Still to come: the hub, the PAC1934 and shunt, the regulators (the P3V3, P5V
and VIN_HV rails have no source yet), the VBUS TVSs, the LED and output drivers. The enclosure
and the light pipe are BOM-only entries. What V2 is to contain is in [`v2-plan.md`](v2-plan.md).

| File | Holds |
|---|---|
| `hw/v2/upm-v2.kicad_pcb` | Outline, rail keep-outs and mask openings, Board Setup → Physical Stackup, |
| | and the drawings: |
| | enclosure on `User.Enclosure` (User.1), stackup and fab notes on `User.Stackup` |
| | (User.3), dimensions on `User.Dimensions` (User.4) |
| `hw/v2/upm-v2.kicad_pro` | Board-wide rules, net classes, track, via and pair presets |
| `hw/v2/upm-v2.kicad_dru` | Custom rules (§7) |
| `hw/v2/upm-v2.kicad_sch` | Root sheet: J1, J2, J3, J4, D1, E1 and R16 (enclosure bond), the BOM-only parts |
| | and the sheets below |
| `hw/v2/pd.kicad_sch` | U1 (J4's controller, sink) and U2 (J2's, source): TPS25751D and passives |
| `hw/v2/mcu.kicad_sch` | U3 SAMD21E18A, 16 MHz crystal, decoupling, I2C and IRQ pull-ups, |
| | J1's Rd and CC sense, J5 Tag-Connect TC2030-NL (SWD, pads only) |
| `doc/scripts/board_outline.py` | Draws the outline, cut-outs, keep-outs and enclosure drawing (§1) |
| `doc/scripts/place_fixed_parts.py` | Places J1, J2, J3, J4 and D1 at the board ends and E1 with R16 between |
| | J1 and J4, all on the top side (needs KiCad's Python) |
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
2.5 mm. A standard USB-A receptacle, a barrel jack or an upright 2.54 mm header does not
fit.

**Bezels.** The board's top face is on the centre line of the bezel (0.03 mm above it in
the STEP), so a connector whose centre is *h* above the board comes out *h* above the
middle of the bezel. A connector has to reach 2.5 mm past the board end to sit flush with
the bezel's panel face.

`board_outline.py` draws all of this as one locked group, `Outline 1455A802`, and replaces
it when re-run:

```sh
python doc/scripts/board_outline.py hw/v2/upm-v2.kicad_pcb
```

### Connectors, LED and light pipe

Decided 2026-11-19: USB-C in on bezel A, USB-C out to the DUT on bezel B, a light pipe and a
2.54 mm header for three open-drain outputs and GND on bezel B. Everything on a bezel is to sit on its centre line, which is the board's top
face.

Decided 2026-11-20: a second USB-C on bezel A, J4, the PD power input (`v2-plan.md`, Power
architecture). **J1 and J4 are equally spaced across bezel A's 55.5 mm panel**: their centres
are a third of the panel apart, 9.25 mm either side of the middle, so the gaps from the
panel's edge to J1, from J1 to J4 and from J4 to the other edge are all 18.5 mm. Seen from
outside with the board's top side up, J1 (host) is on the left and J4 (power) on the right.
Nothing on the board forces the sides yet: swapping them is swapping `J1_Y` and `J4_Y` in
`board_outline.py` and running both scripts again. Two plugs' 12.85 mm overmoulds leave
5.65 mm between them.

| Ref | Part | Where |
|---|---|---|
| J1, J2, J4 | Würth 632723130112, USB Type-C receptacle, mid-mount, | J2 in the middle of the bezel B end; |
| | 24 pin, 5 A, drawn for a 1.6 mm board | J1 and J4 9.25 mm either side of the |
| | | middle of the bezel A end. Each in a |
| | | 9.5 × 4.7 mm cut-out |
| D1 | Würth 155124M173200 (WL-SFSW), side-view RGB LED, | bezel B end, 12 mm from J2, |
| | common anode, 3.2 × 1.5 × 1.0 mm | behind a 4.8 × 2.0 mm notch |
| J3 | Samtec HTSW-104-08-L-S, 1 × 4 2.54 mm straight header, | bezel B end, 15 mm from J2, |
| | laid flat: SMT tails on the top side | in a 11.2 × 5.87 mm notch |
| M2 | Dialight 515-1351-0188F, 5 mm panel-mount light pipe: | pressed into bezel B, its |
| | Ø 5.0 head, 4.77 mm below it. BOM only | head on the label, in front of D1 |
| M1 | Hammond 1455A802 enclosure. BOM only | |

**The connector is sunk into the board.** Its shell is 3.42 mm high and sits in the
cut-out, 2.00 mm above the board's top face and 1.42 mm below it. That puts the middle of
its opening 0.29 mm above the board, **0.3 mm above the bezel's centre line**. The 0.29 is
dimensioned in detail B of the data sheet, and Würth's STEP model agrees: its stake tips
are 1.89 mm from the shell's centre line and reach 1.6 mm into the board. A standard
top-mount receptacle would be 1.6 mm high.

- **Reach.** The mating face is 2.51 mm beyond the board end, and the bezel is 2.5 mm
  thick there. With the board against a bezel the face is flush with its panel; with the
  board at the other end of its play it is 0.5 to 1.2 mm back. A plug seats as long as the
  face is within about 2.0 mm of the panel, so no cable's overmould has to enter the bezel.
- **Cut-out.** 9.5 mm wide and 4.70 mm deep, with a half-circle relief of 0.5 mm radius at
  each inner corner so the square shell goes in. The data sheet draws the board edge but
  does not dimension it. It is taken 0.25 mm beyond the front stake pads, which is where
  the 2.51 mm comes from.
- **The land pattern is tight for JLCPCB.** It is Würth's, unchanged: 0.4 mm holes in
  0.65 mm pads on a 0.8 mm pitch, plated slots down to 0.4 × 0.9 mm, a non-plated slot of
  0.65 × 0.95 mm that comes within 0.10 mm of a pad. See §8.

**The LED shines along the board into the end of the light pipe.** Its lens is 2.2 mm wide
and 1.0 mm high, standing on the board, so all of it faces the upper half of the pipe. The
pipe is Ø 3.56 mm at its end, and its axis is on the board's top face. The lower half of the
pipe would hit the board end, hence the notch. The pipe (since 2026-11-20 the 515-1351-0188F,
its Ø 5.0 head resting on the label) ends 1.74 mm behind the bezel, inside the 4.8 × 2.0 mm
notch. D1's lens tip is at the notch's bottom. The gap to the pipe is therefore 0.26 mm with
the board against bezel B, 0.51 mm centred and 0.76 mm at the other end of its play; Dialight's
drawing shows 0.26 to 0.50 mm. How bright it looks has not been tried: check it on the
bench. Each colour takes 20 mA at most.

The LED is a plain RGB part, three cathodes and a common anode, driven from three MCU
pins. There is no white die: no side-view RGBW part without a built-in controller turned
up.

**The output header lies flat in a notch in the board end** (decided 2026-11-19). It is a
straight header, not a right-angle one: its 5.08 mm tails are soldered to 1.0 × 5.1 mm pads
on the top side and its insulator (10.16 wide, 2.54 long, 2.49 thick) sits in the notch.
**The post tips end 2.51 mm past the board end, in line with J2's mating face**, so they
are flush with the bezel's panel and the bezel opening is the shroud: a Dupont housing goes
in through the opening and the notch and onto the posts, which are not exposed. The pin row
is 0.32 mm above the copper plus the solder, about 0.35 mm above the board's top face,
against 0.29 for the USB-C opening. A right-angle header would put it at 1.52 mm (Samtec
TSW/HTSW -RA), and no single-row 2.54 mm mid-mount part turned up.

- **Notch.** 11.2 mm wide and 5.87 mm deep (5.84 post + 2.54 insulator − 2.51 reach), with
  a half-circle relief of 0.5 mm radius at each inner corner as for the USB-C cut-outs. The
  insulator's rear face sits against the inner wall. The insulator reaches 0.9 mm below the
  board's top face and a Dupont housing about the same, which is why the board has to give
  way: the housing passes through the notch on its way to the insulator's front face,
  3.33 mm inside the board end.
- **Mating housing.** Checked against a Harwin M20-1060400 1 × 4 crimp housing (drawing
  M20-106XX00: 10.36 ± 0.30 wide, 2.50 thick, 14.00 long, mating pin 5.5 to 6.3 mm) in
  `mech/upm-v2-assembly.sc` (§9). The notch moves with the board and passes the largest
  housing with 0.27 mm per side. The bezel opening also has to allow for the board's play:
  it can shift sideways in the card guides until J2's shell meets its opening, 0.30 mm
  either way. The first opening, 10.76 × 3.09 mm, let a housing at its largest hit the
  bezel by 0.25 mm with the board shifted; the 11.7 × 3.3 mm opening leaves 0.22 mm.

- **HTSW, not TSW.** The same header with an LCP insulator: Samtec rates TSW for leaded
  wave soldering only and HTSW for lead-free reflow. Lead style -08 (tail 5.08, post 5.84),
  plating -L (10 µin gold on the posts, tin tails). Print HTSW-XXX-XX-XXX-X-XX-XX-XX rev BQ.
- **Forces.** The insulator's lower 0.9 mm butts against the notch's inner wall, so pushing a
  plug on loads the board, not the joints. Only pulling a plug off loads the four solder
  joints. Try it on the bench.
- **Pin 1** is on the left seen from outside, nearest the board's bottom (rail) edge, and
  pin 4 is nearest J2. Which pin is GND is still to be decided in the schematic.
- **Placement.** 15 mm from J2 leaves 3.5 mm between a 1 × 4 Dupont housing and the
  12.85 mm overmould of a USB-C plug in J2, about what the light pipe has on the other side.
- **Assembly.** It is an SMT part placed off its usual axis, with the insulator over the
  notch: place and solder it by hand, or ask the assembler.

**Bezel machining**, seen from outside, with the board's top side up:

| Bezel | Opening | Size | Position |
|---|---|---|---|
| A and B | USB-C | 9.80 × 4.02 mm, follows the shell: | B: middle of the width. A: two, 9.25 mm |
| | | ends R 1.78 centred 3.12 mm either side | left (J1) and right (J4) of the middle. |
| | | | Centre 0.3 mm above the bezel's centre line |
| | | of the middle and 0.23 mm above and | |
| | | below the centre line, 0.46 mm flanks | |
| B | Light pipe | Ø 3.96 ± 0.05 mm, straight | on the centre line, 12.0 mm right of the |
| | | (0.156" ± 0.002); the head rests on the label | connector |
| B | Outputs (J3) | 11.7 × 3.3 mm, corners up to R 0.5. | 15.0 mm left of the connector; centre |
| | | Passes a 1 × 4 crimp housing | 0.35 mm above the bezel's centre line |

The connector shell is 9.20 × 3.42 mm at the mouth, measured in Würth's STEP model: its
ends are arcs of 1.48 mm radius joined by 0.46 mm straight flanks. (Earlier notes said
9.65; that is not the mouth.) The openings follow it at 0.3 mm all round, as the plain
10.2 × 4.0 mm rectangle did. A plug's overmould is up to 12.85 mm wide (USB Type-C
specification, release 2.4), which leaves 3.1 mm to the light pipe's Ø 5.0 head.

### Enclosure bond

Decided 2026-11-22: the extrusion is bonded to GND at one point, by a spring on the board.
It is anodized all over and the bezels are polycarbonate, so without a bond it is floating
metal around the board: an ESD strike charges it until it arcs to something.

| Ref | Part | Where |
|---|---|---|
| E1 | Würth 331246501860 (WE-SECF, size 2460), SMT contact finger: | top side, on the board's centre |
| | 5.0 × 2.6 mm, 6.0 mm high unloaded, working height 3.7 to | line between J1 and J4, pad centre |
| | 5.8 mm. Phosphor bronze, nickel plated, one 2.0 × 2.2 mm pad | 6.5 mm from the bezel A end |
| R16 | 0603 between E1 (net `ENCLOSURE`) and GND: 0 Ω | top side, next to E1 |

- **Top side, so the board is assembled from one side** (2026-11-22). The first choice was the
  shorter 331256381840 (4.0 mm high, working height 2.5 to 3.8 mm) on the bottom side, against
  the floor 2.92 mm below the board. It cannot reach the roof, and it was the only part on the
  bottom. Its footprint and symbol stay in kicadlib.
- **Working height.** The extrusion's roof is 4.45 mm above the board (4.47 in the STEP),
  flat across the middle 58 mm. E1 is compressed from 6.0 to about 4.45 mm, inside its 3.7 to
  5.8 mm range with 0.75 mm to spare downwards and 1.35 mm upwards. Würth states no force.
  It is the one part on the board that is higher than the 4.0 mm design height, on purpose.
- **The anodising has to come off where E1 lands.** A spring does not get through it. Strip a
  patch of the roof, about 8 × 8 mm, in the middle of the width and centred 7 mm inside the
  bezel A mouth: E1 touches with the flat top of its arm, which is above its pad, 4.85 to
  6.9 mm from the board end (Würth's STEP model), and the board end is 0.5 to 1.2 mm inside the
  mouth. Cover the bare metal straight away with an aluminium antioxidant
  joint compound or plain grease. A conductive conversion coat (trivalent, SurTec 650 or a
  touch-up pen) is the better finish, but a static and ESD bond does not need it.
- **Insert the board bezel B end first, through the bezel A mouth.** E1 is then the last
  thing in and slides over only the last few millimetres of the roof. The arm leaves the
  foot, turns in a loop and rises as a ramp, about 60° steep, to its flat top over the foot.
  The loop is inboard and the arm's tip towards bezel A, so on the way in the mouth of the
  extrusion meets the ramp and pushes the arm down. It has to go down 1.55 mm: press it down
  with a finger or a spudger as it enters, do not force it against the edge. On the way out
  the roof slides against the tip, over the same few millimetres.
- **R16** is one 0603 footprint so the bond can be chosen on the bench: 0 Ω for a hard bond
  (fitted), or 1 MΩ with a few nF soldered on top of it if a DC-isolated enclosure turns out
  to be wanted. The CRCW database library has no 0 Ω row, so R16 is a plain `Device:R` with
  Vishay's CRCW06030000Z0EA as its part number.
- **Not connected here:** the USB-C shells (S1 of J1, J2 and J4) are still open in the
  schematic. The intention is to tie them straight to the GND plane.
- **Footprint.** `Jonas:Wurth_331246501860`, generated from the data sheet's land pattern.
  The solder foot starts 0.65 mm from the foot end (data sheet; 0.66 in Würth's STEP model),
  which is where the pad is. The 3D model is that STEP, at its unloaded height.

### Placing them

J1, J2, J3, J4, D1 and E1 are locked on the board. `place_fixed_parts.py` puts them
there from the positions in `board_outline.py` (E1's is `SPRING_X` in the script itself), links
them to their symbols and sets their nets from the netlist, so Update PCB from Schematic leaves
them where they are. R16 is placed next to E1 the first time and not locked:

```sh
kicad-cli sch export netlist --format kicadsexpr -o upm-v2.net hw/v2/upm-v2.kicad_sch
JONAS_KICADLIB=<kicadlib> python doc/scripts/place_fixed_parts.py hw/v2/upm-v2.kicad_pcb upm-v2.net
```

**The USB-C symbol is the connector's mating face** (2026-11-22), so a pin can be found on the
real part from the schematic: the view into the receptacle as on page 1 of Würth's data sheet,
turned a quarter turn clockwise. The A row is the right-hand column with A1 at the top, the B
row the left-hand column with B12 at the top, and the A row is the one on the board's top
side. `scripting/gen_wurth_632723130112_symbol.py` in kicadlib draws it.

The symbols and footprints are in kicadlib (`conn/Wurth_632723130112`, `conn/Wurth_331246501860`,
`led/LED1204_155124M173200`, footprints `Jonas:Wurth_632723130112`, `Jonas:Wurth_331246501860` and
`Jonas:LED_Wurth_155124M173200_3.2x1.5mm_Horizontal`), and for J3 `conn/Samtec_HTSW-104-08-L-S`
with `Jonas:Samtec_HTSW-104-08-L-S_EdgeMount`. The footprints were drawn from the data
sheets for this board and are on kicadlib's manual-review list. The connector's 3D model is
Würth's own STEP and the LED's is a generated box. J3's is Samtec's own STEP (TraceParts,
HTSW-104-08-S-S: the plating code does not change the geometry). Data sheets:
[connector](https://www.we-online.com/components/products/datasheet/632723130112.pdf),
[LED](https://www.we-online.com/components/products/datasheet/155124M173200.pdf),
[light pipe](https://s3-us-west-2.amazonaws.com/catsy.557/Dialight_datasheet_515_VPM_5mm.pdf),
[header](https://suddendocs.samtec.com/prints/htsw-xxx-xx-xxx-x-xx-xx-xx-mkt.pdf) (Samtec's
server refuses requests without a samtec.com referrer; open it from www.samtec.com/products/htsw).

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
| `Power_3A` | DUT power: J1 and J4 VBUS, the 5 V | 1.5 mm, 1.0 mm minimum, | 3 A on 1 oz outer copper, |
| | buck, the path switches → eFuse | clearance 0.2 mm | 10 K rise, up to 20 V |
| | → shunt → DUT connector | | |
| `Power_0A5` | the UPM's own 5 V and 3.3 V | 0.4 mm | the UPM's own supply, |
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
9. **Slots.** J1, J2 and J4 need plated slots of 0.4 × 0.9, 0.5 × 1.1 and 0.5 × 1.5 mm and a
   non-plated slot of 0.65 × 0.95 mm. They are not to be enlarged or rounded without
   asking.

The fab drawing is on an A3 sheet.

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
| USB-C receptacle: holes within | hole clearance 0.1 mm between | Würth's pattern has 0.10 to |
| the land pattern | pads and holes of the footprint | 0.28 mm; the board rule is 0.3 |
| USB-C receptacle: pads to the | edge clearance 0.1 mm for the | 0.23 mm to the cut-out, 0.25 to |
| cut-out and the locating holes | footprint's pads | the board end, 0.10 to a locating |
| | | slot; the board rule is 0.5 |
| Output header laid flat: pads | edge clearance 0.2 mm for J3's | the pads stop 0.25 mm short of |
| to the notch | pads | the notch's inner wall |
| TPS25751D: merged lands within | clearance 0.09 mm between pads | TI's REF0038A land keeps 0.10 mm |
| the footprint | of the REF0038A footprint | between the merged pin groups |
| | | (PPHV / VBUS_IN, PP5V / VBUS); |
| | | the board rule is 0.15 |

The first three rules were checked in KiCad 10.0.8 with a deliberate violation: a track in
a rail strip, a 0.5 mm `Power_3A` track, a 0.12 mm track and a USB pair with 5 mm skew were
all reported. The two connector rules only relax the board rules inside J1, J2 and J4 (they match the
footprint, so they cover J4 without a change): without
them DRC reports 154 violations there, with them none. Tracks to those pads still keep the
board rules. The TPS25751D rule (2026-11-20) clears the 4 violations U1 and U2 report without it.

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
| 3 | **J1 / J2 / J4 land pattern against JLCPCB's limits.** From their capabilities page: PTH |
| | annular ring 0.15 mm minimum (the pattern has 0.125), pad holes 0.45 mm apart (0.40), |
| | NPTH to copper 0.2 mm (0.10). Their slot limits were not looked up; the pattern needs |
| | plated slots 0.4 and 0.5 mm wide and a non-plated one 0.65 mm wide. Ask before ordering |
| 4 | Board length 79.5 or 80.0 mm (§1) |
| 5 | Board thickness against the 1.63 mm guides (§1). The bare rail strips fit while the |
| | board is under about 1.73 mm; ±10 % allows 1.76 mm. Measure the first boards. The |
| | strips can be sanded, and JLC04161H-3313 is 0.034 mm thinner |
| 6 | Bezel machining per §1. Decide how: the bezels are polycarbonate |
| 7 | Assign `Power_3A`, `Power_0A5` and `Kelvin_SENSE` in the schematic (§4) |
| 8 | Production jobsets, as in PoEtato (`pcb_outputs.kicad_jobset`), when there is |
| | something to release |
| 9 | Brightness through the light pipe, and the LED's pad 1 against a real part (§1) |
| 10 | ~~The PD power input has no connector yet.~~ Done 2026-11-20: J4 on bezel A, J1 and J4 |
| | equally spaced (§1), in the assembly and on the back label as well (§9) |
| 11 | J3 on the bench: pull a Dupont housing off a soldered sample, and check that Dupont |
| | housings go through the bezel opening and the notch and seat on the posts, with the |
| | board at both ends of its play (§1) |
| 12 | **Enclosure bond (§1).** Strip the patch in the extrusion's roof and decide its finish. |
| | On the first board: check that the board slides in with E1 fitted, and the resistance |
| | from the extrusion to GND |
| 13 | The USB-C shells (S1) are not connected in the schematic yet (§1, Enclosure bond) |
| 14 | E1 and R16 are not in `mech/upm-v2-pcb.step` or the SolidCraft assembly yet (§9). E1's |
| | model is Würth's, at its unloaded height, so it will show 1.55 mm into the roof |

## 9. Mechanical assembly

`mech/` holds the enclosure, the bezels as they are to be machined and the board, put
together in SolidCraft (2026-11-19; J4 added 2026-11-20):

| File | Holds |
|---|---|
| `mech/upm-v2-assembly.sc` | The SolidCraft design: extrusion, Bezel A, Bezel B, bezel screws, the board, |
| | a Harwin M20-1060400 housing mated on J3, the Dialight light pipe and the two labels |
| `mech/upm-v2-assembly.step` | All of it as one STEP (the labels as solids, without their print) |
| `mech/labels/upm-v2-bezel-labels.vectorcraft` | The label artwork (VectorCraft) |
| `mech/labels/label-front-lcsc.ai`, `label-back-lcsc.ai` | The labels as LCSC gets them (see Label artwork below), with a proof PDF |
| `mech/labels/cut-*.svg`, `decal-*.png` | Cut lines and print exported for the SolidCraft design |
| `mech/bezel-a.step`, `mech/bezel-b.step` | The bezels with their openings, for machining |
| `mech/upm-v2-pcb.step` | The board, from `kicad-cli pcb export step`, origin in the middle of the board |
| `mech/Hammond_1455A802.stp` | Hammond's model (2013), from the library |
| `mech/Dialight_51513510188F.stp` | Dialight's model of the 515-1351-0188F light pipe, from the library |

- **Placement.** Hammond's model has the extrusion along Z (0 to 81), the width along X and the
  height along Y; bezel B is the one at +Z. The board's length runs along Z, its top side
  faces +Y, and it is centred between the bezel plateaus (Z 0.5 and 80.5), 0.25 mm end play
  each side. Its top face is at Y −1.597, 0.03 mm above the cavity's centre line (§1).
- **Openings** are cuts in the bezels driven by parameters of the design (`usb_w`, `usb_h`,
  `usb_r`, `usb_above`, `usb_a_dx`, `pipe_d`, `pipe_x`, `hdr_w`, `hdr_h`, `hdr_above`, `hdr_x`).
  The numbers are those of §1. Bezel A has two USB-C openings, "USB-C opening A" for J1 at
  `encl_cx + usb_a_dx` (+X, left seen from outside) and "USB-C opening A J4" at
  `encl_cx - usb_a_dx`; `usb_a_dx` is 55.5 / 6 = 9.25 mm, as `J1_Y` and `J4_Y` in
  `board_outline.py`.
- **Housing** is drawn from Harwin's drawing M20-106XX00, not their own model, which
  TraceParts gives out only with a login.
- **Light pipe** is Dialight's own model of the 515-1351-0188F (2026-11-20; it replaced the
  flush 515-1313-0125F, whose head sat 0.53 mm down in the label). The file has its axis along
  +Z, the underside of the Ø 5.0 head at z 0, the lens at +0.76 and the end at −4.77. It is
  placed by parameters: axis at (`encl_cx + pipe_x`, `board_top`), the head on the label at
  `pipe_face_z + label_t`. So the lens stands 0.79 mm proud of the bezel, and the pipe ends
  1.74 mm behind it, in the board's 4.8 × 2.0 mm notch. It is pressed in after the label (see
  the assembly order below), and it comes after the labels in the design's history.
- **Board import.** When the board changes, delete the `UPM V2 PCB` component and insert
  `mech/upm-v2-pcb.step` again with the matrix
  `[0,1,0,"encl_cx + play_x", 0,0,1,"board_top - 1.6 mm", 1,0,0,"board_z"]`.
- **Checked:** no interference between the board's parts and the extrusion or the bezels. The
  only overlap is the light pipe's four crush ribs (Ø 4.11) in their Ø 3.96 hole, the press
  fit (0.013 mm³, in the top 0.9 mm of the hole). The pipe clears the label, the notch and
  D1. Its end is 0.51 mm from D1's lens and from the notch's bottom with the board centred.
  The parameter `play_x` shifts the housing sideways to try the board's play in the card
  guides (0.30 mm either way); with the housing at its largest (`hsg_w` 10.66) it clears
  the bezel by 0.22 mm per side. Checked again with J4 (2026-11-20): J1 and J4 sit centred
  in their openings, and the only other overlaps are inside Würth's connector model itself
  (housing and shield parts, the same on all three).
- **Labels** (2026-11-20). Each fills its recess: 0.4 mm PET printed on the back
  (`label_film`) plus 0.13 mm 3M 468MP (`label_adh`), so `label_t` is 0.53 mm, about 0.03 mm
  proud of the plateau before the adhesive settles. The label is meant to be ordered online
  from LCSC's front panel service, which offers both. With the label flush, the
  USB-C mating face is 0.5 mm further from the outer surface than it is from the recess floor,
  so 1.0 to 1.7 mm instead of 0.5 to 1.2 mm. That is still within the 2.0 mm a plug needs (§1).
  Each label lies on its bezel's
  label recess floor (bezel B at `pipe_face_z`, bezel A at `recess_a_z`). It is extruded from the label's
  cut lines, `mech/labels/cut-front.svg` and `cut-back.svg`. A decal of the print,
  `decal-front.png` and `decal-back.png`, lies on top. The named views "Bezel B from outside
  (front label)" and "Bezel A from outside (back label)" show them as a user sees them.
  Checked: the windows sit centred on the openings and the labels interfere with nothing.
  If the artwork's cut lines change, export the Cut layer again and replace the curves of the
  sketches "Label front cut lines" and "Label back cut lines". Then point the extrusions
  "Label front" and "Label back" at the new curve ids: they store their profile by curve
  id, and "all profiles" would fill the windows in. If only the print changes, replace the
  decals.
- **Label artwork for LCSC** (`mech/labels`, 2026-11-20). LCSC states a cutting accuracy of
  ±0.3 mm, with outlines usually about 0.2 mm small and cut-outs about 0.2 mm large. It wants
  at least 1.5 mm between cut-outs and from cut-outs to the edge, and text printed on the
  back with strokes over 0.25 mm. So:
  - **Outline:** 55.1 × 8.46, R 0.5 (the recess less 0.2 all round).
  - **USB-C window:** 10.4 × 4.62, R 2.08, the opening plus 0.3 all round. With plus 0.4,
    only 1.50 mm would be left above it; with plus 0.3 it is 1.60. The back label has two,
    centred 9.25 mm either side of the middle like J1 and J4, 8.1 mm apart.
  - **Back label text** (2026-11-20, with J4): "UPM" over "V2" left of J1's window, "USB
    HOST" under J1, "PD IN" under J4, and "USB POWER MONITOR" on three lines right of J4.
    The right-hand block is 9.4 mm wide (MONITOR) and sits 1.9 mm from the window and from
    the edge. "PD POWER IN" would have run into MONITOR on the bottom line.
  - **Header window:** 12.5 × 4.1, R 0.9, the opening plus 0.4.
  - **Light-pipe window:** Ø 4.5. The pipe's Ø 4.11 ribs always pass, and its Ø 5.0 head
    always covers the cut edge, even with LCSC's ±0.3 mm. There is no text under it: the head
    would reach into the bottom line, so STATUS was dropped (2026-11-20).
  - **Text:** all small text is Arial Black 5 pt. Its thinnest stroke, measured, is 0.257 mm
    (Arial Bold 5 pt is thinner). The text sits 0.6 mm from the bottom edge. "OUT" is left of
    the header window, because only 1.8 mm is left above it. The ground symbol has 0.75 pt
    (0.26 mm) bars with 0.5 pt gaps.
  - **Colour:** the background is 85 % K, CMYK, and runs 1 mm past the outline with no
    knock-outs; the cut removes the windows. White ink is the spot colour "White"; the cut
    lines are the spot colour "CutContour", 0.25 pt.
  - **Files to order from:** `label-front-lcsc.ai` and `label-back-lcsc.ai`, one per label
    because LCSC takes one design per order. The page is the label plus the 1 mm bleed
    (57.1 × 10.46). Text is converted to outlines, and the colours are CMYK plus the two spot
    colours. `upm-v2-labels-lcsc-proof.pdf` shows both labels with their bleed.
  - **Source:** `upm-v2-bezel-labels.vectorcraft`, where the text is still live.
  - **Ask LCSC:** how they want white ink and cut lines marked, whether the adhesive can be
    left out around the windows, and whether the page should include the bleed.
- **Assembly order for a bezel:**
  1. Clean the recess floor of the loose bezel.
  2. Lay the label using a jig with pins through the light-pipe hole and the USB-C opening.
  3. Press the light pipe in from the front by its head until the head sits on the label. Its
     head clamps the label around the window.
  4. Fit the bezel to the enclosure.
- **Updating the board:** export it again with
  `JONAS_KICADLIB=<kicadlib> kicad-cli pcb export step --subst-models --include-silkscreen
  --include-soldermask --user-origin 69.75x60mm -o mech/upm-v2-pcb.step hw/v2/upm-v2.kicad_pcb`
  and replace the `UPM V2 PCB` import in the design.
