'''
Functions to connect to the Moonraker API and perform actions.
'''
import json
import math
import requests


class MoonrakerAPI:
    ''' Create Moonraker API class '''
    def __init__(self, moonraker_settings):
        self.moonraker_host = moonraker_settings['host']
        self.moonraker_port = str(moonraker_settings['port'])
        self.moonraker_url = f"http://{self.moonraker_host}:{self.moonraker_port}"
        self.bed_base_temp = False
        self.extruder_base_temp = False

    def printer_state(self):
        ''' Get printer status '''
        url = f"{self.moonraker_url}/printer/objects/query?print_stats"
        try:
            ret = requests.get(url)
        except requests.exceptions.ConnectionError:
            return False
        try:
            return ret.json()['result']['status']['print_stats']['state']
        except KeyError:
            return False

    def printing_stats(self):
        ''' Get stats for bed heater, hotend, and printing percent '''
        url = f"{self.moonraker_url}/printer/objects/query?heater_bed&extruder&display_status"
        data = requests.get(url).json()

        bed_temp = data['result']['status']['heater_bed']['temperature']
        bed_target = data['result']['status']['heater_bed']['target']
        ## Set base temperatures to make heating progress start from the bottom of strip
        if not self.bed_base_temp:
            self.bed_base_temp = bed_temp if bed_temp else 0

        extruder_temp = data['result']['status']['extruder']['temperature']
        extruder_target = data['result']['status']['extruder']['target']
        ## Set base temperatures to make heating progress start from the bottom of strip
        if not self.extruder_base_temp:
            self.extruder_base_temp = extruder_temp if extruder_temp else 0

        return {
            'bed': {
                'temp': float(bed_temp),
                'heating_percent': heating_percent(bed_temp, bed_target, self.bed_base_temp),
                'power_percent': round(data['result']['status']['heater_bed']['power'] * 100)
            },
            'extruder': {
                'temp': float(extruder_temp),
                'heating_percent': heating_percent(extruder_temp, extruder_target, self.extruder_base_temp),
                'power_percent': round(data['result']['status']['extruder']['power'] * 100)
            },
            'printing': {
                'done_percent': round(data['result']['status']['display_status']['progress'] * 100)
            }
        }

def heating_percent(temp, target, base_temp):
    ''' Get heating percent for given component '''
    if target == 0.0:
        return 0
    return math.floor(((temp - base_temp) * 100) / (target - base_temp))
