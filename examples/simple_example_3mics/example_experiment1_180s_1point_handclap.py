import os
from datetime import datetime, timedelta

from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot
from pysoundlocalization.visualization.wave_plot import wave_plot

# Create simulation and add a room with 4 microphones
simulation = Simulation.create()
room1 = simulation.add_room("School Room", [(0, 0), (0, 10), (10, 10), (10, 0)])
mic1 = room1.add_microphone(0, 0)
mic2 = room1.add_microphone(1.8, 0)
mic3 = room1.add_microphone(0.9, 3.2)

# Add audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
audio1_filepath = "output_MIC1_2024-11-09_18-24-32_018020.wav"
mic1.add_audio(Audio(filepath=audio1_filepath))

audio2_filepath = "output_MIC2_2024-11-09_18-24-32_777688.wav"
mic2.add_audio(Audio(filepath=audio2_filepath))

audio3_filepath = "output_MIC3_2024-11-09_18-24-31_911530.wav"
mic3.add_audio(Audio(filepath=audio3_filepath))

# PREPROCESSING
# --------------

# Ensure that all audio files are of same sample rate
SampleRateConverter.convert_all_to_lowest_sample_rate(room1)

# # Sync audio from all audio files using their known timestamps of when recordings started
# audio1_timestamp = datetime(2024, 11, 9, 18, 24, 32,18020)
# audio2_timestamp = datetime(2024, 11, 9, 18, 24, 32,777688)
# audio3_timestamp = datetime(2024, 11, 9, 18, 24, 31,911530)
# audio_timestamps = [audio1_timestamp, audio2_timestamp, audio3_timestamp]
# audio_references = [mic1.get_audio(), mic2.get_audio(), mic3.get_audio()]
# SampleTrimmer.sync_audio(audio_references, audio_timestamps)

# Sync the beginning manually
SampleTrimmer.trim_from_beginning(
    mic1.get_audio(), timedelta(seconds=1, microseconds=18020)
)
SampleTrimmer.trim_from_beginning(
    mic2.get_audio(), timedelta(seconds=1, microseconds=777688)
)
SampleTrimmer.trim_from_beginning(mic3.get_audio(), timedelta(microseconds=911530))

# Trim from end to make them of equal length
SampleTrimmer.trim_from_end(mic1.get_audio(), timedelta(microseconds=759700))
SampleTrimmer.trim_from_beginning(mic3.get_audio(), timedelta(microseconds=866190))

print(mic1.get_audio())
print(mic2.get_audio())
print(mic3.get_audio())

# for mic in room1.mics:
# print(mic.get_audio())
# wave_plot(mic.get_audio())

# print sample with index where amplitude threshold over 0.8
# threshold = 0.8
# for i, sample in enumerate(mic.get_audio().audio_signal):
#     if abs(sample) > threshold:
#         print(f"Sample {i} exceeds threshold with amplitude {sample}")

# Total samples in 14.13seconds: 617400

# MIC1: Sample 181657-182573 -> 916 samples
# MIC2: Sample 183999-184457 -> 458 samples
# MIC3: Sample 185135-186346 -> 1211 samples


# Splice all audio in room to a smaller sample of 20 seconds (that includes a handclap)
# SampleTrimmer.slice_all_from_to(room1, timedelta(seconds=15), timedelta(seconds=25))

# Show claps in spectogram
# spectrogram_plot(mic1.get_audio())
# mic1.get_audio().play()

# Try to remove frequencies of machine sound
# frequency_filter_chain = FrequencyFilterChain()
# frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=2000, order=5))
#
# nmf = NonNegativeMatrixFactorization()
#
# for mic in room1.mics:
#     frequency_filter_chain.apply(mic.get_audio())
#     NoiseReducer.reduce_noise(audio=mic.get_audio())
#
#     # Reduce first 0.5s of weird noise due to noise reduce algorithm
#     SampleTrimmer.trim_from_beginning(mic.get_audio(), timedelta(seconds=1))
#     SampleTrimmer.trim_from_end(mic.get_audio(), timedelta(seconds=0.5))

# reconstructed_sounds = nmf.run(mic.get_audio())
# for i in range(len(reconstructed_sounds)):
#     print(f"Playing recostructed sound {i + 1}")
#     audio = Audio.create_from_signal(reconstructed_sounds[i], mic.get_audio().get_sample_rate())
#     audio = NoiseReducer.reduce_noise(audio=audio)
#     audio.play()
# print(mic.get_audio())

# Compute all TDoA and DoA for all mic pairs
tdoa_pairs = room1.compute_all_tdoa(
    sample_rate=SampleRateConverter.get_lowest_sample_rate(room1),
    print_intermediate_results=True,
)
print(f"TDoA for all mic pairs: {tdoa_pairs}")

doa_pairs = room1.compute_all_doa(tdoa_pairs, print_intermediate_results=True)
print(f"DoA for all mic pairs: {doa_pairs}")

# Approximate and visualize the sound source position
x, y = room1.multilaterate_sound_source(tdoa_pairs)
print(f"Approximated source position: x={x}, y={y}")

room1.add_sound_source_position(x, y)
room1.visualize()
