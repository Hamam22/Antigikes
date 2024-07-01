from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageDeleteForbidden
import asyncio

from antigcast.helpers.admins import *
from antigcast.helpers.tools import extract
from antigcast.helpers.database import *


@Bot.on_message(filters.command("pl") & ~filters.private & Admin)
async def mute_handler(app: Bot, message: Message):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("Berikan saya ID pengguna yang ingin di mute")

    user = await extract(message)
    user_id = user.id
    group_id = message.chat.id

    issuer_id = message.from_user.id
    issuer_name = message.from_user.first_name

    if user_id == issuer_id:
        return await message.reply_text("Kamu tidak bisa mute diri sendiri")
    elif user_id == app.me.id:
        return await message.reply_text("Kamu tidak bisa mute bot")

    xxnx = await message.reply("`Menambahkan pengguna ke dalam daftar mute...`")

    muted = await get_muted_users_in_group(group_id)
    if any(user['user_id'] == user_id for user in muted):
        await xxnx.edit("**Pengguna ini sudah ada di daftar mute**")
        await asyncio.sleep(10)
        await xxnx.delete()
        return

    try:
        kon = await app.get_users(user_id)
        kon_name = kon.first_name

        await mute_user_in_group(group_id, user_id, issuer_id, issuer_name)

        await xxnx.edit(f"**Pengguna berhasil di mute**\n- Nama: {kon_name}\n- User ID: `{user_id}`\n- Di-mute oleh: {issuer_name}")
        await asyncio.sleep(10)
        await xxnx.delete()
    except Exception as e:
        await xxnx.edit(f"**Gagal mute pengguna:** `{e}`")


@Bot.on_message(filters.command("ungdel") & ~filters.private & Admin)
async def unmute_handler(app: Bot, message: Message):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("Berikan saya ID pengguna yang ingin di unmute")

    user = await extract(message)
    user_id = user.id
    group_id = message.chat.id

    if user_id == message.from_user.id:
        return await message.reply_text("Kamu tidak bisa unmute diri sendiri")
    elif user_id == app.me.id:
        return await message.reply_text("Kamu tidak bisa unmute bot")

    xxnx = await message.reply("`Menghapus pengguna dari daftar mute...`")

    muted = await get_muted_users_in_group(group_id)
    if not any(user['user_id'] == user_id for user in muted):
        await xxnx.edit("**Pengguna ini tidak ada di daftar mute**")
        await asyncio.sleep(10)
        await xxnx.delete()
        return

    try:
        await unmute_user_in_group(group_id, user_id)

        await xxnx.edit(f"**Pengguna berhasil di unmute**\n- Nama: {user.first_name}\n- User ID: `{user_id}`")
        await asyncio.sleep(10)
        await xxnx.delete()
        await message.delete()
    except Exception as e:
        await xxnx.edit(f"**Gagal unmute pengguna:** `{e}`")


@Bot.on_message(filters.command("gmuted") & ~filters.private & Admin)
async def muted(app: Bot, message: Message):
    group_id = message.chat.id
    kons = await get_muted_users_in_group(group_id)

    if not kons:
        return await message.reply("**Belum ada pengguna yang di mute.**")

    resp = await message.reply("**Memuat database...**")

    msg = "**Daftar pengguna yang di mute**\n\n"
    num = 0

    for user in kons:
        num += 1
        user_id = user['user_id']
        user_name = (await app.get_users(user_id)).first_name
        muted_by_name = user['muted_by']['name']
        msg += f"**{num}. {user_name}**\n└ User ID: `{user_id}`\n└ Di-mute oleh: {muted_by_name}\n\n"

    await resp.edit(msg, disable_web_page_preview=True)
    

@Bot.on_message(filters.command("clearmuted") & ~filters.private & Admin)
async def clear_muted(app: Bot, message: Message):
    group_id = message.chat.id
    muted_users = await get_muted_users_in_group(group_id)

    if not muted_users:
        return await message.reply("**Tidak ada pengguna yang di mute untuk dihapus.**")

    await clear_muted_users_in_group(group_id)
    await message.reply("**Semua pengguna yang di mute telah dihapus untuk grup ini.**")


@Bot.on_message(filters.text & ~filters.private & filters.group, group=54)
async def delete_muted_messages(app: Bot, message: Message):
    user_id = message.from_user.id
    group_id = message.chat.id

    muted_users = await get_muted_users_in_group(group_id)
    if any(user['user_id'] == user_id for user in muted_users):
        try:
            await message.delete()
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.delete()
        except MessageDeleteForbidden:
            pass
