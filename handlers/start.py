from aiogram import types, Dispatcher


async def cmd_start(message: types.Message) -> None:
    await message.answer(
        "Welcome to DeFi Portfolio Bot!\n"
        "Please send your Ethereum address to start tracking."
    )


def register(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
