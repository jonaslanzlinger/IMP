from datetime import timedelta
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
import tkinter as tk
from tkinter import filedialog

"""
This script demonstrates the usage of the SampleTrimmer class to trim an audio file.
It involves the selection of a file path to the audio file, loading the audio file,
trimming the audio file, and exporting the trimmed audio file.
"""

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    title="Select an Audio File", filetypes=[("WAV files", "*.wav")]
)

if not file_path:
    raise ValueError("No file was selected.")

audio = Audio(filepath=file_path)

# Use SampleTrimmer to trim the audio file, here some examples:
SampleTrimmer.trim_from_beginning(
    audio=audio, time_delta=timedelta(seconds=4, milliseconds=220)
)
SampleTrimmer.trim_from_end(
    audio=audio, time_delta=timedelta(seconds=1, milliseconds=100)
)
SampleTrimmer.slice_from_beginning(
    audio=audio, time_delta=timedelta(seconds=2, milliseconds=150)
)
SampleTrimmer.slice_from_end(
    audio=audio, time_delta=timedelta(seconds=3, milliseconds=500)
)
SampleTrimmer.slice_from_to(
    audio=audio,
    start_time=timedelta(seconds=1),
    end_time=timedelta(seconds=20),
)

audio.export(output_filepath=file_path.replace(".wav", "_trimmed.wav"))
