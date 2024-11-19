from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
# import data.connection as dataPostgres
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramAPIError
import data.connection as dataPostgres
# import psutil
import tgBot.bot_keyboards.bot_keyboards as kb
import logging
# import gc
from concurrent.futures import ThreadPoolExecutor
# from run import process_audio_file
import re
# import shutil  # For deleting directories and their content
import asyncio
import os




router = Router()


async def forward_message_to_user(bot: Bot, from_chat_id: int, message_id: int, to_chat_id: int):
    try:
        await bot.forward_message(chat_id=to_chat_id, from_chat_id=from_chat_id, message_id=message_id)
        logging.info(f"Message with ID {message_id} forwarded to user {to_chat_id}.")
    except Exception as e:
        logging.error(f"Error forwarding message: {e}")

async def format_column_namesForDatabase(input_string: str) -> str:
    # Check if the input is a valid string
    if not isinstance(input_string, str) or input_string.strip() == "":
        raise ValueError("Input must be a non-empty string.")
    
    # Log the input received
    logging.debug(f"Input string received: {input_string}")

    # Split the input into base name and extension
    base_name, extension = os.path.splitext(input_string)

    # Clean the base name
    cleaned_string = re.sub(r"[\'@()\-.!#$%^&*]", "_", base_name)  # Updated regex to clean unwanted characters
    formatted_name = cleaned_string.replace(" ", "_").lower()

    # Return the formatted name with the original extension
    return f"{formatted_name}{extension}"


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    userName = message.from_user.username
    await dataPostgres.insert_user_if_not_exists(user_id, userName)
     # Path to your image
    photo = FSInputFile("./tgBot/images/photo_2024-09-13_10-23-12.jpg")
    await message.answer_photo(
        photo, 
        caption=(
        "Welcome to MinusGolos bot\n\n"
        "Send a audio file and get minus of sended audio file\n\n"
        f"U can choose for returning the output with 0% vocal or 15% or 50%.\n\n"
        f"Press 0% if u want to get only the minus of song\n"
        f"Press 15% if u want to get audio with a little vocal\n"
        f"Press 50% if you want to get audio with 50% of the vocal sound\n\n\n"
        f"Send a link of video from YouTube and get mp3 file\n\n"
        "Great point, Day by day the bot will become faster"),
        reply_markup=kb.main)
    

@router.message(Command("help"))
async def cmd_help(message: Message):
    photo = FSInputFile("./tgBot/images/help.jpg")
    # Sending an image with text
    # First message with the main instructions and general information
    await message.answer_photo(
        photo,
        caption=(
            f"Send song and get a minus of song\n\n"
            f"0% button - it is button for getting the 0% vocal audio file\n"
            f"15% button - it is button for getting the audio with 15% vocal volume for better quality\n"
            f"50% button - it is button for getting the audio with 50% vocal volume for better melody\n"
            "If u get error that process is too long please try again\n\n"
            "Do not forget. Day by day the bot will become more and more faster\n"
            "U can check it by practicing ...\n\n"
            "If u have technical problems. U can contact admin"
            
    ))


@router.message(Command("Premium"))
async def cmd_help(message: Message):
    await message.answer("Upgrade price for 30 days: $2.\n\nFeatures include:\n- Increased duration up to 10 minutes\n- Increased file size up to 25 MB\n- No advertisements\n\nTo get premium, please contact @haveNoIdeaYet.")




ADMIN_ID = 1031267509
forwarding_enabled = False


@router.message(Command("turn_on"))
async def turn_on_forwarding(message: Message):
    """Command to turn on message forwarding (only admin can turn it on)."""
    global forwarding_enabled
    if message.from_user.id == ADMIN_ID:
        forwarding_enabled = True
        await message.answer("Message forwarding has been turned ON.")
    else:
        await message.answer("You don't have permission to use this command.")

@router.message(Command("turn_off"))
async def turn_off_forwarding(message: Message):
    """Command to turn off message forwarding (only admin can turn it off)."""
    global forwarding_enabled
    if message.from_user.id == ADMIN_ID:
        forwarding_enabled = False
        await message.answer("Message forwarding has been turned OFF.")
    else:
        await message.answer("You don't have permission to use this command.")

async def forward_message_to_users(from_chat_id: int, message_id: int, bot: Bot):
    global forwarding_enabled
    users = await dataPostgres.get_user_ids()
    if not forwarding_enabled or not users:
        print("Message forwarding is disabled or no users to forward to. Skipping...")
        return

    for user_id in users:
        try:
            await bot.forward_message(chat_id=user_id, from_chat_id=from_chat_id, message_id=message_id)
            print(f"Message forwarded to user: {user_id}")
        except TelegramAPIError as e:
            print(f"Failed to forward message to user {user_id}: {e}")
        await asyncio.sleep(0.03)  # 30 milliseconds delay to respect Telegram API limits

@router.message()
async def handle_message_reklama(message: Message):
    """
    Handles incoming messages to the bot and forwards them to a list of users
    only if forwarding is enabled. This function is restricted to the admin.
    """
    global forwarding_enabled

    # Check if the user is the admin
    if message.from_user and message.from_user.id != ADMIN_ID:
        return  # Exit early if the user is not the admin

    # Only forward the message if forwarding is enabled
    if forwarding_enabled:
        await forward_message_to_users(from_chat_id=message.chat.id, message_id=message.message_id, bot=message.bot)
    else:
        await message.answer("Message forwarding is currently disabled.")

@router.callback_query(F.data.startswith("mix_vocals"))
async def handle_playlist_move(callback: CallbackQuery, bot: Bot):
    # Extract playlist name and song_id from the callback data
    _, id_input, vocal_percentage = callback.data.split(":")
    vocal_percentage = int(vocal_percentage)
    file_id = await dataPostgres.get_file_id_by_id(int(id_input))
    chat_id = callback.from_user.id
    processing_message = await callback.message.edit_text("Please wait ...")

    if await dataPostgres.check_file_exists_with_percentage(file_id, vocal_percentage):
        while True:
            if await dataPostgres.check_file_exists_with_percentage(file_id, vocal_percentage, "negative_one"):
                await asyncio.sleep(10)
                logging.info(f"waiting a process")
            else:
                id = await dataPostgres.get_output_id_for_percentage(file_id, vocal_percentage)
                from_chat_id, message_id = await dataPostgres.get_chat_and_message_id_by_id(id, vocal_percentage)
                await forward_message_to_user(bot, from_chat_id, message_id, chat_id)
                break
    else:
        await dataPostgres.update_out_id_by_percent(file_id, -1, vocal_percentage)
        save_directory = f'./inputSongs{vocal_percentage}:{id_input}:{chat_id}'
        os.makedirs(save_directory, exist_ok=True)

        file_name = await dataPostgres.get_name_by_id(file_id)
        # Define the full path where the audio file will be saved
        file_path = os.path.join(save_directory, await format_column_namesForDatabase(file_name))

        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, destination=file_path)

        
    await asyncio.sleep(3)
    await bot.delete_message(chat_id, processing_message.message_id)