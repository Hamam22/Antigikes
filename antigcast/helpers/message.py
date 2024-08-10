from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
from config import Bot

async def isGcast(client, message):
    # Membaca kata-kata terlarang dari bl.txt
    with open('bl.txt', 'r') as file:
        bl_words = [line.strip().lower() for line in file.readlines()]
    
    # Membaca teks pesan dan mengubahnya menjadi huruf kecil
    message_text = message.text.lower()
    
    # Memeriksa apakah teks pesan mengandung kata-kata terlarang
    for word in bl_words:
        if word in message_text:
            return True
    
    return False

@Bot.on_message(filters.text)
async def handle_message(client, message: Message):
    if await isGcast(client, message):
        try:
            await message.delete()
        except Exception as e:
            print(f"Error deleting message: {e}")

