import yt_dlp

def download_audio_from_youtube(url, output_path="downloads"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"Downloading audio from: {url}")
        ydl.download([url])

# Example usage
youtube_url = "https://www.youtube.com/watch?v=G3Y3o8psQBc&ab_channel=MINORKARAOKE"
download_audio_from_youtube(youtube_url)