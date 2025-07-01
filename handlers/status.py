"""Backward-compatible status command module."""

from aiogram import Dispatcher, types
from aiogram.filters import Command

from . import lp


async def cmd_status(message: types.Message) -> None:
    """Delegate to lp.status for actual implementation."""
    await lp.status(message)


def register(dp: Dispatcher) -> None:
    dp.message.register(cmd_status, Command("status"))
