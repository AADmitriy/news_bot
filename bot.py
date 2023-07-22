import asyncio
import logging

from aiogram import Dispatcher, Bot

from config_reader import config
from handlers.common import router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    )
    dp = Dispatcher()
    bot = Bot(token=config.bot_token.get_secret_value())

    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
