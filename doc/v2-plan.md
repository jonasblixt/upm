# UPM V2 plan

Proposed changes for UPM V2, based on the R1 reviews:

- [review/hw-r1-review.md](review/hw-r1-review.md)
- [review/sw-review.md](review/sw-review.md)

References such as "HW 1" or "F3" point to items in those reviews. Part numbers
here are families to evaluate, not verified selections.

## Open questions

These set the scope of V2 and should be answered before schematic work starts.

| Question | Why it matters |
|----------|----------------|
| µA-level sleep current measurement needed? | One shunt can't resolve both µA and A; needs a second range |
| Fast transients (inrush, spikes) of interest? | 1024 SPS PAC1934 is too slow; affects the choice of monitor |

Answered: maximum DUT current 3 A, and USB-PD up to 20 V is in scope (Power
architecture, below).

## Power architecture

Decided 2026-11-20. R1 powers the DUT from the upstream port's VBUS, which limits
it to what a host port supplies (HW 1, HW 6). V2 keeps that as the fallback and
adds a USB-PD power input.

**The DUT port (J2) is a USB-PD source** with fixed voltages up to 20 V at 3 A
(60 W). There is no PPS, no EPR and no 5 A, so there is no cable e-marker
discovery and no VCONN supply. The UPM puts more than 5 V on the DUT only when
the DUT asks for it, so a PD trigger cable covers barrel-jack DUTs too.

**Two power sources:**

- **J1, the host port:** data and 5 V. A plain sink, with 5.1 kΩ Rd on each CC
  and both CC lines to the MCU's ADC to read the host's Rp level (default,
  1.5 A or 3 A). There is no PD on J1.
- **J4, the PD power input:** a third USB-C on bezel A, with J1 and J4 equally
  spaced (`v2-pcb.md` §1). It is a PD sink that asks a charger for one voltage,
  set per installation: 5, 9, 12, 15 or 20 V.

**What the DUT is offered:**

| Connected | DUT gets |
|---|---|
| J1 only | 5 V. The current is the host's advertisement less the UPM's own draw, 3 A at most |
| J4, at 9 to 20 V | 5 V at 3 A from a local buck, plus the configured voltage passed through from J4, at the charger's current for it up to 3 A |
| J4, at 5 V or a non-PD supply | 5 V passed through from J4. The buck is not used |

In J1-only mode a PD DUT gets the exact budget in the source capabilities. A
non-PD DUT only sees the three Rp levels. **By default it gets the highest level
within the budget**, so 1.5 A from a 3 A host. A firmware setting can pass the
host's level on instead, with the current limit as the backstop. The firmware
watches J1's CC and offers less when the host does.

**DUT power at power-up: off by default** (decided 2026-11-20). It is a firmware
setting, kept in flash, so it can become on or the last state later. The
hardware already defaults to off: J2's PD controller doesn't source until the
MCU has loaded its configuration.

**PD controllers: two TI TPS25751D** (decided 2026-11-20), one per port, on the
SAMD21E18's I2C. The MCU loads each one's configuration (TI's "patch bundle")
over I2C at start-up, as in TI app note SLVAFV8A, and controls it through the
host interface (TRM SLVUCR8B). No EEPROM is needed. The TPS25751D integrates:

- a 5 V / 3 A source switch (PP5V to VBUS) with current limit and UVP/OVP,
- a 20 V / 5 A bidirectional high-voltage switch (PPHV to VBUS_IN) with
  reverse-current protection, UVP/OVP and slew-rate control,
- CC pins tolerant to 26 V, which covers the CC over-voltage item below.

The symbol is `power_mgmt:TPS25751D` and the footprint
`Jonas:Texas_REF0038A_WQFN-38-2EP_4x6mm_P0.4mm`, both in kicadlib. The
datasheets are in `Z:\Library\Datasheets\power_mgmt\tps25751\`.

**Power path:**

- **J4 controller (sink):** J4's VBUS to its VBUS_IN, its PPHV to the UPM's
  high-voltage node, `VIN_HV`.
- **J2 controller (source):** PPHV from `VIN_HV` for the configured voltage,
  PP5V from the DUT 5 V rail for 5 V, VBUS and VBUS_IN to J2 through the
  shunt. The two switches and their slew control replace the separate path
  switches.
- **DUT 5 V rail:** a buck from `VIN_HV`, or J1's VBUS through an ideal diode,
  with the buck taking priority. **J1's path blocks reverse current: the UPM
  must never drive the host's VBUS.** The 20 V from the DUT side is held off
  inside the TPS25751D, by PP5V's switch.
- The UPM powers itself from J1 or J4, OR'd. With J4 connected, a host reboot
  that drops J1's VBUS then doesn't power-cycle the DUT. The hub's VBUS_DET
  follows J1 alone, and LOCAL_PWR shows whether J4 is present: the hub reports
  self-powered only when it is. The TPS25751Ds run from the UPM's 3.3 V, so an
  MCU reset leaves the PD contract alone.

**Measurement:** PAC1934 channels for the DUT, J4 and J1, plus one spare. 20 V is
within the PAC1934's 32 V.

**To settle in the schematic:**

- With J4 at 5 V, whether J2's controller can source its 5 V offer through PPHV,
  or the 5 V rail needs a bypass around the buck (TRM SLVUCR8B).
- Whether a separate eFuse is still needed after J2's controller, given the
  TPS25751D's own limits.

Settled 2026-11-20 (`hw/v2/pd.kicad_sch`, data sheet Tables 8-5 and 8-6):

- **U1 (J4, sink):** ADCIN1 tied to LDO_3V3, ADCIN2 to LDO_1V5, which selects
  "AlwaysEnableSink" at I2C address 0x20. It sinks 5 V onto VIN_HV before any
  configuration, so J4 alone starts the UPM; PD stays off until the MCU loads the
  configuration.
- **U2 (J2, source):** both ADCIN pins to GND, which selects "SafeMode" at 0x21.
  There is no sink path and no PD until the configuration is loaded.
- Both I2C controller ports are unused, pulled up to LDO_3V3, and all GPIOs are
  tied to GND, as TI says.
- **Capacitors, as on TI's EVM:**
  - 10 µF on VIN_3V3, LDO_3V3, LDO_1V5 and PP5V,
  - 4.7 µF / 50 V on VBUS,
  - 220 pF on each CC line,
  - 2 × 22 µF + 22 µF + 2 × 100 nF on VIN_HV,
  - 150 µF POSCAP on P5V (PP5V needs 120 µF).
- The REF0038A land's 0.10 mm gaps have a DRC rule (`v2-pcb.md` §7).

**MCU pins** (`hw/v2/mcu.kicad_sch`; R1's I2C pins kept):

| Pin | Use |
|---|---|
| PA00, PA01 | I2C_SDA, I2C_SCL (SERCOM1), 2.2 kΩ pull-ups |
| PA10, PA11 | J1 CC1/CC2 (AIN18/19) through 10 kΩ, with 5.1 kΩ Rd at J1 |
| PA14, PA15 | 16 MHz crystal (NX2520SA, 12 pF) |
| PA16, PA17 | PDI_IRQ_N (U1), PDD_IRQ_N (U2): EXTINT0/1, 10 kΩ pull-ups |
| PA24, PA25 | USB D−/D+ to the hub |
| PA30, PA31, RESET_N | SWD on a Tag-Connect TC2030-NL footprint (J5) |
| PA02–PA09, PA18, PA19, PA22, PA23, PA27, PA28 | free: hub, PAC1934, LED, outputs |

## Must change

### Power path

- **Replace the NCP380** (a 5.5 V part). J2's TPS25751D now switches and
  protects the DUT's VBUS; if a separate eFuse is still needed (see above), it
  has:
  - a rating of 28 V or more, for 20 V PD with margin,
  - reverse-current blocking, for DUTs with their own supply,
  - an adjustable current limit at or above the target DUT current,
  - built-in output discharge, which removes Q1A and R17 (HW 9, discharge
    sequencing),
  - a fault output routed to an MCU interrupt pin (F7).
- **Over-voltage protection on the CC and VBUS pins of J2 and J4.** A cable
  with CC shorted to VBUS puts 20 V on CC. The TPS25751D's CC pins tolerate
  26 V; VBUS still needs a TVS at each connector.
- **Default the DUT switch to off independently of the MCU**, and let the
  firmware decide the state after a reset. A watchdog or debugger reset should
  not power-cycle the DUT (HW 7).
- **Give the hub its own reset**, driven by the supervisor only and not shared
  with the SWD header (HW 7).

### Measurement

- **Match the shunt to the current limit** (HW 2). For 3 A full scale on the
  PAC1934, use 33 mΩ (about 46 µA per count).
- **Measure the DUT voltage on the connector side of the shunt** (HW 2).
- **Strap the PAC1934 SLOW pin low**, or route it to the MCU (HW 5, E1).
- **Low-current sleep measurements (if required):** add a high-value shunt in
  series with the main one, shorted by a MOSFET when current rises, and read it
  on a second PAC1934 channel.
- **Fast transients (if required):** use a faster single-channel monitor with
  energy accumulation for the DUT channel (TI INA228 is one to evaluate), and
  keep the PAC1934 for the aux inputs.

### Carry-over fixes from R1

- Do not fit the extra USB2512B CRFILT/PLLFILT capacitors, C5 and C7 (HW 3).
- Correct the MIC23150 footprint, including the exposed pad, and verify the
  pinout (HW 4).
- Connect the crystal case pads to GND.
- Route 90 Ω USB pairs on F.Cu over the ground plane. Keep the DUT pair short by
  placing the hub near the downstream connector, and don't cross plane slots
  (HW 8).
- Give J4 more GND pins, and keep output return currents separate from the
  sense reference.
- Add ESD protection and RC filtering on the aux sense inputs.

## Should change

- **USB-C upstream connector**, USB 2.0 only with two 5.1 kΩ pull-downs on CC,
  replacing micro-B.
- **USB data switch on DUT D+/D-** (a 2:1 analog switch such as the TS3USB221
  class). It allows a simulated unplug, including for DUTs with their own power,
  and charge-only tests.
- **Let the hub control DUT power too.** Route the hub's PRTPWR1 to an MCU input
  and have the firmware AND it into the switch enable. Standard tools such as
  `uhubctl` and the kernel's port-power controls then work without the custom
  tool.
- **SAMD21E18 instead of SAMD21E15.** It has the same footprint, with 256 KB
  flash and 32 KB RAM: room for a USB bootloader, so firmware can be updated
  without SWD.
- **LEDs:** VBUS on, fault, and the hub's SUSP_IND.
- **Flyback diodes on the open-collector outputs**, if they may drive relay
  coils.
- **Board-revision straps** (GPIO pins tied high or low) so the firmware can
  identify the hardware revision.

## Firmware

- **Replace the hand-written USB stack** with an established one, such as
  TinyUSB:
  - fixes the hang, STALL and descriptor bugs at the source (F1, F2, F6),
  - gives a per-unit serial number from the SAMD21 unique ID,
  - adds WinUSB/MS OS 2.0 descriptors so Windows needs no driver.
- **Robustness:**
  - timer-driven sampling instead of `nop` loops (F4, F9),
  - bounded I2C transactions with error handling (F3),
  - PAC ALERT handled through an interrupt,
  - watchdog enabled.
- **Timestamp samples** so the host can compute rates and detect gaps.
- **Versioned protocol:** report the protocol version, sample rate and shunt
  values to the host, so it never hard-codes assumptions like the ×100 energy
  factor (E1).
- **USB bootloader** (UF2 or DFU) on the larger MCU.

## Host software

- **A small library** for device access, unit conversion and energy
  calculation, used by every client.
- **A daemon**, covering the README's "future improvements":
  - remote control over a TCP or Unix socket,
  - logging, for example to CSV.
- **A CLI** for scripting: power on/off/cycle, read once, log.
- **The TUI**, kept as one client of the daemon.
- **Device selection by serial number** (P4).
- **udev rule:** `MODE="0660"` with a group, or `TAG+="uaccess"`, instead of
  world-writable (P6).
