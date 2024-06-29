import asyncio
from antigcast import Bot, app
from sys import version as pyver

from antigcast.config import LOGGER, LOG_CHANNEL_ID
from pyrogram import __version__ as pyrover
from pyrogram import idle
from antigcast.helpers.tools import checkExpired

loop = asyncio.get_event_loop_policy().get_event_loop()

msg = ""
**🇲🇨Berhasil Di Aktifkan🇲🇨*
**📩Anti Gcast Pelerr📩**
**Python Version** `{}`
**Pyrogram Version** `{}`
"""

async def main():
    try:
        await app.start()
        app.me = await app.get_me()
        username = app.me.username
        namebot = app.me.first_name
        log = await app.send_message(LOG_CHANNEL_ID, msg.format(pyver.split()[0], pyrover))
        LOGGER("INFO").info(f"{namebot} | [ @{username} ] | 🔥 BERHASIL DIAKTIFKAN! 🔥")
    except Exception as e:
        print(e)
    LOGGER("INFO").info(f"[🔥 BOT AKTIF! 🔥]")
    await checkExpired()
    await idle()

LOGGER("INFO").info("Starting Bot...")
loop.run_until_complete(main())
