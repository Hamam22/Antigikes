import os
import logging
from logging.handlers import RotatingFileHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "6852141063:AAHYHmI_XlhvLntnPkpJtAyC-zC9RWTK4YU")
BOT_WORKERS = int(os.environ.get("BOT_WORKERS", "4"))

APP_ID = int(os.environ.get("APP_ID", "19593289"))
API_HASH = os.environ.get("API_HASH", "4fb53b0fbe7f33f8062fb934d0e4a4bb")

LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "-1002024799257"))

MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "mongodb+srv://nprotect:nprotect@nprotect.zjnqv8t.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.environ.get("DB_NAME", "NPROTECT")
BROADCAST_AS_COPY = True

PLUG = dict(root="antigcast/plugins")

OWNER_ID = [int(x) for x in (os.environ.get("OWNER_ID", "5027198970").split())]
OWNER_NAME = os.environ.get("OWNER_NAME", "RedflixHD")


LOG_FILE_NAME = "antigcast_logs.txt"
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50000000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

CREATOR = [
    5027198970, # Zelda
    1977120689, # Naka
    1736494994, # Naka
]

OWNER_ID.append(5027198970) # Zelda
OWNER_ID.append(1977120689) # Naka
OWNER_ID.append(1736494994) # Naka
