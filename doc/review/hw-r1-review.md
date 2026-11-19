# UPM R1 hardware review

Review of the R1 hardware (`hw/upm.sch`, `hw/upm.net`, `hw/upm.kicad_pcb`,
`hw/Release/R1/`) against the datasheets in `datasheets/`.

No KiCad DRC was run; layout observations come from parsing `hw/upm.kicad_pcb`
directly.

## Summary

| # | Severity | Area | Issue |
|---|----------|------|-------|
| 1 | High | Power | FB1 rated 500 mA but carries board + DUT current up to the 1.0–1.35 A switch limit |
| 2 | High | Measurement | PAC1934 full scale (1.0 A) is below the NCP380 current limit |
| 3 | High | USB hub | CRFILT/PLLFILT capacitance 11× the datasheet maximum |
| 4 | Verify | Power | MIC23150 footprint has no exposed pad |
| 5 | Medium | Measurement | PAC1934 SLOW pin pulled high, so it samples at 8 SPS |
| 6 | Medium | USB hub | Hub strapped as self-powered on a bus-powered board |
| 7 | Medium | Reset | Any MCU reset power-cycles the DUT and resets the hub |
| 8 | Medium | Layout | DUT USB pair is roughly 130–140 Ω differential, not 90 Ω |
| 9 | Low | Misc | Crystal case pads, RBIAS value, SWO, J4 inputs, discharge order |

## High

### 1. FB1 is undersized for the VBUS path

FB1 (BLM18BB121SN1D) sits between J3 VBUS and `P5V0`, so it carries the whole
board's current plus the DUT's. It is rated 500 mA with up to 0.3 Ω DCR.

The NCP380 current limit set by R16 = 21 kΩ is 1.00 / 1.18 / 1.35 A
(min / typ / max, NCP380 datasheet eq. 6–8). FB1 can therefore run at about
2.5× its rating before the switch trips, dropping around 0.35 V.

**Fix:** use a ferrite rated for 2 A or more with under 50 mΩ DCR, or a 0 Ω link.

Also decide deliberately how much current to allow. A 1.2 A limit pulls well
beyond the 500 mA a USB 2.0 upstream port is meant to supply.

### 2. PAC1934 clips below the current limit

With the 100 mΩ shunt (R22) and the PAC1934's ±100 mV sense range, full scale is
1.0 A. The switch allows up to 1.35 A, so readings flatten between those values.

**Fix (pick one):**

- R22 = 50 mΩ, giving a 2 A range.
- R16 ≈ 30 kΩ, giving a limit of 0.75 / 0.88 / 1.01 A.

| R16 | I_lim min | typ | max |
|-----|-----------|-----|-----|
| 21 k (R1) | 1.00 A | 1.18 A | 1.35 A |
| 27 k | 0.82 A | 0.96 A | 1.11 A |
| 30 k | 0.75 A | 0.88 A | 1.01 A |
| 33 k | 0.69 A | 0.81 A | 0.93 A |

**Related:** the PAC measures VBUS on SENSE1+, which is the switch side of R22.
The reported voltage is therefore higher than at J2 by I × 0.1 Ω (100 mV at 1 A).
Firmware can correct this as V_dut = V_bus − V_sense.

### 3. USB2512B CRFILT/PLLFILT capacitance too large

DS00001692C says CRFILT and PLLFILT may have "up to a 0.1 µF low-ESR capacitor"
to VSS. Each pin currently has 0.1 µF + 1.0 µF:

- CRFILT (pin 14): C3 + C5
- PLLFILT (pin 34): C6 + C7

**Fix:** do not fit C5 and C7.

### 4. MIC23150 footprint has no exposed pad (verify)

U2 uses `DFN-8_2x2mm_Pitch0.5mm`, whose own description reads
"No exposed pad". Distributors list the MIC23150-SYMT as an 8-pin TDFN with an
exposed pad.

The MIC23150 datasheet isn't in `datasheets/`, so neither the pad's required
connection nor the symbol's pinout (SW 1/2, EN 3, SNS 4, AGND 5, VIN 6/7, PGND 8)
has been checked.

**Fix:** add the datasheet to the repo, verify the pinout, and switch to a
footprint with the exposed pad and ground vias if the package has one.

## Medium

### 5. PAC1934 samples at 8 SPS, not 1024

R13 pulls SLOW/ALERT high. While that pin acts as SLOW and is high, the PAC
samples at 8 SPS regardless of the programmed rate.

`sw/pac193x.c:27-31` writes CTRL = 0x00. That leaves the pin in its SLOW role,
so it stays high and the device runs at 8 SPS.

**Fix (pick one):**

- Firmware: set the ALERT_PIN bit (CTRL bit 3).
- Firmware: drive PA02 low.
- Hardware: change R13 to a pull-down.

### 6. Hub strapped as self-powered

CFG_SEL[1:0] = 00 (R6 and R7 pull-downs) selects the default configuration:
self-powered, reporting 2 mA from upstream. The board is actually bus-powered,
so the host's power accounting is wrong.

This may be intentional. It lets DUTs that request 500 mA configure, which a
correctly reported bus-powered hub would refuse (100 mA per port). If it is
intentional, document it. If not, pull HS_IND/CFG_SEL1 high to select
bus-powered operation.

### 7. Shared reset power-cycles the DUT

`RST_N` is one net shared by:

- the SAMD21 RESET_N
- the USB2512B RESET_N
- the LP3470 output
- J1 pin 10 (SWD nRESET)

When the MCU is in reset its pins float, and R15 pulls the NCP380 EN low. Any
debugger reset, watchdog reset or firmware update therefore:

- removes DUT VBUS, and
- resets the hub, re-enumerating everything downstream.

Defaulting to off is safe, but a remote power-cycler may want the DUT to stay
powered across MCU resets. If so:

- give the hub its own reset (LP3470 only, not the SWD header), and
- change R15 to a pull-up, or choose a default state deliberately.

### 8. DUT USB pair impedance

DUT_USB_D_P/N are routed as 0.127 mm traces with a gap of about 0.27 mm, mostly
on B.Cu, for about 45 mm with 2 vias. On OSH Park's 0.17 mm prepreg that is
roughly 130–140 Ω differential (first-order microstrip estimate), against a
90 Ω target.

Two further points:

- B.Cu references the In2 P3V3 plane rather than ground.
- Near U8 (around x = 133, y = 98.6), D+ on B.Cu crosses the slot that the
  DUT_USB_VBUS trace cuts in In2.

It will likely work at high speed but has little margin.

**Fix:** use a 90 Ω pair (wider traces, tighter gap) on F.Cu over the In1
ground plane, and avoid crossing plane slots.

## Low

- **Crystal case pads:** X1 and X2 pins 2 and 4 are unconnected. NDK
  recommends tying them to GND.
- **RBIAS:** R5 is 12.1 kΩ; the datasheet specifies 12.0 kΩ ±1%.
- **SWO:** J1 pin 6 is wired to PA28 as SWO, but the SAMD21's Cortex-M0+ has no
  SWO. Harmless.
- **J4 auxiliary sense inputs:**
  - They go straight to PAC1934 pins with no ESD protection or RC filtering.
  - Pin 2 is the header's only GND. It is shared by the open-collector output
    return currents and the sense reference, so output current shifts the
    aux-channel VBUS readings.
- **Discharge sequencing:** `sw/main.c:122-123` turns on DUT_DISCHARGE before
  clearing DUT_USB_EN. The NCP380 takes 1–3 ms to turn off, so R17 (0603,
  0.1 W) briefly dissipates about 125 mW. Swap the two writes.

## Looks good

- NCP380 EN pull-down, so VBUS defaults to off; FLAG_N routed to the MCU.
- 120 µF polymer capacitor on the downstream port, as USB requires.
- USBLC6-4 ESD protection on both the upstream and downstream connectors.
- PAC1934 sense traces tap directly at the R22 pads (Kelvin connection).
- DUT VBUS current path is 0.6 mm wide on the outer layer.
- Solid In1 ground plane under the top-layer routing.
- 1 kΩ SWCLK pull-up, per the SAMD21 design guidelines.
- LP3470 supervisor with a 200 ms reset timeout (C18 = 100 nF).
- PAC1934 exposed pad left floating, which its datasheet allows ("not
  electrically connected").
