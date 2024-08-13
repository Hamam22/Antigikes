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
async def tambah_ke_blacklist(app: Bot, message: Message):
    trigger = get_arg(message)
    if not trigger and message.reply_to_message:
        trigger = message.reply_to_message.text or message.reply_to_message.caption

    if not trigger:
        await message.reply("Error: Tidak ada kata yang diberikan untuk blacklist.")
        return

    response = await message.reply(f"`Menambahkan` {trigger} `ke dalam blacklist...`")
    try:
        await add_bl_word(trigger.lower())
        await response.edit(f"`{trigger}` berhasil ditambahkan ke dalam blacklist.")
    except Exception as e:
        await response.edit(f"Error: `{e}`")

    await asyncio.sleep(5)
    await response.delete()
    await message.delete()

@Bot.on_message(filters.command("delbl") & ~filters.private & Admin)
async def hapus_dari_blacklist(app: Bot, message: Message):
    trigger = get_arg(message)
    if not trigger and message.reply_to_message:
        trigger = message.reply_to_message.text or message.reply_to_message.caption

    if not trigger:
        await message.reply("Error: Tidak ada kata yang diberikan untuk dihapus dari blacklist.")
        return

    response = await message.reply(f"`Menghapus` {trigger} `dari blacklist...`")
    try:
        await remove_bl_word(trigger.lower())
        await response.edit(f"`{trigger}` berhasil dihapus dari blacklist.")
    except ValueError as e:
        await response.edit(f"Error: `{e}`")  # Penanganan error khusus jika tidak ditemukan
    except Exception as e:
        await response.edit(f"Error: `{e}`")

    await asyncio.sleep(5)
    await response.delete()
    await message.delete()


@Bot.on_message(filters.group, group=1)
async def deletermessag(app : Bot, message : Message):
    text = f"Maaf, Grup ini tidak terdaftar di dalam list. Silahkan hubungi @Zenithnewbie Untuk mendaftarkan Group Anda.\n\n**Bot akan meninggalkan group!**"
    chat = message.chat.id
    chats = await get_actived_chats()
    if chat not in chats:
        await message.reply(text=text)
        await asyncio.sleep(5)
        try:
            await app.leave_chat(chat)
        except UserNotParticipant as e:
            print(e)
        return
    
    # Delete
    try:
        await message.delete()
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.delete()
    except MessageDeleteForbidden:
        pass
