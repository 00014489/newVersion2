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
import subprocess

    
# Initialize task_starting as True or False based on your requirements
task_starting = True

def get_audio_duration(file_path):
    try:
        # Use FFprobe to get the duration
        result = subprocess.run(
            ["ffprobe", "-i", file_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        duration = result.stdout.strip()
        return duration
    except Exception as e:
        logging.error(f"Failed to get duration of the file: {file_path}, Error: {e}")
        return None

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
                            logging.info(f"audio is located in {mp3_file_path_send}")
                            try:
                                logging.info(f"startig a sending")
                                file_to_sendS = FSInputFile(mp3_file_path_send, filename=mp3_file_path_send.name)
                                sendFile = await bot.send_audio(chat_id=user_id, audio=file_to_sendS)
                                original_duration = await dataPostgres.get_duration_by_id(song_id_send)
                                while True:    
                                    if sendFile.audio:
                                        audio_duration = sendFile.audio.duration
                                        if 0 <= abs(original_duration - audio_duration) <= 1.0:
                                            logging.info("Correct sending")
                                            break
                                        else:
                                            try:
                                                await bot.delete_message(chat_id=user_id, message_id=sendFile.message_id)
                                                logging.info("Deleted incorrectly sent audio message.")

                                            except Exception as e:
                                                logging.error(f"Failed to delete message: {e}")
                                            try:
                                                sendFile = await bot.send_audio(chat_id=user_id, audio=file_to_sendS)
                                            except FileNotFoundError as fnf_error:
                                                logging.error(f"File not found: {fnf_error}")
                                                logging.info("Skipping this retry due to missing file.")
                                                sendFile = None
                                                break  # Skip retry if the file cannot be found
                                            except Exception as e:
                                                logging.error(f"Error sending audio file: {e}")
                                                logging.info("Skipping this retry due to sending error.")
                                if sendFile:
                                    id = await track_message(sendFile, vocal_percentage)
                                    logging.info(f"Message ID is {sendFile.message_id}")

                                    file_id = await dataPostgres.get_file_id_by_id(song_id_send)
                                    await dataPostgres.update_out_id_by_percent(file_id, id, vocal_percentage)
                                    await deleting_folder(f"sendSongs{vocal_percentage}:{song_id_send}:{user_id}")
                                else:
                                    logging.info("sendFile is None, skipping post-send operations.")

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
                            logging.info(f"audio is located in {mp3_file_path}")
                            try:
                                audio_duration_down = get_audio_duration(mp3_file_path)
                                original_down_duration = await dataPostgres.get_duration_by_id_links(song_id)
                                logging.info(f"duration before sending {audio_duration_down}")
                                if 0 <= abs(original_down_duration - float(audio_duration_down)) <= 1.0:
                                    logging.info(f"startig a sending")
                                    file_to_send = FSInputFile(mp3_file_path, filename=mp3_file_path.name)
                                    downFile = await bot.send_audio(chat_id=user_id_down, audio=file_to_send)
                                    while True:
                                        if downFile.audio:
                                            down_duration = downFile.audio.duration
                                            if 0 <= abs(original_down_duration - down_duration) <= 1.0:
                                                logging.info("Correct sending")
                                                break
                                            else:
                                                try:
                                                    await bot.delete_message(chat_id=user_id, message_id=downFile.message_id)
                                                    logging.info("Deleted incorrectly sent audio message.")

                                                except Exception as e:
                                                    logging.error(f"Failed to delete message: {e}")
                                                try:
                                                    downFile = await bot.send_audio(chat_id=user_id, audio=file_to_send)
                                                except FileNotFoundError as fnf_error:
                                                    logging.error(f"File not found: {fnf_error}")
                                                    logging.info("Skipping this retry due to missing file.")
                                                    downFile = None
                                                    break  # Skip retry if the file cannot be found
                                                except Exception as e:
                                                    logging.error(f"Error sending audio file: {e}")
                                                    logging.info("Skipping this retry due to sending error.")
                                    if downFile:
                                        await dataPostgres.update_linksYou_message_id(song_id, downFile.message_id)
                                        await deleting_folder(f"down{song_id}")
                                    else:
                                        logging.info("downFile is None, skipping post-send operations.")
                                else:
                                    await deleting_folder(f"down{song_id}")
                                    await dataPostgres.update_order_list_true(song_id)

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