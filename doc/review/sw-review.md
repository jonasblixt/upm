# UPM firmware and PC tool review

Review of the SAMD21 firmware (`sw/`) and the ncurses PC tool (`sw/tools/upm/`).
This is a code review only: nothing was built or run on hardware. Items marked
"likely" follow from reading the code and the datasheets but have not been
reproduced.

See also [hw-r1-review.md](hw-r1-review.md). Some issues below interact with the
hardware.

## Summary

| # | Severity | Where | Issue |
|---|----------|-------|-------|
| F1 | High | `sw/usb.c:284` | Unknown descriptor request hangs the firmware |
| F2 | High | `sw/usb.c:301-303` | GET_STATUS sends a stray ZLP and blocks the main loop (likely) |
| F3 | High | `sw/i2c.c`, `sw/pac193x.c` | I2C errors ignored; several unbounded waits; no watchdog |
| F4 | High | `sw/main.c:94-97` | Read issued about 1 ms after REFRESH_V, which the PAC NACKs (likely) |
| P1 | High | `sw/tools/upm/upm.c:94-106` | NULL handle dereferenced when open fails |
| E1 | High | `sw/tools/upm/upm.c:53-64` | Energy conversion uses an unexplained ×100 factor |
| F5 | Medium | `sw/main.c:85` | `in.outputs` uninitialised, so the reported output state is wrong at start |
| F6 | Medium | `sw/usb.c:57-62, 104-105, 264` | String descriptor bugs; every unit has serial "UPM" |
| F7 | Medium | `sw/main.c` | NCP380 FLAG_N (overcurrent) never read or reported |
| F8 | Medium | `sw/usb.c:207-227, 325-330` | Buffers rewritten or re-armed while the USB DMA may use them |
| F9 | Low | various | Stack alignment, descriptor nits, `-O0` timing, toolchain prefix |
| P2–P7 | Medium/Low | `sw/tools/upm/` | Short reads, aux-channel scaling, device selection, libusb cleanup, udev permissions |

## Firmware

### F1. Unknown descriptor request hangs the firmware (High)

`usb_enumerate()` ends its GET_DESCRIPTOR chain with `while(1);` (`sw/usb.c:284`).
Any descriptor the firmware doesn't know locks up the MCU until reset.

Examples of requests that trigger it:

- a string index other than 0 or 1
- Windows' MS OS string descriptor query (string 0xEE)
- any other descriptor type

Other unhandled requests fall through `default:` with no response. These include
GET_CONFIGURATION, GET/SET_INTERFACE, CLEAR_FEATURE (used by
`libusb_clear_halt`) and interface/endpoint GET_STATUS. The host then waits for
its control-transfer timeout, about 5 s.

**Fix:** STALL EP0 for unsupported requests (set STALLRQ1/STALLRQ0 in
EPSTATUSSET(0)) instead of looping or ignoring them.

### F2. GET_STATUS sends a stray zero-length packet (High, likely)

```c
case USB_GET_STATUS:
    usb_send_ep0((uint8_t *) &device_status, 2);
    usb_send_ep0(NULL,0);
```

The status stage of a control read is an OUT ZLP from the host. The second
`usb_send_ep0()` arms an extra IN ZLP and then busy-waits, with no timeout, for
it to be sent.

No further IN token arrives on EP0 until the next control read, so:

1. The whole main loop stops: no PAC reads and no data to the host.
2. When the next control read arrives, its data stage receives the stale ZLP
   instead of the real descriptor.

`lsusb -v` issues a device GET_STATUS, so it is a plausible trigger.

**Fix:** remove the second `usb_send_ep0(NULL,0)`. Also add a timeout to
`usb_send_ep0()`; commit e9040a0 added one to `usb_send()` only.

### F3. I2C error handling (High)

None of the `i2c_*` return values are checked by `pac193x.c`. After a NACK, the
code still calls `i2c_write_byte()` and `i2c_read_byte()` on a bus it no longer
owns. Several waits have no exit:

- `sw/i2c.c:71`: `i2c_start()` waits for MB/SB only. A bus error (INTFLAG.ERROR)
  is never seen.
- `sw/i2c.c:105-114` and `136-145`: these loops exit only on a flag, which never
  comes if no transaction is in progress.
- There's no SERCOM bus timeout (CTRLA.INACTOUT / LOWTOUTEN) and no watchdog.

A single glitch on the PAC bus therefore freezes the device permanently. Hardware
review item 7 notes that an MCU reset also power-cycles the DUT, so a hang
followed by a manual or watchdog reset is disruptive either way.

**Fix:**

- Bound every wait.
- Propagate errors from `i2c_*` and abort the transaction on failure.
- Enable LOWTOUTEN/INACTOUT.
- Add a WDT once the loop can no longer block indefinitely.

### F4. PAC read issued inside the 1 ms post-REFRESH window (High, likely)

The PAC1934 datasheet (§4.1) says "Changes written to the control and
configuration registers take effect 1 mS after a REFRESH command is sent. Any
new commands written within this 1 mS window will be ignored and NACKed."

`sw/main.c:94-97` sends REFRESH_V and then waits `0xfff` iterations of a `nop`
loop. At `-O0` and 48 MHz with 1 flash wait state, that is roughly 0.8–1.3 ms,
with no margin. A NACKed read then hits F3. Separately, a NACK means the values
returned for that iteration are garbage.

**Fix:** use a timer-based delay of at least 1.5 ms, or poll with retries once
I2C errors are handled. The 14 ms start-up delay in `pac193x_init()`
(`sw/pac193x.c:23-24`) has the same dependency on `-O0` code generation.

### F5. Output state reported uninitialised (Medium)

`struct upm_in in;` (`sw/main.c:85`) is a stack variable that is never
initialised. Its `outputs` field is only updated when a command arrives.
Meanwhile the firmware switches DUT VBUS on at boot (`sw/main.c:40`).

The TUI therefore shows random ON/OFF states until each output has been toggled
once.

**Fix:** zero-initialise `in`, then set `in.outputs = 1` to match the boot
state. Better still, derive `outputs` from the PORT OUT register each time it
is reported.

### F6. String descriptors (Medium)

- **Wrong length:** `usb_string_id` declares `bLength = 0x16` (22) but is only
  8 bytes long (`sw/usb.c:104-105`). It should be `0x08`.
- **Swapped LANGID:** `"\x04\x03\x04\x09"` (`sw/usb.c:264`) sends LANGID 0x0904.
  US English, 0x0409, is sent as bytes `09 04`.
- **One string for everything:** manufacturer, product and serial all use index
  1 (`sw/usb.c:60-62`). Every unit therefore reports serial "UPM", so
  multiple UPMs on one host can't be told apart (see P4).
  - **Fix:** build the serial from the SAMD21 128-bit serial number words at
    0x0080A00C and 0x0080A040–0x0080A048.
- **Placeholder VID/PID:** 0xFFFF/0x0003 is not an assigned ID (the code comments
  say so). It's fine for a hobby tool, but it may collide with other hobby
  devices.

### F7. Overcurrent flag ignored (Medium)

PA05 (DUT_USB_FLAG_N) is set up as an input (`sw/main.c:36`) but never read. The
host can't tell that the NCP380 has tripped on overcurrent or thermal limit.

**Fix:** report it in `struct upm_in`. The `outputs` word has spare bits, so
the protocol doesn't need to change size.

### F8. USB buffer races (Medium)

- **Torn packets:** when `usb_send()` times out (`sw/usb.c:220-225`), BK1RDY
  stays set. The next call `memcpy`s into `ep3_buf_in` while that bank is still
  armed, so the host can receive a mix of two samples.
  - **Fix:** clear BK1RDY on timeout, or skip the copy while the bank is busy.
- **Early re-arm:** `usb_get_buf()` clears BK0RDY, re-arming EP2, before
  `main()` has read the command (`sw/usb.c:328`). A second OUT packet could
  overwrite it mid-parse. Today the host sends one OUT per IN, so this is
  latent.
  - **Fix:** copy the buffer before re-arming.

### F9. Low

- **Stack:**
  - The initial SP is `&stack[__STACK_SIZE-1]` (`sw/init.c:157`). This is odd,
    so the core truncates it to 4-byte alignment, which is not the 8-byte
    alignment AAPCS requires. Use `&stack[__STACK_SIZE]`.
  - The Makefile sets the stack to 256 bytes (`-D__STACK_SIZE=0x100`), which is
    tight at `-O0`. 4 KB of SRAM is available.
- **Power descriptor:** the comment on `bmAttributes = 0x80` says "Self powered",
  but 0x80 means bus-powered. `MaxPower = 0xfa` claims 500 mA for the MCU
  function. 100 mA (0x32) is plenty and would still configure behind a
  bus-powered hub (see hardware review item 6).
- **SET_CONFIGURATION:** a value of 0 (unconfigure) still sets `_enumerated`.
- **Device qualifier:** returned even though the SAMD21 is full-speed only. The
  spec says a full-speed-only device should STALL this request.
- **Timing:** all delays are `nop` loops whose length depends on `-O0`. A SysTick
  or TC-based delay would survive an optimisation-level change.
- **Toolchain:** `CROSS_COMPILE ?= arm-eabi-`. Most distributions ship
  `arm-none-eabi-`.
- **PAC sample rate:** the PAC still samples at 8 SPS because of the SLOW pin
  (hardware review item 5). The firmware can fix this without a board change by
  writing CTRL bit 3 (ALERT_PIN) in `pac193x_init()`.

## Energy scaling (firmware, PC tool and hardware together)

### E1. Unexplained ×100 in `raw2mWh()` (High)

The PAC1934 datasheet (Eq. 4-9, unipolar) gives:

    Energy [J] = VPOWER_ACC / 2^28 × PowerFSR / fs,   PowerFSR = 3.2 V² / Rsense = 32 W

so:

    mWh = VPOWER_ACC / 2^28 × 32 / fs / 3.6

`raw2mWh()` (`sw/tools/upm/upm.c:53-64`) uses fs = 1024 and then multiplies by an
extra 100. The likely explanation is that the PAC actually runs at 8 SPS
(hardware review item 5), which is 128× fewer samples than assumed. The ×100
looks like an empirical correction for that. If so:

- Today, energy reads about 22 % low (100/128).
- After fixing the SLOW pin, energy will read 100× high.

**Fix:**

- Fix the sample rate (F9, last item).
- Remove the ×100.
- Better: compute energy from the actual sample rate, or report fs (or the
  CTRL register) in `struct upm_in` so the host doesn't have to assume.

Voltage and current scaling (`× 32 / 0xFFFF`, `× 1000 / 0xFFFF` mA for 0.1 Ω)
are correct for channel 0.

## PC tool

### P1. NULL handle dereferenced when open fails (High)

`sw/tools/upm/upm.c:94-106`:

```c
h = libusb_open_device_with_vid_pid(ctx, 0xffff, 0x0003);
if (libusb_kernel_driver_active(h, 0)) ...
err = libusb_claim_interface(h, 0);
...
if (h == NULL) {
```

The NULL check comes after `h` has been used. Missing permissions (no udev rule
installed) crashes the tool instead of printing "Could not open device".

**Fix:** move the check directly after the open. It's also simpler to call
`libusb_open(dev, &h)` on the device that `find_device()` already found.

### P2. Short reads not checked (Medium)

`rx_sz` is never compared with `sizeof(struct upm_in)` (`upm.c:131-133`). A short
or zero-length packet is parsed as stale or partial data.

### P3. Aux-channel current assumes a 0.1 Ω shunt (Medium)

Channels 1–3 use the same `× 1000 / 0xFFFF` mA conversion as channel 0
(`upm.c:192-201`). This is only right if the external shunts on J4 are also
0.1 Ω, and that isn't documented. Make the shunt values configurable, for
example with a command-line option.

### P4. First device wins (Medium)

The tool opens the first device with matching VID/PID. Once F6 provides
per-device serials, add a `-s <serial>` option.

### P5. libusb context and cleanup (Low)

- **Mixed contexts:** `libusb_init(&ctx)` creates a private context, but
  `libusb_get_device_list(NULL, …)` and `libusb_exit(NULL)` use the default
  context. Recent libusb warns about this ("API misuse"), and `ctx` is never
  freed. Use `ctx` throughout.
- **No cleanup:** the interface is never released and the handle never closed.
- **Unused uuid:** `-luuid` is linked twice and `uuid/uuid.h` is included, but
  uuid is never used.

### P6. udev rule is world-writable (Low)

`30-upm.rules` sets `MODE="0666"`, so any local user, including service
accounts, can switch DUT power. `GROUP="adm"` has no effect with 0666. Use
`MODE="0660", GROUP="plugdev"` or `TAG+="uaccess"`.

### P7. Documentation (Low)

`sw/tools/upm/gui.txt` describes per-channel `dx`/`ex`/`rx` commands and mAh
units. The tool implements neither: `r` resets all accumulators (PAC REFRESH),
and the display shows mWh.

## Looks good

- Clock tree: 16 MHz XOSC → DPLL at 1 MHz reference → 48 MHz, with 1 flash wait
  state, gives a crystal-accurate USB clock without relying on DFLL clock
  recovery.
- USB pad calibration loaded from NVM OTP4.
- SERCOM1 pin mux (PA00/PA01, function D) and USB mux (PA24/PA25, function G)
  are correct.
- The PAC address (0x20 write, i.e. 7-bit 0x10) matches ADDRSEL tied to GND.
- REFRESH_V is used in the loop, so the accumulators aren't reset on every
  read.
- The VBUS enable defaults to on only after the firmware is running, and the
  hardware pull-down keeps it off before that.
- The protocol structs are packed and shared between firmware and host through
  one header (`sw/protocol.h`).
