from aiogram import types, Dispatcher


async def cmd_settings(message: types.Message) -> None:
    await message.answer("Settings management is not implemented yet.")


def register(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_settings, commands=["settings"])
