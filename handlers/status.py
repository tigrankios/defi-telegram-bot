from aiogram import types, Dispatcher


async def cmd_status(message: types.Message) -> None:
    await message.answer("Portfolio status is not implemented yet.")


def register(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_status, commands=["status"])
