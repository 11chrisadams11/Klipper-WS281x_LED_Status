#!/usr/bin/python3 -u
# pylint: disable=C0326,C0301
'''
Script to take info from Klipper and light up WS281x LED strip based on current status
'''
import sys
import time
import yaml
from rpi_ws281x import Adafruit_NeoPixel
import moonraker_api
import effects


def get_settings():
    ''' Read settings from file '''
    try:
        with open('settings.conf', 'r') as settings_file:
            try:
                settings = yaml.safe_load(settings_file)
                # for key, value in settings['color_settings'].items():
                #     if isinstance(value, dict):
                #         for key2, value2 in settings['color_settings'][key].items():
                #             settings['color_settings'][key][key2] = tuple(value2)
                #     else:
                #         settings['color_settings'][key] = tuple(value)
                return settings
            except yaml.scanner.ScannerError as err:
                print(f'\nSettings file formatted incorrectly:\n\t{err}')
                sys.exit()
    except FileNotFoundError:
        print('\nSettings file (settings.conf) not found.')
        sys.exit()


def run():
    ''' Do work son '''
    settings = get_settings()
    strip_settings = settings['strip_settings']
    effects_settings = settings['effects']
    completion_settings = settings['completion_settings']
    moonraker_settings = settings['moonraker_settings']

    strip = Adafruit_NeoPixel(
        strip_settings['led_count'],
        strip_settings['led_pin'],
        strip_settings['led_freq_hz'],
        strip_settings['led_dma'],
        strip_settings['led_invert'],
        strip_settings['led_brightness'],
        strip_settings['led_channel'],
    )
    strip.begin()

    shutdown_counter = 0
    idle_timer = 0
    old_state = ''
    base_temps = []
    try:
        while True:
            printer_state_ = moonraker_api.printer_state(moonraker_settings)
            # print(printer_state_)
            if printer_state_ == 'printing':
                printing_stats_ = moonraker_api.printing_stats(moonraker_settings, base_temps)
                printing_percent_ = printing_stats_['printing']['done_percent']
                ## Get base temperatures to make heating progress start from the bottom
                if not base_temps:
                    base_temps = [
                        printing_stats_['bed']['temp'],
                        printing_stats_['extruder']['temp']
                    ]

                if printing_percent_ < 1 and printing_stats_['bed']['heating_percent'] < 100:
                    # print(f'Bed heating: {bed_heating_percent}%')
                    effects.progress(
                        strip,
                        printing_stats_['bed']['heating_percent'],
                        effects_settings['bed_heating']['base_color'],
                        effects_settings['bed_heating']['progress_color'],
                        strip_settings
                    )

                if (printing_percent_ < 1 and
                        printing_stats_['extruder']['heating_percent'] < 100 and
                        printing_stats_['bed']['heating_percent'] >= 99):

                    # print(f'Extruder heating: {extruder_heating_percent}%')
                    effects.progress(
                        strip,
                        printing_stats_['extruder']['heating_percent'],
                        effects_settings['hotend_heating']['base_color'],
                        effects_settings['hotend_heating']['progress_color'],
                        strip_settings
                    )

                if (printing_percent_ == 0 and
                        printing_stats_['extruder']['heating_percent'] >= 100 and
                        printing_stats_['bed']['heating_percent'] >= 100):

                    effects.clear_strip(strip)

                if 0 < printing_percent_ < 100:
                    # print(f'Print progress: {printing_percent_}%')
                    effects.progress(
                        strip,
                        printing_percent_,
                        effects_settings['printing']['base_color'],
                        effects_settings['printing']['progress_color'],
                        strip_settings
                    )

            if printer_state_ in ['standby', 'paused', 'error'] and idle_timer < strip_settings['idle_timeout']:
                eval(f"effects.{effects_settings[printer_state_]['effect']}(strip, {effects_settings[printer_state_]['color']}, strip_settings)")

            if printer_state_ == 'complete':
                base_temps = []
                if moonraker_api.power_status(moonraker_settings) == 'on':
                    eval(f"effects.{effects_settings[printer_state_]['effect']}(strip, {effects_settings[printer_state_]['color']}, strip_settings)")
                    shutdown_counter += 1
                    if completion_settings['shutdown_when_complete'] and shutdown_counter > 9:
                        shutdown_counter = 0
                        printing_stats_ = moonraker_api.printing_stats(moonraker_settings, base_temps)
                        bed_temp = printing_stats_['bed']['temp']
                        extruder_temp = printing_stats_['extruder']['temp']
                        print(f'\nBed temp: {round(bed_temp, 2)}\nExtruder temp: {round(extruder_temp, 2)}\n')
                        if (bed_temp < completion_settings['bed_temp_for_shutdown'] and
                                extruder_temp < completion_settings['hotend_temp_for_shutdown']):
                            effects.clear_strip(strip)
                            print(moonraker_api.power_off(moonraker_settings))

            if printer_state_ not in ['printing', 'complete'] and old_state == printer_state_:
                idle_timer += 2
                if idle_timer > strip_settings['idle_timeout']:
                    effects.clear_strip(strip)
            else:
                idle_timer = 0

            old_state = printer_state_
            time.sleep(2)

    except KeyboardInterrupt:
        effects.clear_strip(strip)


if __name__ == '__main__':
    if len(sys.argv) > 1:

        SETTINGS = get_settings()
        STRIP_SETTINGS = SETTINGS['strip_settings']

        STRIP = Adafruit_NeoPixel(
            STRIP_SETTINGS['led_count'],
            STRIP_SETTINGS['led_pin'],
            STRIP_SETTINGS['led_freq_hz'],
            STRIP_SETTINGS['led_dma'],
            STRIP_SETTINGS['led_invert'],
            STRIP_SETTINGS['led_brightness'],
            STRIP_SETTINGS['led_channel'],
        )
        STRIP.begin()

        COLOR = (int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
        BRIGHTNESS = int(sys.argv[4]) if len(sys.argv) > 4 else STRIP_SETTINGS['led_brightness']
        effects.static_color(STRIP, COLOR, BRIGHTNESS)
    else:
        run()
