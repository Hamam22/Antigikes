import asyncio
import os
import sys
from datetime import datetime, timedelta
from antigcast import Bot, app
from antigcast.config import LOGGER, LOG_CHANNEL_ID
from pyrogram import __version__ as pyrover
from pyrogram import idle
from antigcast.helpers.tools import checkExpired

loop = asyncio.get_event_loop_policy().get_event_loop()

msg = """
**🇲🇨Berhasil Di Aktifkan🇲🇨**
**📩Anti Gcast Pelerr📩**
**Python Version** `{}`
**Pyrogram Version** `{}`
"""

async def send_reminder():
    now = datetime.now()
    restart_time = now + timedelta(seconds=43200)  # 12 jam dari sekarang
    reminder_time = restart_time - timedelta(minutes=5)

    while datetime.now() < reminder_time:
        await asyncio.sleep(60)  # Tunggu selama 1 menit
    
    # Kirim pesan pengingat
    reminder_message = f"🗓️ Tanggal: {reminder_time.strftime('%d-%m-%Y')}\n🕕 Jam: {reminder_time.strftime('%H:%M:%S')}"
    print(reminder_message)
    # Jika Anda ingin mengirim ke saluran, gunakan:
    # await app.send_message(LOG_CHANNEL_ID, reminder_message)
    
async def auto_restart():
    # Jalankan pengingat sebagai task latar belakang
    asyncio.create_task(send_reminder())
    
    await asyncio.sleep(43200)  # Tunggu selama 12 jam
    
    # Restart aplikasi
    os.system(f"kill -9 {os.getpid()} && python3 -m antigcast")
    sys.exit(0)

async def main():
    try:
        await app.start()
        app.me = await app.get_me()
        username = app.me.username
        namebot = app.me.first_name
        log = await app.send_message(LOG_CHANNEL_ID, msg.format(sys.version.split()[0], pyrover))
        LOGGER("INFO").info(f"{namebot} | [ @{username} ] | 🔥 BERHASIL DIAKTIFKAN! 🔥")
    except Exception as e:
        LOGGER("ERROR").error(f"Error starting bot: {e}")
    
    LOGGER("INFO").info(f"[🔥 BOT AKTIF! 🔥]")
    await checkExpired()
    
    # Jalankan auto_restart sebagai task latar belakang
    asyncio.create_task(auto_restart())
    
    await idle()

LOGGER("INFO").info("Starting Bot...")
loop.run_until_complete(main())
