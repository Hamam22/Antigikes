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
    try:
        seller = await sellers_collection.find_one({"_id": user_id})
        return seller is not None
    except Exception as e:
        print(f"Error checking seller: {e}")
        return False
        
# Handler perintah /addgc untuk menambah izin grup dengan durasi default 30 hari
@Bot.on_message(filters.command("addgc") & filters.user(OWNER_ID))
async def addgcmessag(app: Bot, message: Message):
    # Memeriksa izin penjual sebelum menjalankan perintah
    if not await is_seller(message.from_user.id):
        return await message.reply("Anda tidak diizinkan untuk menggunakan perintah ini.")
    
    chat_id = message.chat.id
    chat_name = message.chat.title
    hari = get_arg(message)
    if not hari:
        hari = "30"
    xxnx = await message.reply(f"`Menambahkan izin dalam grup ini...`")
    now = datetime.now(timezone("Asia/Jakarta"))
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

# Handler perintah /add untuk menambah izin grup dengan durasi yang ditentukan
@Bot.on_message(filters.command("add") & filters.user(OWNER_ID))
async def addgroupmessag(app: Bot, message: Message):
    # Memeriksa izin penjual sebelum menjalankan perintah
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
    
    now = datetime.now(timezone("Asia/Jakarta"))
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

# Handler perintah /rmgc untuk menghapus izin grup
@Bot.on_message(filters.command("rmgc") & filters.user(OWNER_ID))
async def remgcmessag(app: Bot, message: Message):
    # Memeriksa izin penjual sebelum menjalankan perintah
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

# Handler perintah /groups untuk menampilkan daftar grup yang diizinkan
@Bot.on_message(filters.command("groups") & filters.user(OWNER_ID))
async def get_groupsmessag(app: Bot, message: Message):
    # Memeriksa izin penjual sebelum menjalankan perintah
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
async def addseller_message(app: Bot, message: Message):
    xxnx = await message.reply("`Adding a new seller...`")
    
    if len(message.command) != 2:
        return await xxnx.edit("**Usage**: `/addseller seller_id`")
    
    try:
        seller_id = int(message.command[1])
    except ValueError:
        return await xxnx.edit("Seller ID must be an integer.")
    
    try:
        added = await add_seller(seller_id)
        if added:
            await xxnx.edit(f"**Seller Added**\nSeller ID: `{seller_id}`")
    except Exception as e:
        print(f"Error adding seller: {e}")
        await xxnx.edit("An error occurred while adding the seller.")
    
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()

# Bot command to remove a seller
@Bot.on_message(filters.command("remseller") & filters.user(OWNER_ID))
async def remseller_message(app: Bot, message: Message):
    seller_id = int(message.command[1]) if len(message.command) > 1 else None

    if not seller_id:
        return await message.reply("`Please provide the Seller ID to remove.`")
        
    xxnx = await message.reply("`Removing seller...`")
    try:
        removed = await rem_seller(seller_id)
        if removed:
            await xxnx.edit(f"**Seller with Seller ID `{seller_id}` has been removed.**")
        else:
            await xxnx.edit(f"**Seller with Seller ID `{seller_id}` not found.**")
    except Exception as e:
        print(f"Error removing seller: {e}")
        await xxnx.edit("An error occurred while removing the seller.")
    
    await asyncio.sleep(10)
    await xxnx.delete()
    await message.delete()

# Bot command to list all sellers
@Bot.on_message(filters.command("listsellers") & filters.user(OWNER_ID))
async def listsellers_message(app: Bot, message: Message):
    sellers = await list_sellers()
    if not sellers:
        return await message.reply("**No sellers registered yet.**")

    resp = await message.reply("**Loading database...**")
    msg = f"**List of Sellers**\n\n"
    num = 0

    for seller in sellers:
        seller_id = seller.get('_id')
        added_at = seller.get('added_at', None)
        
        # Convert time to Asia/Jakarta timezone
        if added_at:
            added_at = added_at.astimezone(timezone('Asia/Jakarta')).strftime("%Y-%m-%d %H:%M:%S")
        else:
            added_at = "Unknown"

        num += 1
        msg += (
            f"**{num}. Seller ID: `{seller_id}`**\n"
            f"└ Added at: `{added_at}`\n\n"
        )

    await resp.edit(msg, disable_web_page_preview=True)
