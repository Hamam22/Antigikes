import asyncio

from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message

from antigcast.config import OWNER_ID
from antigcast.helpers.tools import extract
from antigcast.helpers.database import get_muted_users, mute_user, unmute_user, get_actived_chats

@Bot.on_message(filters.command("pl") & filters.user(OWNER_ID))
async def mute_handler(app: Bot, message: Message):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("Berikan saya kata terlarang yang ingin di hapus")
        
    user = await extract(message)
    user_id = user.id

    if user_id == message.from_user.id:
        return await message.reply_text("Kamu tidak bisa melakukan kata terlarang pada diri sendiri")
    elif user_id == app.me.id:
        return await message.reply_text("Kamu tidak bisa melakukan kata terlarang pada Bot")
    elif user_id in OWNER_ID:
        return await message.reply_text("Kamu tidak bisa melakukan Global Delete pada Developer Bot")

    xxnx = await message.reply("`Berhasil memasukan kata terlarang...`")

    muted = await get_muted_users()
    if user_id in muted:
        await xxnx.edit("**Maaf, Pengguna ini sudah ada di daftar kata terlarang**")
        await asyncio.sleep(10)
        await xxnx.delete()
        await message.delete()
        return
    
    try:
        kon = await app.get_users(user_id)
        kon_name = kon.first_name

        await mute_user(user_id)

        await xxnx.edit(f"**Berhasil Masukan kata terlarang**\n- Name: {kon_name}\n- User ID: `{user_id}`")
        await asyncio.sleep(10)
        await xxnx.delete()
        await message.delete()
    except Exception as e:
        await xxnx.edit(f"**Gagal menambahkan kata terlarang:** `{e}`")

@Bot.on_message(filters.command("ungdel") & filters.user(OWNER_ID))
async def unmute_handler(app: Bot, message: Message):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("Berikan saya id/username atau reply ke pesan")
        
    user = await extract(message)
    user_id = user.id

    if user_id == message.from_user.id:
        return await message.reply_text("Kamu tidak bisa melakukan Global Delete pada diri sendiri")
    elif user_id == app.me.id:
        return await message.reply_text("Kamu tidak bisa melakukan Global Delete pada Bot")
    elif user_id in OWNER_ID:
        return await message.reply_text("Kamu tidak bisa melakukan Global Delete pada Developer Bot")
        
    xxnx = await message.reply("`Membuka Global Mute..`")

    muted = await get_muted_users()
    if user_id not in muted:
        await xxnx.edit("**Maaf, Pengguna ini tidak ada di daftar Global Mute**")
        await asyncio.sleep(10)
        await xxnx.delete()
        await message.delete()
        return

    try:
        kon = await app.get_users(user_id)
        kon_name = kon.mention

        await unmute_user(user_id)

        await xxnx.edit(f"**Global Unmute Berhasil**\n- Name: {kon_name}\n- User ID: `{user_id}`")
        await asyncio.sleep(10)
        await xxnx.delete()
        await message.delete()
    except Exception as e:
        await xxnx.edit(f"**Global Unmute Gagal:** `{e}`")

@Bot.on_message(filters.command("gmuted") & filters.user(OWNER_ID))
async def muted(app: Bot, message: Message):
    kons = []
    konlos = await get_actived_chats()
    for user in konlos:
        kons.append(user)
        
    if not kons:
        return await message.reply("**Belum Ada Daftar Gmute.**")
    
    resp = await message.reply("**Memuat database...**")

    msg = "**Daftar Global Mute**\n\n"
    num = 0

    for x in kons:
        num += 1
        try:
            get = await app.get_users(int(x))
            gname = get.mention
            msg += f"**{num}. {gname}**\n└ User ID: `{x}`\n\n"
        except:
            msg += f"**{num}. {x}**\n\n"

    await resp.edit(msg, disable_web_page_preview=True)
