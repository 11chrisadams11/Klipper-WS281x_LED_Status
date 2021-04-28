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

----

rpi_ws281x library instructions for needed changes depending on GPIO pin used: https://github.com/jgarff/rpi_ws281x
