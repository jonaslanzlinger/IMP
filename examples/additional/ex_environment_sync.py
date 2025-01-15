from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.core.Simulation import Simulation
from datetime import datetime

"""
This script demonstrates the usage of the SampleTrimmer.sync_environment method.

Synchronizing the environment will trim the audio files to the same length,
while preserving the start time of the recordings, and the relative time between
the recordings. This is necessary for the audio files to be used in the
localization algorithm; otherwise, it will not work correctly.
"""

simulation = Simulation.create()

environment = simulation.add_environment(
    "Test Environment",
    [
        (0, 0),
        (100, 0),
        (100, 100),
        (0, 100),
    ],
)
# environment.visualize()

mic1 = environment.add_microphone(x=1, y=1)
mic2 = environment.add_microphone(x=99, y=1)
mic3 = environment.add_microphone(x=99, y=99)
mic4 = environment.add_microphone(x=1, y=99)
# environment.visualize()

mic1.set_audio(
    Audio(filepath="../../data/11_pump/pi1_audio_2024-11-07_10-30-45_977581.wav")
)
mic1.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 977581))

mic2.set_audio(
    Audio(filepath="../../data/11_pump/pi2_audio_2024-11-07_10-30-45_474498.wav")
)
mic2.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 474498))

mic3.set_audio(
    Audio(filepath="../../data/11_pump/pi3_audio_2024-11-07_10-30-46_550904.wav")
)
mic3.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 46, 550904))

mic4.set_audio(
    Audio(filepath="../../data/11_pump/pi4_audio_2024-11-07_10-30-45_728052.wav")
)
mic4.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 728052))

print("Before syncing:")
print("Mic1 duration:", mic1.get_audio().get_duration())
print("Mic2 duration:", mic2.get_audio().get_duration())
print("Mic3 duration:", mic3.get_audio().get_duration())
print("Mic4 duration:", mic4.get_audio().get_duration())

# Synchronizing the environment will trim the audio files to the same length,
# while preserving the start time of the recordings, and the relative time between
# the recordings. This is necessary for the audio files to be used in the
# localization algorithms, because the recordings start at different timestamps.
SampleTrimmer.sync_environment(environment)

print("After syncing:")
print("Mic1 duration:", mic1.get_audio().get_duration())
print("Mic2 duration:", mic2.get_audio().get_duration())
print("Mic3 duration:", mic3.get_audio().get_duration())
print("Mic4 duration:", mic4.get_audio().get_duration())
