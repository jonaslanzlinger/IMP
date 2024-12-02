import os
from datetime import datetime, timedelta
import numpy as np

from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Environment import Environment
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot
from pysoundlocalization.visualization.wave_plot import wave_plot
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)

simulation = Simulation.create()

environment = simulation.add_environment(
    "Classroom Simulation", [(0, 0), (8.35, 0), (8.35, 9.89), (0, 9.89)]
)

mic1 = environment.add_microphone(1, 1, name="Microphone-1")
mic2 = environment.add_microphone(7.35, 1, name="Microphone-2")
mic3 = environment.add_microphone(7.35, 8.51, name="Microphone-3")
mic4 = environment.add_microphone(1, 8.89, name="Microphone-4")

1650
1280
0
1000
# in samples

audio1_original = Audio(filepath="classroom_2024-11-28_15-00-00-000000_pi1_audio.wav")
mic1.set_audio(audio1_original)
mic1.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 0))
SampleTrimmer.trim_from_beginning(mic1.get_audio(), timedelta(microseconds=0))

audio2_original = Audio(filepath="classroom_2024-11-28_15-00-00-000000_pi2_audio.wav")
mic2.set_audio(audio2_original)
mic2.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 0))
# 381 samples too much
SampleTrimmer.trim_from_beginning(mic2.get_audio(), timedelta(microseconds=8639))

audio3_original = Audio(filepath="classroom_2024-11-28_15-00-00-000000_pi3_audio.wav")
mic3.set_audio(audio3_original)
mic3.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 0))
# 1720 samples too much
SampleTrimmer.trim_from_beginning(mic3.get_audio(), timedelta(microseconds=39002))

audio4_original = Audio(filepath="classroom_2024-11-28_15-00-00-000000_pi4_audio.wav")
mic4.set_audio(audio4_original)
mic4.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 0))
# 742 samples too much
SampleTrimmer.trim_from_beginning(mic4.get_audio(), timedelta(microseconds=16825))

for mic in environment.get_mics():
    audio = mic.get_audio()
    # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)

for mic in environment.get_mics():
    audio = mic.get_audio()
    # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()

SampleRateConverter.convert_all_to_lowest_sample_rate(environment)

SampleTrimmer.sync_environment(environment)
# SampleTrimmer.slice_all_from_to(
#     environment, timedelta(seconds=0), timedelta(seconds=25)
# )

for mic in environment.get_mics():
    audio = mic.get_audio()
    # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()

# frequency_filter_chain = FrequencyFilterChain()
# frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=2000, order=5))
# for mic in environment.get_mics():
# frequency_filter_chain.apply(mic.get_audio())

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)

for mic in environment.get_mics():
    audio = mic.get_audio()
    # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()

# NoiseReducer.reduce_all_noise(environment)

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)

for mic in environment.get_mics():
    audio = mic.get_audio()
    # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()

algorithm_choice = "threshold"
all_multilaterations = []
n_sound_sources = 1
# environment.chunk_audio_signals_by_duration(chunk_duration=timedelta(milliseconds=1000))

# result_dict = environment.multilaterate(
#     algorithm=algorithm_choice,
#     number_of_sound_sources=n_sound_sources,
#     threshold=0.3,
# )
# all_multilaterations.append(result_dict)

# for i, object in enumerate(all_multilaterations):
#     print(dict[object])

# multilaterate_plot(environment, all_multilaterations)


# nmf = NonNegativeMatrixFactorization(sample_rate=44100, n_components=n_sound_sources)
# all_sound_sources_nmf = nmf.experimental_run_for_all_audio_in_environment(environment)
all_sound_sources_nmf = {
    mic1: [
        audio1_original,
    ],
    mic2: [audio2_original],
    mic3: [audio3_original],
    mic4: [audio4_original],
}

for i_sound_src in range(n_sound_sources):
    # for mic in environment.get_mics():
    #     mic.set_audio(all_sound_sources_nmf[mic][i_sound_src])
    # for mic in environment.get_mics():
    #     audio = mic.get_audio()
    #     # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    #     # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    #     # audio.play()
    # AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)
    environment.chunk_audio_signals_by_duration(
        chunk_duration=timedelta(milliseconds=1000)
    )
    result_dict = environment.multilaterate(
        algorithm=algorithm_choice,
        number_of_sound_sources=n_sound_sources,
        threshold=0.05,
    )
    all_multilaterations.append(result_dict)

# Reset audio to original audio
mic1.set_audio(audio1_original)
mic2.set_audio(audio2_original)
mic3.set_audio(audio3_original)
mic4.set_audio(audio4_original)
# environment.chunk_audio_signals_by_duration(chunk_duration=timedelta(milliseconds=1000))

result_dict = environment.multilaterate(
    algorithm=algorithm_choice,
    number_of_sound_sources=n_sound_sources,
    threshold=0.5,
)


for i, object in enumerate(all_multilaterations):
    print(dict[object])

multilaterate_plot(environment, all_multilaterations)
