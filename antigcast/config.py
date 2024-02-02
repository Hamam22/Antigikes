import os
import logging
from logging.handlers import RotatingFileHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "6722954472:AAHmB2oRYgGqGkuD6Jbg07bunIkmO73TqXs")
BOT_WORKERS = int(os.environ.get("BOT_WORKERS", "4"))

APP_ID = int(os.environ.get("APP_ID", "28633257"))
API_HASH = os.environ.get("API_HASH", "0330ec89ddab0d2bfdf8e263a68ec510")

LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "-1002109470361"))

MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "mongodb+srv://KalengRobot:1234@cluster0.jjdvosf.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.environ.get("DB_NAME", "KalengRobot")
BROADCAST_AS_COPY = True

PLUG = dict(root="antigcast/plugins")

OWNER_ID = [int(x) for x in (os.environ.get("OWNER_ID", "6364920674").split())]
OWNER_NAME = os.environ.get("OWNER_NAME", "Kalengsarden1")


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
    6364920674, # Kaleng
    1977120689, # Naka
]

OWNER_ID.append(6364920674) # Kaleng
OWNER_ID.append(1977120689) # Naka
