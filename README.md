# Klipper-WS281x_LED_Status
This script will take the printer status from Klipper/Moonraker and apply different effects to a WS281x LED strip.

The code has been migrated from the OctoPrint-WS281x_LED_Status (https://github.com/cp2004/OctoPrint-WS281x_LED_Status) plugin to work with Klipper.

----

## Directions for use

1. Clone/copy code to file on Raspberry Pi running Klipper and Moonraker
2. Make script executable
   1. ```chmod 744 ./klipper-ledstrip.py```
4. Install prerequsits 
   1. ```pip3 install requests rpi_ws281x adafruit-circuitpython-neopixel```
5. Change values in script (LED pin, colors, reverse)
6. Optionally, change effect called for standby, paused, and error states
7. Run script before starting print
   1. ```./klipper-ledstrip.py```

### Single run for static colors

```
./klipper-ledstrip.py <red> <green> <blue> <brightness:optiona>

Example:
  ./klipper-ledstrip.py 255 255 255 255 ## Full brightness white
  ./klipper-ledstrip.py 255 0 0 ## Red with default brightness specified in the script
```

#### To call from gcode shell commands (thanks to [JV_JV](https://www.reddit.com/user/JV_JV/) for the setup directions)
Add custom entries to printer.cfg 

```
[gcode_shell_command led_off]
command: ./home/pi/my_klipper_ledstrip.py 0 0 0
timeout: 2.
verbose: True

[gcode_shell_command led_white]
command: ./home/pi/my_klipper_ledstrip.py 255 255 255
timeout: 2.
verbose: True

[gcode_shell_command led_purple]
command: ./home/pi/my_klipper_ledstrip.py 255 0 255
timeout: 2.
verbose: True

[gcode_macro LED_OFF]
gcode:
    RUN_SHELL_COMMAND CMD=led_off

[gcode_macro LED_WHITE]
gcode:
    RUN_SHELL_COMMAND CMD=led_white

[gcode_macro LED_PURPLE]
gcode:
    RUN_SHELL_COMMAND CMD=led_purple
```

----

rpi_ws281x library instructions for needed changes depending on GPIO pin used: https://github.com/jgarff/rpi_ws281x
