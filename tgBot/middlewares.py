from aiogram import BaseMiddleware
from aiogram.types import Message, Update, FSInputFile, InputFile
import io
# from aiogram.exceptions import TelegramAPIError
from tgBot.youLink.links import download_audio_from_youtube
# from aiogram.dispatcher.middlewares.base import CancelHandler
import os
import yt_dlp
import re
import tgBot.bot_keyboards.inlineKeyboards as kbIn
import data.connection as dataPostgres
import logging
import aiohttp
import urllib.parse



async def get_audio_duration(url):
    if False: # for checking the database
        return 700
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,  # Suppress download logs
            'noplaylist': True,
            'skip_download': True,  # Avoid downloading, just get metadata
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get('duration', 0)  # Duration in seconds if available
            return duration
                        


async def is_playlist_link(url):
    if False: # for database
        return True
    else:    
    # Parse the URL to check for a "list" parameter, indicating a playlist
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Check if 'list' parameter exists in the URL
        if 'list' in query_params:
            return True

        # Optionally, verify URL content (e.g., some YouTube links may have "list" in other ways)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                # Further checks could go here if needed, like inspecting response headers
                return False
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
        if event.message:
            message = event.message  # Extract the Message object
            user_id = message.from_user.id
            username = message.from_user.username
            userPremium = True
            messageText = message.text
            if messageText and messageText.startswith("/"):
                print("skiping the command")
                return await handler(event, data)
            # print("we are here 1")
            try:
                if userPremium:
                    # print("we are here 2")
                    # print(f"message text is {messageText}")
                    if messageText is not None and ("youtube.com" in messageText or "youtu.be" in messageText):
                    # if messageText and "youtube.com" in messageText or "youtu.be" in messageText and messageText != None:
                        # code for saving the url and user_id to the database.
                        filtred = normalize_youtube_url(messageText.strip())
                        # print("we are here 3")
                        # if await is_playlist_link(filtred):
                            # message.reply("Please send only one file not playlist")
                            # return
                        if await dataPostgres.link_exists(filtred):
                            duration = await dataPostgres.get_link_duration(filtred)
                            print(f"Found in database")
                            # return duration
                        else:
                            duration = await get_audio_duration(filtred)
                            await dataPostgres.insert_links(filtred, duration)
                        # isPlaylist = await is_playlist_link(filtred)
                        if duration < 600: #and isPlaylist == False:
                            proccesing_messagee = await message.reply("Processing your YouTube audio...")

                            
                            if False: # if exist
                                return
                            else:
                                try:
                                    # Download audio from YouTube
                                    mp3_path = await download_audio_from_youtube(filtred)
                                    
                                    # Send the downloaded audio file to the user
                                    if os.path.exists(mp3_path):
                                        audio_file = FSInputFile(mp3_path)
                                        await message.answer_document(audio_file)
                                        # Optionally, delete the file after sending
                                        os.remove(mp3_path)
                                        await proccesing_messagee.delete()
                                    else:
                                        await message.reply("Error: Could not find the downloaded file.")

                                except Exception as e:
                                    await message.reply(f"Error downloading audio: {e}")
                                    print(f"Error: {e}")
                        else:
                             await message.reply("Your link out of limits. no more thant 10 minutes and no playlists.")
                    elif message.audio:
                        # await message.reply("geting a audio")
                        await self.handle_audio_message(message)
                    else:
                        print(f"Unhandled message type from {username} (ID: {user_id})")
                        await message.reply("Please send aduio of link of youtube")

                    # Pass the event to the handler
                    return await handler(event, data)

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

    async def handle_audio_message(self, message: Message):
        """
        Process audio files sent as audio (music).
        """
        audio = message.audio
        # Download and process the audio file if needed
        print(f"Received audio file: {audio.file_id} - {audio.file_name}")
        await message.reply("Received your audio file!")

        file_id = message.audio.file_id
        file_name = message.audio.file_name or "Unknown_Song.mp3"
        file_size = message.audio.file_size / (1024 * 1024)  # Convert size to MB
        file_duration = message.audio.duration / 60  # Convert duration to minutes

        # Validation: Check if the file is larger than 15 MB or longer than 6 minutes
        if file_size > 15:
            await message.reply(f"The song is too big ({file_size:.2f} MB). Please send a song smaller than 15 MB.")
            return
        if file_duration > 6:
            await message.reply(f"The song is too long ({file_duration:.2f} minutes). Please send a song shorter than 6 minutes.")
            return

        if not await dataPostgres.check_file_exists(file_id):
            # Get the file name without the extension
            file_name_without_extension = os.path.splitext(file_name)[0]
            
            # Insert into the database with the file name without the extension
            await dataPostgres.insert_into_input_file(file_id, format_column_namesForDatabase(file_name), file_name_without_extension)

        try:
            await message.reply("Please select the vocal percentage...", reply_markup=await kbIn.percent_choose(file_id))
        except Exception as e:
            logging.error(f"Error processing audio file: {e}", exc_info=True)
            await message.reply(f"Failed to process {file_name} due to an error: {str(e)}")