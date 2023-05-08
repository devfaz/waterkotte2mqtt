#!/usr/bin/env python3
import requests
import json
import logging
import re
import paho.mqtt.client as mqtt
import time
import os
from pprint import pprint, pformat
from math import floor


hostname = os.environ.get('WK_HOSTNAME')
username = os.environ.get('WK_USERNAME')
password = os.environ.get('WK_PASSWORD')
mqtt_username = os.environ.get('MQTT_USERNAME')
mqtt_password = os.environ.get('MQTT_PASSWORD')
mqtt_host = os.environ.get('MQTT_HOST')
url = 'http://' + hostname

client = mqtt.Client()
client.username_pw_set(mqtt_username, password=mqtt_password)
client.connect(mqtt_host, 1883, 60)
client.loop_start()

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
cache = {}

tag_map = {
    #
    # infos based on
    # https://github.com/openhab/openhab1-addons/blob/master/bundles/binding/org.openhab.binding.ecotouch/src/main/java/org/openhab/binding/ecotouch/EcoTouchTags.java
    #
    # Temp Draußen
    'temperature_outside': {'tag': 'A1', 'type': 'analog', 'divisor': 10 },
    'temperature_outside_1h': {'tag': 'A2', 'type': 'analog', 'divisor': 10 },
    'temperature_outside_24h': {'tag': 'A3', 'type': 'analog', 'divisor': 10 },

    #
    # State cooling
    'state_sourcepump': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 0 },
    'state_heatingpump': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 1 },
    'state_evd': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 2 },
    'state_compressor1': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 3 },
    'state_compressor2': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 4 },
    'state_extheater': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 5 },
    'state_alarm': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 6 },
    'state_cooling': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 7 },
    'state_water': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 8 },
    'state_pool': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 9 },
    'state_solar': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 10 },
    'state_cooling4way': { 'type': 'boolean', 'tag': 'I51', 'bitnum': 11 },
    # Rücklauf Soll
    'temperature_return_set': {'tag': 'A10', 'type': 'analog', 'divisor': 10 },
    # Rücklauf
    'temperature_return': { 'tag': 'A11', 'type': 'analog', 'divisor': 10 },
    # Vorlauf
    'temperature_flow': { 'tag': 'A12', 'type': 'analog', 'divisor': 10 },
    # Warmwasser
    'temperature_water': { 'tag': 'A19', 'type': 'analog', 'divisor': 10 },
    # Quelleneintrittstemperatur
    'temperature_source_in': { 'tag': 'A4', 'type': 'analog', 'divisor': 10 },
    # Quellenaustrittstemperatur
    'temperature_source_out': { 'tag': 'A5', 'type': 'analog', 'divisor': 10 },
    # Temperatur Vorlauf
    'temperature_flow': {'tag': 'A12', 'type': 'analog', 'divisor': 10 },
    # temperature_water
    'temperature_water': {'tag': 'A19', 'type': 'analog', 'divisor': 10 },
    # Geforderte Temperatur im Heizbetrieb
    'temperature_heating_set': {'tag': 'A31', 'type': 'analog', 'divisor': 10},
    # Sollwertvorgabe Heizkreistemperatur
    'temperature_heating_set2': {'tag': 'A32', 'type': 'analog', 'divisor': 10},
    # Aktuelle Kühlkreistemperatur
    'temperature_cooling_return': {'tag': 'A33', 'type': 'analog', 'divisor': 10},
    # Geforderte Temperatur im Kühlbetrieb
    'temperature_cooling_set': {'tag': 'A34', 'type': 'analog', 'divisor': 10},
    # Sollwertvorgabe Kühlbetrieb
    'temperature_cooling_set2': {'tag': 'A35', 'type': 'analog', 'divisor': 10},
    # % Heizungsumwälzpumpe
    'percent_heat_circ_pump': {'tag': 'A51', 'type': 'analog', 'divisor': 10},
    # % Quellenpumpe
    'percent_source_pump': {'tag': 'A52', 'type': 'analog', 'divisor': 10},
    # Hysterese Heizung
    'hysteresis_heating': {'tag': 'A61', 'type': 'analog', 'divisor': 10},

    # Verdampfungsdruck
    'pressure_evaporation': {'tag': 'A8', 'type': 'analog', 'divisor': 10},
    # Kondensationsdruck
    'pressure_condensation': {'tag': 'A15', 'type': 'analog', 'divisor': 10},
    # Meldungen von Ausfällen F0xx die zum Wärmepumpenausfall führen
    'alarm': { 'type': 'number', 'tag': 'I52' },
    'alarm_motorprotect1': { 'type': 'boolean', 'tag': 'I52', 'bitnum': 0},
    'alarm_motorprotect2': { 'type': 'boolean', 'tag': 'I52', 'bitnum': 1},
    'alarm_phase': { 'type': 'boolean', 'tag': 'I52', 'bitnum': 2},
    'alarm_source': { 'type': 'boolean', 'tag': 'I52', 'bitnum': 3},
    'alarm_hdpressostat': { 'type': 'boolean', 'tag': 'I52', 'bitnum': 4},
    'alarm_ndpressostat': { 'type': 'boolean', 'tag': 'I52', 'bitnum': 5},
    'alarm_pressure_evd': { 'type': 'boolean', 'tag': 'I52', 'bitnum': 6},
    'alarm_temp_evd': { 'type': 'boolean', 'tag': 'I52', 'bitnum': 7},
    'alarm_wet': { 'type': 'boolean', 'tag': 'I52', 'bitnum': 8},
    # German: Unterbrechungen
    'interruptions': { 'type': 'number', 'tag': 'I53' },
}

def is_set(x, n):
    return x & 2 ** n != 0 

ValuesPerRequest = 15

logging.info("Starting...")
while True:
    if 'cookies' not in cache:
        try:
            r = requests.get(url + '/cgi/login?username=' + username + '&password=' + password)
            r.raise_for_status()
            cache['cookies'] = r.cookies
        except Exception as e:
            logging.error("Login failed: %s" % e)
            cache = {}
            time.sleep(10)
            continue

    tag_cache = {}
    tag_map_keys = list(tag_map.keys())
    runs = floor(len(tag_map_keys) / ValuesPerRequest) + 1
    logging.debug("Doing %s runs" % runs)
    i = 0
    while i < runs:
        logging.debug("Run %s" % i)
        metrics = tag_map_keys[i * ValuesPerRequest : (i+1)*ValuesPerRequest]

        params = ''
        for index in range(len(metrics)):
            params += "&t%s=%s" % (index+1, tag_map[metrics[index]]['tag'])

        logging.debug("Request-Params: %s" % params)

        try:
            r = requests.get(url + "/cgi/readTags?n=%s" % len(metrics) + params, cookies=cache['cookies']);
            logging.info(r.url)
            r.raise_for_status()
            logging.debug("Got anwer: %s" % r.text)
        except Exception as e:
            logging.warning("Request failed: %s" % e)
            # reset cookies
            cache = {}
            time.sleep(10)
        else:
            values = re.findall('^#(.+)\s+([A-Z_]+)([^0-9-]+)([0-9-]+)\s+([0-9-]+)', r.text, re.MULTILINE)
            for value in values:
                tag = value[0]
                state = value[1]
                value = value[4]
                if state == 'S_OK':
                    tag_cache[tag] = int(value)
                else:
                    logging.warning("E_INACTIVETAG: %s" % tag)

            i += 1

    logging.debug(pformat(tag_cache))

    for metric in tag_map.keys():
        # https://github.com/chboland/pywaterkotte/blob/master/pywaterkotte/ecotouch.py#L22
        # may allow to detect type
        # A = float / 10
        # I = Bit
        # D = Bool
        tag = tag_map[metric]['tag']
        if tag in tag_cache.keys():
          raw_value = tag_cache[tag]

          if tag_map[metric]['type'] == 'analog' or tag_map[metric]['type'] == 'number':
              if 'divisor' in tag_map[metric].keys():
                div = tag_map[metric]['divisor']
                value = raw_value / div
              else:
                value = raw_value / 1
          elif tag_map[metric]['type'] == 'boolean':
              if is_set(raw_value, tag_map[metric]['bitnum']):
                value = 1
              else:
                value = 0
          else:
              value = raw_value

          if metric not in cache or cache[metric] != value:
            logging.info("Sending %s = %s to MQTT" % (metric, value))
            client.publish("rest-to-mqtt/%s/%s" % (hostname, metric), payload=value, retain=True)
            cache[metric] = value
          else:
            logging.info("Already transfered %s = %s" % (metric, value))
            
    logging.info("Sleeping...")
    time.sleep(60)


