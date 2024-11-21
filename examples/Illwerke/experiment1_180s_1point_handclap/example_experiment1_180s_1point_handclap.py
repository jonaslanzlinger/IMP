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
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.visualization.wave_plot import wave_plot
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer

# Create simulation and add an environment with 4 microphones
simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Machine Environment", [(0, 0), (0, 10), (10, 10), (10, 0)]
)
mic1 = environment1.add_microphone(6.61, 0)
mic2 = environment1.add_microphone(6.61, 3.89)
mic3 = environment1.add_microphone(0, 3.89)
mic4 = environment1.add_microphone(0, 0)

# Add audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
audio1_filepath = "output_MIC1_2024-11-07_10-30-45_977581.wav"
mic1.set_audio(Audio(filepath=audio1_filepath))

audio2_filepath = "output_MIC2_2024-11-07_10-30-45_474498.wav"
mic2.set_audio(Audio(filepath=audio2_filepath))

audio3_filepath = "output_MIC3_2024-11-07_10-30-46_550904.wav"
mic3.set_audio(Audio(filepath=audio3_filepath))

audio4_filepath = "output_MIC4_2024-11-07_10-30-45_728052.wav"
mic4.set_audio(Audio(filepath=audio4_filepath))

# PREPROCESSING
# --------------

# Ensure that all audio files are of same sample rate
SampleRateConverter.convert_all_to_lowest_sample_rate(environment1)

# Sync audio from all audio files using their known timestamps of when recordings started
audio1_timestamp = datetime(2024, 11, 7, 10, 30, 45, 977581)
audio2_timestamp = datetime(2024, 11, 7, 10, 30, 45, 474498)
audio3_timestamp = datetime(2024, 11, 7, 10, 30, 46, 550904)
audio4_timestamp = datetime(2024, 11, 7, 10, 30, 45, 728052)
audio_timestamps = [
    audio1_timestamp,
    audio2_timestamp,
    audio3_timestamp,
    audio4_timestamp,
]
audio_references = [
    mic1.get_audio(),
    mic2.get_audio(),
    mic3.get_audio(),
    mic4.get_audio(),
]
SampleTrimmer.sync_audio(audio_references, audio_timestamps)

# Splice all audio in environment to a smaller sample of 20 seconds (that includes a handclap)
SampleTrimmer.slice_all_from_to(
    environment1, timedelta(seconds=15), timedelta(seconds=25)
)

# Show claps in spectogram
spectrogram_plot(
    mic1.get_audio().get_audio_signal_by_index(0), mic1.get_audio().get_sample_rate()
)
# mic1.get_audio().play()

# Try to remove frequencies of machine sound
frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=2000, order=5))

nmf = NonNegativeMatrixFactorization()

for mic in environment1.get_mics():
    wave_plot(
        mic.get_audio().get_audio_signal_by_index(0), mic.get_audio().get_sample_rate()
    )
    frequency_filter_chain.apply(mic.get_audio())
    NoiseReducer.reduce_noise(audio=mic.get_audio())

    # Reduce first 0.5s of weird noise due to noise reduce algorithm
    SampleTrimmer.trim_from_beginning(mic.get_audio(), timedelta(seconds=1))
    SampleTrimmer.trim_from_end(mic.get_audio(), timedelta(seconds=0.5))

    # reconstructed_sounds = nmf.run(mic.get_audio())
    # for i in range(len(reconstructed_sounds)):
    #     print(f"Playing recostructed sound {i + 1}")
    #     audio = Audio.create_from_signal(reconstructed_sounds[i], mic.get_audio().get_sample_rate())
    #     audio = NoiseReducer.reduce_noise(audio=audio)
    #     audio.play()
    # print(mic.get_audio())
    wave_plot(
        mic.get_audio().get_audio_signal_by_index(0), mic.get_audio().get_sample_rate()
    )

AudioNormalizer.peak_normalize(environment1, -10)
for mic in environment1.get_mics():
    wave_plot(
        mic.get_audio().get_audio_signal_by_index(0), mic.get_audio().get_sample_rate()
    )

# for mic in environment1.get_mics():
#     wave_plot(
#         mic.get_audio().get_audio_signal_by_index(0), mic.get_audio().get_sample_rate()
#     )

algorithm_choice = "gcc_phat"

dict = environment1.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.06
)

for i, object in enumerate(dict):
    print(dict[object])

multilaterate_plot(environment1, dict)

# # Compute all TDoA and DoA for all mic pairs
# tdoa_pairs = environment1.compute_all_tdoa(
#     print_intermediate_results=True,
# )
# print(f"TDoA for all mic pairs: {tdoa_pairs}")

# doa_pairs = environment1.compute_all_doa(tdoa_pairs, print_intermediate_results=True)
# print(f"DoA for all mic pairs: {doa_pairs}")

# # Approximate and visualize the sound source position
# x, y = environment1.multilaterate_sound_source(tdoa_pairs)
# print(f"Approximated source position: x={x}, y={y}")

# environment1.add_sound_source_position(x, y)
# environment1.visualize()
