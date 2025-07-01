import asyncio
from aiogram import Bot, Dispatcher

from config import load_config
from handlers import register_handlers
from services.monitor import monitor_all_users


async def main() -> None:
    config = load_config()
    bot = Bot(token=config.bot_token, parse_mode="HTML")
    dp = Dispatcher(bot)

    register_handlers(dp)
    asyncio.create_task(monitor_all_users(bot))

    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
