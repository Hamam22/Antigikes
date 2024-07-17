from antigcast import Bot
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageDeleteForbidden, PeerIdInvalid, UserNotParticipant
import asyncio

from antigcast.helpers.admins import *
from antigcast.helpers.tools import extract
from antigcast.helpers.database import *

# Other handlers ...

@Bot.on_message(filters.group & ~filters.private, group=54)
async def delete_muted_messages(app: Bot, message: Message):
    if message.from_user is None:
        return

    user_id = message.from_user.id
    username = message.from_user.username
    name = (message.from_user.first_name or "") + (
        " " + message.from_user.last_name if message.from_user.last_name else ""
    )
    group_id = message.chat.id
    group_name = message.chat.title

    muted_users = await get_muted_users_in_group(group_id)
    if any(u['user_id'] == user_id for u in muted_users):
        print(f"Pesan dari pengguna yang di-mute: {user_id} ({username}) di grup {group_name} ({group_id})")
        try:
            await message.delete()
            print(f"Pesan dari pengguna yang di-mute {user_id} ({username}) di grup {group_name} ({group_id}) berhasil dihapus")
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.delete()
            print(f"Pesan dari pengguna yang di-mute {user_id} ({username}) di grup {group_name} ({group_id}) berhasil dihapus setelah menunggu {e.value} detik")
        except MessageDeleteForbidden:
            print(f"Tidak dapat menghapus pesan dari pengguna yang di-mute: {user_id} ({username}) di grup {group_name} ({group_id}). Pastikan bot memiliki izin untuk menghapus pesan.")
        except Exception as e:
            print(f"Gagal menghapus pesan dari pengguna yang di-mute {user_id} ({username}) di grup {group_name} ({group_id}): {e}")

print("Handler untuk delete_muted_messages sudah diinisialisasi")
