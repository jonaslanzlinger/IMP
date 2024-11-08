from datetime import datetime

from core.Audio import Audio
from preprocessing.SampleTrimmer import SampleTrimmer

audio1 = Audio(filepath='example_audio/pi1_audio.wav')
audio2 = Audio(filepath='example_audio/pi2_audio.wav')

#SampleTrimmer.slice_from_beginning(audio, seconds=5)
#SampleTrimmer.slice_from_to(audio, 0,15)

audio1_timestamp = datetime(2024, 11, 8, 12, 0, 15, 0)
audio2_timestamp = datetime(2024, 11, 8, 12, 0, 15, 0)
audio_timestamps = [audio1_timestamp, audio2_timestamp]

audio_files = [audio1, audio2]

print(audio1)
print(audio2)

SampleTrimmer.sync_audio(audio_files, audio_timestamps)

print(audio1)
print(audio2)

#audio1.play()
#audio.trim_from_beginning(to=XY)
#
#audio.