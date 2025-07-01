from aiogram import Dispatcher

from . import start, status, settings


def register_handlers(dp: Dispatcher) -> None:
    start.register(dp)
    status.register(dp)
    settings.register(dp)
