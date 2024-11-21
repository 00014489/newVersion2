import logging
import re
import shutil
from aiogram import Bot
from concurrent.futures import ThreadPoolExecutor
import asyncio
import data.connection as dataPostgres
from aiogram.types import Message, FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram.exceptions import TelegramBadRequest
from pathlib import Path


    
# Initialize task_starting as True or False based on your requirements
task_starting = True

async def track_message(message: Message, percentage: int):
    message_id = message.message_id
    chat_id = message.chat.id

    if chat_id:
        return await dataPostgres.insert_chat_and_message_id(chat_id, message_id, percentage)

async def run_task_send(base_dir, bot: Bot):
    global task_starting  # Change this to the new variable name
    while task_starting:  # Update this line to use the new variable name
        logging.info("Running the scheduled task...")
        
        # Check and match input song folders
        await check_and_match_song_folders(base_dir, bot)

        # Sleep for 10 seconds before the next run
        await asyncio.sleep(10)


async def check_and_match_song_folders(base_dir: str, bot: Bot):
    send_songs_pattern = r"^sendSongs(\d+):(\d+):(\d+)$"
    down_folder_pattern = r"^down(\d+)$"
    base_path = Path(base_dir)
    # found_matching_folders = []

    # Use ThreadPoolExecutor for I/O bound directory and file checking
    with ThreadPoolExecutor() as pool:
        folder_list = await asyncio.get_event_loop().run_in_executor(pool, base_path.iterdir)

        for folder in folder_list:
            if folder.is_dir():
                # Handle "sendSongs" folders
                if folder.name.startswith("sendSongs"):
                    match = re.match(send_songs_pattern, folder.name)
                    if match:
                        vocal_percentage, song_id_send, user_id = match.groups()
                        # logging.info(f"found the folder with vocal persentage{vocal_percentage}")
                        logging.info(f"user id is {user_id} in down")

                        # Look for the .mp3 file in the "sendSongs" folder
                        mp3_files = list(folder.glob("*.mp3"))
                        if mp3_files:
                            mp3_file_path_send = mp3_files[0]  # Assuming only one .mp3 file per folder
                            # logging.info(f"audio is located in {mp3_file_path_send}")
                            try:
                                # logging.info(f"startig a sending")
                                # original_filename_ = mp3_file_path_send.name  # Extract the original file name
                                logging.info(f"startig a sending")
                                file_to_sendS = FSInputFile(mp3_file_path_send, filename=mp3_file_path_send.name)
                                sendFile = await bot.send_audio(chat_id=user_id, audio=file_to_sendS)
                                id = await track_message(sendFile, vocal_percentage)
                                logging.info(f"Message ID is {sendFile.message_id}")

                                file_id = await dataPostgres.get_file_id_by_id(song_id_send)
                                await dataPostgres.update_out_id_by_percent(file_id, id, vocal_percentage)
                                await deleting_folder(f"sendSongs{vocal_percentage}:{song_id_send}:{user_id}")

                            except TelegramBadRequest as e:
                                logging.error(f"Failed to send audio for song_id {song_id_send}: {e}")
                                await bot.send_message(chat_id=user_id, text="Please try again.")
                            except Exception as e:
                                logging.error(f"Unexpected error for song_id {song_id_send}: {e}")
                            # found_matching_folders.append((vocal_percentage, song_id, user_id, mp3_file_path, folder))
                        else:
                            logging.warning(f"No .mp3 file found in sendSongs folder: {folder}")

                # Handle "down0" folders
                elif folder.name.startswith("down"):
                    match = re.match(down_folder_pattern, folder.name)
                    if match:
                        song_id = match.group(1)
                        user_id_down = await dataPostgres.get_chat_idBy_id(song_id)
                        logging.info(f"user id is {user_id_down} in down")

                        # Look for the .mp3 file in the "down0" folder
                        mp3_files = list(folder.glob("*.mp3"))
                        if mp3_files:
                            mp3_file_path = mp3_files[0]  # Assuming only one .mp3 file per folder
                            # logging.info(f"audio is located in {mp3_file_path}")
                            try:
                                # await asyncio.sleep(3)
                                # original_filename = mp3_file_path.name  # Extract the original file name
                                logging.info(f"startig a sending")
                                file_to_send = FSInputFile(mp3_file_path, filename=mp3_file_path.name)
                                downFile = await bot.send_audio(chat_id=user_id_down, audio=file_to_send)
                                # downFile = await bot.send_audio(chat_id=user_id_down, audio=FSInputFile(mp3_file_path))
                                # id = await track_message(sendFile, vocal_percentage)
                                # logging.info(f"Message ID is {sendFile.message_id}")
                                await dataPostgres.update_linksYou_message_id(song_id, downFile.message_id)
                                await deleting_folder(f"down{song_id}")
                                # file_id = await dataPostgres.get_file_id_by_id(song_id)
                                # await dataPostgres.update_out_id_by_percent(file_id, id, vocal_percentage)

                            except TelegramBadRequest as e:
                                logging.error(f"Failed to send audio for song_id {song_id}: {e}")
                                await bot.send_message(chat_id=user_id_down, text="Please try again.")
                            except Exception as e:
                                logging.error(f"Unexpected error for song_id {song_id}: {e}")
                            # found_matching_folders.append((None, song_id, None, mp3_file_path, folder))
                        else:
                            logging.warning(f"No .mp3 file found in down0 folder: {folder}")


async def schedule_daily_task():
    """
    Schedule the `check_and_update_premium_status` function to run daily.
    """
    scheduler = AsyncIOScheduler()
    # Schedule the function to run daily at 10:00 AM
    trigger = CronTrigger(hour=10, minute=0)
    # Pass the async function reference without awaiting it
    scheduler.add_job(dataPostgres.check_and_update_premium_status, trigger)
    scheduler.start()
    logging.info("Scheduler started for daily premium status check.")

    # Keep the scheduler running
    await asyncio.Event().wait()

async def deleting_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        logging.info(f"Deleted folder: {folder_path}")
    except Exception as e:
        logging.error(f"Failed to delete folder {folder_path}: {e}")
        # await bot.send_message(chat_id=user_id, text="Please try again.")