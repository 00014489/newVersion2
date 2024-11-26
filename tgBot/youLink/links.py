import yt_dlp
import os
import data.connection as dataPostgres
from yt_dlp.utils import YoutubeDLError

# Path to cookies.txt file
# COOKIES_FILE_PATH = '/home/MinusGolos/Projects/newVersion2/cookies.txt'

def download_audio_from_youtube(id):
    try:
        # Get the URL from your database or other data source
        url = dataPostgres.get_url_By_id(id)
        output_path = f"down{id}"

        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)

        # yt-dlp options for downloading and processing
        ydl_opts = {
            'cookiefile': '/home/MinusGolos/Projects/newVersion2/cookies.txt',  # Path to cookies for authentication (moved to the first place)
            'format': 'bestaudio/best',  # Download the best audio
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Set the output file template
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',  # Convert to MP3
                'preferredquality': '192',  # Set audio quality
            }],
        }

        # Create a YouTubeDL instance
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading audio from: {url}")
            # Extract information without downloading the file
            info_dict = ydl.extract_info(url, download=False)
            file_path = ydl.prepare_filename(info_dict)  # Prepare the file path for the audio

            # Start downloading and processing the audio
            ydl.download([url])

            # Update the file extension to mp3 after processing
            mp3_path = os.path.splitext(file_path)[0] + ".mp3"

            print(f"Download complete. MP3 file path: {mp3_path}")
            return mp3_path  # Return the final MP3 file path

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def get_audio_duration(url):
    try:
        ydl_opts = {
            'cookiefile': '/home/MinusGolos/Projects/newVersion2/cookies.txt',  # Use cookies for authentication
            'format': 'bestaudio/best',
            'quiet': True,  # Suppress download logs
            'noplaylist': True,
            'skip_download': True,  # Avoid downloading, just get metadata
        }

        # Check if the cookies file exists
        if not os.path.exists(ydl_opts['cookies']):
            print("Cookies file does not exist.")
            return None

        # Creating a YoutubeDL instance
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract the duration (in seconds) if available
            duration = info.get('duration', 0)
            return duration

    except YoutubeDLError as e:
        print(f"Error with yt-dlp: {e}")
        return None  # Return None or a default value if an error occurs

    except Exception as e:
        print(f"Error extracting duration: {e}")
        return None  # Return None or a default value if an error occurs