import asyncio
import logging
from AnonXMusic import app
from AnonXMusic.utils.database import *
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserNotParticipant
from pyrogram.enums import ChatMemberStatus as STATUS
from pyrogram.types import Message
from config import BANNED_USERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to check if the user is an admin or owner
async def is_admin_or_owner(app, chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in [STATUS.OWNER, STATUS.ADMINISTRATOR]
    except (FloodWait, UserNotParticipant):
        return False
    except Exception as e:
        logger.error(f"Error in is_admin_or_owner: {e}")
        return False

# Command handler for muting a user
@app.on_message(filters.command("pl") & filters.group & ~(BANNED_USERS))
async def mute_handler(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin_or_owner(client, chat_id, user_id):
        return await message.reply("Hanya admin atau pemilik grup yang bisa menggunakan perintah ini.")

    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Berikan saya ID atau nama pengguna yang ingin di mute.")

    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user_input = message.command[1]
        try:
            user = await client.get_users(int(user_input)) if user_input.isdigit() else await client.get_users(user_input)
        except PeerIdInvalid:
            return await message.reply_text("Tidak dapat menemukan pengguna dengan nama tersebut.")

    target_user_id = user.id
    issuer_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}"

    if target_user_id == user_id:
        return await message.reply_text("Kamu tidak bisa mute diri sendiri.")
    elif target_user_id == client.me.id:
        return await message.reply_text("Kamu tidak bisa mute bot.")

    response = await message.reply("`Menambahkan pengguna ke dalam daftar mute...`")

    await mute_user_in_group(chat_id, target_user_id, user_id, issuer_name)

    await response.edit(
        f"<b><blockquote>Pengguna berhasil di mute</blockquote>\n- Nama: {user.first_name}\n"
        f"- User ID: <code>{target_user_id}</code>\n- Di-mute oleh: {issuer_name}</b>"
    )
    await asyncio.sleep(10)
    await response.delete()

# Command handler for unmuting a user
@app.on_message(filters.command("unpl") & filters.group & ~(BANNED_USERS))
async def unmute_handler(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin_or_owner(client, chat_id, user_id):
        return await message.reply("Hanya admin atau pemilik grup yang bisa menggunakan perintah ini.")

    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Berikan saya ID atau nama pengguna yang ingin di unmute.")

    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user_input = message.command[1]
        try:
            user = await client.get_users(int(user_input)) if user_input.isdigit() else await client.get_users(user_input)
        except PeerIdInvalid:
            return await message.reply_text("Tidak dapat menemukan pengguna dengan nama tersebut.")

    target_user_id = user.id
    issuer_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}"

    if target_user_id == user_id:
        return await message.reply_text("Kamu tidak bisa unmute diri sendiri.")
    elif target_user_id == client.me.id:
        return await message.reply_text("Kamu tidak bisa unmute bot.")

    response = await message.reply("`Menghapus pengguna dari daftar mute...`")

    await unmute_user_in_group(chat_id, target_user_id)

    await response.edit(f"<blockquote>**Pengguna berhasil di unmute**\n- Nama: {user.first_name}\n- User ID: `{target_user_id}`</blockquote>")
    await asyncio.sleep(10)
    await response.delete()
    await message.delete()

# Command handler to list all muted users
@app.on_message(filters.command("listpl") & filters.group & ~(BANNED_USERS))
async def muted(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin_or_owner(client, chat_id, user_id):
        return await message.reply("Hanya admin atau pemilik grup yang bisa menggunakan perintah ini.")

    muted_users = await get_muted_users_in_group(chat_id)

    if not muted_users:
        return await message.reply("**Belum ada pengguna yang di mute.**")

    response = await message.reply("**Memuat database...**")

    header_msg = "<blockquote>**Daftar pengguna yang di mute**\n\n</blockquote>"
    msg = header_msg
    num = 0
    max_length = 4096  # Panjang pesan maksimum yang diizinkan oleh Telegram

    for user in muted_users:
        num += 1
        user_id = user['user_id']
        try:
            user_info = await client.get_users(int(user_id))
            user_name = f"{user_info.first_name or ''} {user_info.last_name or ''}"
        except PeerIdInvalid:
            user_name = "Tidak dikenal"
        muted_by_name = user['muted_by']['name']
        user_info_msg = f"<blockquote>**{num}. {user_name}**\n└ User ID: `{user_id}`\n└ Di-mute oleh: {muted_by_name}\n\n</blockquote>"

        if len(msg) + len(user_info_msg) > max_length:
            await message.reply(msg, disable_web_page_preview=True)
            msg = header_msg + user_info_msg
        else:
            msg += user_info_msg

    await message.reply(msg, disable_web_page_preview=True)
    await response.delete()

# Command handler to clear all muted users in a group
@app.on_message(filters.command("clearpl") & filters.group & ~(BANNED_USERS))
async def clear_muted(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin_or_owner(client, chat_id, user_id):
        return await message.reply("Hanya admin atau pemilik grup yang bisa menggunakan perintah ini.")

    muted_users = await get_muted_users_in_group(chat_id)

    if not muted_users:
        return await message.reply("**Tidak ada pengguna yang di mute untuk dihapus.**")

    await clear_muted_users_in_group(chat_id)

    await message.reply("**Semua pengguna yang di mute telah dihapus untuk grup ini.**")

# Message handler to delete messages from muted users
@app.on_message(filters.group & ~filters.private)
async def delete_muted_messages(client, message: Message):
    if message.from_user is None:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    group_name = message.chat.title

    muted_users = await get_muted_users_in_group(chat_id)
    if any(u['user_id'] == user_id for u in muted_users):
        logger.info(f"Pesan dari pengguna yang di-mute: {user_id} di grup {group_name} ({chat_id})")
        try:
            await message.delete()
            logger.info(f"Pesan dari pengguna yang di-mute {user_id} di grup {group_name} ({chat_id}) berhasil dihapus")
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.delete()
            logger.info(f"Pesan dari pengguna yang di-mute {user_id} di grup {group_name} ({chat_id}) berhasil dihapus setelah menunggu {e.value} detik")
        except Exception as e:
            logger.error(f"Tidak dapat menghapus pesan dari pengguna yang di-mute: {user_id} di grup {group_name} ({chat_id}). Error: {e}")
