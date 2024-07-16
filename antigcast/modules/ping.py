import asyncio
from datetime import datetime, timedelta
from time import time
from pyrogram import Client, filters
from pyrogram.types import Message
from antigcast import Bot

from antigcast.config import *


START_TIME_UTC = datetime.utcnow()
START_TIME_WIB = START_TIME_UTC + timedelta(hours=7)
START_TIME_WIB_ISO = START_TIME_WIB.replace(microsecond=0).isoformat()


TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60**2 * 24),
    ("hour", 60**2),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else "s"}')
    return ", ".join(parts)

@Bot.on_message(filters.command("pung") & filters.group, group=28)
async def ping_pong(client: Client, message: Message):
    start = time()
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME_UTC).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    m_reply = await message.reply("Pinging...")
    delta_ping = time() - start
    await m_reply.edit(
        "**PONG!!**🏓 \n"
        f"**• Pinger -** `{delta_ping * 1000:.3f}ms`\n"
        f"**• Uptime -** `{uptime}`\n"
        f"\n<details><summary>More Info</summary><blockquote>\n"
        f"**Detailed Information**\n"
        f"- Ping Time: `{delta_ping * 1000:.3f}ms`\n"
        f"- Uptime: `{uptime}`\n"
        "</blockquote></details>"
    )


@Bot.on_message(filters.command("time") & filters.group, group=27)
async def get_uptime(client: Client, message: Message):
    current_time_utc = datetime.utcnow()
    current_time_wib = current_time_utc + timedelta(hours=7)
    uptime_sec = (current_time_utc - START_TIME_UTC).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        "🤖 **Bot Status:**\n"
        f"• **Uptime:** `{uptime}`\n"
        f"• **Start Time:** `{START_TIME_WIB_ISO}` (WIB)\n"
        f"\n<details><summary>More Info</summary><blockquote>\n"
        f"**Detailed Information**\n"
        f"- Current UTC Time: `{current_time_utc}`\n"
        f"- Current WIB Time: `{current_time_wib}`\n"
        f"- Uptime in Seconds: `{uptime_sec}`\n"
        "</blockquote></details>"
    )
