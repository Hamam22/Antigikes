import asyncio
from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageDeleteForbidden, UserNotParticipant

from antigcast.helpers.tools import *
from antigcast.helpers.admins import *
from antigcast.helpers.message import *
from antigcast.helpers.database import get_bl_words, add_bl_word, remove_bl_word

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

    await asyncio.sleep(3)
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

    await asyncio.sleep(3)
    await response.delete()
    await message.delete()

@Bot.on_message(filters.command("listbl") & ~filters.private & Admin)
async def daftar_blacklist(app: Bot, message: Message):
    try:
        bl_words = await get_bl_words()
        if not bl_words:
            await message.reply("Tidak ada kata-kata yang di-blacklist.")
            return

        bl_list = "\n".join([f"{idx + 1}. {word}" for idx, word in enumerate(bl_words)])
        response_text = f"**Daftar kata-kata yang di-blacklist ({len(bl_words)} kata):**\n{bl_list}"
        await message.reply(response_text)
    except Exception as e:
        await message.reply(f"Error: `{e}`")


@Bot.on_message(filters.command("listblgroups") & ~filters.private & Admin)
async def daftar_grup_blacklist(app: Bot, message: Message):
    try:
        bl_groups = await get_bl_groups()
        if not bl_groups:
            await message.reply("Tidak ada grup yang menggunakan perintah blacklist.")
            return

        group_list = "\n".join([f"{idx + 1}. {group['group_name']} (ID: {group['chat_id']})" for idx, group in enumerate(bl_groups)])
        response_text = f"**Daftar grup yang menggunakan perintah blacklist ({len(bl_groups)} grup):**\n{group_list}"
        await message.reply(response_text)
    except Exception as e:
        await message.reply(f"Error: `{e}`")

@Bot.on_message(filters.text & ~filters.private & Member & Gcast)
async def deletermessag(app: Bot, message: Message):
    text = "Maaf, Grup ini tidak terdaftar di dalam list. Silahkan hubungi @Zenithnewbie Untuk mendaftarkan Group Anda.\n\n**Bot akan meninggalkan group!**"
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

    # Hapus pesan
    try:
        await message.delete()
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.delete()
    except MessageDeleteForbidden:
        pass
