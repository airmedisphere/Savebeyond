# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
import time
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser

class batch_temp(object):
    IS_BATCH = {}
    PROGRESS_DATA = {}

async def progress_tracker(client, status_msg_id, chat_id):
    last_update = 0
    while status_msg_id in batch_temp.PROGRESS_DATA:
        current_time = time.time()
        if current_time - last_update >= 2:
            data = batch_temp.PROGRESS_DATA.get(status_msg_id)
            if data:
                try:
                    await client.edit_message_text(chat_id, status_msg_id, f"**{data['status']}:** {data['progress']:.1f}%")
                    last_update = current_time
                except:
                    pass
        await asyncio.sleep(1)

def progress(current, total, status_msg_id, status_type):
    if total > 0:
        batch_temp.PROGRESS_DATA[status_msg_id] = {
            'status': status_type,
            'progress': (current * 100 / total)
        }

# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url = "https://t.me/kingvj01")
    ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_bots')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id,
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>",
        reply_markup=reply_markup,
        reply_to_message_id=message.id
    )
    return

# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"{HELP_TXT}"
    )

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id,
        text="**Batch Successfully Cancelled.**"
    )

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
            return
        try:
            try:
                await TechVJUser.join_chat(message.text)
            except Exception as e:
                await client.send_message(message.chat.id, f"Error : {e}", reply_to_message_id=message.id)
                return
            await client.send_message(message.chat.id, "Chat Joined", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            await client.send_message(message.chat.id, "Chat already Joined", reply_to_message_id=message.id)
        except InviteHashExpired:
            await client.send_message(message.chat.id, "Invalid Link", reply_to_message_id=message.id)
        return

    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")

        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        if LOGIN_SYSTEM == True:
            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                return
            api_id = int(await db.get_api_id(message.from_user.id))
            api_hash = await db.get_api_hash(message.from_user.id)
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
                await acc.connect()
            except:
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
        else:
            if TechVJUser is None:
                await client.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                return
            acc = TechVJUser

        batch_temp.IS_BATCH[message.from_user.id] = False

        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break

            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied:
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try:
                        await handle_private(client, acc, message, username, msgid)
                    except Exception as e:
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            await asyncio.sleep(WAITING_TIME)

        if LOGIN_SYSTEM == True:
            try:
                await acc.disconnect()
            except:
                pass
        batch_temp.IS_BATCH[message.from_user.id] = True

async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty:
        return

    msg_type = get_message_type(msg)
    if not msg_type:
        return

    if CHANNEL_ID:
        try:
            chat = int(CHANNEL_ID)
        except:
            chat = message.chat.id
    else:
        chat = message.chat.id

    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return

    smsg = await client.send_message(message.chat.id, '**Processing...**', reply_to_message_id=message.id)

    asyncio.create_task(progress_tracker(client, smsg.id, message.chat.id))

    caption = msg.caption if msg.caption else None

    try:
        if batch_temp.IS_BATCH.get(message.from_user.id):
            return

        if "Document" == msg_type:
            ph_path = None
            try:
                ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
            except:
                pass

            file = await acc.download_media(msg, progress=progress, progress_args=[smsg.id, "Downloading"])

            if batch_temp.IS_BATCH.get(message.from_user.id):
                if file and os.path.exists(file):
                    os.remove(file)
                if ph_path and os.path.exists(ph_path):
                    os.remove(ph_path)
                return

            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[smsg.id, "Uploading"])

            if ph_path and os.path.exists(ph_path):
                os.remove(ph_path)
            if file and os.path.exists(file):
                os.remove(file)

        elif "Video" == msg_type:
            ph_path = None
            try:
                ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
            except:
                pass

            file = await acc.download_media(msg, progress=progress, progress_args=[smsg.id, "Downloading"])

            if batch_temp.IS_BATCH.get(message.from_user.id):
                if file and os.path.exists(file):
                    os.remove(file)
                if ph_path and os.path.exists(ph_path):
                    os.remove(ph_path)
                return

            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[smsg.id, "Uploading"])

            if ph_path and os.path.exists(ph_path):
                os.remove(ph_path)
            if file and os.path.exists(file):
                os.remove(file)

        elif "Animation" == msg_type:
            file = await acc.download_media(msg, progress=progress, progress_args=[smsg.id, "Downloading"])

            if batch_temp.IS_BATCH.get(message.from_user.id):
                if file and os.path.exists(file):
                    os.remove(file)
                return

            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            if file and os.path.exists(file):
                os.remove(file)

        elif "Sticker" == msg_type:
            file = await acc.download_media(msg, progress=progress, progress_args=[smsg.id, "Downloading"])

            if batch_temp.IS_BATCH.get(message.from_user.id):
                if file and os.path.exists(file):
                    os.remove(file)
                return

            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            if file and os.path.exists(file):
                os.remove(file)

        elif "Voice" == msg_type:
            file = await acc.download_media(msg, progress=progress, progress_args=[smsg.id, "Downloading"])

            if batch_temp.IS_BATCH.get(message.from_user.id):
                if file and os.path.exists(file):
                    os.remove(file)
                return

            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[smsg.id, "Uploading"])
            if file and os.path.exists(file):
                os.remove(file)

        elif "Audio" == msg_type:
            ph_path = None
            try:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
            except:
                pass

            file = await acc.download_media(msg, progress=progress, progress_args=[smsg.id, "Downloading"])

            if batch_temp.IS_BATCH.get(message.from_user.id):
                if file and os.path.exists(file):
                    os.remove(file)
                if ph_path and os.path.exists(ph_path):
                    os.remove(ph_path)
                return

            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[smsg.id, "Uploading"])

            if ph_path and os.path.exists(ph_path):
                os.remove(ph_path)
            if file and os.path.exists(file):
                os.remove(file)

        elif "Photo" == msg_type:
            file = await acc.download_media(msg, progress=progress, progress_args=[smsg.id, "Downloading"])

            if batch_temp.IS_BATCH.get(message.from_user.id):
                if file and os.path.exists(file):
                    os.remove(file)
                return

            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            if file and os.path.exists(file):
                os.remove(file)

    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    finally:
        if smsg.id in batch_temp.PROGRESS_DATA:
            del batch_temp.PROGRESS_DATA[smsg.id]
        try:
            await client.delete_messages(message.chat.id, [smsg.id])
        except:
            pass

def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass

# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01
