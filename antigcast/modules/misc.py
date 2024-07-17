import os

from antigcast import Bot

import os, requests, asyncio, math, time, wget
from pyrogram import filters, Client
from pyrogram.types import Message

from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL


@Bot.on_message(filters.command('id'))
async def showid(client, message):
    chat_type = message.chat.type
    replied_to_msg = message.reply_to_message
    if replied_to_msg:
        return await message.reply_text(f"""The forwarded message channel {replied_to_msg.chat.title}'s id is, <code>{replied_to_msg.chat.id}</code>.""")
    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text(f'★ User ID: <code>{message.from_user.id}</code>')

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply_text(f'★ Group ID: <code>{message.chat.id}</code>')

    elif chat_type == enums.ChatType.CHANNEL:
        await message.reply_text(f'★ Channel ID: <code>{message.chat.id}</code>')


@Bot.on_message(filters.command(['song', 'mp3']) & filters.group)
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

@Bot.on_message(filters.command(["video", "mp4"]) & filters.group)
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
