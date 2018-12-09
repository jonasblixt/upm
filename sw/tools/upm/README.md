
Install udev rules:

copy '30-upm.rules' to /etc/udev/rules.d/

Reload udev rules:

udevadm control --reload-rules && udevadm trigger
