import asyncio
import datetime

from pytz import timezone
from dateutil.relativedelta import relativedelta

from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message

from antigcast.config import OWNER_ID
from antigcast.helpers.tools import *
from antigcast.helpers.database import *


#SUPPORT BY PYROGRAM !!!!!!



async def is_seller(user_id):
    sellers = await list_sellers()
    return any(seller['_id'] == user_id for seller in sellers)


@Bot.on_message(filters.command("addgc") & filters.user(OWNER_ID))
async def addgcmessag(app: Bot, message: Message):
    # SOURCE PYROGRAM
    if not await is_seller(message.from_user.id):
        return await message.reply("Anda tidak diizinkan untuk menggunakan perintah ini.")

    chat_id = message.chat.id
    chat_name = message.chat.title
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    hari = get_arg(message)
    if not hari:
        hari = "30"
    xxnx = await message.reply(f"`Menambahkan izin dalam grup ini..`")
    now = datetime.datetime.now(timezone("Asia/Jakarta"))
    expired = now + relativedelta(days=int(hari))
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
    except BaseException as e:
        print(e)

    await xxnx.edit(f"**BOT AKTIF**\nGroup: `{chat_name}`\nExp: `{expired_datetime}` | `{hari} Hari..`")
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()


@Bot.on_message(filters.command("rmgc") & filters.user(OWNER_ID))
async def remgcmessag(app: Bot, message: Message):
    # SOURCE PYROGRAM
    if not await is_seller(message.from_user.id):
        return await message.reply("Anda tidak diizinkan untuk menggunakan perintah ini.")

    chat_id = int(get_arg(message))

    if not chat_id:
        chat_id = message.chat.id
        
    xxnx = await message.reply(f"`Menghapus izin dalam grup ini..`")
    try:
        await rem_actived_chat(chat_id)
        await rem_expired_date(chat_id)
    except BaseException as e:
        print(e)

    await xxnx.edit(f"Removed `{chat_id}` | Group ini tidak diizinkan untuk menggunakan Bot..`")
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()


@Bot.on_message(filters.command("groups") & filters.user(OWNER_ID))
async def get_groupsmessag(app: Bot, message: Message):
    # SOURCE PYROGRAM
    if not await is_seller(message.from_user.id):
        return await message.reply("Anda tidak diizinkan untuk menggunakan perintah ini.")

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

@Bot.on_message(filters.command("add") & filters.user(OWNER_ID))
async def addgroupmessag(app: Bot, message: Message):
    # SOURCE PYROGRAM
    if not await is_seller(message.from_user.id):
        return await message.reply("Anda tidak diizinkan untuk menggunakan perintah ini.")

    xxnx = await message.reply(f"`Menambahkan izin dalam grup ini..`")
    
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


@Bot.on_message(filters.command("addseller") & filters.user(OWNER_ID))
async def add_seller(app: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply("Gunakan format: `/addseller user_id`")

    seller_id = message.command[1]

    try:
        seller_id = int(seller_id)
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name or ""
        success = await add_seller(seller_id, user_id, username, first_name, last_name)
        if success:
            await message.reply(f"User dengan ID `{seller_id}` telah ditambahkan sebagai seller.")
        else:
            await message.reply("Terjadi kesalahan saat menambahkan seller.")
    except ValueError:
        await message.reply("User ID harus berupa angka.")
    except Exception as e:
        print(f"Error: {e}")
        await message.reply("Terjadi kesalahan saat menambahkan seller.")

@Bot.on_message(filters.command("remseller") & filters.user(OWNER_ID))
async def remove_seller(app: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply("Gunakan format: `/remseller user_id`")

    seller_id = message.command[1]

    try:
        seller_id = int(seller_id)
        success = await rem_seller(seller_id)
        if success:
            await message.reply(f"User dengan ID `{seller_id}` telah dihapus dari daftar seller.")
        else:
            await message.reply("Terjadi kesalahan saat menghapus seller.")
    except ValueError:
        await message.reply("User ID harus berupa angka.")
    except Exception as e:
        print(f"Error: {e}")
        await message.reply("Terjadi kesalahan saat menghapus seller.")

@Bot.on_message(filters.command("listseller") & filters.user(OWNER_ID))
async def list_sellers(app: Bot, message: Message):
    sellers = await list_sellers()
    if not sellers:
        return await message.reply("Tidak ada seller yang terdaftar.")

    msg = "**Daftar Seller**\n\n"
    for idx, seller in enumerate(sellers, 1):
        seller_name = seller.get('seller_name', 'Unknown')
        added_by = seller.get('added_by', {})
        added_by_name = added_by.get('username', 'Unknown')
        added_at = seller.get('added_at', 'Unknown')

        # Mengubah waktu ke zona waktu Asia/Jakarta
        if added_at != 'Unknown':
            added_at = added_at.astimezone(timezone("Asia/Jakarta")).strftime("%d-%m-%Y %H:%M:%S")

        msg += f"{idx}. {seller_name} (ID: `{seller['_id']}`)\n  Ditambahkan oleh: {added_by_name} pada {added_at}\n"

    await message.reply(msg)
