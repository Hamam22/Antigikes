import asyncio
from antigcast import Bot, app
from antigcast.config import LOGGER, LOG_CHANNEL_ID
from pyrogram import idle
from antigcast.helpers.tools import checkExpired

loop = asyncio.get_event_loop_policy().get_event_loop()

msg = """
**Berhasil Di Aktifkan**
**Python Version** `{}`
**Pyrogram Version** `{}`
"""

async def main():
    try:
        await app.start()
        app.me = await app.get_me()
        username = app.me.username
        namebot = app.me.first_name
        # Pastikan pyver dan pyrover sudah didefinisikan
        log = await app.send_message(LOG_CHANNEL_ID, msg.format(pyver.split()[0], pyrover))
        LOGGER.info(f"{namebot} | [ @{username} ] | 🔥 BERHASIL DIAKTIFKAN! 🔥")
    except Exception as e:
        print(e)
    LOGGER.info("[🔥 BOT AKTIF! 🔥]")
    await checkExpired()
    await idle()

LOGGER.INFO("Starting Bot...")
loop.run_until_complete(main())
