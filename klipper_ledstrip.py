#!/usr/bin/env python3
# pylint: disable=C0326
'''
Script to take info from Klipper and light up WS281x LED strip based on current status
'''

import sys
import json
import math
import time
import requests
from rpi_ws281x import Adafruit_NeoPixel

LED_COUNT      = 10      # Number of LED pixels.
LED_PIN        = 10      # GPIO pin connected to the pixels (18 uses PWM, 10 uses SPI).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 100     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

## Colors to use                 R    G    B
BED_HEATING_BASE_COLOR        = (0  , 0  , 255)
BED_HEATING_PROGRESS_COLOR    = (238, 130, 238)
HOTEND_HEATING_BASE_COLOR     = (238, 130, 238)
HOTEND_HEATING_PROGRESS_COLOR = (255, 0  , 0  )
PRINT_BASE_COLOR              = (0  , 0  , 0  )
PRINT_PROGRESS_COLOR          = (0  , 255, 0  )
STANDBY_COLOR                 = (255, 0  , 255)
COMPLETE_COLOR                = (235, 227, 9  )
PAUSED_COLOR                  = (0  , 255, 0  )
ERROR_COLOR                   = (255, 0  , 0  )

## Reverses the direction of progress and chase
REVERSE = True

SHUTDOWN_WHEN_COMPLETE = True
BED_TEMP_FOR_OFF       = 35
HOTEND_TEMP_FOR_OFF    = 30

def printer_state():
    ''' Get printer status '''
    url = 'http://localhost:7125/printer/objects/query?print_stats'
    ret = requests.get(url)
    return json.loads(ret.text)['result']['status']['print_stats']['state']


def component_temp(component, just_temp=True):
    ''' Get temperature of given component '''
    url = f'http://localhost:7125/printer/objects/query?{component}'
    temp_data = json.loads(requests.get(url).text)['result']['status'][component]
    return temp_data['temperature'] if just_temp else temp_data


def heating_percent(component):
    ''' Get heating percent for given component '''
    temp = component_temp(component, False)
    if temp['target'] == 0.0:
        return 0
    return math.floor(temp['temperature'] / temp['target'] * 100)


def printing_percent():
    ''' Get printing progress percent '''
    url = 'http://localhost:7125/printer/objects/query?display_status'
    req = json.loads(requests.get(url).text)
    return math.floor(req['result']['status']['display_status']['progress']*100)


def power_off():
    ''' Power off the printer '''
    url = 'http://localhost:7125/machine/device_power/off?printer'
    return requests.post(url).text


def average(num_a, num_b):
    ''' Average two given numbers '''
    return round((num_a + num_b) / 2)


def mix_color(colour1, colour2, percent_of_c1=None):
    ''' Mix two colors to a given percentage '''
    if percent_of_c1:
        colour1 = [x * percent_of_c1 for x in colour1]
        percent_of_c2 = 1 - percent_of_c1
        colour2 = [x * percent_of_c2 for x in colour2]

    col_r = average(colour1[0], colour2[0])
    col_g = average(colour1[1], colour2[1])
    col_b = average(colour1[2], colour2[2])
    return tuple([int(col_r), int(col_g), int(col_b)])


def color_brightness_correction(color, brightness):
    ''' Adjust given color to set brightness '''
    brightness_correction = brightness / 255
    return (
        int(color[0] * brightness_correction),
        int(color[1] * brightness_correction),
        int(color[2] * brightness_correction)
    )


def progress(strip, percent, base_color, progress_color):
    ''' Set LED strip to given progress with base and progress colors '''
    strip.setBrightness(LED_BRIGHTNESS)
    num_pixels = strip.numPixels()
    upper_bar = (percent / 100) * num_pixels
    upper_remainder, upper_whole = math.modf(upper_bar)
    pixels_remaining = num_pixels

    for i in range(int(upper_whole)):
        pixel = ((num_pixels - 1) - i) if REVERSE else i
        strip.setPixelColorRGB(pixel, *color_brightness_correction(progress_color, LED_BRIGHTNESS))
        pixels_remaining -= 1

    if upper_remainder > 0.0:
        tween_color = mix_color(progress_color, base_color, upper_remainder)
        pixel = ((num_pixels - int(upper_whole)) - 1) if REVERSE else int(upper_whole)
        strip.setPixelColorRGB(pixel, *color_brightness_correction(tween_color, LED_BRIGHTNESS))
        pixels_remaining -= 1

    for i in range(pixels_remaining):
        pixel = (
            ((pixels_remaining - 1) - i)
            if REVERSE
            else ((num_pixels - pixels_remaining) + i)
        )
        strip.setPixelColorRGB(pixel, *color_brightness_correction(base_color, LED_BRIGHTNESS))

    strip.show()


def fade(strip, color, speed='slow'):
    ''' Fade entire strip with given color and speed '''
    speed = 0.05 if speed == 'slow' else 0.005
    for pixel in range(strip.numPixels()):
        strip.setPixelColorRGB(pixel, *color)
    strip.show()

    for i in range(LED_BRIGHTNESS):
        strip.setBrightness(i)
        strip.show()
        time.sleep(speed)

    time.sleep(speed * 5)

    for i in range(LED_BRIGHTNESS, -1, -1):
        strip.setBrightness(i)
        strip.show()
        time.sleep(speed)


def chase(strip, color, reverse):
    ''' Light one LED from one ond of the strip to the other, optionally reversed '''
    strip.setBrightness(LED_BRIGHTNESS)
    for i in reversed(range(strip.numPixels()+1)) if reverse else range(strip.numPixels()+1):
        for pixel in range(strip.numPixels()):
            print(i, pixel)
            if i == pixel:
                strip.setPixelColorRGB(pixel, *color_brightness_correction(color, LED_BRIGHTNESS))
            else:
                strip.setPixelColorRGB(pixel, 0, 0, 0)
            strip.show()
            time.sleep(0.01)


def bounce(strip, color):
    ''' Bounce one LED back and forth '''
    chase(strip, color, False)
    chase(strip, color, True)


def chase_ghost(strip, color, reverse):
    ''' Light one LED from one ond of the strip to the other, optionally reversed '''
    strip.setBrightness(LED_BRIGHTNESS)
    for i in reversed(range(strip.numPixels()+5)) if reverse else range(strip.numPixels()+5):
        for pixel in range(strip.numPixels()):
            if i == pixel:
                brightness = LED_BRIGHTNESS/4 if reverse else LED_BRIGHTNESS
                strip.setPixelColorRGB(pixel, *color_brightness_correction(color, brightness))
            elif i - 1 == pixel:
                brightness = (LED_BRIGHTNESS/4)*2 if reverse else (LED_BRIGHTNESS/4)*3
                strip.setPixelColorRGB(pixel, *color_brightness_correction(color, brightness))
            elif i - 2 == pixel:
                brightness = (LED_BRIGHTNESS/4)*3 if reverse else (LED_BRIGHTNESS/4)*2
                strip.setPixelColorRGB(pixel, *color_brightness_correction(color, brightness))
            elif i - 3 == pixel:
                brightness = LED_BRIGHTNESS if reverse else LED_BRIGHTNESS/4
                strip.setPixelColorRGB(pixel, *color_brightness_correction(color, brightness))
            else:
                strip.setPixelColorRGB(pixel, 0, 0, 0)
            strip.show()
            time.sleep(0.01)


def ghost_bounce(strip, color):
    ''' Bounce one LED back and forth '''
    chase_ghost(strip, color, False)
    chase_ghost(strip, color, True)


def clear_strip(strip):
    ''' Turn all pixels of LED strip off '''
    for i in range(strip.numPixels()):
        strip.setPixelColorRGB(i, 0, 0, 0)
    strip.show()


def run():
    ''' Do work son '''
    strip = Adafruit_NeoPixel(LED_COUNT,
                              LED_PIN,
                              LED_FREQ_HZ,
                              LED_DMA,
                              LED_INVERT,
                              LED_BRIGHTNESS,
                              LED_CHANNEL)
    strip.begin()

    shutdown_counter = 0
    try:
        while True:
            printer_state_ = printer_state()
            print(printer_state_)
            while printer_state_ == 'printing':

                bed_heating_percent = heating_percent('heater_bed')
                while bed_heating_percent < 99:
                    # print(f'Bed heating percent: {bed_heating_percent}')
                    progress(strip,
                             bed_heating_percent,
                             BED_HEATING_BASE_COLOR,
                             BED_HEATING_PROGRESS_COLOR)
                    time.sleep(2)
                    bed_heating_percent = heating_percent('heater_bed')

                extruder_heating_percent = heating_percent('extruder')
                while extruder_heating_percent < 99:
                    # print(f'Extruder heating percent: {extruder_heating_percent}')
                    progress(strip,
                             extruder_heating_percent,
                             HOTEND_HEATING_BASE_COLOR,
                             HOTEND_HEATING_PROGRESS_COLOR)
                    time.sleep(2)
                    extruder_heating_percent = heating_percent('extruder')

                printing_percent_ = printing_percent()
                while 0 < printing_percent_ < 100:
                    # print(f'Print progress percent: {printing_percent_}')
                    progress(strip,
                             printing_percent_,
                             PRINT_BASE_COLOR,
                             PRINT_PROGRESS_COLOR)
                    time.sleep(2)
                    printing_percent_ = printing_percent()

                printer_state_ = printer_state()

            while printer_state_ == 'standby':
                fade(strip, STANDBY_COLOR, 'slow')
                printer_state_ = printer_state()

            while printer_state_ == 'paused':
                bounce(strip, PAUSED_COLOR)
                printer_state_ = printer_state()

            while printer_state_ == 'error':
                fade(strip, ERROR_COLOR, 'fast')
                printer_state_ = printer_state()

            while printer_state_ == 'complete':
                ghost_bounce(strip, COMPLETE_COLOR)
                shutdown_counter += 1
                if SHUTDOWN_WHEN_COMPLETE and shutdown_counter > 9:
                    shutdown_counter = 0
                    bed_temp = component_temp('heater_bed')
                    extruder_temp = component_temp('extruder')
                    if bed_temp < BED_TEMP_FOR_OFF and extruder_temp < HOTEND_TEMP_FOR_OFF:
                        clear_strip(strip)
                        print(power_off())
                        sys.exit()
                printer_state_ = printer_state()

            time.sleep(2)
            printer_state_ = printer_state()

    except KeyboardInterrupt:
        clear_strip(strip)


if __name__ == '__main__':
    run()
