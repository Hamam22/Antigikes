import os
import time
import asyncio
import requests
import wget
import yt_dlp
from youtubesearchpython import SearchVideos
from youtube_search import YoutubeSearch
from pyrogram import Client, filters
from pyrogram.types import Message
from antigcast import Bot

# Helper function to search for YouTube videos
def search_youtube(query):
    results = YoutubeSearch(query, max_results=1).to_dict()
    if not results:
        return None
    return results[0]

# Helper function to download thumbnail
def download_thumbnail(url, title):
    thumb_name = f"{title}.jpg"
    thumb = requests.get(url, allow_redirects=True)
    with open(thumb_name, "wb") as thumb_file:
        thumb_file.write(thumb.content)
    return thumb_name

# Helper function to calculate duration in seconds
def calculate_duration(duration):
    secmul, dur, dur_arr = 1, 0, duration.split(":")
    for i in range(len(dur_arr) - 1, -1, -1):
        dur += int(float(dur_arr[i])) * secmul
        secmul *= 60
    return dur

# Function to download audio from YouTube
@Bot.on_message(filters.command("audio"))
async def download_song(client, message):
    query = " ".join(message.command[1:])
    print(query)
    m = await message.reply("**🔄 Sedang mencari...**")

    try:
        result = search_youtube(query)
        if not result:
            await m.edit("**⚠️ Tidak ada hasil ditemukan. Pastikan nama lagu yang Anda ketik benar.**")
            return

        link = f"https://youtube.com{result['url_suffix']}"
        title = result["title"][:40]
        thumbnail = result["thumbnails"][0]
        thumb_name = download_thumbnail(thumbnail, title)
        duration = result["duration"]
        views = result["views"]
        channel_name = result["channel"]

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

        dur = calculate_duration(duration)

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
        return

    finally:
        if 'audio_file' in locals():
            os.remove(audio_file)
        if 'thumb_name' in locals():
            os.remove(thumb_name)

# Function to download video from YouTube
@Bot.on_message(filters.command(["yt", "video"]))
async def ytmusic(client, message: Message):
    query = " ".join(message.command[1:])
    await message.delete()
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    requester = f"[{user_name}](tg://user?id={user_id})"

    m = await client.send_message(message.chat.id, f"**Sedang mencari, mohon tunggu...**")

    if not query:
        await m.edit(
            "**😴 Lagu tidak ditemukan di YouTube.**\n\n» Mungkin Anda salah mengetik, periksa kembali tulisan Anda."
        )
        return

    try:
        search = SearchVideos(query, offset=1, mode="dict", max_results=1)
        mi = search.result()
        mio = mi["search_result"]
        video_link = mio[0]["link"]
        title = mio[0]["title"]
        video_id = mio[0]["id"]
        channel_name = mio[0]["channel"]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        await asyncio.sleep(0.6)
        thumbnail_file = wget.download(thumbnail_url)

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

        with YoutubeDL(opts) as ytdl:
            info_dict = ytdl.extract_info(video_link, download=True)
            video_file = f"{info_dict['id']}.mp4"
        
        caption = (
            f"❄ **Judul:** [{title}]({video_link})\n"
            f"💫 **Channel:** {channel_name}\n"
            f"✨ **Pencarian:** {query}\n"
            f"🥀 **Diminta oleh:** {requester}"
        )

        await client.send_video(
            message.chat.id,
            video=open(video_file, "rb"),
            duration=int(info_dict["duration"]),
            file_name=info_dict["title"],
            thumb=thumbnail_file,
            caption=caption,
            supports_streaming=True,
        )
        await m.delete()

    except Exception as e:
        await m.edit(f"**Gagal mengunduh.** \n**Error:** `{str(e)}`")
        return

    finally:
        if 'thumbnail_file' in locals() and os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)
        if 'video_file' in locals() and os.path.exists(video_file):
            os.remove(video_file)
