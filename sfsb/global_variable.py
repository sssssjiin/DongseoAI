from utils import config


class Config:
    config = config.YAMLConfiguration("config.yml")
    config.load()
