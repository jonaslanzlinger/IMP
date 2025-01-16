import os
import re
from datetime import datetime, timedelta
from pydub import AudioSegment

"""
Script to synchronize audio files from a given folder to match the start and end timestamps.
The script trims the audio files based on the latest start timestamp and earliest end timestamp.
The trimmed files are saved with a "trimmed_" prefix in the same folder.

Note: Re-running the script will re-trim the newly trimmed files and iteratively add trimmed_trimmed_... files.
"""

# Example: '../audio_files/Sandbox Experiments/Basic_Test_Mosquito'
folder_path = input("Please enter the path to the folder containing the audio files: ")

pattern = re.compile(r"output_MIC\d+_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_\d{6})\.wav")

file_info = {}
# Iterate through each file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".wav"):
        match = pattern.search(filename)
        if match:
            # Parse the timestamp from the filename
            timestamp_str = match.group(1)
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S_%f")
            file_path = os.path.join(folder_path, filename)

            audio = AudioSegment.from_wav(file_path)
            duration_ms = len(audio)

            # Store start timestamp, file path, and duration
            file_info[filename] = {
                "path": file_path,
                "start": timestamp,
                "duration": duration_ms,
            }

# Find the latest start timestamp and the earliest end timestamp
latest_start = max(info["start"] for info in file_info.values())
earliest_end = min(
    info["start"] + timedelta(milliseconds=info["duration"])
    for info in file_info.values()
)

# Calculate the duration all files should have after trimming
sync_duration_ms = int((earliest_end - latest_start).total_seconds() * 1000)

# Process each audio file to trim based on the offset and duration
for filename, info in file_info.items():

    trimmed_file_path = os.path.join(folder_path, f"trimmed_{filename}")

    # Calculate the offset for trimming
    offset_ms = int((latest_start - info["start"]).total_seconds() * 1000)

    # Load the audio file and trim start and end
    audio = AudioSegment.from_wav(info["path"])
    trimmed_audio = audio[offset_ms : offset_ms + sync_duration_ms]

    # Export the trimmed file (will overwrite if it exists)
    trimmed_audio.export(trimmed_file_path, format="wav")

print("Audio files have been synchronized to start and end at the same time.")
