from pyrogram import filters
from antigcast.helpers.database import *

async def isGcast(filter, client, update):
    message_text = update.text.lower()  # Ambil teks pesan dan ubah ke huruf kecil

    # Ambil daftar kata-kata blacklist
    blacklist_words = await get_bl_words()

    # Baca daftar kata dari file 'bl.txt'
    with open('bl.txt', 'r') as file:
        blacklist_file_words = [w.lower().strip() for w in file.readlines()]

    # Gabungkan daftar blacklist
    blacklist_words.extend(blacklist_file_words)

    # Cek apakah pesan mengandung kata dari blacklist
    if any(word in message_text for word in blacklist_words):
        return True

    # Cek apakah pengguna sedang dibisukan
    user_id = update.from_user.id
    muted_users = await get_muted_users()

    if user_id in muted_users:
        return True

    return False

Gcast = filters.create(isGcast)
