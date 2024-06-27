import asyncio
import datetime

from pytz import timezone
from dateutil.relativedelta import relativedelta

from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message

from antigcast.config import *
from antigcast.helpers.tools import *
from antigcast.helpers.database import *


@Bot.on_message(filters.command("addgc") & filters.user(OWNER_ID))
async def addgcmessag(app: Bot, message: Message):
    chat_id = message.chat.id
    chat_name = message.chat.title
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    hari = get_arg(message)
    if not hari:
        hari = "30"
    xxnx = await message.reply(f"`Menambahakan izin dalam grup ini..`")
    now = datetime.datetime.now(timezone("Asia/Jakarta"))
    expired = now + relativedelta(days=int(hari))
    expired_datetime = expired.strftime("%d-%m-%Y %H:%M:%S")
    chats = await get_actived_chats()
    if chat_id in chats:
        msg = await message.reply("Maaf, Group ini sudah di izinkan untuk menggunakan Bot.")
        await asyncio.sleep(10)
        await msg.delete()
        return
    
    try:
        added = await add_actived_chat(chat_id, user_id, username)
        if added:
            await set_expired_date(chat_id, expired, user_id, username)
    except BaseException as e:
        print(e)

    await xxnx.edit(f"**BOT AKTIF**\nGroup: `{chat_name}`\nExp: `{expired_datetime}` | `{hari} Hari..`")
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()


@Bot.on_message(filters.command("add") & filters.user(OWNER_ID))
async def addgroupmessag(app: Bot, message: Message):
    xxnx = await message.reply(f"`Menambahakan izin dalam grup ini..`")
    
    if len(message.command) < 3:
        return await xxnx.edit(f"**Gunakan Format** : `/add group_id hari`")
    
    try:
        command, group, hari = message.command[:3]
        chat_id = int(group)
        days = int(hari)
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name
    except ValueError:
        return await xxnx.edit("Group ID dan hari harus berupa angka.")
    
    now = datetime.datetime.now(timezone("Asia/Jakarta"))
    expired = now + relativedelta(days=days)
    expired_datetime = expired.strftime("%d-%m-%Y %H:%M:%S")
    
    chats = await get_actived_chats()
    if chat_id in chats:
        msg = await message.reply("Maaf, Group ini sudah diizinkan untuk menggunakan Bot.")
        await asyncio.sleep(10)
        await msg.delete()
        return
    
    try:
        added = await add_actived_chat(chat_id, user_id, username)
        if added:
            await set_expired_date(chat_id, expired, user_id, username)
    except Exception as e:
        print(e)
    
    await xxnx.edit(f"**BOT AKTIF**\nGroup ID: `{group}`\nExp: `{expired_datetime}` | `{hari} Hari..`")
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()

@Bot.on_message(filters.command("rmgc") & filters.user(OWNER_ID))
async def remgcmessag(app : Bot, message : Message):
    chat_id = int(get_arg(message))

    if not chat_id:
        chat_id = message.chat.id
        
    xxnx = await message.reply(f"`Menghapus izin dalam grup ini..`")
    try:
        await rem_actived_chat(chat_id)
        await rem_expired_date(chat_id)
    except BaseException as e:
        print(e)

    await xxnx.edit(f"Removed `{chat_id}` | Group ini tidak di izinkan untuk mengunakan Bot..`")
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()

@Bot.on_message(filters.command("groups") & filters.user(OWNER_ID))
async def get_groupsmessag(app: Bot, message: Message):
    group = []
    chats = await get_actived_chats()
    for chat in chats:
        group.append(chat)
    if not group:
        return await message.reply("**Belum Ada Group yang Terdaftar.**")
    resp = await message.reply("**Memuat database...**")
    msg = f"**Daftar Group Aktif**\n\n"
    num = 0
    for gc in group:
        expired = await get_expired_date(int(gc))
        added_by = await get_added_by(int(gc))
        if not expired:
            expired_datetime = "None"
        else:
            expired_datetime = expired.strftime("%d-%m-%Y %H:%M:%S")
        if not added_by:
            added_by_info = "Unknown"
        else:
            added_by_info = f"[{added_by['username']}](tg://user?id={added_by['user_id']})"
        try:
            get = await app.get_chat(int(gc))
            gname = get.title
            glink = get.invite_link
            gid = get.id
            num += 1
            msg += (f"**{num}. {gname}**\n"
                    f"├ Group ID: `{gid}`\n"
                    f"├ Link: [Tap Here]({glink})\n"
                    f"├ Expired: `{expired_datetime}`\n"
                    f"└ Added by: {added_by_info}\n\n")
        except:
            msg += (f"**{num}. {gc}**\n"
                    f"├ Expired: `{expired_datetime}`\n"
                    f"└ Added by: {added_by_info}\n\n")

    await resp.edit(msg, disable_web_page_preview=True)


@Bot.on_message(filters.command("addseller") & filters.user(OWNER_ID))
async def addsellermessag(app: Bot, message: Message):
    xxnx = await message.reply(f"`Menambahkan penjual baru..`")
    
    if len(message.command) != 2:
        return await xxnx.edit(f"**Gunakan Format** : `/addseller seller_id`")
    
    try:
        seller_id = int(message.command[1])
    except ValueError:
        return await xxnx.edit("Seller ID harus berupa angka.")
    
    try:
        added = await add_seller(seller_id, message.from_user.id, message.from_user.username)
        if added:
            await xxnx.edit(f"**Penjual Ditambahkan**\nSeller ID: `{seller_id}`")
    except Exception as e:
        print(f"Error adding seller: {e}")
        await xxnx.edit("Terjadi kesalahan saat menambahkan penjual.")
    
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()


@Bot.on_message(filters.command("remseller") & filters.user(OWNER_ID))
async def remsellermessag(app: Bot, message: Message):
    seller_id = int(message.command[1]) if len(message.command) > 1 else None

    if not seller_id:
        return await message.reply("`Silakan berikan Seller ID untuk menghapus penjual.`")
        
    xxnx = await message.reply(f"`Menghapus penjual..`")
    try:
        removed = await rem_seller(seller_id)
        if removed:
            await xxnx.edit(f"**Penjual dengan Seller ID `{seller_id}` telah dihapus.**")
        else:
            await xxnx.edit(f"**Penjual dengan Seller ID `{seller_id}` tidak ditemukan.**")
    except Exception as e:
        print(f"Error removing seller: {e}")
        await xxnx.edit("Terjadi kesalahan saat menghapus penjual.")
    
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()


@Bot.on_message(filters.command("listsellers") & filters.user(OWNER_ID))
async def listsellersmessag(app: Bot, message: Message):
    sellers = await list_sellers()
    if not sellers:
        return await message.reply("**Belum ada penjual yang terdaftar.**")

    resp = await message.reply("**Memuat database...**")
    msg = f"**Daftar Penjual**\n\n"
    num = 0
    for seller in sellers:
        added_by = seller.get('added_by', {})
        added_by_info = f"[{added_by.get('username', 'Unknown')}](tg://user?id={added_by.get('user_id', 0)})"

        # Format nama penjual sesuai dengan permintaan Anda
        user_id = added_by.get('user_id', 0)
        first_name = added_by.get('first_name', 'Unknown')
        last_name = added_by.get('last_name', '')
        user_link = f"[{added_by.get('username', 'Unknown')}](tg://user?id={added_by.get('user_id', 0)})"

        seller_id = seller.get('_id')
        seller_name = seller.get('seller_name', 'Unknown')
        added_at = seller.get('added_at', 'Unknown')
        num += 1
        msg += (f"**{num}. Penjual ID: `{seller_id}`**\n"
                f"├ Nama Penjual: {user_link}\n"  # Menggunakan format nama yang diinginkan
                f"├ Ditambahkan oleh: {added_by_info}\n"
                f"└ Ditambahkan pada: `{added_at}`\n\n")

    await resp.edit(msg, disable_web_page_preview=True)
