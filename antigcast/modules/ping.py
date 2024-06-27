import asyncio
from datetime import datetime
from time import time
from pyrogram import Client, filters
from pyrogram.types import Message
from antigcast import Bot

from antigcast.config import *

# Waktu mulai bot
START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()

# Definisi unit waktu untuk durasi uptime
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60**2 * 24),
    ("hour", 60**2),
    ("min", 60),
    ("sec", 1),
)

# Fungsi untuk mengubah detik menjadi format waktu manusia
async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else "s"}')
    return ", ".join(parts)

# Perintah ping
@bot.on_message(filters.command("ping"))
async def ping_pong(app: Client, message: Message):
    start = time()
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    m_reply = await message.reply("Pinging...")
    delta_ping = time() - start
    await m_reply.edit(
        "**PONG!!**🏓 \n"
        f"**• Pinger -** `{delta_ping * 1000:.3f}ms`\n"
        f"**• Uptime -** `{uptime}`\n"
    )

# Perintah uptime
@bot.on_message(filters.command("uptime"))
async def get_uptime(app: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        "🤖 **Bot Status:**\n"
        f"• **Uptime:** `{uptime}`\n"
        f"• **Start Time:** `{START_TIME_ISO}`"
    )
