import yt_dlp
import os
import data.connection as dataPostgres

def download_audio_from_youtube(id):
    url = dataPostgres.get_url_By_id(id)
    output_path = f"down{id}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
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
