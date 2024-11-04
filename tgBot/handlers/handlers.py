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

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    userName = message.from_user.username
    # await dataPostgres.insert_user_if_not_exists(user_id, userName)
     # Path to your image
    photo = FSInputFile("./tgBot/images/photo_2024-09-13_10-23-12.jpg")
    await message.answer_photo(
        photo, 
        caption=(
        "Welcome to MinusGolos bot\n\n"
        "Send a audio file and get minus of sended audio file\n\n"
        f"  U can choose for returning the output with 0% vocal or 15% or 50%.\n\n"
        f"      Press 0% if u want to get only the minus of song\n"
        f"      Press 15% if u want to get audio with a little vocal\n"
        f"      Press 50% if you want to get audio with 50% of the vocal sound\n\n\n"
        f"Send a link of file from YouTube and get mp3 file\n\n"
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
    await message.answer("I am working on it")
    # photo = FSInputFile("./deploymentbot/images/help.jpg")
    # Sending an image with text
    # First message with the main instructions and general information
    # await message.answer_photo(
    #     photo,
    #     caption=(
    #         f"Send song and get a minus of song\n\n"
    #         f"0% button - it is button for getting the 0% vocal audio file\n"
    #         f"15% button - it is button for getting the audio with 15% vocal volume for better quality\n"
    #         f"50% button - it is button for getting the audio with 50% vocal volume for better melody\n"
    #         "If u get error that process is too long please try again\n\n"
    #         "Do not forget. Day by day the bot will become more and more faster\n"
    #         "U can check it by practicing ...\n\n"
    #         "If u have technical problems. U can contact admin"
            
    # ))


ADMIN_ID = 1031267509
# forwarding_enabled = False

@router.message(Command("turn_on"))
async def turn_on_forwarding(message: Message):
    """Command to turn on message forwarding (only admin can turn it on)."""
    # global forwarding_enabled
    if message.from_user.id == ADMIN_ID:
        # forwarding_enabled = True
        await message.answer("Message forwarding has been turned ON.")
    # else:
        # await message.answer("You don't have permission to use this command.")


@router.message(Command("turn_off"))
async def turn_off_forwarding(message: Message):
    
    """Command to turn off message forwarding (only admin can turn it off)."""
    # global forwarding_enabled
    if message.from_user.id == ADMIN_ID:
        # forwarding_enabled = False
        await message.answer("Message forwarding has been turned OFF.")
    # else:
        # await message.answer("You don't have permission to use this command.")