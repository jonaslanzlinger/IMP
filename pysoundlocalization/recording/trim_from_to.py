import os
from pydub import AudioSegment
from datetime import datetime, timedelta


def trim_audio(input_path, output_path, start_time, end_time):
    """
    Function to trim the audio file from start to end time.

    Args:
        input_path (str): Path to the input audio file.
        output_path (str): Path to save the trimmed audio file.
        start_time (datetime): Start time to trim the audio.
        end_time (datetime): End time to trim the audio.
    """
    audio = AudioSegment.from_wav(input_path)

    print(f"Trimmed audio length: {end_time - start_time}")

    # Convert the timestamps to milliseconds
    start_ms = (
        start_time.hour * 3600 + start_time.minute * 60 + start_time.second
    ) * 1000 + start_time.microsecond // 1000
    end_ms = (
        end_time.hour * 3600 + end_time.minute * 60 + end_time.second
    ) * 1000 + end_time.microsecond // 1000

    trimmed_audio = audio[start_ms:end_ms]

    trimmed_audio.export(output_path, format="wav")
    print(f"Trimmed audio saved to: {output_path}")


input_path = input("Enter the path to the audio file: ").strip()

if not os.path.exists(input_path):
    print("The specified file does not exist.")
else:
    audio = AudioSegment.from_wav(input_path)

    total_duration_ms = len(audio)
    total_duration = str(timedelta(milliseconds=total_duration_ms))
    print(f"Total audio length: {total_duration}")

    start_time_str = input("Enter the start timestamp (H:MM:SS.mmm): ").strip()
    end_time_str = input("Enter the end timestamp (H:MM:SS.mmm): ").strip()

    try:
        start_time = datetime.strptime(start_time_str, "%H:%M:%S.%f")
        end_time = datetime.strptime(end_time_str, "%H:%M:%S.%f")
    except ValueError:
        print("Invalid timestamp format. Please use H:MM:SS.mmm format.")
        exit()

    file_name, file_extension = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(
        os.path.dirname(input_path),
        f"from{start_time_str.replace(':', '').replace('.', '')}_to{end_time_str.replace(':', '').replace('.', '')}_{file_name}{file_extension}",
    )

    trim_audio(
        input_path=input_path,
        output_path=output_path,
        start_time=start_time,
        end_time=end_time,
    )
