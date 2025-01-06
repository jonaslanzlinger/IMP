import os
from pydub import AudioSegment
from datetime import datetime, timedelta


# Function to trim the audio file from start to end time
def trim_audio(input_path, output_path, start_time, end_time):
    # Load the audio file
    audio = AudioSegment.from_wav(input_path)

    # Convert milliseconds to HH:MM:SS.mmm format using timedelta
    print(f"Trimmed audio length: {end_time - start_time}")

    # Convert the timestamps to milliseconds
    start_ms = (
        start_time.hour * 3600 + start_time.minute * 60 + start_time.second
    ) * 1000 + start_time.microsecond // 1000
    end_ms = (
        end_time.hour * 3600 + end_time.minute * 60 + end_time.second
    ) * 1000 + end_time.microsecond // 1000

    # Trim the audio from start_ms to end_ms
    trimmed_audio = audio[start_ms:end_ms]

    # Export the trimmed audio to a new file
    trimmed_audio.export(output_path, format="wav")
    print(f"Trimmed audio saved to: {output_path}")


# Get the file path from the user input
input_path = input("Enter the path to the audio file: ").strip()

# Check if the file exists
if not os.path.exists(input_path):
    print("The specified file does not exist.")
else:
    # Load the audio file to get the total duration
    audio = AudioSegment.from_wav(input_path)

    # Get the total length of the audio file in milliseconds
    total_duration_ms = len(audio)

    # Convert milliseconds to HH:MM:SS.mmm format using timedelta
    total_duration = str(timedelta(milliseconds=total_duration_ms))

    # Print the total length of the audio file
    print(f"Total audio length: {total_duration}")

    # Input the start and end timestamps from the user
    start_time_str = input("Enter the start timestamp (H:MM:SS.mmm): ").strip()
    end_time_str = input("Enter the end timestamp (H:MM:SS.mmm): ").strip()

    # Convert input timestamps to datetime objects
    try:
        start_time = datetime.strptime(start_time_str, "%H:%M:%S.%f")
        end_time = datetime.strptime(end_time_str, "%H:%M:%S.%f")
    except ValueError:
        print("Invalid timestamp format. Please use H:MM:SS.mmm format.")
        exit()

    # Create the output file path with the format "fromTo_timestamp_..."
    file_name, file_extension = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(
        os.path.dirname(input_path),
        f"from{start_time_str.replace(':', '').replace('.', '')}_to{end_time_str.replace(':', '').replace('.', '')}_{file_name}{file_extension}",
    )

    # Call the function to trim the audio and save it
    trim_audio(input_path, output_path, start_time, end_time)
