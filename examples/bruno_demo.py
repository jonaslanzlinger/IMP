import os
from datetime import datetime, timedelta
import numpy as np

from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot

simulation = Simulation.create()
environment1 = simulation.add_environment(
    "School Environment", [(0, 0), (8.35, 0), (8.35, 9.89), (0, 9.89)]
)
mic1 = environment1.add_microphone(1, 1, name="mic1")
mic2 = environment1.add_microphone(7.35, 1, name="mic2")
mic3 = environment1.add_microphone(7.35, 8.51, name="mic3")
mic4 = environment1.add_microphone(1, 8.89, name="mic4")

audio1_filepath = "../08_versuch_classroom_syncatmic3_3sources/pi1_audio.wav"
mic1.set_audio(Audio(filepath=audio1_filepath))
mic1.set_recording_start_time(datetime(2024, 11, 9, 18, 24, 32, 18020))

audio2_filepath = "../08_versuch_classroom_syncatmic3_3sources/pi2_audio.wav"
mic2.set_audio(Audio(filepath=audio2_filepath))
mic2.set_recording_start_time(datetime(2024, 11, 9, 18, 24, 32, 777688))

audio3_filepath = "../08_versuch_classroom_syncatmic3_3sources/pi3_audio.wav"
mic3.set_audio(Audio(filepath=audio3_filepath))
mic3.set_recording_start_time(datetime(2024, 11, 9, 18, 24, 31, 911530))

audio4_filepath = "../08_versuch_classroom_syncatmic3_3sources/pi4_audio.wav"
mic4.set_audio(Audio(filepath=audio4_filepath))
mic4.set_recording_start_time(datetime(2024, 11, 9, 18, 24, 31, 911530))

SampleTrimmer.slice_all_from_to(
    environment1, timedelta(seconds=20), timedelta(seconds=29.8)
)

spectrogram_plot(
    audio_signal=mic1.get_audio().get_audio_signal(index=0),
    sample_rate=44100,
)

environment1.chunk_audio_signals_by_duration(chunk_duration=timedelta(milliseconds=100))

print(environment1.get_mics()[0].get_audio().get_num_chunks())

dict = [
    {
        "12000": (3.49, 1.1),
        "57000": (3.5, 1.9),
        "100000": (3.47, 2.7),
        "136000": (3.52, 3.6),
        "180000": (3.5, 4.7),
        "224000": (3.48, 5.5),
        "280000": (3.51, 6.3),
        "328000": (3.52, 6.9),
        "366000": (3.5, 7.7),
        "420000": (3.49, 8.7),
    },
    {
        "34000": (6.1, 8.3),
        "100000": (6.0, 7.0),
        "160000": (6.05, 5.1),
        "246000": (5.9, 3.6),
        "300000": (6.05, 2.7),
        "366000": (6.0, 1.3),
    },
]

multilaterate_plot(environment1, dict)
