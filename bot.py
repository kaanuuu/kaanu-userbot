import asyncio
import random
import re
from datetime import datetime, timedelta
from telethon import TelegramClient, events, functions, types
from telethon.tl.types import Message
import json
import os

# Configuration
API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
OWNER_ID = int(os.environ.get('OWNER_ID', 8740604188))
PHONE = os.environ.get('PHONE', '')

# Bot instance
bot = TelegramClient('userbot', API_ID, API_HASH)

# Data storage
data_file = 'data.json'
if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        data = json.load(f)
else:
    data = {
        'messages': [],
        'auto_reply': {},
        'auto_delete': {},
        'raids': {},
        'muted': [],
        'banned': []
    }

def save_data():
    with open(data_file, 'w') as f:
        json.dump(data, f)

# Helper functions
async def is_owner(event):
    return event.sender_id == OWNER_ID

async def is_admin(event):
    try:
        sender = await event.get_sender()
        chat = await event.get_chat()
        if chat.is_group:
            permissions = await bot.get_permissions(chat, sender)
            return permissions.is_admin
    except:
        pass
    return False

# Command handlers
@bot.on(events.NewMessage(pattern=r'\.alive$'))
async def alive(event):
    await event.reply(f"""🤖 **KaAnU UserBot** 
✅ **Status:** Alive & Working
⚡ **Latency:** {round(bot.latency * 1000)}ms
👑 **Owner:** ᴋᴀᴀɴᴜ
💻 **Uptime:** Active
━━━━━━━━━━━━━━
ᴍᴀᴅᴇ ʙʏ ᴋᴀᴀɴᴜ""")

@bot.on(events.NewMessage(pattern=r'\.ping$'))
async def ping(event):
    start = datetime.now()
    await event.reply('🏓 Pong!')
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await event.reply(f'🏓 **Pong!** `{ms:.2f}ms`')

@bot.on(events.NewMessage(pattern=r'\.help$'))
async def help_cmd(event):
    help_text = """
**🤖 KaAnU UserBot Commands**

**📌 General:**
.alive - Show bot status
.ping - Check latency
.help - Show this help

**📝 Message Management:**
.add <msg> - Add a message (Owner only)
.addlist - Show all messages (Owner only)
.radd <num> - Delete message by number (Owner only)

**🔄 Auto Reply:**
.rr on - Enable auto reply
.rr off - Disable auto reply

**🛡️ Moderation:**
.del_msg (reply) - Delete user's messages (Admin)
.clear (reply) - Clear all messages
.ban @user - Ban user
.mute @user - Mute user

**⚔️ Raid:**
.raid @user/reply <count> - Raid user (max 1000)

**⏰ Auto Delete:**
.delmsg <seconds> - Auto delete messages
.rdelmsg - Stop auto delete

━━━━━━━━━━━━━━
ᴍᴀᴅᴇ ʙʏ ᴋᴀᴀɴᴜ
"""
    await event.reply(help_text)

@bot.on(events.NewMessage(pattern=r'\.add (.+)'))
async def add_message(event):
    if not await is_owner(event):
        return
    msg = event.pattern_match.group(1)
    data['messages'].append(msg)
    save_data()
    await event.reply(f"✅ Message added! (ID: {len(data['messages'])-1})")

@bot.on(events.NewMessage(pattern=r'\.addlist$'))
async def list_messages(event):
    if not await is_owner(event):
        return
    if not data['messages']:
        await event.reply("❌ No messages added yet!")
        return
    msg_list = "\n".join([f"{i}. {msg}" for i, msg in enumerate(data['messages'])])
    await event.reply(f"**📋 Saved Messages:**\n\n{msg_list}")

@bot.on(events.NewMessage(pattern=r'\.radd (\d+)'))
async def remove_message(event):
    if not await is_owner(event):
        return
    index = int(event.pattern_match.group(1))
    if 0 <= index < len(data['messages']):
        removed = data['messages'].pop(index)
        save_data()
        await event.reply(f"✅ Removed: `{removed}`")
    else:
        await event.reply("❌ Invalid message ID!")

@bot.on(events.NewMessage(pattern=r'\.rr (on|off)'))
async def auto_reply_toggle(event):
    if not await is_owner(event):
        return
    chat_id = event.chat_id
    status = event.pattern_match.group(1)
    if status == 'on':
        data['auto_reply'][str(chat_id)] = True
        await event.reply("✅ Auto-reply **enabled** for this chat!")
    else:
        data['auto_reply'][str(chat_id)] = False
        await event.reply("❌ Auto-reply **disabled** for this chat!")
    save_data()

@bot.on(events.NewMessage)
async def auto_reply_handler(event):
    if event.is_private or event.is_group:
        chat_id = str(event.chat_id)
        if data['auto_reply'].get(chat_id, False) and data['messages']:
            if not event.out and event.sender_id != OWNER_ID:
                msg = random.choice(data['messages'])
                await asyncio.sleep(random.uniform(1, 3))
                await event.reply(msg)

@bot.on(events.NewMessage(pattern=r'\.del_msg'))
async def delete_user_msgs(event):
    if not await is_admin(event):
        await event.reply("❌ You need to be an admin to use this!")
        return
    reply = await event.get_reply_message()
    if not reply:
        await event.reply("❌ Reply to a user's message!")
        return
    user_id = reply.sender_id
    chat_id = event.chat_id
    
    try:
        async for msg in bot.iter_messages(chat_id, from_user=user_id):
            await msg.delete()
            await asyncio.sleep(0.5)
        await event.reply(f"✅ Deleted all messages from user!")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

@bot.on(events.NewMessage(pattern=r'\.clear'))
async def clear_messages(event):
    if not await is_admin(event):
        await event.reply("❌ You need to be an admin!")
        return
    reply = await event.get_reply_message()
    if not reply:
        await event.reply("❌ Reply to a message to clear from!")
        return
    
    try:
        async for msg in bot.iter_messages(event.chat_id, offset_id=reply.id):
            await msg.delete()
            await asyncio.sleep(0.3)
        await event.reply("✅ Chat cleared!")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

@bot.on(events.NewMessage(pattern=r'\.ban'))
async def ban_user(event):
    if not await is_admin(event):
        await event.reply("❌ You need to be an admin!")
        return
    args = event.message.text.split()
    if len(args) < 2:
        await event.reply("❌ Usage: .ban @user")
        return
    try:
        user = await bot.get_entity(args[1])
        await bot(functions.channels.EditBannedRequest(
            channel=event.chat_id,
            participant=user,
            banned_rights=types.ChatBannedRights(
                until_date=None,
                view_messages=True
            )
        ))
        await event.reply(f"✅ User {user.first_name} banned!")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

@bot.on(events.NewMessage(pattern=r'\.mute'))
async def mute_user(event):
    if not await is_admin(event):
        await event.reply("❌ You need to be an admin!")
        return
    args = event.message.text.split()
    if len(args) < 2:
        await event.reply("❌ Usage: .mute @user")
        return
    try:
        user = await bot.get_entity(args[1])
        await bot(functions.channels.EditBannedRequest(
            channel=event.chat_id,
            participant=user,
            banned_rights=types.ChatBannedRights(
                until_date=datetime.now() + timedelta(days=30),
                send_messages=True
            )
        ))
        await event.reply(f"✅ User {user.first_name} muted for 30 days!")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

@bot.on(events.NewMessage(pattern=r'\.raid (@\w+|reply) (\d+)'))
async def raid_user(event):
    if not await is_owner(event):
        return
    args = event.message.text.split()
    count = int(args[-1])
    if count > 1000:
        await event.reply("❌ Maximum limit is 1000!")
        return
    
    target = None
    if args[1] == 'reply':
        reply = await event.get_reply_message()
        if reply:
            target = reply.sender_id
    else:
        try:
            user = await bot.get_entity(args[1])
            target = user.id
        except:
            pass
    
    if not target:
        await event.reply("❌ User not found!")
        return
    
    if not data['messages']:
        await event.reply("❌ No messages in database! Add some with .add")
        return
    
    await event.reply(f"🔥 Starting raid on user with {count} messages...")
    for i in range(min(count, 1000)):
        msg = random.choice(data['messages'])
        try:
            await bot.send_message(event.chat_id, msg)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            if (i+1) % 50 == 0:
                await event.reply(f"✅ {i+1} messages sent...")
        except:
            break
    await event.reply("✅ Raid completed!")

@bot.on(events.NewMessage(pattern=r'\.delmsg (\d+)'))
async def auto_delete_msgs(event):
    if not await is_owner(event):
        return
    seconds = int(event.pattern_match.group(1))
    chat_id = str(event.chat_id)
    data['auto_delete'][chat_id] = {
        'active': True,
        'seconds': seconds,
        'start_time': datetime.now().isoformat()
    }
    save_data()
    await event.reply(f"✅ Auto-delete enabled! Messages will be deleted after {seconds} seconds.")

@bot.on(events.NewMessage(pattern=r'\.rdelmsg'))
async def remove_auto_delete(event):
    if not await is_owner(event):
        return
    chat_id = str(event.chat_id)
    if chat_id in data['auto_delete']:
        del data['auto_delete'][chat_id]
        save_data()
        await event.reply("✅ Auto-delete disabled!")
    else:
        await event.reply("❌ Auto-delete not active!")

# Auto delete background task
async def auto_delete_task():
    while True:
        await asyncio.sleep(10)
        for chat_id, settings in list(data['auto_delete'].items()):
            if settings['active']:
                try:
                    chat = await bot.get_entity(int(chat_id))
                    async for msg in bot.iter_messages(chat, limit=10):
                        if msg.date < datetime.now() - timedelta(seconds=settings['seconds']):
                            await msg.delete()
                except:
                    pass

# Start bot
async def main():
    await bot.start(phone=PHONE)
    print("🤖 UserBot Started Successfully!")
    print(f"👑 Owner: {OWNER_ID}")
    print(f"📊 Messages loaded: {len(data['messages'])}")
    asyncio.create_task(auto_delete_task())
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
