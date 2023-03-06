#!/usr/bin/python3 -u
# pylint: disable=C0326,C0301
'''
Script to take info from Klipper and light up WS281x LED strip based on current status
'''
import os
import sys
import time
import yaml
import threading
from rpi_ws281x import Adafruit_NeoPixel
import moonraker_api
import effects
import utils

def get_settings():
    ''' Read settings from file '''
    script_path = os.path.dirname(os.path.realpath(__file__))
    try:
        with open(f'{script_path}/settings.conf', 'r') as settings_file:
            try:
                settings = yaml.safe_load(settings_file)
                return settings
            except yaml.scanner.ScannerError as err:
                print(f'\nSettings file formatted incorrectly:\n\t{err}')
                sys.exit()
    except FileNotFoundError:
        print('\nSettings file (settings.conf) not found. Adding sample settings.')
        with open(f'{script_path}/settings_sample.conf', 'r') as sample_settings_file:
            with open(f'{script_path}/settings.conf', 'w') as settings_file:
                settings_file.write(sample_settings_file.read())
        return get_settings()


def set_strip(strip_settings):
    strip = Adafruit_NeoPixel(
        strip_settings['led_count'],
        strip_settings['led_pin'],
        strip_settings['led_freq_hz'],
        strip_settings['led_dma'],
        strip_settings['led_invert'],
        strip_settings['led_brightness'],
        strip_settings['led_channel'],
    )
    return strip


def run():
    ''' Do work son '''
    settings = get_settings()
    
    moonraker_settings = settings['moonraker_settings']
    moonraker_api_cl = moonraker_api.MoonrakerAPI(moonraker_settings)
    
    strip_settings = settings['strip_settings']
    effects_settings = settings['effects']
    strip = set_strip(strip_settings)
    strip.begin()

    effects_cl = effects.Effects(strip, strip_settings, effects_settings)
    bed_progress = effects.Progress(strip, strip_settings, effects_settings['bed_heating'])
    hotend_progress = effects.Progress(strip, strip_settings, effects_settings['hotend_heating'])
    printing_progress = effects.Progress(strip, strip_settings, effects_settings['printing'])

    shutdown_counter = 0
    idle_timer = 0
    old_state = ''
    test_counter = 0
    try:
        while True:
            printer_state = moonraker_api_cl.printer_state()
            # print(printer_state)
            if printer_state == 'printing':
                printing_stats = moonraker_api_cl.printing_stats()
                printing_percent = printing_stats['printing']['done_percent']

                ## Set bed heating progress
                # print(printing_percent)
                if (printing_percent < 1 or printing_percent == 100) and printing_stats['bed']['heating_percent'] < 100:
                    bed_progress.set_progress(printing_stats['bed']['heating_percent'])

                ## Set hotend heating progress
                if (
                    (printing_percent < 1 or printing_percent == 100) and
                    printing_stats['extruder']['heating_percent'] < 100 and
                    printing_stats['bed']['heating_percent'] >= 99
                ):
                    hotend_progress.set_progress(printing_stats['extruder']['heating_percent'])

                ## Clear strip if bed and hotend heating are both done and print percent is 0
                if (
                    printing_percent == 0 and
                    printing_stats['extruder']['heating_percent'] >= 100 and
                    printing_stats['bed']['heating_percent'] >= 100
                ):
                    printing_progress.clear_strip()

                ## Set printing progress
                if 0 < printing_percent < 100:
                    printing_progress.set_progress(printing_percent)

            if printer_state != 'printing' and old_state == printer_state:
                idle_timer += 2
                if idle_timer > strip_settings['idle_timeout']:
                    effects_cl.stop_thread()
                    while effects_cl.effect_running:
                        time.sleep(0.1)
                    effects_cl.clear_strip()
            else:
                idle_timer = 0

            if old_state != printer_state:
                effects_cl.stop_thread()
                while effects_cl.effect_running:
                    time.sleep(0.1)
                effects_cl.start_thread()
                if printer_state in ['complete', 'standby', 'paused', 'error']:
                    effect_thread = threading.Thread(target=effects_cl.run_effect, args=(printer_state,)).start()

            old_state = printer_state
            time.sleep(2)

    except:
        effects_cl.stop_thread()
        while effects_cl.effect_running:
            time.sleep(0.1)
        effects_cl.clear_strip()

if __name__ == '__main__':
    if len(sys.argv) > 1:

        strip_settings = get_settings()['strip_settings']

        strip = set_strip(strip_settings)
        strip.begin()

        color = (int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
        brightness = int(sys.argv[4]) if len(sys.argv) > 4 else strip_settings['led_brightness']

        for pixel in range(strip.numPixels()):
            strip.setPixelColorRGB(pixel, *utils.color_brightness_correction(color, brightness))
        strip.show()
    else:
        run()
