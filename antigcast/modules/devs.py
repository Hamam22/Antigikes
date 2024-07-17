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

@Bot.on_message(filters.command("update") & ~filters.private & filters.user(CREATOR))
async def handle_update(app: Bot, message: Message):
    try:
        out = subprocess.check_output(["git", "pull"], stderr=subprocess.STDOUT).decode("UTF-8")
        if "Already up to date." in str(out):
            return await message.reply(out, quote=True)
        elif len(out) > 4096:
            await send_large_output(message, out)
        else:
            await message.reply(f"```{out}```", quote=True)
        os.execl(sys.executable, sys.executable, "-m", "antigcast")
    except subprocess.CalledProcessError as e:
        await message.reply(f"Git pull failed with error code {e.returncode}:\n{e.output.decode('UTF-8')}", quote=True)
    except Exception as e:
        await message.reply(f"An error occurred while trying to update:\n{str(e)}", quote=True)

@Bot.on_message(filters.command("restart") & filters.user(CREATOR))
async def handle_restart(app: Bot, message: Message):
    try:
        await message.reply("✅ System berhasil direstart", quote=True)
        os.execl(sys.executable, sys.executable, "-m", "antigcast")
    except Exception as e:
        await message.reply(f"An error occurred while trying to restart:\n{str(e)}", quote=True)

@Bot.on_message(filters.command("gcast") & filters.user(CREATOR))
async def gcast_hndl(app: Bot, message: Message):
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
        except Exception:
            failed += 1
    await out.edit(f"**Berhasil Mengirim Pesan Ke {done} Group.**\n**Gagal Mengirim Pesan Ke {failed} Group.**")
