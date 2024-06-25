import asyncio

from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageDeleteForbidden, UserNotParticipant

from antigcast.config import *
from antigcast.helpers.tools import *
from antigcast.helpers.admins import *
from antigcast.helpers.message import *
from antigcast.helpers.database import *

@Bot.on_message(filters.command("bl") & ~filters.private & Admin)
async def addblmessag(app: Bot, message: Message):
    trigger = get_arg(message)
    if message.reply_to_message:
        trigger = message.reply_to_message.text or message.reply_to_message.caption

    if not trigger:
        return await message.reply("`Tidak ada kata yang diberikan untuk dimasukkan ke dalam blacklist.`")

    xxnx = await message.reply(f"`Menambahkan` {trigger} `ke dalam blacklist..`")
    try:
        await add_bl_word(trigger.lower())
        await xxnx.edit(f"`{trigger}` `berhasil ditambahkan ke dalam blacklist..`")
    except Exception as e:
        await xxnx.edit(f"Error: `{e}`")

    await asyncio.sleep(5)
    await xxnx.delete()
    await message.delete()

@Bot.on_message(filters.command("delbl") & ~filters.private & Admin)
async def deldblmessag(app: Bot, message: Message):
    trigger = get_arg(message)
    if message.reply_to_message:
        trigger = message.reply_to_message.text or message.reply_to_message.caption

    if not trigger:
        return await message.reply("`Tidak ada kata yang diberikan untuk dihapus dari blacklist.`")

    xxnx = await message.reply(f"`Menghapus` {trigger} `dari blacklist..`")
    try:
        await remove_bl_word(trigger.lower())
        await xxnx.edit(f"`{trigger}` `berhasil dihapus dari blacklist..`")
    except Exception as e:
        await xxnx.edit(f"Error: `{e}`")

    await asyncio.sleep(5)
    await xxnx.delete()
    await message.delete()

@Bot.on_message(filters.text & ~filters.private & Gcast)
async def deletermessag(app: Bot, message: Message):
    text = (
        "Maaf, grup ini tidak terdaftar dalam list. "
        "Silahkan hubungi @Zenithnewbie untuk mendaftarkan grup Anda.\n\n"
        "**Bot akan meninggalkan grup!**"
    )
    chat = message.chat.id
    chats = await get_actived_chats()
    if chat not in chats:
        await message.reply(text=text)
        await asyncio.sleep(5)
        try:
            await app.leave_chat(chat)
        except UserNotParticipant as e:
            print(f"Error leaving chat: {e}")
        return

    # Delete the message
    try:
        await message.delete()
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.delete()
    except MessageDeleteForbidden:
        pass
