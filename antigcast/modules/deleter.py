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


@Bot.on_message(filters.text & ~filters.private & Member & Gcast)
async def deletermessag(app: Bot, message: Message):
    text = "<blockquote>Maaf, Grup ini tidak terdaftar di dalam list. Silahkan hubungi @Zenithnewbie Untuk mendaftarkan Group Anda.\n\n**Bot akan meninggalkan group!**</blockquote>"
    chat = message.chat.id
    print(f"Received message in chat: {chat}")  # Debugging: Print chat ID

    # Mendapatkan daftar chat aktif
    chats = await get_actived_chats()
    print(f"Active chats: {chats}")  # Debugging: Print daftar chat aktif

    if chat not in chats:
        print(f"Chat {chat} not in active chats. Replying and leaving...")  # Debugging: Chat tidak terdaftar
        await message.reply(text=text)
        await asyncio.sleep(5)
        try:
            await app.leave_chat(chat)
            print(f"Bot has left chat {chat}")  # Debugging: Berhasil meninggalkan chat
        except Exception as e:
            print(f"Error while leaving chat {chat}: {e}")  # Debugging: Menangani kesalahan saat meninggalkan chat
        return
    else:
        print(f"Chat {chat} is in active chats. Processing message deletion...")  # Debugging: Chat terdaftar

    try:
        await message.delete()
        print(f"Message in chat {chat} deleted")  # Debugging: Pesan berhasil dihapus
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.delete()
        print(f"Message in chat {chat} deleted after flood wait")  # Debugging: Pesan dihapus setelah menunggu flood
    except Exception as e:
        print(f"Error while deleting message in chat {chat}: {e}")  # Debugging: Menangani kesalahan saat menghapus pesan
