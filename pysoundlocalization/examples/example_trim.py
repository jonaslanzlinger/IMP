from datetime import datetime, timedelta
from core.Audio import Audio
from preprocessing.SampleTrimmer import SampleTrimmer

# Various slicing and trimming methods
audio = Audio(filepath='example_audio/pi1_audio.wav')
SampleTrimmer.slice_from_beginning(audio, timedelta(seconds=15, milliseconds=100))
SampleTrimmer.slice_from_end(audio, timedelta(seconds=14, milliseconds=600))
SampleTrimmer.trim_from_beginning(audio, timedelta(milliseconds=1500))
SampleTrimmer.trim_from_end(audio, timedelta(seconds=2))
SampleTrimmer.slice_from_to(audio, timedelta(seconds=5, milliseconds=100), timedelta(seconds=10))


# Sync the audio based on known timestamps of when the respective recordings started
# Very useful as it is necessary to have perfectly synced audio to effectively compute time delays
audio1 = Audio(filepath='example_audio/pi1_audio.wav')
audio2 = Audio(filepath='example_audio/pi2_audio.wav')

audio1_timestamp = datetime(2024, 11, 8, 12, 0, 15, 0)
audio2_timestamp = datetime(2024, 11, 8, 12, 0, 17, 0)
audio_timestamps = [audio1_timestamp, audio2_timestamp]

audio_files = [audio1, audio2]

print(audio1)
print(audio2)
# TODO: currently, sync_audio has a rounding error (likely from duration) that makes it such that audio2 has just 1 sample more than audio1
SampleTrimmer.sync_audio(audio_files, audio_timestamps)

print(audio1)
print(audio2)