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
from simulate_noise_util import extension
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter

simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Simulation", [(0, 0), (100, 0), (150, 50), (100, 100), (0, 100)]
)
mic1 = environment1.add_microphone(10, 10)
mic2 = environment1.add_microphone(90, 10)
mic3 = environment1.add_microphone(90, 90)
mic4 = environment1.add_microphone(10, 90)

sound1 = Audio(filepath="buzzer.wav")
sound2 = Audio(filepath="hammer.wav")
print(f"Sound 1 duration: {sound1.get_sample_rate()}")
print(f"Sound 2 duration: {sound2.get_sample_rate()}")
lowest_sample_rate = SampleRateConverter.convert_list_of_audios_to_lowest_sample_rate(
    [sound1, sound2]
)
source_positions = [
    {
        int(lowest_sample_rate * 1): (40, 80, sound1),
        int(lowest_sample_rate * 2.5): (40, 80, sound1),
        int(lowest_sample_rate * 4.1): (40, 80, sound1),
        int(lowest_sample_rate * 5.5): (40, 80, sound1),
        int(lowest_sample_rate * 7): (40, 80, sound1),
    },
    {
        int(lowest_sample_rate * 1.6): (75, 20, sound2),
        int(lowest_sample_rate * 2.0): (85, 27, sound2),
        int(lowest_sample_rate * 3.1): (98, 34, sound2),
        int(lowest_sample_rate * 3.6): (105, 41, sound2),
        int(lowest_sample_rate * 4.5): (112, 49, sound2),
        int(lowest_sample_rate * 5.0): (122, 55, sound2),
        int(lowest_sample_rate * 6.0): (130, 60, sound2),
    },
]

audio_background_noise = Audio(filepath="factory.wav")
print(f"Background noise duration: {audio_background_noise.get_duration()}")

environment1 = extension(
    environment=environment1,
    sample_rate=lowest_sample_rate,
    source_sources=source_positions,
    background_noise=audio_background_noise,
    loudness_mix=[0.1, 0.1, 1.0],
)

audio1 = mic1.get_audio()
audio2 = mic2.get_audio()
audio3 = mic3.get_audio()
audio4 = mic4.get_audio()

AudioNormalizer.normalize_environment_to_max_amplitude(environment1, 0.8)


audio1.play()

# wave_plot(
#     audio1.get_audio_signal(),
#     audio1.get_sample_rate(),
# )
# wave_plot(
#     audio2.get_audio_signal(),
#     audio2.get_sample_rate(),
# )
# wave_plot(
#     audio3.get_audio_signal(),
#     audio3.get_sample_rate(),
# )
# wave_plot(
#     audio4.get_audio_signal(),
#     audio4.get_sample_rate(),
# )

spectrogram_plot(
    audio_signal=audio1.get_audio_signal_unchunked(),
    sample_rate=audio1.get_sample_rate(),
)

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=300, order=5))
for mic in environment1.get_mics():
    frequency_filter_chain.apply(mic.get_audio())

spectrogram_plot(
    audio_signal=audio1.get_audio_signal_unchunked(),
    sample_rate=audio1.get_sample_rate(),
)

NoiseReducer.reduce_noise(audio=audio1)

spectrogram_plot(
    audio_signal=audio1.get_audio_signal_unchunked(),
    sample_rate=audio1.get_sample_rate(),
)

nmf = NonNegativeMatrixFactorization(
    number_of_sources_to_extract=2, sample_rate=audio1.get_sample_rate()
)
all_audio_nmf = nmf.experimental_run_for_all_audio_in_environment(environment1)

algorithm_choice = "threshold"

all_dicts = []

current_audio_index = 0

mic1.set_audio(all_audio_nmf[mic1][0])
mic2.set_audio(all_audio_nmf[mic2][0])
mic3.set_audio(all_audio_nmf[mic3][0])
mic4.set_audio(all_audio_nmf[mic4][0])
AudioNormalizer.normalize_environment_to_max_amplitude(environment1, 0.8)
environment1.chunk_audio_signals_by_duration(chunk_duration=timedelta(milliseconds=500))
result_dict = environment1.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.3
)
all_dicts.append(result_dict)

mic1.set_audio(all_audio_nmf[mic1][1])
mic2.set_audio(all_audio_nmf[mic2][1])
mic3.set_audio(all_audio_nmf[mic3][1])
mic4.set_audio(all_audio_nmf[mic4][1])
AudioNormalizer.normalize_environment_to_max_amplitude(environment1, 0.8)
environment1.chunk_audio_signals_by_duration(chunk_duration=timedelta(milliseconds=500))
result_dict = environment1.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.3
)
all_dicts.append(result_dict)

# mic1.set_audio(all_audio_nmf[mic1][2])
# mic2.set_audio(all_audio_nmf[mic2][2])
# mic3.set_audio(all_audio_nmf[mic3][2])
# mic4.set_audio(all_audio_nmf[mic4][2])
# AudioNormalizer.normalize_environment_to_max_amplitude(environment1, 0.8)
# environment1.chunk_audio_signals_by_duration(
#     chunk_duration=timedelta(milliseconds=1000)
# )
# result_dict = environment1.multilaterate(
#     algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.5
# )
# # AudioNormalizer.normalize_to_max_amplitude(environment1, 0.8)
# # result_dict = environment1.multilaterate(
# #     algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.2
# # )
# all_dicts.append(result_dict)

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
