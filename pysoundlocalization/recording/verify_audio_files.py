import soundfile as sf
import tkinter as tk
from tkinter import filedialog


def display_intro():
    print("This script reads and analyzes .wav audio files.")
    print("For each audio file, the following information will be displayed:")
    print("- Sample rate (in Hz)")
    print("- Shape (number of samples and channels)")
    print("- Number of channels (1 for mono, 2 for stereo)")
    print("- Duration of the file (in seconds)\n")


def read_and_display_audio_info(file_path: str):
    try:
        # read details
        data, sample_rate = sf.read(file_path)
        duration_seconds = len(data) / sample_rate
        # (num_samples, num_channels) -> stereo
        # (num_samples,) -> mono
        shape = data.shape

        # Print details
        print(f"File: {file_path}")
        print(f"Sample Rate: {sample_rate} Hz")
        print(f"Shape: {shape}")
        print(f"Channels: {1 if len(shape) == 1 else shape[1]}")
        print(f"Duration: {duration_seconds:.2f} seconds\n")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


if __name__ == "__main__":
    display_intro()

    while True:
        user_input = (
            input("Would you like to add more audio files? (y/n): ").strip().lower()
        )
        if user_input == "y":
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="Select an Audio File", filetypes=[("WAV files", "*.wav")]
            )
            if file_path:
                print(f"Added file: {file_path}")
                read_and_display_audio_info(file_path=file_path)
            else:
                print("No file selected.")
        elif user_input == "n":
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
