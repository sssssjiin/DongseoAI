from utils import config


class Config:
    emotiv = config.YAMLConfiguration("emotiv.yml")
    emotiv.load()
