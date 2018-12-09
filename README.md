## UPM - USB Power Monitor

This device monitors current and voltage for USB powered devices.

![](https://github.com/jonpe960/upm/raw/master/doc/photo.jpg)
Assembled PCB

![](https://github.com/jonpe960/upm/raw/master/doc/system_diagram.png)
The device has a built in, two port, USB hub. One of the down stream ports'
connects to the USB A connector and the other down stream port is connected to
the microcontroller.

An integrade analog frontend that contains a 16 bit ADC and differential
amplifier measures the voltage and current of the down stream VBUS supply. Three
auxillary diff inputs are available on a pin header.

It is possible to control the output VBUS with the on board power switch, which
also has built in short circuit protection. Three auxillary, open collector,
outputs are available on pin header.

![](https://github.com/jonpe960/upm/raw/master/doc/screenshot.png)

The ncurses based TUI, displaying voltage, current and energy usage. 

# Intended usage

This project came from a need to remotley monitor and power cycle USB powered devices.

# Future improvements

 - Add domain/tcp socket listener for remote control
 - Support for logging



