import asyncio

import numpy as np

import cortex
import listeners
from global_variable import Config

from pprint import pprint


# import logging

# logging.basicConfig(level=logging.DEBUG)

class Callbacks:
    __eye_timestamp = list()
    __eye_warning = list()

    @classmethod
    def pow_handler(cls, data):
        right = data["AF3/theta"] / data["AF3/gamma"]
        left = data["AF4/theta"] / data["AF4/gamma"]

        flicker = (right + left) / 2

        if len(cls.__eye_timestamp) > 10:
            cls.__eye_timestamp.pop(0)
            cls.__eye_warning.pop(0)

        cls.__eye_timestamp.append(flicker)

        eye_flicker_std = np.std(cls.__eye_timestamp)
        eye_flicker_mean = np.mean(cls.__eye_timestamp)

        if 20 < eye_flicker_mean:
            cls.__eye_warning.append(True)
        else:
            cls.__eye_warning.append(False)

        if cls.__eye_warning.count(True) > 5:
            # TODO 경고 메세지 전송
            print("경고")

    @classmethod
    def met_handler(cls, data):
        pprint(data["foc"])

    @classmethod
    def mot_handler(cls, data):
        pass


async def main():
    token, session = await api.prepare()
    await api.subscribe(token, session, ["pow", "met"])
    await asyncio.sleep(600)
    await api.unsubscribe(token, session, ["pow", "met"])


api = cortex.Wrapper(client_id=Config.emotiv.get("Client_ID"), client_secret=Config.emotiv.get("Client_Secret"),
                     main=main)
api.register_listener(listeners.PowerListener(Callbacks.pow_handler))
api.register_listener(listeners.MetricListener(Callbacks.met_handler))

api.run()
