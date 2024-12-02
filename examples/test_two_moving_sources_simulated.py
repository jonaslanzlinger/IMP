from pysoundlocalization.visualization.wave_plot import wave_plot
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from datetime import timedelta
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.core.Simulation import Simulation
from datetime import datetime
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
import time
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
import numpy as np
from pysoundlocalization.core.Environment import Environment
from simulate_noise_util import generate_microphone_audio

simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Simulation", [(0, 0), (10, 0), (10, 10), (0, 10)]
)
mic1 = environment1.add_microphone(1, 1)
mic2 = environment1.add_microphone(9, 1)
mic3 = environment1.add_microphone(9, 9)
mic4 = environment1.add_microphone(1, 9)

# how to add sounds
source_positions = [
    {44100: (4, 9), 88200: (4, 7)},
    {132300: (8, 1)},
    {150000: (1, 1)},
    # {220000: (5, 5)},
    # {260000: (5, 5)},
    # {300000: (5, 5)},
    # {340000: (5, 5)},
    # {380000: (5, 5)},
]

environment1 = generate_microphone_audio(environment1, 44100, source_positions)

audio1 = mic1.get_audio()
audio2 = mic2.get_audio()
audio3 = mic3.get_audio()
audio4 = mic4.get_audio()

AudioNormalizer.normalize_environment_to_max_amplitude(environment1, 0.8)

wave_plot(
    audio1.get_audio_signal(),
    audio1.get_sample_rate(),
)
wave_plot(
    audio2.get_audio_signal(),
    audio2.get_sample_rate(),
)
wave_plot(
    audio3.get_audio_signal(),
    audio3.get_sample_rate(),
)
wave_plot(
    audio4.get_audio_signal(),
    audio4.get_sample_rate(),
)

nmf = NonNegativeMatrixFactorization(sample_rate=audio1.get_sample_rate())
all_audio_nmf = nmf.experimental_run_for_all_audio_in_environment(environment1)

algorithm_choice = "threshold"

all_dicts = []

current_audio_index = 0

mic1.set_audio(all_audio_nmf[mic1][0])
mic2.set_audio(all_audio_nmf[mic2][0])
mic3.set_audio(all_audio_nmf[mic3][0])
mic4.set_audio(all_audio_nmf[mic4][0])
AudioNormalizer.normalize_environment_to_max_amplitude(environment1, 0.8)
environment1.chunk_audio_signals_by_duration(
    chunk_duration=timedelta(milliseconds=1000)
)
result_dict = environment1.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.5
)
all_dicts.append(result_dict)

mic1.set_audio(all_audio_nmf[mic1][1])
mic2.set_audio(all_audio_nmf[mic2][1])
mic3.set_audio(all_audio_nmf[mic3][1])
mic4.set_audio(all_audio_nmf[mic4][1])
AudioNormalizer.normalize_environment_to_max_amplitude(environment1, 0.8)
environment1.chunk_audio_signals_by_duration(
    chunk_duration=timedelta(milliseconds=1000)
)
result_dict = environment1.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.5
)
# AudioNormalizer.normalize_to_max_amplitude(environment1, 0.8)
# result_dict = environment1.multilaterate(
#     algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.2
# )
all_dicts.append(result_dict)

# FAKE


# Reset audio to original audio
mic1.set_audio(audio1)
mic2.set_audio(audio2)
mic3.set_audio(audio3)
mic4.set_audio(audio4)
# environment1.chunk_audio_signals_by_duration(chunk_duration=timedelta(milliseconds=200))

for i, object in enumerate(all_dicts):
    print(dict[object])

multilaterate_plot(environment1, all_dicts)
