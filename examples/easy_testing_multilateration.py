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

import numpy as np
from pysoundlocalization.visualization.wave_plot import wave_plot
from pysoundlocalization.core.Audio import Audio

# Create simulation and add an environment with 5 microphones
simulation = Simulation.create()
environment1 = simulation.add_environment(
    "School Environment", [(0, 0), (0, 3000), (3000, 3000), (3000, 0)]
)
mic1 = environment1.add_microphone(1000, 1000, name="1")
mic2 = environment1.add_microphone(1000, 2000, name="2")
mic3 = environment1.add_microphone(2000, 2000, name="3")
mic4 = environment1.add_microphone(2000, 1000, name="4")
# mic5 = environment1.add_microphone(0, 0, name="5")

sample_rate = 44100
duration_sine = 0.1
silence_duration = 0.1
frequency = 440
amplitude = 0.5

t_sine = np.linspace(0, duration_sine, int(sample_rate * duration_sine), endpoint=False)
sine_wave = amplitude * np.sin(2 * np.pi * frequency * t_sine)
silence = np.zeros(int(sample_rate * silence_duration))

# Corrected concatenation for each microphone
audio_signal = np.concatenate([silence] * 0 + [sine_wave] * 10 + [silence] * 90)
audio = Audio.create_from_signal(audio_signal, 44100)
mic1.set_audio(audio)

audio_signal = np.concatenate([silence] * 29 + [sine_wave] * 10 + [silence] * 61)
audio = Audio.create_from_signal(audio_signal, 44100)
mic2.set_audio(audio)

audio_signal = np.concatenate([silence] * 37 + [sine_wave] * 10 + [silence] * 53)
audio = Audio.create_from_signal(audio_signal, 44100)
mic3.set_audio(audio)

audio_signal = np.concatenate([silence] * 29 + [sine_wave] * 10 + [silence] * 61)
audio = Audio.create_from_signal(audio_signal, 44100)
mic4.set_audio(audio)

# # Compute all TDoA and DoA for all mic pairs
tdoa_pairs = environment1.compute_all_tdoa(
    sample_rate=SampleRateConverter.get_lowest_sample_rate(environment1),
    print_intermediate_results=True,
)

# Approximate and visualize the sound source position
x, y = environment1.multilaterate_sound_source(tdoa_pairs)
print(f"Approximated source position: x={x}, y={y}")

environment1.add_sound_source_position(x, y)
environment1.visualize()
