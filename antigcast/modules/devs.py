import os
import sys
import asyncio
import subprocess

from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from antigcast.config import *
from antigcast.helpers.tools import *
from antigcast.helpers.database import *

async def send_msg(chat_id, message: Message):
    try:
        if BROADCAST_AS_COPY is False:
            await message.forward(chat_id=chat_id)
        elif BROADCAST_AS_COPY is True:
            await message.copy(chat_id=chat_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(int(e.value))
        return send_msg(chat_id, message)

@Bot.on_message(filters.command("update") & filters.user(CREATOR))
async def handle_update(app : Bot, message : Message):
    out = subprocess.check_output(["git", "pull"]).decode("UTF-8")
    if "Already up to date." in str(out):
        return await message.reply(out, quote=True)
    elif int(len(str(out))) > 4096:
        await send_large_output(message, out)
    else:
        await message.reply(f"```{out}```", quote=True)
    os.execl(sys.executable, sys.executable, "-m", "antigcast")


@Bot.on_message(filters.command("restart") & filters.user(CREATOR))
async def handle_restart(app : Bot, message : Message):
    await message.reply("✅ System berhasil direstart", quote=True)
    os.execl(sys.executable, sys.executable, "-m", "antigcast")

@Bot.on_message(filters.command("clean") & filters.user(CREATOR))
async def handle_clean(app : Bot, message : Message):
    count = 0
    for file_name in os.popen("ls").read().split():
        try:
            os.remove(file_name)
            count += 1
        except:
            pass
    subprocess.run(["rm", "-rf", "downloads"], check=True)
    await message.reply(f"✅ {count} sampah berhasil di bersihkan")
    
@Bot.on_message(filters.command("gcast") & filters.user(CREATOR))
async def gcast_hndl(app : Bot, message : Message):
    groups = await get_actived_chats()
    msg = get_arg(message)
    if message.reply_to_message:
        msg = message.reply_to_message

    if not msg:
        await message.reply(text="**Reply atau berikan saya sebuah pesan!**")
        return
    
    out = await message.reply(text="**Memulai Broadcast...**")
    
    if not groups:
        await out.edit(text="**Maaf, Broadcast Gagal Karena Belum Ada Grup Yang Terdaftar**")
        return
    
    done = 0
    failed = 0
    for group in groups:
        try:
            await send_msg(group, message=msg)
            done += 1
        except:
            failed += 1
    await out.edit(f"**Berhasil Mengirim Pesan Ke {done} Group.**\n**Gagal Mengirim Pesan Ke {failed} Group.**")
