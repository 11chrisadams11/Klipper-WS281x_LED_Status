'''
Functions to connect to the Moonraker API and perform actions.
'''
import json
import math
import requests


def printer_state():
    ''' Get printer status '''
    url = 'http://localhost:7125/printer/objects/query?print_stats'
    try:
        ret = requests.get(url)
    except requests.exceptions.ConnectionError:
        return False
    try:
        return json.loads(ret.text)['result']['status']['print_stats']['state']
    except KeyError:
        return False


def power_status():
    ''' Get printer power status '''
    url = 'http://localhost:7125/machine/device_power/devices?device=printer'
    ret = requests.get(url)
    return json.loads(ret.text)['result']['devices'][0]['status']



def printing_stats(base_temps):
    ''' Get stats for bed heater, hotend, and printing percent '''
    url = f'http://localhost:7125/printer/objects/query?heater_bed&extruder&display_status'
    data = json.loads(requests.get(url).text)

    bed_temp = data['result']['status']['heater_bed']['temperature']
    bed_target = data['result']['status']['heater_bed']['target']
    bed_base_temp = base_temps[0] if base_temps else 0

    extruder_temp = data['result']['status']['extruder']['temperature']
    extruder_target = data['result']['status']['extruder']['target']
    extruder_base_temp = base_temps[1] if base_temps else 0

    return {
        'bed': {
            'temp': float(bed_temp),
            'heating_percent': heating_percent(bed_temp, bed_target, bed_base_temp),
            'power_percent': round(data['result']['status']['heater_bed']['power'] * 100)
        },
        'extruder': {
            'temp': float(extruder_temp),
            'heating_percent': heating_percent(extruder_temp, extruder_target, extruder_base_temp),
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


def power_off():
    ''' Power off the printer '''
    url = 'http://localhost:7125/machine/device_power/off?printer'
    return requests.post(url).text
