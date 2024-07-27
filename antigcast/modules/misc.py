import os
import asyncio
from datetime import datetime
from antigcast import Bot
from pyrogram import enums, filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant

# Fungsi untuk mendapatkan informasi file dari pesan
def get_file_id(message):
    if message.photo:
        return {
            'message_type': 'Foto',
            'file_id': message.photo.file_id
        }
    elif message.document:
        return {
            'message_type': 'Dokumen',
            'file_id': message.document.file_id
        }
    # Tangani jenis file lain atau kembalikan None jika tidak ada file
    return None

# Fungsi untuk mengekstrak ID pengguna dan username dari pesan
def extract_user(message):
    if message.reply_to_message:
        from_user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username
    else:
        from_user_id = message.from_user.id
        username = message.from_user.username
    return from_user_id, username

# Perintah untuk menampilkan informasi ID pengguna atau obrolan
@Bot.on_message("id")
async def show_id(client, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        user_id = message.chat.id
        first = message.from_user.first_name
        last = message.from_user.last_name or ""
        username = message.from_user.username
        dc_id = message.from_user.dc_id or ""
        await message.reply_text(f"➲ Nama Depan: {first}\n➲ Nama Belakang: {last}\n➲ Username: {username}\n➲ ID Telegram: {user_id}\n➲ ID DC: {dc_id}", quote=True)

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        _id = f"➲ ID Obrolan: {message.chat.id}\n"
        
        if message.reply_to_message:
            from_user_id, _ = extract_user(message)
            replied_user_id = message.reply_to_message.from_user.id if message.reply_to_message.from_user else 'Anonymous'
            _id += (
                f"➲ ID Pengguna: {from_user_id}\n"
                f"➲ ID Pengguna yang Dibalas: {replied_user_id}\n"
            )
            file_info = get_file_id(message.reply_to_message)
        else:
            from_user_id, _ = extract_user(message)
            _id += f"➲ ID Pengguna: {from_user_id}\n"
            file_info = get_file_id(message)
        if file_info:
            _id += f"{file_info['message_type']}: {file_info['file_id']}\n"
        await message.reply_text(_id, quote=True)

# Perintah untuk menampilkan informasi pengguna
@Bot.on_message("info")
async def user_info(client, message):
    status_message = await message.reply_text("`Mohon tunggu....`")
    from_user_id, _ = extract_user(message)
    try:
        from_user = await client.get_users(from_user_id)
    except Exception as error:
        return await status_message.edit(str(error))
    
    if from_user is None:
        return await status_message.edit("ID pengguna tidak valid atau pesan tidak spesifik")
    
    message_out_str = f"➲ Nama Depan: {from_user.first_name}\n"
    last_name = from_user.last_name or "Tidak ada"
    message_out_str += f"➲ Nama Belakang: {last_name}\n"
    message_out_str += f"➲ ID Telegram: {from_user.id}\n"
    username = from_user.username or "Tidak ada"
    message_out_str += f"➲ Username: @{username}\n"
    dc_id = from_user.dc_id or "[Pengguna tidak memiliki DP yang valid]"
    message_out_str += f"➲ ID DC: {dc_id}\n"
    message_out_str += f"➲ Tautan Pengguna: [Klik di sini](tg://user?id={from_user.id})\n"
    
    if message.chat.type in (enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL):
        try:
            chat_member_p = await message.chat.get_member(from_user.id)
            joined_date = (chat_member_p.joined_date or datetime.now()).strftime("%Y.%m.%d %H:%M:%S")
            message_out_str += f"➲ Bergabung dalam obrolan ini pada: {joined_date}\n"
        except UserNotParticipant:
            pass
    
    chat_photo = from_user.photo
    if chat_photo:
        local_user_photo = await client.download_media(chat_photo.big_file_id)
        buttons = [[InlineKeyboardButton('Tutup ✘', callback_data='close_data')]]
        await message.reply_photo(
            photo=local_user_photo,
            quote=True,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption=message_out_str,
            disable_notification=True
        )
        os.remove(local_user_photo)
    else:
        buttons = [[InlineKeyboardButton('Tutup ✘', callback_data='close_data')]]
        await message.reply_text(
            text=message_out_str,
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True,
            disable_notification=True
        )
    await status_message.delete()
