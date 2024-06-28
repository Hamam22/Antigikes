from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageDeleteForbidden
import asyncio

from antigcast.config import OWNER_ID
from antigcast.helpers.tools import extract
from antigcast.helpers.database import (
    get_muted_users_in_group,
    mute_user_in_group,
    unmute_user_in_group,
    clear_muted_users_in_group
)

@Bot.on_message(filters.command("pl") & filters.user(OWNER_ID))
async def mute_handler(app: Bot, message: Message):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("Berikan saya ID pengguna yang ingin di mute")

    user = await extract(message)
    user_id = user.id
    group_id = message.chat.id

    if user_id == message.from_user.id:
        return await message.reply_text("Kamu tidak bisa mute diri sendiri")
    elif user_id == app.me.id:
        return await message.reply_text("Kamu tidak bisa mute bot")
    elif user_id in OWNER_ID:
        return await message.reply_text("Kamu tidak bisa mute developer bot")

    xxnx = await message.reply("`Menambahkan pengguna ke dalam daftar mute...`")

    muted = await get_muted_users_in_group(group_id)
    if user_id in muted:
        await xxnx.edit("**Pengguna ini sudah ada di daftar mute**")
        await asyncio.sleep(10)
        await xxnx.delete()
        return

    try:
        kon = await app.get_users(user_id)
        kon_name = kon.first_name
        kon_id = kon.id

        await mute_user_in_group(group_id, kon_id)

        await xxnx.edit(f"**Pengguna berhasil di mute**\n- Nama: {kon_name}\n- User ID: `{kon_id}`")
        await asyncio.sleep(10)
        await xxnx.delete()
    except Exception as e:
        await xxnx.edit(f"**Gagal mute pengguna:** `{e}`")


@Bot.on_message(filters.command("ungdel") & filters.user(OWNER_ID))
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
    elif user_id in OWNER_ID:
        return await message.reply_text("Kamu tidak bisa unmute developer bot")

    xxnx = await message.reply("`Menghapus pengguna dari daftar mute...`")

    muted = await get_muted_users_in_group(group_id)
    if user_id not in muted:
        await xxnx.edit("**Pengguna ini tidak ada di daftar mute**")
        await asyncio.sleep(10)
        await xxnx.delete()
        return

    try:
        kon = await app.get_users(user_id)
        kon_name = kon.first_name
        kon_id = kon.id

        await unmute_user_in_group(group_id, kon_id)

        await xxnx.edit(f"**Pengguna berhasil di unmute**\n- Nama: {kon_name}\n- User ID: `{kon_id}`")
        await asyncio.sleep(10)
        await xxnx.delete()
        await message.delete()
    except Exception as e:
        await xxnx.edit(f"**Gagal unmute pengguna:** `{e}`")


@Bot.on_message(filters.command("gmuted") & filters.user(OWNER_ID))
async def muted(app: Bot, message: Message):
    group_id = message.chat.id
    kons = await get_muted_users_in_group(group_id)

    if not kons:
        return await message.reply("**Belum ada pengguna yang di mute.**")

    resp = await message.reply("**Memuat database...**")

    msg = "**Daftar pengguna yang di mute**\n\n"
    num = 0

    for x in kons:
        num += 1

        try:
            get = await app.get_users(int(x))
            gname = get.mention
            gid = get.id
            msg += f"**{num}. {gname}**\n└ User ID: `{gid}`\n\n"
        except Exception:
            msg += f"**{num}. {x}**\n\n"

    await resp.edit(msg, disable_web_page_preview=True)


@Bot.on_message(filters.command("clearmuted") & filters.user(OWNER_ID))
async def clear_muted(app: Bot, message: Message):
    group_id = message.chat.id
    await clear_muted_users_in_group(group_id)
    await message.reply("**Semua pengguna yang di mute telah dihapus untuk grup ini.**")


@Bot.on_message(filters.text & ~filters.private)
async def delete_muted_messages(app: Bot, message: Message):
    user_id = message.from_user.id
    group_id = message.chat.id

    muted_users = await get_muted_users_in_group(group_id)
    if user_id in muted_users:
        try:
            await message.delete()
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.delete()
        except MessageDeleteForbidden:
            pass
