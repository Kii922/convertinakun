import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from utils.logger import setup_logger

# Inisialisasi Logger
setup_logger()
logger = logging.getLogger(__name__)

async def main():
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN belum diset di .env! Bot tidak dapat berjalan.")
        return

    # Inisialisasi Bot dengan standar ParseMode HTML
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Inisialisasi Dispatcher (Aiogram 3 secara default menggunakan MemoryStorage untuk FSM)
    # MemoryStorage sangat ideal karena data akan hilang ketika proses bot restart,
    # memastikan tidak ada persistent state/data akun yang tertinggal.
    dp = Dispatcher()

    # --- Router Registration ---
    from handlers import start, message, callback, admin
    dp.include_router(admin.router) # Admin diletakkan paling atas agar command admin diutamakan
    dp.include_router(start.router)
    dp.include_router(message.router)
    dp.include_router(callback.router)

    logger.info("Memulai Telegram VPN Converter Bot...")
    try:
        # Hapus pending updates agar bot tidak memproses pesan lama saat dihidupkan
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Session bot ditutup.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot dimatikan oleh user.")
