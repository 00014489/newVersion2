import os
import logging
import data.connection as dataPostgres
import time
import gc
import subprocess
from spleeter.separator import Separator
import tensorflow as tf
from pathlib import Path
import shutil
# import data.connection as dataPostgres


logging.basicConfig(level=logging.INFO)

# TensorFlow configuration
try:
    gpus = tf.config.list_physical_devices('GPU')  # Updated API
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
            # Alternative: tf.config.set_logical_device_configuration if needed
except RuntimeError as e:
    logging.error(f"Error setting TensorFlow memory growth: {e}")

# Enable eager execution for TensorFlow
tf.config.run_functions_eagerly(True)

def convert_to_wav(file_input, new_folder, base_name):
    input_file = f"./{file_input}"
    """Convert the input file to WAV format synchronously."""
    logging.info(f"datas base name = {base_name}, output {new_folder}, input_file = {input_file}")
    wav_input_file = os.path.join(new_folder, f'{base_name}.wav')
    process = subprocess.run(
        ['ffmpeg', '-i', input_file, wav_input_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion error: {process.stderr.decode()}")
    return wav_input_file

def run_spleeter(wav_input_file, new_folder):
    """Separate the audio using Spleeter."""
    separator = Separator('spleeter:2stems')
    
    # Clear the previous session to avoid any conflicts
    # tf.keras.backend.clear_session()
    tf.keras.backend.clear_session()

    # Run Spleeter's TensorFlow-based operation
    separator.separate_to_file(wav_input_file, new_folder)

def convert_accompaniment_to_mp3(accompaniment_file, new_folder, base_name, output_format='mp3'):
    """Convert the accompaniment (without vocals) to MP3 format synchronously."""
    output_file = os.path.join(new_folder, f'{base_name}_0_MG.{output_format}')
    process = subprocess.run(
        ['ffmpeg', '-i', accompaniment_file, '-c:a', 'libmp3lame', '-b:a', '192k', output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion error: {process.stderr.decode()}")
    return output_file

def mix_vocals_and_accompaniment(accompaniment_file, vocals_file, vocal_percentage, new_folder, base_name, output_format='mp3'):
    """Mix vocals into the accompaniment file based on the vocal percentage and convert to MP3 format."""
    output_file = os.path.join(new_folder, f'{base_name}_{vocal_percentage}_MG.{output_format}')

    vocal_volume = int(vocal_percentage) / 100.0
    accompaniment_volume = 1  # Full volume for accompaniment

    filter_complex = (
        f"[0:a]volume={accompaniment_volume}[a];"
        f"[1:a]volume={vocal_volume}[v];"
        f"[a][v]amix=inputs=2:duration=longest"
    )

    process = subprocess.run(
        ['ffmpeg', '-i', accompaniment_file, '-i', vocals_file,
         '-filter_complex', filter_complex,
         '-c:a', 'libmp3lame', '-q:a', '0', output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg mixing error: {process.stderr.decode()}")

    return output_file

    

def process_audio_file(vocal_percentage: int, id_input: int, user_id: int, file_path: str, output_format='mp3'):
    """Process audio file with specified vocal percentage mixed into accompaniment."""
    start_time = time.time()
    name_inTable, input_name = dataPostgres.get_name_by_songId(id_input)  # Assuming this is a synchronous call
    
    if file_path is None:
        raise FileNotFoundError(f"No audio file found for base name: {input_name}")

    output_directory = f'./sendSongs{vocal_percentage}:{id_input}:{user_id}'
    os.makedirs(output_directory, exist_ok=True)  # Create the output directory

    if not str(name_inTable).endswith('.wav'):
        # logging.info("we are here mf")
        wav_input_file = convert_to_wav(file_path, output_directory, input_name)
    else:
        wav_input_file = file_path

    logging.info(f"Starting Spleeter separation for {wav_input_file}")
    run_spleeter(wav_input_file, output_directory)
    logging.info(f"Completed Spleeter separation for {wav_input_file}")

    accompaniment_file = os.path.join(output_directory, input_name, f'accompaniment.wav')
    vocals_file = os.path.join(output_directory, input_name, 'vocals.wav')

    if not os.path.exists(accompaniment_file):
        raise FileNotFoundError(f"Accompaniment file {accompaniment_file} does not exist.")
    if int(vocal_percentage) > 0 and not os.path.exists(vocals_file):
        raise FileNotFoundError(f"Vocal file {vocals_file} does not exist.")

    logging.info(f"Mixing with vocal percentage: {vocal_percentage}%")

    if int(vocal_percentage) == 0:
        convert_accompaniment_to_mp3(accompaniment_file, output_directory, input_name, output_format)
    else:
        mix_vocals_and_accompaniment(accompaniment_file, vocals_file, vocal_percentage, output_directory, input_name, output_format)


    # Clean up intermediate files
    # os.remove(accompaniment_file)
    # if file_path != wav_input_file:
    #     os.remove(wav_input_file)

    elapsed_time = time.time() - start_time
    logging.info(f"Processing completed in {elapsed_time:.2f} seconds.")
    save_directory = f'./inputSongs{vocal_percentage}:{id_input}:{user_id}'
    # Remove the save_directory folder and its contents
    # shutil.rmtree(save_directory, ignore_errors=True)
    logging.info(f"Deleted temporary directory: {save_directory}")
    gc.collect()