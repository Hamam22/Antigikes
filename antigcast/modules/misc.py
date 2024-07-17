import os

from antigcast import Bot
from pyrogram import enums

import os, requests, asyncio, math, time, wget
from pyrogram import filters, Client
from pyrogram.types import Message

from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

from datetime import datetime
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
    from_user_id = message.from_user.id
    username = message.from_user.username  # Opsional, tergantung kebutuhan Anda
    return from_user_id, username

# Perintah untuk menampilkan informasi ID pengguna atau obrolan
@Bot.on_message(filters.command('id'))
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
        _id = ""
        _id += f"➲ ID Obrolan: {message.chat.id}\n"
        
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
            _id += (
                f"➲ ID Pengguna: {from_user_id}\n"
            )
            file_info = get_file_id(message)
        if file_info:
            _id += (
                f"{file_info['message_type']}: {file_info['file_id']}\n"
            )
        await message.reply_text(_id, quote=True)

# Perintah untuk menampilkan informasi pengguna
@Bot.on_message(filters.command(["info"]))
async def user_info(client, message):
    status_message = await message.reply_text("`Mohon tunggu....`")
    from_user = None
    from_user_id, _ = extract_user(message)
    try:
        from_user = await client.get_users(from_user_id)
    except Exception as error:
        return await status_message.edit(str(error))
    if from_user is None:
        return await status_message.edit("ID pengguna tidak valid atau pesan tidak spesifik")
    message_out_str = ""
    message_out_str += f"➲ Nama Depan: {from_user.first_name}\n"
    last_name = from_user.last_name or "Tidak ada"
    message_out_str += f"➲ Nama Belakang: {last_name}\n"
    message_out_str += f"➲ ID Telegram: {from_user.id}\n"
    username = from_user.username or "Tidak ada"
    dc_id = from_user.dc_id or "[Pengguna tidak memiliki DP yang valid]"
    message_out_str += f"➲ ID DC: {dc_id}\n"
    message_out_str += f"➲ Username: @{username}\n"
    message_out_str += f"➲ Tautan Pengguna: [Klik di sini](tg://user?id={from_user.id})\n"
    if message.chat.type in ((enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL)):
        try:
            chat_member_p = await message.chat.get_member(from_user.id)
            joined_date = (chat_member_p.joined_date or datetime.now()).strftime("%Y.%m.%d %H:%M:%S")
            message_out_str += f"➲ Bergabung dalam obrolan ini pada: {joined_date}\n"
        except UserNotParticipant:
            pass
    chat_photo = from_user.photo
    if chat_photo:
        local_user_photo = await client.download_media(message=chat_photo.big_file_id)
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

@Bot.on_message(filters.command(['song', 'mp3']) & filters.group, group=46)
async def song(client, message):
    user_id = message.from_user.id 
    user_name = message.from_user.first_name 
    rpk = "["+user_name+"](tg://user?id="+str(user_id)+")"
    query = ' '.join(message.command[1:])
    
    m = await message.reply(f"**Mencari lagumu...!\n {query}**")
    
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]       
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f'thumb{title}.jpg'
        
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
        
        performer = f"[Mᴋɴ Bᴏᴛᴢ™]" 
        duration = results[0]["duration"]
        
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

    except Exception as e:
        print(str(e))
        return await m.edit("**Tidak ditemukan. Silakan periksa ejaan atau coba link lain.**")
                
    try:
        cap = "**BY›› [Mᴋɴ Bᴏᴛᴢ™](https://t.me/mkn_bots_updates)**"
        
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        
        await message.reply_audio(
            audio_file,
            caption=cap,            
            quote=False,
            title=title,
            duration=dur,
            performer=performer,
            thumb=thumb_name
        )            
        await m.delete()
        
    except Exception as e:
        await m.edit("**🚫 Kesalahan 🚫**")
        print(e)
    
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)
        
def get_text(message: Message) -> [None, str]:
    text_to_return = message.text
    if message.text is None:
        return None
    if " " not in text_to_return:
        return None
    try:
        return message.text.split(None, 1)[1]
    except IndexError:
        return None

@Bot.on_message(filters.command(["video", "mp4"]) & filters.group, group=65)
async def vsong(client, message: Message):
    urlissed = get_text(message)
    pablo = await client.send_message(message.chat.id, f"**Mencari video** `{urlissed}`")
    if not urlissed:
        return await pablo.edit("Syntax command tidak valid. Silakan cek menu bantuan untuk informasi lebih lanjut!")     
    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)
    except Exception as e:
        return await pablo.edit_text(f"**Unduhan gagal. Silakan coba lagi..♥️** \n**Kesalahan :** `{str(e)}`")       
    
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"""**JUDUL :** [{thum}]({mo})\n**DIMINTA OLEH :** {message.from_user.mention}"""

    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,        
        reply_to_message_id=message.id 
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)
