from pysoundlocalization.core.Audio import Audio
from datetime import timedelta
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.visualization.environment_wave_plot import (
    environment_wave_plot,
)
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.util.simulate_noise_util import generate_audios
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.preprocessing.NotchFilter import NotchFilter
from pysoundlocalization.preprocessing.HighCutFilter import HighCutFilter
from datetime import datetime
from pysoundlocalization.visualization.environment_spectrogram_plot import (
    environment_spectrogram_plot,
)
import copy

"""
This script demonstrates the localization of two moving sound sources within a classroom environment.

Note, uncomment the respective code parts to see the results of the individual steps.
"""

# ##################
# Global Variables #
# ##################

original_audios = [None, None, None, None]

# #############
# DEMO SCRIPT #
# #############

# #######################
# PHASE 1 - ENVIRONMENT #
# #######################
print("PHASE 1 - ENVIRONMENT")

simulation = Simulation.create()

environment = simulation.add_environment(
    name="Simulation",
    vertices=[
        (0, 10),
        (50, 0),
        (100, 10),
        (100, 25),
        (110, 25),
        (110, 85),
        (100, 85),
        (100, 100),
        (0, 100),
    ],
)

mic_1 = environment.add_microphone(x=5, y=15)
mic_2 = environment.add_microphone(x=95, y=15)
mic_3 = environment.add_microphone(x=95, y=95)
mic_4 = environment.add_microphone(x=5, y=95)

# ##############################
# PHASE 1.5 - Audio Generation #
# ##############################
print("PHASE 1.5 - Audio Generation")

buzzer = Audio(filepath="../../data/00_SOUND_BANK/sounds/buzzer_sound.wav")
knock = Audio(filepath="../../data/00_SOUND_BANK/sounds/knock_sound.wav")
# print(f"Sound 1 duration: {buzzer.get_sample_rate()}")
# print(f"Sound 2 duration: {knock.get_sample_rate()}")
lowest_sample_rate = SampleRateConverter.convert_list_of_audios_to_lowest_sample_rate(
    audio_list=[buzzer, knock]
)
source_positions = [
    {
        "sound": buzzer,
        int(lowest_sample_rate * 1): (50, 85),
        int(lowest_sample_rate * 3): (50, 85),
        int(lowest_sample_rate * 5): (50, 85),
        int(lowest_sample_rate * 7): (50, 85),
    },
    {
        "sound": knock,
        int(lowest_sample_rate * 1.5): (10, 50),
        int(lowest_sample_rate * 2.3): (25, 50),
        int(lowest_sample_rate * 3.7): (40, 50),
        int(lowest_sample_rate * 4.2): (55, 50),
        int(lowest_sample_rate * 4.6): (70, 50),
        int(lowest_sample_rate * 5.5): (85, 50),
        int(lowest_sample_rate * 6.0): (100, 50),
    },
]

n_sound_sources = len(source_positions)

factory_sound_audio = Audio(
    filepath="../../data/00_SOUND_BANK/noise/factory_sound.wav",
    convert_to_sample_rate=lowest_sample_rate,
)
# factory_sound_audio.play()
# print(f"Background noise duration: {factory_sound_audio.get_duration()}")
# print(f"sample rate: {factory_sound_audio.get_sample_rate()}")

environment = generate_audios(
    environment=environment,
    sample_rate=lowest_sample_rate,
    source_sources=source_positions,
    background_noise=factory_sound_audio,
    loudness_mix=[0.3, 0.3, 1.0],
    default_sound_duration=0.3,
)

# The following commented code is needed in case the audio files are loaded instead of generated
# for i, mic in enumerate(environment.get_mics()):
#     audio = Audio(filepath=f"audio_{i+1}.wav")
#     mic.set_audio(audio=audio)
#     mic.set_recording_start_time(start_time=datetime.now())
# SampleRateConverter.convert_all_to_lowest_sample_rate(environment=environment)
# SampleTrimmer.sync_environment(environment=environment)

original_audios = [None, None, None, None]

for i, mic in enumerate(environment.get_mics()):
    original_audios[i] = copy.deepcopy(mic.get_audio())

# ##########################
# PHASE 2 - PRE-PROCESSING #
# ##########################
print("PHASE 2 - PRE-PROCESSING")

AudioNormalizer.normalize_environment_to_max_amplitude(
    environment=environment, max_amplitude=1.0
)

environment_wave_plot(environment=environment)
environment_spectrogram_plot(environment=environment)

frequency_filter_chain = FrequencyFilterChain()

frequency_filter_chain.add_filter(filter=LowCutFilter(cutoff_frequency=500, order=5))
frequency_filter_chain.add_filter(
    filter=NotchFilter(target_frequency=2760, quality_factor=10)
)
frequency_filter_chain.add_filter(filter=HighCutFilter(cutoff_frequency=4000, order=5))

for mic in environment.get_mics():
    audio = mic.get_audio()
    frequency_filter_chain.apply(audio=audio)
    AudioNormalizer.normalize_audio_to_max_amplitude(audio=audio, max_amplitude=1.0)
    # NoiseReducer.reduce_noise(audio=audio)
    # AudioNormalizer.normalize_audio_to_max_amplitude(audio=audio, max_amplitude=1.0)

# environment_wave_plot(environment=environment)
# environment_spectrogram_plot(environment=environment)

for mic in environment.get_mics():
    NoiseReducer.reduce_noise(audio=mic.get_audio())
    AudioNormalizer.normalize_audio_to_max_amplitude(
        audio=mic.get_audio(), max_amplitude=1.0
    )

# environment_wave_plot(environment=environment)
# environment_spectrogram_plot(environment=environment)

n_sound_sources = 2
sample_rate = environment.get_sample_rate()

nmf = NonNegativeMatrixFactorization(
    number_of_sources_to_extract=n_sound_sources,
    sample_rate=sample_rate,
)
all_sound_sources_nmf = nmf.run_for_environment(environment=environment)

for i_sound_src in range(n_sound_sources):
    for mic in environment.get_mics():
        audio = all_sound_sources_nmf[mic][i_sound_src]
        mic.set_audio(audio=audio)

    AudioNormalizer.normalize_environment_to_max_amplitude(
        environment=environment, max_amplitude=1.0
    )

    # environment_wave_plot(environment=environment)
    # environment_spectrogram_plot(environment=environment)

# ####################
# PHASE 3 - Localize #
# ####################
print("PHASE 3 - LOCALIZE")

algorithm_choice = "threshold"
sources_positions = []
current_audio_index = 0

for i_sound_src in range(n_sound_sources):
    for mic in environment.get_mics():
        audio = all_sound_sources_nmf[mic][i_sound_src]
        mic.set_audio(audio=audio)

    AudioNormalizer.normalize_environment_to_max_amplitude(
        environment=environment, max_amplitude=1.0
    )

    environment.chunk_audio_signals_by_duration(
        chunk_duration=timedelta(milliseconds=1000)
    )

    source_pos = environment.localize(
        algorithm=algorithm_choice,
        threshold=0.5,
    )
    sources_positions.append(source_pos)

for i, mic in enumerate(environment.get_mics()):
    mic.set_audio(audio=original_audios[0])
    mic.set_recording_start_time(start_time=datetime.now())

# ###############
# FINAL RESULTS #
# ###############
print("FINAL RESULTS")

multilaterate_plot(environment=environment, dict_list=sources_positions)
