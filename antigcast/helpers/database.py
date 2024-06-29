import datetime
from pytz import timezone
from antigcast.config import MONGO_DB_URI, DB_NAME
from motor.motor_asyncio import AsyncIOMotorClient

# Koneksi ke MongoDB
mongo_client = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo_client[DB_NAME]

# Koleksi yang digunakan
userdb = db['USERS']
serchat = db['SERVEDCHATS']
actchat = db['ACTIVEDCHATS']
blackword = db['BLACKWORDS']
owner = db['OWNERS']
exp = db['EXP']
globaldb = db['GLOBALMUTE']
mute_collection = db['GROUPMUTE']
sellers_collection = db['ADDSELLER']
impdb = db['PRETENDER']

# USERS
def new_user(id):
    return dict(
        id=id,
        join_date=datetime.date.today().isoformat(),
        ban_status=dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        ),
    )

async def add_user(id):
    user = new_user(id)
    await userdb.insert_one(user)

async def is_user_exist(id):
    user = await userdb.find_one({"id": int(id)})
    return bool(user)

async def total_users_count():
    count = await userdb.count_documents({})
    return count

async def get_all_users():
    return userdb.find({})

async def delete_user(user_id):
    await userdb.delete_many({"id": int(user_id)})

async def remove_ban(id):
    ban_status = dict(
        is_banned=False,
        ban_duration=0,
        banned_on=datetime.date.max.isoformat(),
        ban_reason="",
    )
    await userdb.update_one({"id": id}, {"$set": {"ban_status": ban_status}})

async def ban_user(user_id, ban_duration, ban_reason):
    ban_status = dict(
        is_banned=True,
        ban_duration=ban_duration,
        banned_on=datetime.date.today().isoformat(),
        ban_reason=ban_reason,
    )
    await userdb.update_one({"id": user_id}, {"$set": {"ban_status": ban_status}})

async def get_ban_status(id):
    default = dict(
        is_banned=False,
        ban_duration=0,
        banned_on=datetime.date.max.isoformat(),
        ban_reason="",
    )
    user = await userdb.find_one({"id": int(id)})
    return user.get("ban_status", default)

async def get_all_banned_users():
    return userdb.find({"ban_status.is_banned": True})

# SERVED_CHATS
async def get_served_chats() -> list:
    servedchats = await serchat.find_one({"servedchat": "servedchat"})
    if not servedchats:
        return []
    return servedchats["servedchats"]

async def add_served_chat(trigger) -> bool:
    servedchats = await get_served_chats()
    servedchats.append(trigger)
    await serchat.update_one({"servedchat": "servedchat"}, {"$set": {"servedchats": servedchats}}, upsert=True)
    return True

async def rem_served_chat(trigger) -> bool:
    servedchats = await get_served_chats()
    servedchats.remove(trigger)
    await serchat.update_one({"servedchat": "servedchat"}, {"$set": {"servedchats": servedchats}}, upsert=True)
    return True

# ACTIVED_CHATS
async def get_actived_chats() -> list:
    activedchats = await actchat.find_one({"activedchat": "activedchat"})
    if not activedchats:
        return []
    return activedchats["activedchats"]

async def add_actived_chat(trigger) -> bool:
    activedchats = await get_actived_chats()
    activedchats.append(trigger)
    await actchat.update_one({"activedchat": "activedchat"}, {"$set": {"activedchats": activedchats}}, upsert=True)
    return True

async def rem_actived_chat(trigger) -> bool:
    activedchats = await get_actived_chats()
    if trigger in activedchats:
        activedchats.remove(trigger)
        await actchat.update_one({"activedchat": "activedchat"}, {"$set": {"activedchats": activedchats}}, upsert=True)
        return True
    else:
        return False

# BLACKLIST_WORD
async def get_bl_words() -> list:
    filters = await blackword.find_one({"filter": "filter"})
    if not filters:
        return []
    return filters["filters"]

async def add_bl_word(trigger) -> bool:
    x = trigger.lower()
    filters = await get_bl_words()
    filters.append(x)
    await blackword.update_one({"filter": "filter"}, {"$set": {"filters": filters}}, upsert=True)
    return True

async def remove_bl_word(trigger) -> bool:
    x = trigger.lower()
    filters = await get_bl_words()
    filters.remove(x)
    await blackword.update_one({"filter": "filter"}, {"$set": {"filters": filters}}, upsert=True)
    return True

# OWNER
async def get_owners() -> list:
    owners = await owner.find_one({"owner": "owner"})
    if not owners:
        return []
    return owners["owners"]

async def add_owner(trigger) -> bool:
    owners = await get_owners()
    owners.append(trigger)
    await owner.update_one({"owner": "owner"}, {"$set": {"owners": owners}}, upsert=True)
    return True

async def remove_owner(trigger) -> bool:
    owners = await get_owners()
    owners.remove(trigger)
    await owner.update_one({"owner": "owner"}, {"$set": {"owners": owners}}, upsert=True)
    return True

# EXPIRED DATE
async def get_expired_date(chat_id):
    group = await exp.find_one({'_id': chat_id})
    if group:
        return group.get('expire_date')
    else:
        return None

async def rem_expired_date(chat_id):
    await exp.update_one({"_id": chat_id}, {"$unset": {"expire_date": ""}}, upsert=True)

async def rem_expired(chat_id):
    await exp.delete_one({"_id": chat_id})

async def remove_expired():
    async for group in exp.find({"expire_date": {"$lt": datetime.datetime.now()}}):
        await rem_expired(group["_id"])
        await rem_actived_chat(group["_id"])
        gc = group["_id"]
        exptext = f"Masa Aktif {gc} Telah Habis dan telah dihapus dari database."
        print(exptext)

async def set_expired_date(chat_id, expire_date):
    await exp.update_one({'_id': chat_id}, {'$set': {'expire_date': expire_date}}, upsert=True)

# GLOBAL DELETE
async def get_muted_users() -> list:
    mutedusers = await globaldb.find_one({"muteduser": "muteduser"})
    if not mutedusers:
        return []
    return mutedusers["mutedusers"]

async def mute_user(uid_id) -> bool:
    mutedusers = await get_muted_users()
    mutedusers.append(uid_id)
    await globaldb.update_one({"muteduser": "muteduser"}, {"$set": {"mutedusers": mutedusers}}, upsert=True)
    return True

async def unmute_user(uid_id) -> bool:
    mutedusers = await get_muted_users()
    mutedusers.remove(uid_id)
    await globaldb.update_one({"muteduser": "muteduser"}, {"$set": {"mutedusers": mutedusers}}, upsert=True)
    return True

# GROUP MUTE
async def get_user_name(user_id, app):
    try:
        user = await app.get_users(user_id)
        return user.first_name
    except Exception:
        return "unknown"

async def get_muted_users_in_group(group_id, app):
    doc = await mute_collection.find_one({'group_id': group_id})
    if doc and 'user_data' in doc:
        if isinstance(doc['user_data'], list):
            user_data_dict = {}
            for item in doc['user_data']:
                user_id = item['user_id']
                admin_id = item['admin_id']
                user_name = await get_user_name(user_id, app)
                admin_name = await get_user_name(admin_id, app)
                user_data_dict[str(user_id)] = {
                    'name': user_name,
                    'muted_by': {
                        'id': admin_id,
                        'name': admin_name
                    }
                }
            await mute_collection.update_one(
                {'group_id': group_id},
                {'$set': {'user_data': user_data_dict}}
            )
            return user_data_dict
        return doc['user_data']
    return {}

async def mute_user_in_group(group_id, user_id, user_name, issuer_id, issuer_name):
    await mute_collection.update_one(
        {'group_id': group_id},
        {
            '$set': {
                f'user_data.{user_id}': {
                    'name': user_name,
                    'muted_by': {
                        'id': issuer_id,
                        'name': issuer_name
                    }
                }
            }
        },
        upsert=True
    )

async def unmute_user_in_group(group_id, user_id):
    await mute_collection.update_one(
        {'group_id': group_id},
    {'$unset': {f'user_data.{user_id}': ""}},
    upsert=True
    )

# SELLER
async def add_seller(user_id):
    await sellers_collection.update_one(
        {'seller': 'seller'},
        {'$addToSet': {'sellers': user_id}},
        upsert=True
    )

async def remove_seller(user_id):
    await sellers_collection.update_one(
        {'seller': 'seller'},
        {'$pull': {'sellers': user_id}},
        upsert=True
    )

async def get_sellers():
    doc = await sellers_collection.find_one({'seller': 'seller'})
    if doc:
        return doc.get('sellers', [])
    return []

# PRETENDER
async def get_pretender(chat_id):
    return await impdb.find_one({'chat_id': chat_id})

async def add_pretender(chat_id, user_id, user_name, timestamp):
    await impdb.update_one(
        {'chat_id': chat_id},
        {'$set': {
            'user_id': user_id,
            'user_name': user_name,
            'timestamp': timestamp
        }},
        upsert=True
    )

async def remove_pretender(chat_id):
    await impdb.delete_one({'chat_id': chat_id})

# MAIN FUNCTION TO RUN PERIODIC TASKS
async def periodic_task():
    await remove_expired()

# This function is to schedule the periodic task using `schedule`
def start_scheduler():
    import asyncio
    import schedule
    import time

    loop = asyncio.get_event_loop()

    schedule.every().day.at("00:00").do(lambda: loop.create_task(periodic_task()))

    while True:
        schedule.run_pending()
        time.sleep(1)
