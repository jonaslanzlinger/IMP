# Script to trim and output the first X seconds of an audio file
import os
from pydub import AudioSegment

# Function to trim the audio file
def trim_audio(input_path, output_path, seconds):
    # Load the audio file
    audio = AudioSegment.from_wav(input_path)

    # Trim the audio to the first 'seconds' seconds
    trimmed_audio = audio[:seconds * 1000]  # Convert seconds to milliseconds

    # Export the trimmed audio to a new file
    trimmed_audio.export(output_path, format="wav")
    print(f"Trimmed audio saved to: {output_path}")


# Get the file path and number of seconds from the user input
input_path = input("Enter the path to the audio file: ").strip()
seconds = int(input("Enter the number of seconds to keep from the start of the audio file: ").strip())

# Check if the file exists
if not os.path.exists(input_path):
    print("The specified file does not exist.")
else:
    # Create the output file path with the format "firstXseconds_..." where X is the number of seconds
    file_name, file_extension = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(os.path.dirname(input_path), f"first{seconds}seconds_{file_name}{file_extension}")

    # Call the function to trim the audio and save it
    trim_audio(input_path, output_path, seconds)