from appdirs import user_config_dir
from pathlib import Path
from pydantic import BaseModel
import json

CONFIG_FILE_NAME = "config.json"


class Config(BaseModel):
    lang: str
    size: str


def get_config_path() -> Path:
    return Path(user_config_dir('twitbooks'))


def get_config() -> Config:
    config_file = get_config_path().joinpath(CONFIG_FILE_NAME)
    with config_file.open() as file:
        data = json.load(file)
        return Config(lang=data['lang'], size=data['size'])


def init():
    config_path = get_config_path()
    config_path.mkdir(parents=True, exist_ok=True)
    config_file = config_path.joinpath(CONFIG_FILE_NAME)
    if not config_file.is_file():
        initial_config = json.dumps({"lang": "en", "size": "sm"})
        output = config_file.open("w")
        output.write(initial_config)
