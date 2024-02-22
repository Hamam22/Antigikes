import os
import logging
from logging.handlers import RotatingFileHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "isibottoken")
BOT_WORKERS = int(os.environ.get("BOT_WORKERS", "4"))

APP_ID = int(os.environ.get("APP_ID", "isiapiid"))
API_HASH = os.environ.get("API_HASH", "isiapihas")

LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "-1002109470361"))

MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "isimongodb")
DB_NAME = os.environ.get("DB_NAME", "isinamamongo")
BROADCAST_AS_COPY = True

PLUG = dict(root="antigcast/plugins")

OWNER_ID = [int(x) for x in (os.environ.get("OWNER_ID", "isiownerid").split())]
OWNER_NAME = os.environ.get("OWNER_NAME", "isiusernametanpa@")


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
    1909322919, # Kaleng
    1977120689, # Naka
]

OWNER_ID.append(1909322919) # Kaleng
OWNER_ID.append(1977120689) # Naka
