import asyncio

import callbacks
import cortex
import listeners
from global_variable import Config


# import logging

# logging.basicConfig(level=logging.DEBUG)


async def main():
    token, session = await api.prepare()
    await api.subscribe(token, session, ["pow", "met"])
    await asyncio.sleep(600)
    await api.unsubscribe(token, session, ["pow", "met"])


api = cortex.Wrapper(client_id=Config.config.get("Emotiv.Client_ID"),
                     client_secret=Config.config.get("Emotiv.Client_Secret"),
                     main=main)
api.register_listener(listeners.PowerListener(callbacks.pow_handler))
api.register_listener(listeners.MetricListener(callbacks.met_handler))

api.run()
