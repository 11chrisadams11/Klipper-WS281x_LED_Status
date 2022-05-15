# pylint: disable=C0301
'''
LED strip effects functions
'''
import math
import time
from random import randint
import utils


class Effects:
    ''' Create effect class '''
    def __init__(self, strip, strip_settings, effects_settings):
        self.thread_stopped = False
        self.strip = strip
        self.strip_brightness = strip_settings['led_brightness']
        self.effects_settings = effects_settings
        self.printer_state = 'standby'
        self.effect_running = False
        self.effect_speed = ''
        self.effect_reverse = ''

        self.pixel_map = {
            'complete': [],
            'standby': [],
            'paused': [],
            'error': [],
        }
        for state in self.pixel_map:
            effect_color_1 = effects_settings[state]['color_1'] if ('color_1' in effects_settings[state] and effects_settings[state]['color_1']) else [255, 255, 255]
            effect_color_2 = effects_settings[state]['color_2'] if ('color_2' in effects_settings[state] and effects_settings[state]['color_2']) else None
            self.pixel_map[state] = self.set_pixel_map(effect_color_1, effect_color_2)

    def stop_thread(self):
        self.thread_stopped = True

    def start_thread(self):
        self.thread_stopped = False

    def set_pixel_map(self, effect_color_1, effect_color_2):
        ''' Create a list of pixel colors based on color settings and strip length '''
        pixel_map = []
        if effect_color_1 != 'rainbow' and not effect_color_2:
            for i in range(self.strip.numPixels()):
                pixel_map.append(effect_color_1)
        elif effect_color_1 != 'rainbow' and effect_color_2:
            spacing = 100 / (self.strip.numPixels() - 2)
            for i in range(self.strip.numPixels()):
                if i == 0:
                    pixel_map.append(effect_color_1)
                elif i == self.strip.numPixels() - 1:
                    pixel_map.append(effect_color_2)
                else:
                    pixel_map.append(utils.mix_color(effect_color_2, effect_color_1, (spacing * i) / 100))
        elif effect_color_1 == 'rainbow':
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
                    pixel_map.append(colors['red'])
                if 0 < i < (halfish_pixels - 1):
                    pixel_map.append(utils.mix_color(colors['green'], colors['red'], (bottom_half_spacing * i) / 100))
                if i == (halfish_pixels - 1):
                    pixel_map.append(colors['green'])
                if (halfish_pixels - 1) < i < self.strip.numPixels():
                    pixel_map.append(utils.mix_color(colors['purple'], colors['green'], (top_half_spacing * upper_count) / 100))
                    upper_count += 1

        return pixel_map
        

    def get_pixel_map(self):
        ''' Return created pixel map '''
        return self.pixel_map

    def set_speed(self, slow, fast):
        ''' Set speed factor based on given setting '''
        if isinstance(self.effect_speed, (int, float)):
            speed = self.effect_speed
        elif self.effect_speed.lower() not in ['fast', 'slow']:
            speed = fast
        else:
            speed = slow if self.effect_speed.lower() == 'slow' else fast
        return speed

    def run_effect(self, printer_state):
        ''' Run the effect specified '''
        self.printer_state = printer_state
        effect = self.effects_settings[printer_state]['effect'] if 'effect' in self.effects_settings[printer_state] else 'solid'
        if effect not in ['solid', 'fade', 'chase', 'bounce', 'chase_ghost', 'ghost_bounce', 'fill', 'fill_unfill', 'fill_chase', 'twinkle', 'twinkle_colors', 'noise', 'wave', 'slava_ukraini']:
            effect = 'solid'
        self.effect_speed = self.effects_settings[printer_state]['speed'] if 'speed' in self.effects_settings[printer_state] else 'fast'
        self.effect_reverse = self.effects_settings[printer_state]['reverse'] if 'reverse' in self.effects_settings[printer_state] else False

        while not self.thread_stopped:
            self.effect_running = True
            eval(f"self.{effect}()")
            self.effect_running = False

    def clear_strip(self):
        ''' Turn all pixels of LED strip off '''
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColorRGB(i, 0, 0, 0)
        self.strip.show()

    def solid(self):
        ''' Set static color for entire strip with no effect '''
        for pixel, color in enumerate(self.pixel_map[self.printer_state]):
            self.strip.setPixelColorRGB(pixel, *utils.color_brightness_correction(color, self.strip_brightness))
        self.strip.show()

    def fade(self):
        ''' Fade entire strip with given color and speed '''
        speed = self.set_speed(0.01, 0.005)
        for pixel, color in enumerate(self.pixel_map[self.printer_state]):
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
        
        time.sleep(speed * 5)

    def chase(self):
        ''' Light one LED from one ond of the strip to the other, optionally reversed '''
        speed = self.set_speed(0.01, 0.005)
        self.strip.setBrightness(self.strip_brightness)
        for i in reversed(range(len(self.pixel_map[self.printer_state]) + 1)) if self.effect_reverse else range(len(self.pixel_map[self.printer_state]) + 1):
            for pixel, color in enumerate(self.pixel_map[self.printer_state]):
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
        for i in reversed(range(len(self.pixel_map[self.printer_state]) + 5)) if self.effect_reverse else range(len(self.pixel_map[self.printer_state]) + 5):
            for pixel, color in enumerate(self.pixel_map[self.printer_state]):
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

    def fill(self, delay=True):
        ''' Fill strip one pixel at a time '''
        speed = self.set_speed(0.1, 0.05)
        self.clear_strip()
        for pixel in reversed(range(len(self.pixel_map[self.printer_state]))) if self.effect_reverse else range(len(self.pixel_map[self.printer_state])):
            self.strip.setPixelColorRGB(pixel, *self.pixel_map[self.printer_state][pixel])
            self.strip.show()
            time.sleep(speed)
        if delay:
            time.sleep(speed * 5)

    def fill_unfill(self):
        ''' Fill strip one pixel at a time and clear in reverse '''
        speed = self.set_speed(0.1, 0.05)
        self.fill(delay=False)
        time.sleep(speed * 2)
        for pixel in reversed(range(len(self.pixel_map[self.printer_state]), -1, -1)) if self.effect_reverse else range(len(self.pixel_map[self.printer_state]), -1, -1):
            self.strip.setPixelColorRGB(pixel, 0, 0, 0)
            self.strip.show()
            time.sleep(speed)
        time.sleep(speed * 2)

    def fill_chase(self):
        ''' Fill strip one pixel at a time and clear in chase '''
        speed = self.set_speed(0.1, 0.05)
        self.fill(delay=False)
        time.sleep(speed * 2)
        for pixel in reversed(range(len(self.pixel_map[self.printer_state]))) if self.effect_reverse else range(len(self.pixel_map[self.printer_state])):
            self.strip.setPixelColorRGB(pixel, 0, 0, 0)
            self.strip.show()
            time.sleep(speed)

    def twinkle(self):
        ''' Flash single pixels, in specified color(s), at random '''
        speed = self.set_speed(0.1, 0.05)
        self.strip.setBrightness(self.strip_brightness)
        self.clear_strip()
        for _ in range(int(2 / speed)):
            pixel = randint(0, len(self.pixel_map[self.printer_state]) - 1)
            self.strip.setPixelColorRGB(pixel, *self.pixel_map[self.printer_state][pixel])
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
        for r in range(int(2 / speed)):
            for _ in range(randint(1, self.strip.numPixels() / 2)):
                rand_off = randint(0, 1)
                i = randint(0, self.strip.numPixels() - 1)
                r = randint(0, 255) if rand_off else 0
                g = randint(0, 255) if rand_off else 0
                b = randint(0, 255) if rand_off else 0
                self.strip.setPixelColorRGB(i, r, g, b)
            self.strip.show()
            time.sleep(speed)

    def wave(self):
        ''' Simulate waving flag '''
        speed = self.set_speed(0.1, 0.05)
        self.strip.setBrightness(self.strip_brightness)

        for i in reversed(range(len(self.pixel_map[self.printer_state]) + 8)) if self.effect_reverse else range(len(self.pixel_map[self.printer_state]) + 8):
            for pixel, color in enumerate(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(pixel, *color)
            if 0 <= i < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i, *utils.color_brightness_correction(self.pixel_map[self.printer_state][i], 80))
            if 0 <= i - 1 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 1, *utils.color_brightness_correction(self.pixel_map[self.printer_state][i - 1], 60))
            if 0 <= i - 2 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 2, *utils.color_brightness_correction(self.pixel_map[self.printer_state][i - 2], 40))
            if 0 <= i - 3 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 3, *utils.color_brightness_correction(self.pixel_map[self.printer_state][i - 3], 20))
            if 0 <= i - 4 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 4, *utils.color_brightness_correction(self.pixel_map[self.printer_state][i - 4], 40))
            if 0 <= i - 5 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 5, *utils.color_brightness_correction(self.pixel_map[self.printer_state][i - 5], 60))
            if 0 <= i - 6 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 6, *utils.color_brightness_correction(self.pixel_map[self.printer_state][i - 6], 80))
            self.strip.show()
            time.sleep(speed)

    def slava_ukraini(self):
        ''' Simulate waving flag '''
        speed = self.set_speed(0.1, 0.05)
        self.strip.setBrightness(self.strip_brightness)
        color1 = [0, 0, 255] if self.effect_reverse else [255, 255, 0]
        color2 = [255, 255, 0] if self.effect_reverse else [0, 0, 255]

        for i in reversed(range(len(self.pixel_map[self.printer_state]) + 8)) if self.effect_reverse else range(len(self.pixel_map[self.printer_state]) + 8):
            for pixel in range(len(self.pixel_map[self.printer_state])):
                self.strip.setPixelColorRGB(pixel, *color1 if pixel < ((self.strip.numPixels() - 1) / 2) else color2)
            if 0 <= i < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i, *utils.color_brightness_correction(color1 if i < ((self.strip.numPixels() - 1) / 2) else color2, 80))
            if 0 <= i - 1 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 1, *utils.color_brightness_correction(color1 if i - 1 < ((self.strip.numPixels() - 1) / 2) else color2, 60))
            if 0 <= i - 2 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 2, *utils.color_brightness_correction(color1 if i - 2 < ((self.strip.numPixels() - 1) / 2) else color2, 40))
            if 0 <= i - 3 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 3, *utils.color_brightness_correction(color1 if i - 3 < ((self.strip.numPixels() - 1) / 2) else color2, 20))
            if 0 <= i - 4 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 4, *utils.color_brightness_correction(color1 if i - 4 < ((self.strip.numPixels() - 1) / 2) else color2, 40))
            if 0 <= i - 5 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 5, *utils.color_brightness_correction(color1 if i - 5 < ((self.strip.numPixels() - 1) / 2) else color2, 60))
            if 0 <= i - 6 < len(self.pixel_map[self.printer_state]):
                self.strip.setPixelColorRGB(i - 6, *utils.color_brightness_correction(color1 if i - 6 < ((self.strip.numPixels() - 1) / 2) else color2, 80))
            self.strip.show()
            time.sleep(speed)


class Progress:
    def __init__(self, strip, strip_settings, effect_settings):
        self.strip = strip
        self.strip_brightness = strip_settings['led_brightness']
        self.base_color = effect_settings['base_color']
        self.progress_color = effect_settings['progress_color']
        self.effect_reverse = effect_settings['reverse'] if 'reverse' in effect_settings else False
        self.num_pixels = self.strip.numPixels()

    def set_progress(self, percent):
        upper_bar = (percent / 100) * self.num_pixels
        upper_remainder, upper_whole = math.modf(upper_bar)
        pixels_remaining = self.num_pixels
        self.strip.setBrightness(self.strip_brightness)

        for i in range(int(upper_whole)):
            pixel = ((self.num_pixels - 1) - i) if self.effect_reverse else i
            self.strip.setPixelColorRGB(
                pixel,
                *utils.color_brightness_correction(
                    self.progress_color,
                    self.strip_brightness
                )
            )
            pixels_remaining -= 1

        if upper_remainder > 0.0:
            tween_color = utils.mix_color(self.progress_color, self.base_color, upper_remainder)
            pixel = (
                ((self.num_pixels - int(upper_whole)) - 1)
                if self.effect_reverse
                else int(upper_whole)
            )
            self.strip.setPixelColorRGB(
                pixel,
                *utils.color_brightness_correction(
                    tween_color,
                    self.strip_brightness
                )
            )
            pixels_remaining -= 1

        for i in range(pixels_remaining):
            pixel = (
                ((pixels_remaining - 1) - i)
                if self.effect_reverse
                else ((self.num_pixels - pixels_remaining) + i)
            )
            self.strip.setPixelColorRGB(
                pixel,
                *utils.color_brightness_correction(
                    self.base_color,
                    self.strip_brightness
                )
            )

        self.strip.show()

    def clear_strip(self):
        ''' Turn all pixels of LED strip off '''
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColorRGB(i, 0, 0, 0)
        self.strip.show()
