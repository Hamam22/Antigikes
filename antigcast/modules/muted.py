import asyncio
from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, PeerIdInvalid, UserNotParticipant
from pyrogram.enums import ChatMemberStatus as STATUS
from antigcast.helpers.tools import extract
from antigcast.helpers.database import *

async def is_admin_or_owner(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in [STATUS.OWNER, STATUS.ADMINISTRATOR]
    except (FloodWait, UserNotParticipant):
        return False
    except Exception:
        return False

async def get_user_from_message(app, message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    if len(message.command) < 2:
        return None
    user_input = message.command[1]
    try:
        if user_input.isdigit():
            return await app.get_users(int(user_input))
        return await app.get_users(user_input)
    except PeerIdInvalid:
        return None

async def handle_mute_unmute(app, message, action):
    if not await is_admin_or_owner(app, message.chat.id, message.from_user.id):
        return await message.reply_text("Kamu harus menjadi admin untuk menggunakan perintah ini.")
    
    user = await get_user_from_message(app, message)
    if not user:
        return await message.reply_text("Berikan saya ID atau nama pengguna yang valid.")
    
    user_id = user.id
    group_id = message.chat.id
    issuer_id = message.from_user.id
    issuer_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}"
    
    if user_id == issuer_id:
        return await message.reply_text(f"Kamu tidak bisa {action} diri sendiri.")
    if user_id == app.me.id:
        return await message.reply_text(f"Kamu tidak bisa {action} bot.")
    
    if await is_admin_or_owner(app, message.chat.id, user_id):
        return await message.reply_text(f"Kamu tidak bisa {action} admin atau owner.")
    
    action_message = await message.reply(f"`{action.capitalize()} pengguna...`")
    muted_users = await get_muted_users_in_group(group_id)
    
    if (action == "mute" and any(u['user_id'] == user_id for u in muted_users)) or \
       (action == "unmute" and not any(u['user_id'] == user_id for u in muted_users)):
        await action_message.edit(f"**Pengguna ini sudah {'di daftar mute' if action == 'mute' else 'tidak ada di daftar mute'}**.")
        await asyncio.sleep(10)
        await action_message.delete()
        return

    try:
        if action == "mute":
            await mute_user_in_group(group_id, user_id, issuer_id, issuer_name)
            await action_message.edit(
                f"<b><blockquote>Pengguna berhasil di mute</blockquote>\n- Nama: {user.first_name or ''} {user.last_name or ''}\n- User ID: <code>{user_id}</code>\n- Di-mute oleh: {issuer_name}</b>"
            )
        else:
            await unmute_user_in_group(group_id, user_id)
            await action_message.edit(
                f"<blockquote>**Pengguna berhasil di unmute**\n- Nama: {user.first_name}\n- User ID: `{user_id}`</blockquote>"
            )
        await asyncio.sleep(10)
        await action_message.delete()
        await message.delete()
    except Exception as e:
        await action_message.edit(f"**Gagal {action} pengguna:** `{e}`")

@Bot.on_message(filters.command("pl"))
async def mute_handler(app: Bot, message: Message):
    await handle_mute_unmute(app, message, "mute")

@Bot.on_message(filters.command("ungdel") & ~filters.private)
async def unmute_handler(app: Bot, message: Message):
    await handle_mute_unmute(app, message, "unmute")

@Bot.on_message(filters.command("gmuted") & ~filters.private)
async def muted(app: Bot, message: Message):
    if not await is_admin_or_owner(app, message.chat.id, message.from_user.id):
        return await message.reply_text("Kamu harus menjadi admin untuk menggunakan perintah ini.")

    group_id = message.chat.id
    muted_users = await get_muted_users_in_group(group_id)
    
    if not muted_users:
        return await message.reply("**Belum ada pengguna yang di mute.**")

    response_msg = await message.reply("**Memuat database...**")

    header_msg = "<blockquote>**Daftar pengguna yang di mute**\n\n</blockquote>"
    msg = header_msg
    max_length = 4096  # Maximum message length allowed by Telegram
    
    for idx, user in enumerate(muted_users, start=1):
        user_id = user['user_id']
        try:
            user_info = await app.get_users(int(user_id))
            user_name = f"{user_info.first_name or ''} {user_info.last_name or ''}"
        except PeerIdInvalid:
            user_name = "Tidak dikenal"
        
        user_info_msg = (
            f"<blockquote>**{idx}. {user_name}**\n"
            f"└ User ID: `{user_id}`\n"
            f"└ Di-mute oleh: {user['muted_by']['name']}\n\n</blockquote>"
        )
        
        if len(msg) + len(user_info_msg) > max_length:
            await message.reply(msg, disable_web_page_preview=True)
            msg = header_msg + user_info_msg
        else:
            msg += user_info_msg
    
    await message.reply(msg, disable_web_page_preview=True)
    await response_msg.delete()

@Bot.on_message(filters.command("clearmuted") & ~filters.private)
async def clear_muted(app: Bot, message: Message):
    if not await is_admin_or_owner(app, message.chat.id, message.from_user.id):
        return await message.reply_text("Kamu harus menjadi admin untuk menggunakan perintah ini.")
    
    group_id = message.chat.id
    muted_users = await get_muted_users_in_group(group_id)
    
    if not muted_users:
        return await message.reply("**Tidak ada pengguna yang di mute untuk dihapus.**")

    await clear_muted_users_in_group(group_id)
    await message.reply("**Semua pengguna yang di mute telah dihapus untuk grup ini.**")

@Bot.on_message(filters.group & ~filters.private)
async def delete_muted_messages(app: Bot, message: Message):
    if message.from_user is None:
        return

    user_id = message.from_user.id
    group_id = message.chat.id
    group_name = message.chat.title

    muted_users = await get_muted_users_in_group(group_id)
    if any(u['user_id'] == user_id for u in muted_users):
        print(f"Pesan dari pengguna yang di-mute: {user_id} di grup {group_name} ({group_id})")
        try:
            await message.delete()
            print(f"Pesan dari pengguna yang di-mute {user_id} di grup {group_name} ({group_id}) berhasil dihapus")
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.delete()
            print(f"Pesan dari pengguna yang di-mute {user_id} di grup {group_name} ({group_id}) berhasil dihapus setelah menunggu {e.value} detik")
        except Exception as e:
            print(f"Tidak dapat menghapus pesan dari pengguna yang di-mute: {user_id} di grup {group_name} ({group_id}). Error: {e}")
