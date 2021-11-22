# pylint: disable=C0301
'''
LED strip effects functions
'''
import math
import time
import utils


def static_color(strip, color, brightness=255):
    ''' Set static color for entire strip '''
    for pixel in range(strip.numPixels()):
        strip.setPixelColorRGB(pixel, *utils.color_brightness_correction(color, brightness))
    strip.show()


def progress(strip, percent, base_color, progress_color, strip_settings):
    ''' Set LED strip to given progress with base and progress colors '''
    strip.setBrightness(strip_settings['led_brightness'])
    num_pixels = strip.numPixels()
    upper_bar = (percent / 100) * num_pixels
    upper_remainder, upper_whole = math.modf(upper_bar)
    pixels_remaining = num_pixels

    for i in range(int(upper_whole)):
        pixel = ((num_pixels - 1) - i) if strip_settings['reverse_direction'] else i
        strip.setPixelColorRGB(
            pixel,
            *utils.color_brightness_correction(
                progress_color,
                strip_settings['led_brightness']
            )
        )
        pixels_remaining -= 1

    if upper_remainder > 0.0:
        tween_color = utils.mix_color(progress_color, base_color, upper_remainder)
        pixel = ((num_pixels - int(upper_whole)) - 1) if strip_settings['reverse_direction'] else int(upper_whole)
        strip.setPixelColorRGB(
            pixel,
            *utils.color_brightness_correction(
                tween_color,
                strip_settings['led_brightness']
            )
        )
        pixels_remaining -= 1

    for i in range(pixels_remaining):
        pixel = (
            ((pixels_remaining - 1) - i)
            if strip_settings['reverse_direction']
            else ((num_pixels - pixels_remaining) + i)
        )
        strip.setPixelColorRGB(
            pixel,
            *utils.color_brightness_correction(
                base_color,
                strip_settings['led_brightness']
            )
        )

    strip.show()


def fade(strip, color, strip_settings, speed='slow', reverse=False):
    ''' Fade entire strip with given color and speed '''
    speed = 0.05 if speed == 'slow' else 0.005
    for pixel in range(strip.numPixels()):
        strip.setPixelColorRGB(pixel, *color)
    strip.show()

    for i in range(strip_settings['led_brightness']):
        strip.setBrightness(i)
        strip.show()
        time.sleep(speed)

    time.sleep(speed * 5)

    for i in range(strip_settings['led_brightness'], -1, -1):
        strip.setBrightness(i)
        strip.show()
        time.sleep(speed)


def slow_fade(strip, color, strip_settings, speed='slow', reverse=False):
    fade(strip, color, strip_settings, speed='slow')


def fast_fade(strip, color, strip_settings, speed='fast', reverse=False):
    fade(strip, color, strip_settings, speed='fast')


def chase(strip, color, strip_settings):
    ''' Light one LED from one ond of the strip to the other, optionally reversed '''
    strip.setBrightness(strip_settings['led_brightness'])
    for i in reversed(range(strip.numPixels()+1)) if strip_settings['reverse_direction'] else range(strip.numPixels()+1):
        for pixel in range(strip.numPixels()):
#            print(i, pixel)
            if i == pixel:
                strip.setPixelColorRGB(
                    pixel,
                    *utils.color_brightness_correction(
                        color,
                        strip_settings['led_brightness']
                    )
                )
            else:
                strip.setPixelColorRGB(pixel, 0, 0, 0)
            strip.show()
            time.sleep(0.01)
    if strip_settings['reverse_direction']:
        clear_strip(strip)


def bounce(strip, color, strip_settings):
    ''' Bounce one LED back and forth '''
    chase(strip, color, strip_settings)
    strip_settings['reverse_direction'] = not strip_settings['reverse_direction']
    chase(strip, color, strip_settings)
    strip_settings['reverse_direction'] = not strip_settings['reverse_direction']


def chase_ghost(strip, color, strip_settings):
    ''' Light one LED from one ond of the strip to the other, optionally reversed '''
    strip.setBrightness(strip_settings['led_brightness'])
    for i in reversed(range(strip.numPixels()+5)) if strip_settings['reverse_direction'] else range(strip.numPixels()+5):
        for pixel in range(strip.numPixels()):
            if i == pixel:
                brightness = strip_settings['led_brightness']/4 if strip_settings['reverse_direction'] else strip_settings['led_brightness']
                strip.setPixelColorRGB(
                    pixel,
                    *utils.color_brightness_correction(
                        color,
                        brightness
                    )
                )
            elif i - 1 == pixel:
                brightness = (strip_settings['led_brightness']/4)*2 if strip_settings['reverse_direction'] else (strip_settings['led_brightness']/4)*3
                strip.setPixelColorRGB(
                    pixel,
                    *utils.color_brightness_correction(
                        color,
                        brightness
                    )
                )
            elif i - 2 == pixel:
                brightness = (strip_settings['led_brightness']/4)*3 if strip_settings['reverse_direction'] else (strip_settings['led_brightness']/4)*2
                strip.setPixelColorRGB(
                    pixel,
                    *utils.color_brightness_correction(
                        color,
                        brightness
                    )
                )
            elif i - 3 == pixel:
                brightness = strip_settings['led_brightness'] if strip_settings['reverse_direction'] else strip_settings['led_brightness']/4
                strip.setPixelColorRGB(
                    pixel,
                    *utils.color_brightness_correction(
                        color,
                        brightness
                    )
                )
            else:
                strip.setPixelColorRGB(pixel, 0, 0, 0)
            strip.show()
            time.sleep(0.01)
    if strip_settings['reverse_direction']:
        clear_strip(strip)


def ghost_bounce(strip, color, strip_settings):
    ''' Bounce one LED back and forth '''
    chase_ghost(strip, color, strip_settings)
    strip_settings['reverse_direction'] = not strip_settings['reverse_direction']
    chase_ghost(strip, color, strip_settings)
    strip_settings['reverse_direction'] = not strip_settings['reverse_direction']


def rainbow(strip, color, strip_settings):
    colors = {
        'violet': (148, 0  , 211),
        'purple': (75 , 0  , 130),
        'blue'  : (0  , 0  , 255),
        'green' : (0  , 255, 0  ),
        'yellow': (255, 255, 0  ),
        'orange': (255, 127, 0  ),
        'red'   : (255, 0  , 0  )
    }

    strip.setPixelColorRGB(0, *colors['red'])
    strip.setPixelColorRGB(1, *utils.mix_color(colors['green'], colors['red'], 0.25))
    strip.setPixelColorRGB(2, *utils.mix_color(colors['green'], colors['red'], 0.50))
    strip.setPixelColorRGB(3, *utils.mix_color(colors['green'], colors['red'], 0.75))
    strip.setPixelColorRGB(4, *colors['green'])
    strip.setPixelColorRGB(5, *utils.mix_color(colors['purple'], colors['green'], 0.20))
    strip.setPixelColorRGB(6, *utils.mix_color(colors['purple'], colors['green'], 0.40))
    strip.setPixelColorRGB(7, *utils.mix_color(colors['purple'], colors['green'], 0.60))
    strip.setPixelColorRGB(8, *utils.mix_color(colors['purple'], colors['green'], 0.80))
    strip.setPixelColorRGB(9, *colors['purple'])
    strip.show()
    time.sleep(2)


def clear_strip(strip):
    ''' Turn all pixels of LED strip off '''
    for i in range(strip.numPixels()):
        strip.setPixelColorRGB(i, 0, 0, 0)
    strip.show()
