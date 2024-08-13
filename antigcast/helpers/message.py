from pyrogram import filters
from antigcast.helpers.database import *

async def isGcast(filter, client, update):
    # Ambil teks pesan
    message_text = update.text.lower()
    
    # Debug: Print pesan yang diterima
    print(f"Pesan yang diterima: {message_text}")

    # Ambil daftar kata-kata blacklist dari database
    db_blacklist_words = await get_bl_words()

    # Debug: Print kata-kata blacklist dari database
    print(f"Kata-kata blacklist dari database: {db_blacklist_words}")

    # Baca daftar kata dari file 'bl.txt'
    try:
        with open('bl.txt', 'r') as file:
            file_blacklist_words = [w.lower().strip() for w in file.readlines()]
    except FileNotFoundError:
        file_blacklist_words = []
    
    # Debug: Print kata-kata blacklist dari file
    print(f"Kata-kata blacklist dari file: {file_blacklist_words}")

    # Gabungkan daftar blacklist
    all_blacklist_words = set(db_blacklist_words + file_blacklist_words)

    # Debug: Print gabungan daftar blacklist
    print(f"Gabungan daftar blacklist: {all_blacklist_words}")

    # Cek apakah pesan mengandung kata-kata dari blacklist
    if any(word in message_text for word in all_blacklist_words):
        print("Pesan mengandung kata-kata blacklist.")
        return True

    # Cek apakah pengguna sedang dibisukan
    user_id = update.from_user.id
    muted_users = await get_muted_users()

    # Debug: Print daftar pengguna yang dibisukan
    print(f"Pengguna yang dibisukan: {muted_users}")

    if user_id in muted_users:
        return True

    return False

Gcast = filters.create(isGcast)
