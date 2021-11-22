'''
Utility functions for LED strip
'''

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
