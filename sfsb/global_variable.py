from utils import config


class Config:
    config = config.YAMLConfiguration("config.yml")
    config.load()


class Metrics:
    current_weather: dict
    metric_data: dict
