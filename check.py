import logging
import os
import psutil
import shutil
import re
import data.connection as dataPostgres
from AI.run import process_audio_file
import time
from pathlib import Path
logging.basicConfig(level=logging.INFO)

# Global variable to control task execution
task_running = True


def delete_send_songs_folders(base_dir):
    """Delete all folders in the base directory that start with 'sendSongs'."""
    for folder_name in os.listdir(base_dir):
        if folder_name.startswith("sendSongs"):
            folder_path = os.path.join(base_dir, folder_name)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)  # Remove the folder and its contents
                logging.info(f"Deleted folder: {folder_path}")


def check_and_match_input_song_folders(base_dir: str):
    folder_pattern = r"^inputSongs(\d+):(\d+):(\d+)$"
    base_path = Path(base_dir)
    found_matching_folders = []

    # List all directories in the base directory
    folder_list = list(base_path.iterdir())

    for folder in folder_list:
        if folder.is_dir() and folder.name.startswith("inputSongs"):
            match = re.match(folder_pattern, folder.name)
            if match:
                vocal_percentage, song_id, user_id = match.groups()
                # Log the matching folder details
                logging.info(f"Found matching folder: {folder.name} for song_id: {song_id}")

                # Get the expected audio file name from the database
                # expected_audio_file_name = dataPostgres.get_name_by_songId(song_id)

                # if expected_audio_file_name:
                #     expected_audio_file_path = folder / expected_audio_file_name

                #     # List all files in the folder and delete unnecessary ones
                #     files_in_folder = list(folder.glob('*'))
                # files_in_folder = list(folder.glob("*.mp3"))
                mp3_file_path = next(folder.glob("*"))
                if mp3_file_path and mp3_file_path.is_file():
                    # mp3_file_path = file_in_folder[0]
                    logging.info(f"Found the file {mp3_file_path}")
                    found_matching_folders.append((vocal_percentage, song_id, user_id, mp3_file_path))
                elif not mp3_file_path:
                    logging.info(f"Folder {folder} is empty. Consider removing it.")

    # Check RAM usage synchronously
    ram_usage = psutil.virtual_memory()
    used_ram_percentage = ram_usage.percent
    if used_ram_percentage > 75:
        logging.warning("RAM usage exceeds 75%. Stopping the current task.")
        global task_running
        task_running = False  # Stop the task loop
        return  # Exit the function to avoid processing audio files

    # Process and send the audio files if any valid ones were found
    if found_matching_folders:
        for vocal_percentage, song_id, user_id, audio_file_path in found_matching_folders:
            time.sleep(10)  # Add a small delay before processing
            try:
                process_and_send_audio(vocal_percentage, song_id, user_id, audio_file_path)
            except Exception as e:
                logging.error(f"Failed to process and send audio for song_id {song_id}: {e}")
    else:
        logging.info("No matching folders found for processing.")


def process_and_send_audio(vocal_percentage, song_id, user_id, audio_file_path):
    print(f"song_id - {song_id}")

    file_name = dataPostgres.get_file_name_by_id(song_id)
    print(f"song_name - {file_name}")
    process_audio_file(vocal_percentage, song_id, user_id, audio_file_path)

def run_task(base_dir):
    global task_running
    
    delete_send_songs_folders(base_dir)
    while task_running:
        logging.info("Running the scheduled task...")

        # First, delete all folders starting with "sendSongs"

        # Check and match input song folders
        check_and_match_input_song_folders(base_dir)

        # Sleep for 10 seconds before the next run
        time.sleep(10)


# Main function to run both tasks concurrently
def main(base_dir):
    run_task(base_dir)

# Entry point for the program
if __name__ == "__main__":
    base_dir = "./"  # Change to your base directory
    try:
        main(base_dir)
    except KeyboardInterrupt:
        logging.info("Program interrupted. Exiting...")