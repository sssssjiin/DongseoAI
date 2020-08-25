import json

import requests

from global_variable import Config

SERVER_URL = Config.config.get("Raspberry.Server_URL")


def led_on():
    url = f"{SERVER_URL}/led/on"
    req = requests.get(url)
    data = json.loads(req.text)
    return data


def led_off():
    url = f"{SERVER_URL}/led/off"
    req = requests.get(url)
    data = json.loads(req.text)
    return data


def motor_set_speed(speed: int):
    url = f"{SERVER_URL}/motor/set_speed?speed={speed}"
    req = requests.get(url)
    data = json.loads(req.text)
    return data


def motor_get_speed():
    url = f"{SERVER_URL}/motor/get_speed"
    req = requests.get(url)
    data = json.loads(req.text)
    return data
