import os
import logging
from logging.handlers import RotatingFileHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "6858482597:AAGXiRVjATRjRkkjGJfLnYdId2tAv2XNuqQ")
BOT_WORKERS = int(os.environ.get("BOT_WORKERS", "4"))

APP_ID = int(os.environ.get("APP_ID", "25639252"))
API_HASH = os.environ.get("API_HASH", "42db0fd56c51ff2b94cf064838eba7c1")

LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "-1002070417836"))

MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "mongodb+srv://tlihtqg184:909090@cluster0.tpctmte.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.environ.get("DB_NAME", "isinamamongo")
BROADCAST_AS_COPY = True

PLUG = dict(root="antigcast/plugins")

OWNER_ID = [int(x) for x in (os.environ.get("OWNER_ID", "6367490039").split())]
OWNER_NAME = os.environ.get("OWNER_NAME", "zenithnewbie")


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
    6367490039, # Kucing
]

OWNER_ID.append(6367490039) # Kucing
