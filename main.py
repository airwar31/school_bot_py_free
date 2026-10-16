"""
School LMS Telegram Bot - Main Application Entry Point
Layered Enterprise Architecture (aiogram 3.x)
"""

import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.core.config import BOT_TOKEN
from bot.core.database import DB_PATH, DatabaseLock
from bot.database.init import init_all_databases
from bot.handlers import setup_routers
from bot.services.vk_service import check_vk_posts_periodically

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)


async def main():
    logging.info("=" * 60)
    logging.info("  🎓 School LMS Telegram Bot - Starting Up")
    logging.info(f"  Database path: {DB_PATH}")
    logging.info("=" * 60)

    if not BOT_TOKEN:
        logging.critical("BOT_TOKEN is not set! Please configure .env file.")
        return

    DatabaseLock.clear_lock()

    try:
        # Initialize complete database schema
        init_all_databases()
        DatabaseLock.mark_initialized()

        bot = Bot(token=BOT_TOKEN)

        # Standard Telegram Bot Commands Menu
        commands = [
            BotCommand(command="start", description="🚀 Начать работу с ботом"),
            BotCommand(command="help", description="📖 Справка по командам"),
            BotCommand(command="today", description="📅 Расписание на сегодня"),
            BotCommand(command="tomorrow", description="📅 Расписание на завтра"),
            BotCommand(command="schedule", description="🔍 Расписание на дату (ГГГГ-ММ-ДД)"),
            BotCommand(command="settings", description="⚙️ Настройки беседы (для групп)"),
            BotCommand(command="toggle_vk", description="🔔 Переключить VK уведомления")
        ]
        await bot.set_my_commands(commands)
        logging.info("Bot commands menu registered successfully")

        # Initialize FSM storage & Dispatcher
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Setup all feature routers
        setup_routers(dp)
        logging.info("All feature routers registered successfully")

        # Launch background VKontakte news synchronization task
        asyncio.create_task(check_vk_posts_periodically(bot))

        logging.info("Starting bot long-polling...")
        await dp.start_polling(bot, skip_updates=True)

    except Exception as e:
        logging.critical(f"Critical error during bot startup: {e}")
        raise


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user")
