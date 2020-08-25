import asyncio

from apscheduler.schedulers.background import BackgroundScheduler

import callbacks
import cortex
import listeners
import weather
from global_variable import Config, Metrics


def weather_job():
    Metrics.current_weather = weather.get_weather("Busan,KR")


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

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(weather_job, "interval", minutes=5)

api.run()
