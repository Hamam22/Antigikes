from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageDeleteForbidden
import asyncio
import aiomcache

from antigcast.helpers.admins import *
from antigcast.helpers.tools import extract
from antigcast.helpers.database import (mute_user_in_group, unmute_user_in_group, 
                              get_muted_users_in_group, clear_muted_users_in_group)


cache = aiomcache.Client("127.0.0.1", 11211)

@Bot.on_message(filters.command("pl") & ~filters.private)
async def mute_handler(app: Bot, message: Message):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("Berikan saya ID pengguna yang ingin di mute")

    user = message.reply_to_message.from_user if message.reply_to_message else await app.get_users(message.command[1])
    user_id = user.id
    group_id = message.chat.id

    issuer_id = message.from_user.id
    issuer_name = message.from_user.first_name

    if user_id == issuer_id:
        return await message.reply_text("Kamu tidak bisa mute diri sendiri")
    elif user_id == app.me.id:
        return await message.reply_text("Kamu tidak bisa mute bot")

    xxnx = await message.reply("`Menambahkan pengguna ke dalam daftar mute...`")

    muted_users = await get_muted_users_in_group(group_id)
    if any(mu['user_id'] == user_id for mu in muted_users):
        await xxnx.edit("**Pengguna ini sudah ada di daftar mute**")
        await asyncio.sleep(10)
        await xxnx.delete()
        return

    try:
        await mute_user_in_group(group_id, user_id, issuer_id, issuer_name)

        await xxnx.edit(f"**Pengguna berhasil di mute**\n- Nama: {user.first_name}\n- User ID: `{user_id}`\n- Di-mute oleh: {issuer_name}")
        await asyncio.sleep(10)
        await xxnx.delete()
    except Exception as e:
        await xxnx.edit(f"**Gagal mute pengguna:** `{e}`")

@Bot.on_message(filters.command("ungdel") & ~filters.private)
async def unmute_handler(app: Bot, message: Message):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("Berikan saya ID pengguna yang ingin di unmute")

    user = message.reply_to_message.from_user if message.reply_to_message else await app.get_users(message.command[1])
    user_id = user.id
    group_id = message.chat.id

    if user_id == message.from_user.id:
        return await message.reply_text("Kamu tidak bisa unmute diri sendiri")
    elif user_id == app.me.id:
        return await message.reply_text("Kamu tidak bisa unmute bot")

    xxnx = await message.reply("`Menghapus pengguna dari daftar mute...`")

    muted_users = await get_muted_users_in_group(group_id)
    if all(mu['user_id'] != user_id for mu in muted_users):
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

@Bot.on_message(filters.command("gmuted") & ~filters.private)
async def muted(app: Bot, message: Message):
    group_id = message.chat.id
    muted_users = await get_muted_users_in_group(group_id)

    if not muted_users:
        return await message.reply("**Belum ada pengguna yang di mute.**")

    resp = await message.reply("**Memuat database...**")

    msg = "**Daftar pengguna yang di mute**\n\n"
    num = 0

    for mu in muted_users:
        num += 1
        user_name = mu['muted_by']['name']
        msg += f"**{num}. {user_name}**\n└ User ID: `{mu['user_id']}`\n└ Di-mute oleh: {mu['muted_by']['name']}\n\n"

    await resp.edit(msg, disable_web_page_preview=True)

@Bot.on_message(filters.command("clearmuted") & ~filters.private)
async def clear_muted(app: Bot, message: Message):
    group_id = message.chat.id
    await clear_muted_users_in_group(group_id)
    await message.reply("**Semua pengguna yang di mute telah dihapus untuk grup ini.**")

@Bot.on_message(filters.text & ~filters.private & filters.group, group=54)
async def delete_muted_messages(app: Bot, message: Message):
    user_id = message.from_user.id
    group_id = message.chat.id

    muted_users = await get_muted_users_in_group(group_id)
    if any(mu['user_id'] == user_id for mu in muted_users):
        try:
            await message.delete()
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.delete()
        except MessageDeleteForbidden:
            pass
