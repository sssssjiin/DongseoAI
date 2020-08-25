import json

import requests

from global_variable import Config

api_key = Config.config.get("Weather.Api_Key")


def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    req = requests.get(url)
    data = json.loads(req.text)
    return data