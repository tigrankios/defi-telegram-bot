import os
from dataclasses import dataclass


@dataclass
class Config:
    bot_token: str


def load_config() -> Config:
    return Config(bot_token=os.getenv("BOT_TOKEN", ""))
