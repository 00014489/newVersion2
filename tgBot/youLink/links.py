import yt_dlp
import os
import data.connection as dataPostgres

# Path to cookies.txt file
COOKIES_FILE_PATH = '/home/MinusGolos/Projects/newVersion2/cookies.txt'

def download_audio_from_youtube(id):
    url = dataPostgres.get_url_By_id(id)
    output_path = f"down{id}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'cookies': COOKIES_FILE_PATH,  # Use cookies for authentication
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"Downloading audio from: {url}")
        info_dict = ydl.extract_info(url, download=False)  # Get video info without downloading
        file_path = ydl.prepare_filename(info_dict)  # Original file path before post-processing
        
        # Perform the download, including post-processing to MP3
        ydl.download([url])
        
        # Replace the extension to match the post-processed file
        mp3_path = os.path.splitext(file_path)[0] + ".mp3"
        
        return mp3_path  # Return the final MP3 file path

async def get_audio_duration(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'cookies': COOKIES_FILE_PATH,  # Use cookies for authentication
        'quiet': True,  # Suppress download logs
        'noplaylist': True,
        'skip_download': True,  # Avoid downloading, just get metadata
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        duration = info.get('duration', 0)  # Duration in seconds if available
        return duration
