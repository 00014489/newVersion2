from aiogram import BaseMiddleware, Bot, exceptions
from aiogram.types import Message, Update
import os
import re
import tgBot.bot_keyboards.inlineKeyboards as kbIn
import data.connection as dataPostgres
import logging
import asyncio


                        
async def forward_message_to_user(bot: Bot, from_chat_id: int, message_id: int, to_chat_id: int):
    try:
        await bot.forward_message(chat_id=to_chat_id, from_chat_id=from_chat_id, message_id=message_id)
        logging.info(f"Message with ID {message_id} forwarded to user {to_chat_id}.")
    except Exception as e:
        logging.error(f"Error forwarding message: {e}")

def format_column_namesForDatabase(input_string: str):
    base_name, extension = os.path.splitext(input_string)
    cleaned_string = re.sub(r'[\'@()\-.]', '', base_name)
    formatted_name = cleaned_string.replace(' ', '_').lower()
    return f"{formatted_name}{extension}"


def normalize_youtube_url(url):
    # Use regex to capture the main URL pattern
    match = re.search(r"(https://www\.youtube\.com/watch\?v=[\w-]+)", url)
    return match.group(1) if match else url

class MessageHandlerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        """
        This method is called automatically for each update.
        """
        # Check if the event is a message
        bot = data.get("bot")
        if event.message:
            message = event.message  # Extract the Message object
            user_id = message.from_user.id
            if user_id < 0:
                await message.reply("This bot in not for groups and channels!")
                return await handler(event, data)
            # username = message.from_user.username
            messageText = message.text
            if messageText and messageText.startswith("/"):
                print("skiping the command")
                return await handler(event, data)
            try:
                if await dataPostgres.check_user_premium(user_id):
                    await main_fun_process(messageText, 600, 25, 10, user_id, message, bot, handler, event, data)
                # elif 
                else:
                    await main_fun_process(messageText, 360, 15, 6, user_id, message, bot, handler, event, data)
            except Exception as e:
                print(f"Error processing message: {e}")
        else:
            # If the event is not a message, simply pass it along
            return await handler(event, data)
        
    async def handle_text_message(self, message: Message):
        """
        Process text messages.
        """
        text = message.text
        # Perform any actions you need with the text, like command handling, etc.
        await message.reply(f"Received your text message: {text}")

async def handle_audio_message(message: Message, file_size_lm: int, file_duration_lm):
    """
    Process audio files sent as audio (music).
    """
    audio = message.audio
    # Download and process the audio file if needed
    print(f"Received audio file: {audio.file_id} - {audio.file_name}")
    # await message.reply("Received your audio file!")

    file_id = message.audio.file_id
    file_name = message.audio.file_name or "Unknown_Song.mp3"
    file_size = message.audio.file_size / (1024 * 1024)  # Convert size to MB
    file_duration = message.audio.duration / 60  # Convert duration to minutes

    # Validation: Check if the file is larger than 15 MB or longer than 6 minutes
    if file_size > file_size_lm:
        await message.reply(f"The song is too big ({file_size:.2f} MB). Please send a song in limits.\n\nLimits: Oridnary users -> Max 15 MB.\nPremium users -> Max 25 MB.")
        return
    if file_duration > file_duration_lm:
        await message.reply(f"The song is too long ({file_duration:.2f} minutes). Please send a song in limits.\n\nLimits: Oridnary users -> Max 6 minutes.\nPremium users -> Max 10 minutes.")
        return

    if not await dataPostgres.check_file_exists(file_id):
        # Get the file name without the extension
        file_name_without_extension = get_file_name_without_extension(file_name)
        logging.info(f"File name {file_name_without_extension}")
        
        # Insert into the database with the file name without the extension
        await dataPostgres.insert_into_input_file(file_id, format_column_namesForDatabase(file_name), file_name_without_extension)

    try:
        await message.reply("Please select the vocal percentage...", reply_markup=await kbIn.percent_choose(file_id))
    except Exception as e:
        logging.error(f"Error processing audio file: {e}", exc_info=True)
        await message.reply(f"Failed to process {file_name} due to an error: {str(e)}")

async def is_message_available(bot: Bot, chat_id: int, message_id: int) -> bool:
    try:
        # Attempt to retrieve the message from the chat
        message = await bot.get_chat(chat_id)
        await bot.get_message(chat_id=chat_id, message_id=message_id)
        return True  # Message is available
    except exceptions.TelegramAPIError:
        # An error indicates the message is not available
        return False
    

def get_file_name_without_extension(file_name: str) -> str:
    # Check if the last 4 characters contain an extension
    if len(file_name) > 4 and file_name[-4] == '.':
        # Return the string without the last 4 characters (extension)
        return file_name[:-4]
    else:
        # No extension, return the string as is
        return file_name    

async def main_fun_process(messageText: str, duration_lm: int, file_size_lm: int, file_duration_lm: int, user_id: int, message: Message, bot: Bot, handler, event, data):
    if messageText is not None and ("youtube.com" in messageText or "youtu.be" in messageText):
        filtred = normalize_youtube_url(messageText.strip())
        pleaseReply = await message.reply("Please wait...")
        # user_id = message.from_user.id
        while(True):
            if await dataPostgres.link_exists(filtred):
                duration = None
                duration = await dataPostgres.get_link_duration(filtred)
                if duration == 0:
                    await asyncio.sleep(5)
                else:
                    logging.info(f"found the duration {duration}")
                    break
            else:
                await dataPostgres.insert_links(filtred, user_id)
                # duration = await get_audio_duration(filtred)
        id = await dataPostgres.get_id_byUrl(filtred)
        await pleaseReply.delete()
        if duration < duration_lm:
            proccesing_messagee = await message.reply("Processing your YouTube audio...")
            

            #checking the file exist on order_list
            if await dataPostgres.check_file_exists_order(id):
                while(True):
                    if await dataPostgres.check_file_exists_order_true(id):
                        await asyncio.sleep(10)
                    else:
                        chat_id, message_id = await dataPostgres.get_link_data(filtred)
                        if message_id == 0:
                            logging.info(f"we are here waiting")
                            await asyncio.sleep(5)
                        else:
                            await forward_message_to_user(bot, chat_id, message_id, user_id)
                            await proccesing_messagee.delete()
                            # await pleaseReply.delete()
                            break
            else:
                await dataPostgres.insert_into_order_list(id)
                await asyncio.sleep(20)
                await proccesing_messagee.delete()
                
            
        else:
                await message.reply("Your link out of limits. \n\nLimits:\nOridinary users -> Max 6 minutesno\nPremium users -> Max 10 minuts.")
        
    elif message.audio:
        # await message.reply("geting a audio")
        await handle_audio_message(message, file_size_lm, file_duration_lm)
    else:
        # print(f"Unhandled message type from {username} (ID: {user_id})")
        await message.reply("Please send aduio of link of youtube")

    # Pass the event to the handler
    return await handler(event, data)
