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
| Maximum DUT current? | Sets the shunt value, switch rating, trace widths and the external supply |
| µA-level sleep current measurement needed? | One shunt can't resolve both µA and A; needs a second range |
| USB-PD / >5 V DUTs in scope? | Needs CC pass-through and a high-voltage power path, a much larger project |
| Fast transients (inrush, spikes) of interest? | 1024 SPS PAC1934 is too slow; affects the choice of monitor |

## Architecture: power the DUT from a separate input

R1 powers the DUT from the upstream port's VBUS. That limits the DUT to what a
host port supplies, and it is why the hub has to claim to be self-powered
(HW 1, HW 6).

**Recommended: 5 V DUTs up to about 3 A.**

- Add a 5 V power input (USB-C sink or barrel jack) that feeds the DUT power
  switch.
- The upstream USB port powers only the UPM itself.
- The hub then truthfully reports self-powered, using LOCAL_PWR to detect the
  external supply.
- The FB1 rating, upstream current budget and hub strap issues disappear.
- This covers Raspberry Pis, dev boards and most remote power-cycling use cases.

**Alternative: USB-PD DUTs (9–20 V).** This needs CC-line pass-through, a
high-voltage switch and much more validation. The PAC1934 can measure up to
32 V, but the rest of the power path changes. Only worth doing if it is
actually needed.

## Must change

### Power path

- **Replace the NCP380** (a 5.5 V part) with a power switch or eFuse that has:
  - an adjustable current limit at or above the target DUT current,
  - built-in output discharge, which removes Q1A and R17 (HW 9, discharge
    sequencing),
  - a fault output routed to an MCU interrupt pin (F7).
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
