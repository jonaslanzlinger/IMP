from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from datetime import datetime
from pysoundlocalization.visualization.environment_spectrogram_plot import (
    environment_spectrogram_plot,
)
from pysoundlocalization.visualization.environment_wave_plot import (
    environment_wave_plot,
)
import copy

"""
This script demonstrates the usage of the NonNegativeMatrixFactorization algorithm
with the library, including the workaround for passing the environment to the NMF.

The script creates an environment with four microphones, where audio data is loaded
consisting of two sound sources without background noises.

The goal is to separate the sound sources and localize them individually.
"""

# ##################
# Global Variables #
# ##################
original_audios = [None, None, None, None]


# #######################
# PHASE 1 - ENVIRONMENT #
# #######################
print("PHASE 1 - ENVIRONMENT")

simulation = Simulation.create()

environment = simulation.add_environment(
    "Simulation",
    [
        (0, 0),
        (120, 0),
        (120, 120),
        (0, 120),
    ],
)

mic_1 = environment.add_microphone(10, 10)
mic_2 = environment.add_microphone(110, 10)
mic_3 = environment.add_microphone(110, 110)
mic_4 = environment.add_microphone(10, 110)

# Load the audio files
audio_1 = Audio(filepath="../../data/17_nmf_example/nmf_example_audio_1.wav")
audio_2 = Audio(filepath="../../data/17_nmf_example/nmf_example_audio_2.wav")
audio_3 = Audio(filepath="../../data/17_nmf_example/nmf_example_audio_3.wav")
audio_4 = Audio(filepath="../../data/17_nmf_example/nmf_example_audio_4.wav")

original_audios[0] = copy.deepcopy(audio_1)
original_audios[1] = copy.deepcopy(audio_2)
original_audios[2] = copy.deepcopy(audio_3)
original_audios[3] = copy.deepcopy(audio_4)

mic_1.set_audio(audio_1)
mic_2.set_audio(audio_2)
mic_3.set_audio(audio_3)
mic_4.set_audio(audio_4)

n_sound_sources = 2

# ##########################
# PHASE 2 - PRE-PROCESSING #
# ##########################
print("PHASE 2 - PRE-PROCESSING")

environment_wave_plot(environment=environment)
environment_spectrogram_plot(environment=environment)

sample_rate = environment.get_sample_rate()
nmf = NonNegativeMatrixFactorization(
    number_of_sources_to_extract=n_sound_sources,
    sample_rate=sample_rate,
)
# The NMF algorithm returns a dictionary with the Microphones as keys, and the
# extracted sound sources as values.
all_sound_sources_nmf = nmf.run_for_environment(
    environment=environment, visualize_results=True
)

# As the NMF algorithm might change the loudness of the individual sound source
# signals, it is important to normalize the audio signals after applying the NMF.
# Therefore, we loop over all sound sources, assign them to the Environment, and
# normalize the Environment to have a maximum amplitude of 1.0.
for i_sound_src in range(n_sound_sources):
    for mic in environment.get_mics():
        audio = all_sound_sources_nmf[mic][i_sound_src]
        mic.set_audio(audio)
    AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1.0)

    # Visualize the individual sound source Audio objects
    environment_wave_plot(environment=environment)
    environment_spectrogram_plot(environment=environment)


# ####################
# PHASE 3 - Localize #
# ####################
print("PHASE 3 - LOCALIZE")

algorithm_choice = "threshold"
sources_positions = []
current_audio_index = 0

# Loop over all isolated sound sources, and assign them to the Microphones
# in the Environment. Then, normalize the Environment to have a maximum
# amplitude of 1.0. Finally, chunk the audio signals by the specified duration
# and multilaterate the sound sources. The estimated positions are appended
# to the sources_positions list.
for i_sound_src in range(n_sound_sources):
    print(f"Multilaterating sound source {i_sound_src + 1} of {n_sound_sources}")

    # Load the audio signals of the sound sources into the Environment
    for mic in environment.get_mics():
        audio = all_sound_sources_nmf[mic][i_sound_src]
        mic.set_audio(audio)

    # Normalize the Environment to have a maximum amplitude of 1.0
    AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1.0)

    # Multilaterate the sound source
    source_pos = environment.localize(
        algorithm=algorithm_choice,
        threshold=0.35,
    )

    # Append the estimated position to the sources_positions list
    sources_positions.append(source_pos)


# ###############
# FINAL RESULTS #
# ###############
print("FINAL RESULTS")

# Because we want to visualize the results, with the original
# Audio objects, we need to load the original Audio objects again
# and assign them to the Microphones in the Environment.
print("Loading original Audio objects")
for i, mic in enumerate(environment.get_mics()):
    audio = original_audios[i]
    mic.set_audio(audio)
    mic.set_recording_start_time(datetime.now())

# Visualize the final result
multilaterate_plot(environment, sources_positions)
