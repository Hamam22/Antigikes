import time
import os
import asyncio
import requests
import wget
import yt_dlp
from youtubesearchpython import SearchVideos
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import *
from antigcast import Bot

# Fungsi untuk mendownload lagu dari YouTube
@Bot.on_message(filters.command("audio"))
async def download_song(client, message):
    query = " ".join(message.command[1:])
    print(query)
    m = await message.reply("**🔄 Sedang mencari...**")

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await m.edit("**⚠️ Tidak ada hasil ditemukan. Pastikan nama lagu yang Anda ketik benar.**")
            print("Tidak ada hasil ditemukan")
            return

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        views = results[0]["views"]
        channel_name = results[0]["channel"]

    except Exception as e:
        await m.edit("**⚠️ Tidak ada hasil ditemukan. Pastikan nama lagu yang Anda ketik benar.**")
        print(f"Error: {str(e)}")
        return

    await m.edit("**📥 Sedang mendownload...**")

    try:
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        # Hitung durasi dalam detik
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(float(dur_arr[i])) * secmul
            secmul *= 60

        await m.edit("**📤 Sedang mengunggah...**")

        # Kirim file audio
        await message.reply_audio(
            audio_file,
            thumb=thumb_name,
            title=title,
            caption=f"{title}\nDipesan oleh: {message.from_user.mention}\nViews: {views}\nChannel: {channel_name}",
            duration=dur
        )

        await m.delete()

    except Exception as e:
        await m.edit("**- Terjadi kesalahan! Mohon coba lagi nanti.**")
        print(f"Error: {str(e)}")

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(f"Error: {str(e)}")

# Fungsi untuk mendownload video dari YouTube
@Bot.on_message(filters.command(["yt", "video"]))
async def ytmusic(client, message: Message):
    urlissed = " ".join(message.command[1:])
    await message.delete()
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chutiya = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    pablo = await client.send_message(message.chat.id, f"**Sedang mencari, mohon tunggu...**")
    if not urlissed:
        await pablo.edit(
            "**😴 Lagu tidak ditemukan di YouTube.**\n\n» Mungkin Anda salah mengetik, periksa kembali tulisan Anda."
        )
        return

    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    thums = mio[0]["channel"]
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
            infoo = ytdl.extract_info(url, False)
            round(infoo["duration"] / 60)
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception as e:
        await pablo.edit(f"**Gagal mengunduh.** \n**Error:** `{str(e)}`")
        return

    c_time = time.time()
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"❄ **Judul:** [{thum}]({mo})\n💫 **Channel:** {thums}\n✨ **Pencarian:** {urlissed}\n🥀 **Diminta oleh:** {chutiya}"
    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        progress_args=(
            pablo,
            c_time,
            f"**» Mohon tunggu...**\n\n**Mengunggah `{urlissed}` dari server YouTube...💫**",
            file_stark,
        ),
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)
