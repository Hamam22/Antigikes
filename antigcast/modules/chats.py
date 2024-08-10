import asyncio
import datetime

from pytz import timezone
from dateutil.relativedelta import relativedelta

from BocilAnti import Bot
from pyrogram import filters
from pyrogram.types import Message

from BocilAnti.config import OWNER_ID
from BocilAnti.helpers.tools import *
from BocilAnti.helpers.database import *


#SUPPORT BY PYROGRAM !!!!!!

async def is_seller(user_id):
    sellers = await list_sellers()
    return any(seller['_id'] == user_id for seller in sellers)


@Bot.on_message(filters.command("addgc"))
async def addgcmessag(app: Bot, message: Message):
    
    if not await is_seller(message.from_user.id):
        return await message.reply("Anda tidak diizinkan untuk menggunakan perintah ini.")
    
    chat_id = message.chat.id
    chat_name = message.chat.title
    hari = get_arg(message)
    if not hari:
        hari = "30"
    xxnx = await message.reply(f"`Menambahkan izin dalam grup ini...`")
    now = datetime.datetime.now(timezone("Asia/Jakarta"))
    expired = now + relativedelta(days=int(hari))
    expired_date = expired.strftime("%d-%m-%Y")
    chats = await get_actived_chats()
    if chat_id in chats:
        msg = await message.reply("Maaf, grup ini sudah diizinkan untuk menggunakan Bot.")
        await asyncio.sleep(10)
        await msg.delete()
        return
    
    try:
        added = await add_actived_chat(chat_id)
        if added:
            await set_expired_date(chat_id, expired)
    except Exception as e:
        print(e)

    await xxnx.edit(f"**BOT AKTIF**\nGrup : `{chat_name}`\nExp : `{expired_date}` | `{hari} Hari..`")
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()


@Bot.on_message(filters.command("add"))
async def addgroupmessag(app: Bot, message: Message):
    
    if not await is_seller(message.from_user.id):
        return await message.reply("Anda tidak diizinkan untuk menggunakan perintah ini.")
    
    xxnx = await message.reply(f"`Menambahkan izin dalam grup ini...`")
    
    if len(message.command) < 3:
        return await xxnx.edit(f"**Gunakan Format**: `/add group_id hari`")
    
    try:
        command, group, hari = message.command[:3]
        chat_id = int(group)
        days = int(hari)
    except ValueError:
        return await xxnx.edit("Group ID dan hari harus berupa angka.")
    
    now = datetime.datetime.now(timezone("Asia/Jakarta"))
    expired = now + relativedelta(days=days)
    expired_date = expired.strftime("%d-%m-%Y")
    
    chats = await get_actived_chats()
    if chat_id in chats:
        msg = await message.reply("Maaf, grup ini sudah diizinkan untuk menggunakan Bot.")
        await asyncio.sleep(10)
        await msg.delete()
        return
    
    try:
        added = await add_actived_chat(chat_id)
        if added:
            await set_expired_date(chat_id, expired)
    except Exception as e:
        print(e)
    
    await xxnx.edit(f"**BOT AKTIF**\nGroup ID: `{group}`\nExp : `{expired_date}` | `{hari} Hari..`")
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()


@Bot.on_message(filters.command("rmgc") & filters.user(OWNER_ID))
async def remgcmessag(app: Bot, message: Message):
    
    if not await is_seller(message.from_user.id):
        return await message.reply("Anda tidak diizinkan untuk menggunakan perintah ini.")
    
    chat_id = int(get_arg(message))

    if not chat_id:
        chat_id = message.chat.id
        
    xxnx = await message.reply(f"`Menghapus izin dalam grup ini...`")
    try:
        await rem_actived_chat(chat_id)
        await rem_expired_date(chat_id)
    except Exception as e:
        print(e)

    await xxnx.edit(f"Removed `{chat_id}` | Grup ini tidak diizinkan untuk menggunakan Bot.")
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()


@Bot.on_message(filters.command("groups"))
async def get_groupsmessag(app: Bot, message: Message):

    if not await is_seller(message.from_user.id):
        return await message.reply("Anda tidak diizinkan untuk menggunakan perintah ini.")
    
    group = []
    chats = await get_actived_chats()
    for chat in chats:
        group.append(chat)
    if not group:
        return await message.reply("**Belum ada grup yang terdaftar.**")
    
    resp = await message.reply("**Memuat database...**")
    msg = f"**Daftar Grup Aktif**\n\n"
    num = 0
    for gc in group:
        expired = await get_expired_date(int(gc))
        if not expired:
            expired_date = "None"
        else:
            expired_date = expired.strftime("%d-%m-%Y")
        try:
            get = await app.get_chat(int(gc))
            gname = get.title
            glink = get.invite_link
            gid = get.id
            num += 1
            msg += f"**{num}. {gname}**\n├ Group ID : `{gid}`\n├ Link : [Tap Here]({glink})\n└ Expired : `{expired_date}`\n\n"
        except:
            msg += f"**{num}. {gc}**\n└ Expired : `{expired_date}`\n\n"

    await resp.edit(msg, disable_web_page_preview=True)
    

@Bot.on_message(filters.command("addseller") & filters.user(OWNER_ID))
async def addsellermessag(app: Bot, message: Message):
    xxnx = await message.reply("`Menambahkan penjual baru...`")
    
    if len(message.command) != 2:
        return await xxnx.edit("**Gunakan Format** : `/addseller seller_id`")
    
    try:
        seller_id = int(message.command[1])
        added_at = datetime.datetime.now(timezone('Asia/Jakarta'))
        
        added = await add_seller(seller_id, added_at)
        if added:
            await xxnx.edit(f"**Penjual Ditambahkan**\nSeller ID: `{seller_id}`\nAdded At: `{added_at}`")
        else:
            await xxnx.edit("Gagal menambahkan penjual.")
    
    except ValueError:
        await xxnx.edit("Seller ID harus berupa angka.")
    except Exception as e:
        print(f"Error adding seller: {e}")
        await xxnx.edit("Terjadi kesalahan saat menambahkan penjual.")


@Bot.on_message(filters.command("rmmseller") & filters.user(OWNER_ID))
async def remsellermessag(app: Bot, message: Message):
    seller_id = int(message.command[1]) if len(message.command) > 1 else None

    if not seller_id:
        return await message.reply("`Silakan berikan Seller ID untuk menghapus penjual.`")
        
    xxnx = await message.reply("`Menghapus penjual...`")
    try:
        removed = await rem_seller(seller_id)
        if removed:
            await xxnx.edit(f"**Penjual dengan Seller ID `{seller_id}` telah dihapus.**")
        else:
            await xxnx.edit(f"**Penjual dengan Seller ID `{seller_id}` tidak ditemukan.**")
    except Exception as e:
        print(f"Error removing seller: {e}")
        await xxnx.edit("Terjadi kesalahan saat menghapus penjual.")


@Bot.on_message(filters.command("listsellers") & filters.user(OWNER_ID))
async def listsellersmessage(app: Bot, message: Message):
    sellers = await list_sellers()
    if not sellers:
        return await message.reply("**Belum ada penjual yang terdaftar.**")

    resp = await message.reply("**Memuat database...**")
    msg = f"**Daftar Penjual**\n\n"
    num = 0

    for seller in sellers:
        seller_id = seller.get('_id')
        added_at = seller.get('added_at')

        if added_at:
            added_at = added_at.astimezone(timezone('Asia/Jakarta')).strftime("%Y-%m-%d %H:%M:%S")
        else:
            added_at = "Unknown"

        num += 1
        msg += (
            f"**{num}. Penjual ID: `{seller_id}`**\n"
            f"└ Ditambahkan pada: `{added_at}`\n\n"
        )

    await resp.edit(msg, disable_web_page_preview=True)
