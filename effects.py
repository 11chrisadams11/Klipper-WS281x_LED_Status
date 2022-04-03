# pylint: disable=C0301
'''
LED strip effects functions
'''
import math
import time
import utils
from random import randint


class Effects:
    def __init__(self, strip, effects_settings, strip_settings):
        self.strip = strip
        self.strip_brightness = strip_settings['led_brightness']

        self.effect = effects_settings['effect'] if 'effect' in effects_settings else 'solid'
        self.effect_color_1 = effects_settings['color_1'] if ('color_1' in effects_settings and effects_settings['color_1']) else [255, 255, 255]
        self.effect_color_2 = effects_settings['color_2'] if ('color_2' in effects_settings and effects_settings['color_2']) else None
        self.effect_speed = effects_settings['speed'] if 'speed' in effects_settings else 'fast'
        self.effect_reverse = effects_settings['reverse'] if 'reverse' in effects_settings else False
        
        self.pixel_map = []
        self.set_pixel_map()

    def set_pixel_map(self):
        if self.effect_color_1 != 'rainbow' and not self.effect_color_2:
            for i in range(self.strip.numPixels()):
                self.pixel_map.append(self.effect_color_1)
        if self.effect_color_1 != 'rainbow' and self.effect_color_2:
            spacing = 100 / (self.strip.numPixels() - 2)
            for i in range(self.strip.numPixels()):
                if i == 0:
                    self.pixel_map.append(self.effect_color_1)
                elif i == self.strip.numPixels() - 1:
                    self.pixel_map.append(self.effect_color_2)
                else:
                    self.pixel_map.append(utils.mix_color(self.effect_color_2, self.effect_color_1, (spacing * i) / 100))
        if self.effect_color_1 == 'rainbow':
            colors = {
                'violet': (148, 0  , 211),
                'purple': (75 , 0  , 130),
                'blue'  : (0  , 0  , 255),
                'green' : (0  , 255, 0  ),
                'yellow': (255, 255, 0  ),
                'orange': (255, 127, 0  ),
                'red'   : (255, 0  , 0  )
            }
            halfish_pixels = math.floor(self.strip.numPixels() / 2)
            bottom_half_spacing = 100 / (halfish_pixels - 1)
            top_half_spacing = 100 / ((self.strip.numPixels() - halfish_pixels))
            upper_count = 1

            for i in range(self.strip.numPixels()):
                if i == 0:
                    self.pixel_map.append(colors['red'])
                if 0 < i < (halfish_pixels - 1):
                    self.pixel_map.append(utils.mix_color(colors['green'], colors['red'], (bottom_half_spacing * i) / 100))
                if i == (halfish_pixels - 1):
                    self.pixel_map.append(colors['green'])
                if (halfish_pixels - 1) < i < self.strip.numPixels():
                    self.pixel_map.append(utils.mix_color(colors['violet'], colors['green'], (top_half_spacing * upper_count) / 100))
                    upper_count += 1

    def get_pixel_map(self):
        return self.pixel_map

    def set_speed(self, slow, fast):
        if isinstance(self.effect_speed, (int, float)):
            speed = self.effect_speed
        elif self.effect_speed.lower() not in ['fast', 'slow']:
            speed = fast
        else:
            speed = slow if self.effect_speed.lower() == 'slow' else fast
        return speed

    def run_effect(self):
        eval(f"self.{self.effect}()")

    def clear_strip(self):
        ''' Turn all pixels of LED strip off '''
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColorRGB(i, 0, 0, 0)
        self.strip.show()

    def solid(self):
        ''' Set static color for entire strip with no effect '''
        for pixel, color in enumerate(self.pixel_map):
            self.strip.setPixelColorRGB(pixel, *utils.color_brightness_correction(color, self.strip_brightness))
        self.strip.show()

    def fade(self):
        ''' Fade entire strip with given color and speed '''
        speed = self.set_speed(0.01, 0.005)
        for pixel, color in enumerate(self.pixel_map):
            self.strip.setPixelColorRGB(pixel, *color)
        self.strip.show()

        for i in range(self.strip_brightness):
            self.strip.setBrightness(i)
            self.strip.show()
            time.sleep(speed)

        time.sleep(speed * 5)

        for i in range(self.strip_brightness, -1, -1):
            self.strip.setBrightness(i)
            self.strip.show()
            time.sleep(speed)

    def chase(self):
        ''' Light one LED from one ond of the strip to the other, optionally reversed '''
        speed = self.set_speed(0.01, 0.005)
        self.strip.setBrightness(self.strip_brightness)
        for i in reversed(range(len(self.pixel_map) + 1)) if self.effect_reverse else range(len(self.pixel_map) + 1):
            for pixel, color in enumerate(self.pixel_map):
                if i == pixel:
                    self.strip.setPixelColorRGB(
                        pixel,
                        *utils.color_brightness_correction(
                            color,
                            self.strip_brightness
                        )
                    )
                else:
                    self.strip.setPixelColorRGB(pixel, 0, 0, 0)
                self.strip.show()
                time.sleep(speed)
        if self.effect_reverse:
            self.clear_strip()

    def bounce(self):
        ''' Bounce one LED back and forth '''
        self.chase()
        self.effect_reverse = not self.effect_reverse
        self.chase()
        self.effect_reverse = not self.effect_reverse

    def chase_ghost(self):
        ''' Light one LED from one ond of the strip to the other, optionally reversed '''
        speed = self.set_speed(0.01, 0.005)
        self.strip.setBrightness(self.strip_brightness)
        for i in reversed(range(len(self.pixel_map) + 5)) if self.effect_reverse else range(len(self.pixel_map) + 5):
            for pixel, color in enumerate(self.pixel_map):
                if i == pixel:
                    brightness = self.strip_brightness / 4 if self.effect_reverse else self.strip_brightness
                    self.strip.setPixelColorRGB(
                        pixel,
                        *utils.color_brightness_correction(
                            color,
                            brightness
                        )
                    )
                elif i - 1 == pixel:
                    brightness = (self.strip_brightness / 4) * 2 if self.effect_reverse else (self.strip_brightness / 4) * 3
                    self.strip.setPixelColorRGB(
                        pixel,
                        *utils.color_brightness_correction(
                            color,
                            brightness
                        )
                    )
                elif i - 2 == pixel:
                    brightness = (self.strip_brightness / 4) * 3 if self.effect_reverse else (self.strip_brightness / 4) * 2
                    self.strip.setPixelColorRGB(
                        pixel,
                        *utils.color_brightness_correction(
                            color,
                            brightness
                        )
                    )
                elif i - 3 == pixel:
                    brightness = self.strip_brightness if self.effect_reverse else self.strip_brightness / 4
                    self.strip.setPixelColorRGB(
                        pixel,
                        *utils.color_brightness_correction(
                            color,
                            brightness
                        )
                    )
                else:
                    self.strip.setPixelColorRGB(pixel, 0, 0, 0)
                self.strip.show()
                time.sleep(speed)
        if self.effect_reverse:
            self.clear_strip()

    def ghost_bounce(self):
        ''' Bounce one LED back and forth '''
        self.chase_ghost()
        self.effect_reverse = not self.effect_reverse
        self.chase_ghost()
        self.effect_reverse = not self.effect_reverse

    def fill(self):
        ''' Fill strip one pixel at a time '''
        speed = self.set_speed(0.1, 0.05)
        self.clear_strip()
        for pixel, color in reversed(enumerate(self.pixel_map)) if self.effect_reverse else enumerate(self.pixel_map):
            self.strip.setPixelColorRGB(pixel, *color)
            self.strip.show()
            time.sleep(speed)

    def fill_unfill(self):
        ''' Fill strip one pixel at a time and clear in reverse '''
        speed = self.set_speed(0.1, 0.05)
        self.fill()
        time.sleep(speed * 2)
        for pixel in reversed(range(len(self.pixel_map), -1, -1)) if self.effect_reverse else range(len(self.pixel_map), -1, -1):
            self.strip.setPixelColorRGB(pixel, 0, 0, 0)
            self.strip.show()
            time.sleep(speed)

    def fill_chase(self):
        ''' Fill strip one pixel at a time and clear in chase '''
        speed = self.set_speed(0.1, 0.05)
        self.fill()
        time.sleep(speed * 2)
        for pixel in reversed(range(len(self.pixel_map))) if self.effect_reverse else range(len(self.pixel_map)):
            self.strip.setPixelColorRGB(pixel, 0, 0, 0)
            self.strip.show()
            time.sleep(speed)

    def twinkle(self):
        ''' Flash single pixels, in specified color(s), at random '''
        speed = self.set_speed(0.1, 0.05)
        self.strip.setBrightness(self.strip_brightness)
        self.clear_strip()
        for r in range(int(2 / speed)):
            pixel = randint(0, len(self.pixel_map) - 1)
            self.strip.setPixelColorRGB(pixel, *self.pixel_map[pixel])
            self.strip.show()
            time.sleep(speed)
            self.clear_strip()

    def twinkle_colors(self):
        ''' Flash single pixels, in random colors, at random '''
        speed = self.set_speed(0.1, 0.05)
        self.strip.setBrightness(self.strip_brightness)
        self.clear_strip()
        for r in range(int(2 / speed)):
            i = randint(0, self.strip.numPixels() - 1)
            r = randint(0, 255)
            g = randint(0, 255)
            b = randint(0, 255)
            self.strip.setPixelColorRGB(i, r, g, b)
            self.strip.show()
            time.sleep(speed)
            self.clear_strip()

    def noise(self):
        ''' Flash multiple pixels, in random colors, at random '''
        speed = self.set_speed(0.1, 0.05)
        self.strip.setBrightness(self.strip_brightness)
        self.clear_strip()
        for r in range(int(2 / speed)):
            for t in range(randint(1, self.strip.numPixels() / 2)):
                i = randint(0, self.strip.numPixels() - 1)
                r = randint(0, 255)
                g = randint(0, 255)
                b = randint(0, 255)
                self.strip.setPixelColorRGB(i, r, g, b)
            self.strip.show()
            time.sleep(speed)
            if randint(0, 1):
                self.clear_strip()

    def wave(self):
        ''' Simulate waving flag '''
        speed = self.set_speed(0.1, 0.05)
        self.strip.setBrightness(self.strip_brightness)

        for i in reversed(range(len(self.pixel_map) + 8)) if self.effect_reverse else range(len(self.pixel_map) + 8):
            for pixel, color in enumerate(self.pixel_map):
                self.strip.setPixelColorRGB(pixel, *color)
            if 0 <= i < len(self.pixel_map):
                self.strip.setPixelColorRGB(i, *utils.color_brightness_correction(self.pixel_map[i], 80))
            if 0 <= i - 1 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 1, *utils.color_brightness_correction(self.pixel_map[i - 1], 60))
            if 0 <= i - 2 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 2, *utils.color_brightness_correction(self.pixel_map[i - 2], 40))
            if 0 <= i - 3 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 3, *utils.color_brightness_correction(self.pixel_map[i - 3], 20))
            if 0 <= i - 4 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 4, *utils.color_brightness_correction(self.pixel_map[i - 4], 40))
            if 0 <= i - 5 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 5, *utils.color_brightness_correction(self.pixel_map[i - 5], 60))
            if 0 <= i - 6 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 6, *utils.color_brightness_correction(self.pixel_map[i - 6], 80))
            self.strip.show()
            time.sleep(speed)

    def slava_ukraini(self):
        ''' Simulate waving flag '''
        speed = self.set_speed(0.1, 0.05)
        self.strip.setBrightness(self.strip_brightness)
        color1 = [0, 0, 255] if self.effect_reverse else [255, 255, 0]
        color2 = [255, 255, 0] if self.effect_reverse else [0, 0, 255]
        
        for i in reversed(range(len(self.pixel_map) + 8)) if self.effect_reverse else range(len(self.pixel_map) + 8):
            for pixel, color in enumerate(self.pixel_map):
                self.strip.setPixelColorRGB(pixel, *color1 if pixel < ((self.strip.numPixels() - 1) / 2) else color2)
            if 0 <= i < len(self.pixel_map):
                self.strip.setPixelColorRGB(i, *utils.color_brightness_correction(color1 if i < ((self.strip.numPixels() - 1) / 2) else color2, 80))
            if 0 <= i - 1 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 1, *utils.color_brightness_correction(color1 if i - 1 < ((self.strip.numPixels() - 1) / 2) else color2, 60))
            if 0 <= i - 2 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 2, *utils.color_brightness_correction(color1 if i - 2 < ((self.strip.numPixels() - 1) / 2) else color2, 40))
            if 0 <= i - 3 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 3, *utils.color_brightness_correction(color1 if i - 3 < ((self.strip.numPixels() - 1) / 2) else color2, 20))
            if 0 <= i - 4 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 4, *utils.color_brightness_correction(color1 if i - 4 < ((self.strip.numPixels() - 1) / 2) else color2, 40))
            if 0 <= i - 5 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 5, *utils.color_brightness_correction(color1 if i - 5 < ((self.strip.numPixels() - 1) / 2) else color2, 60))
            if 0 <= i - 6 < len(self.pixel_map):
                self.strip.setPixelColorRGB(i - 6, *utils.color_brightness_correction(color1 if i - 6 < ((self.strip.numPixels() - 1) / 2) else color2, 80))
            self.strip.show()
            time.sleep(speed)

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
