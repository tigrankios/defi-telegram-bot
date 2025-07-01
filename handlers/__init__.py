from aiogram import Dispatcher

from . import start, settings, lp


def register_handlers(dp: Dispatcher) -> None:
    start.register(dp)
    settings.register(dp)
    lp.register(dp)
