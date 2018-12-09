## UPM - USB Power Monitor

This device monitors current and voltage for USB powered devices.

# Hardware
![](https://github.com/jonpe960/upm/raw/master/doc/photo.jpg)
Assembled PCB 

The PCB is a four layer board, manufactured by OSH Park. The boards can
 be ordered [here](https://oshpark.com/shared_projects/uE5lZDkP)

Schematics, layout and BOM can be found [here](https://github.com/jonpe960/upm/hw/release/R1)

# System description
![](https://github.com/jonpe960/upm/raw/master/doc/system_diagram.png)


The device has a built in, two port, USB hub. One of the down stream ports
connects to the USB A connector and the other down stream port is connected to
the microcontroller.

An integrade analog frontend that contains a 16 bit ADC and differential
amplifier measures the voltage and current of the down stream VBUS supply. Three
auxillary diff inputs are available on a pin header.

It is possible to control the output VBUS with the on board power switch, which
also has built in short circuit protection. Three auxillary, open collector,
outputs are available on pin header.

# Ncurses TUI

![](https://github.com/jonpe960/upm/raw/master/doc/screenshot.png)

The ncurses based TUI, displaying voltage, current and energy usage. 
Outputs can be controled from the TUI:
 - A/a VBUS on/off
 - S/s out1 on/off
 - D/d out2 on/off
 - F/f out3 on/off
 - r Reset energy counters


# Intended usage

This project came from a need to remotley monitor and power cycle USB powered devices.

# Future improvements

 - Add domain/tcp socket listener for remote control
 - Support for logging



