import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Memuat variabel environment dari file .env
load_dotenv()

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/bot.db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

config = Config()
