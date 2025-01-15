from datetime import datetime, timedelta
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer

"""
This script demonstrates the trimming of audio samples and synchronization
of the entire environment based on recording start timestamps.
"""

# Various slicing and trimming methods
audio = Audio(filepath="../data/01_lab_room/pi1_audio.wav")
SampleTrimmer.slice_from_beginning(audio, timedelta(seconds=15, milliseconds=100))
SampleTrimmer.slice_from_end(audio, timedelta(seconds=14, milliseconds=600))
SampleTrimmer.trim_from_beginning(audio, timedelta(milliseconds=1500))
SampleTrimmer.trim_from_end(audio, timedelta(seconds=2))
SampleTrimmer.slice_from_to(
    audio, timedelta(seconds=5, milliseconds=100), timedelta(seconds=10)
)

# Sync the audio based on known timestamps of when the respective recordings started
# Very useful as it is necessary to have perfectly synced audio to effectively compute time delays
audio1 = Audio(filepath="../data/01_lab_room/pi2_audio.wav")
audio2 = Audio(filepath="../data/01_lab_room/pi3_audio.wav")

audio1_timestamp = datetime(2024, 11, 8, 12, 0, 15, 0)
audio2_timestamp = datetime(2024, 11, 8, 12, 0, 17, 0)
audio_timestamps = [audio1_timestamp, audio2_timestamp]

audio_files = [audio1, audio2]

print(audio1.get_audio_signal_unchunked().shape)
print(audio2.get_audio_signal_unchunked().shape)

SampleTrimmer.sync_audio(audio_files, audio_timestamps)

print(audio1.get_audio_signal_unchunked().shape)
print(audio2.get_audio_signal_unchunked().shape)
