import asyncio
from pyrogram import filters, Client
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant


STATUS = enums.ChatMemberStatus

async def is_member(filter, client, update):
    try:
        member = await client.get_chat_member(chat_id=update.chat.id, user_id=update.from_user.id)
    except FloodWait as wait_err:
        await asyncio.sleep(wait_err.seconds)
        return False
    except UserNotParticipant:
        return False
    except Exception:
        return False

    return member.status not in [STATUS.CREATOR, STATUS.ADMINISTRATOR]

async def is_admin(filter, client, update):
    try:
        member = await client.get_chat_member(chat_id=update.chat.id, user_id=update.from_user.id)
    except FloodWait as wait_err:
        await asyncio.sleep(wait_err.seconds)
        return False
    except UserNotParticipant:
        return False
    except Exception:
        return False

    return member.status in [STATUS.CREATOR, STATUS.ADMINISTRATOR]

MemberFilter = filters.create(is_member)
AdminFilter = filters.create(is_admin)
