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
from pysoundlocalization.visualization.wave_plot import wave_plot_environment
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.util.simulate_noise_util import generate_audios
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.preprocessing.NotchFilter import NotchFilter
from pysoundlocalization.preprocessing.HighCutFilter import HighCutFilter
from datetime import datetime
from pysoundlocalization.visualization.spectrogram_plot import (
    spectrogram_plot_environment,
)
from pysoundlocalization.visualization.wave_plot import wave_plot
import os
import copy


# ##################
# Global Variables #
# ##################
current_file_name = os.path.splitext(__file__)[0]
original_audios = [None, None, None, None]

# #############
# DEMO SCRIPT #
# #############

# #######################
# PHASE 1 - ENVIRONMENT #
# #######################
print("PHASE 1 - ENVIRONMENT")

# Create a Simulation: The Simulation is the main object
# that contains all the Environments and Microphones,
# along with the Audio objects that are used.
simulation = Simulation.create()

# Add an Environment to the Simulation: The Environment
# is the object that contains the Microphones and the
# Audio objects. The Environment is defined by a list of
# points that represent the vertices of a polygon.
environment = simulation.add_environment(
    "Simulation",
    [
        (0, 10),
        (80, 0),
        (100, 50),
        (110, 130),
        (50, 130),
        (0, 120),
        (-60, 20),
    ],
)

# Visualize the Environment
environment.visualize()

# Add Microphones to the Environment: The Microphones are
# the objects that hold the Audio objects. The Microphones
# are placed at specific positions in the Environment,
# that are defined by the x and y coordinates.
mic_1 = environment.add_microphone(-50, 25)
mic_2 = environment.add_microphone(78, 4)
mic_3 = environment.add_microphone(105, 126)
mic_4 = environment.add_microphone(1, 118)

# Visualize the Environment with the Microphones
environment.visualize()

# ##############################
# PHASE 1.5 - Audio Generation #
# ##############################
print("PHASE 1.5 - Audio Generation")

# In this phase, the Audio objects are generated.
# This can be helpful for testing purposes, as it
# allows to generate Audio objects with specific
# properties without the need to have recordings.
# The generation simulates the recording by creating
# a np.ndarray with values derived by the Microphone
# positions and the sound sources positions.

# Optionally: Load custom .wav sound files
# If no sound files are loaded, the sounds will be generated
# in such a way that they are maximally distinguishable.
sound_1 = Audio(filepath="../sound_bank/sounds/buzzer_sound.wav")
sound_2 = Audio(filepath="../sound_bank/sounds/knock_sound.wav")

# Normalize the audio signals to have a maximum amplitude of 1.0
AudioNormalizer.normalize_audio_to_max_amplitude(sound_1, 1.0)
AudioNormalizer.normalize_audio_to_max_amplitude(sound_2, 1.0)

# Retrieve some information about the created Audio objects
# print(f"Sound 1 duration: {sound_1.get_duration()}")
# print(f"Sound 2 sample rate: {sound_2.get_sample_rate()}")

# Visualize the Audio objects
wave_plot(
    audio_signal=sound_1.get_audio_signal_unchunked(),
    sample_rate=sound_1.get_sample_rate(),
)
wave_plot(
    audio_signal=sound_2.get_audio_signal_unchunked(),
    sample_rate=sound_2.get_sample_rate(),
)

# Optionally play the Audio objects (POTENTIALLY LOUD!!!)
### sound_1.play()
### sound_2.play()

# Ensure that all Audio objects have the same sample rate
lowest_sample_rate = SampleRateConverter.convert_list_of_audios_to_lowest_sample_rate(
    [sound_1, sound_2]
)

# Specify in this array of dictionaries the sound sources
# and their positions in the environment. Each dictionary
# defines one sound source. The keys of the
# dictionaries are the sample index indicating the start
# of the respective sound. The values are tuples with the
# position at this sample index.
source_positions = [
    {
        "sound": sound_1,  # None if no sound file is loaded
        int(lowest_sample_rate * 1): (50, 85),
        int(lowest_sample_rate * 3): (50, 85),
        int(lowest_sample_rate * 5): (100, 85),
        int(lowest_sample_rate * 7): (100, 85),
    },
    {
        "sound": sound_2,  # None if no sound file is loaded
        int(lowest_sample_rate * 2.0): (10, 50),
        int(lowest_sample_rate * 4.0): (40, 50),
        int(lowest_sample_rate * 6.0): (60, 50),
    },
]

# Additionally, a background noise can be added to the
# environment. This can be useful to simulate a more
# realistic environment. The background noise is added
# to all Microphones in the Environment.
noise = Audio(
    filepath="../sound_bank/noise/factory_sound.wav",
)
noise.resample_audio(lowest_sample_rate)

# Normalize the audio signal to have a maximum amplitude of 1.0
AudioNormalizer.normalize_audio_to_max_amplitude(noise, 1.0)

# Visualize the noise Audio object
wave_plot(
    audio_signal=noise.get_audio_signal_unchunked(),
    sample_rate=noise.get_sample_rate(),
)

# Retrieve some information about the created Audio objects
# print(f"Noise duration: {noise.get_duration()}")
# print(f"Noise sample rate: {noise.get_sample_rate()}")

# Optionally play the Audio object (POTENTIALLY LOUD!!!)
### noise.play()

# Obtain the number of sound sources, as this is needed
# to know how many sources to extract in the NMF step.
n_sound_sources = len(source_positions)

# Generate the Audio objects
# Pass the environment, the sample rate, the source positions,
# the background noise, the loudness mix, and the default sound duration.
# The loudness mix is a list of <n_sound_sources + n_noise> floats that define
# the mixing levels for the sound sources and the noise.
# The default sound duration is the duration of the sound in seconds if no
# sound file is provided.
# Note: the output mix is normalized to have a maximum amplitude of 1.0
environment = generate_audios(
    environment=environment,
    sample_rate=lowest_sample_rate,
    source_sources=source_positions,
    background_noise=noise,
    loudness_mix=[0.6, 0.6, 0.8],
    default_sound_duration=0.3,
)

# The following commented code is the code needed for loading
# the audio files instead of generating them. This can be useful
# for debugging purposes, as it allows to load the same audio
# files every time the script is run. Note that the generation of
# the audio files needs to be commented out in order to load the
# audio files correctly.
# for i, mic in enumerate(environment.get_mics()):
#     audio = Audio(filepath=f"{current_file_name}_audio_{i+1}.wav")
#     mic.set_audio(audio)
#     mic.set_recording_start_time(datetime.now())
# SampleRateConverter.convert_all_to_lowest_sample_rate(environment)
# Sync the environment because the audio files might have different lengths,
# recording times, or sample rates, which causes issues in the processing.
# SampleTrimmer.sync_environment(environment)
# IMPORTANT: When loading the audio files, the number of sound sources
# needs to be set manually, as the audio files do not contain this information.
# This is necessary for the NMF step.
# n_sound_sources = 2

# Visualize the Audio objects of the Environment
wave_plot_environment(environment=environment)
spectrogram_plot_environment(environment=environment)

# Save a copy of the original Audio objects for later use
for i, mic in enumerate(environment.get_mics()):
    original_audios[i] = copy.deepcopy(mic.get_audio())

    # Optionally play the Audio objects of the original audio (POTENTIALLY LOUD!!!)
    ### original_audios[i].play()

# Optionally: Save the generated Audio objects
# to load them at a later point in time, instead of
# generating them again. Also useful for debugging purposes.
for i, audio in enumerate(original_audios):
    audio.export(f"{current_file_name}_audio_{i + 1}.wav")


# ##########################
# PHASE 2 - PRE-PROCESSING #
# ##########################
print("PHASE 2 - PRE-PROCESSING")

# All filters can be added to a FrequencyFilterChain object.
# The FrequencyFilterChain object can then be applied to the
# Audio objects of the Microphones in the Environment.
# The order of the filters in the FrequencyFilterChain object
# defines the order in which the filters are applied to the
# Audio objects => FIFO principle.
frequency_filter_chain = FrequencyFilterChain()

frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=500, order=5))
frequency_filter_chain.add_filter(NotchFilter(target_frequency=2760, quality_factor=10))
frequency_filter_chain.add_filter(HighCutFilter(cutoff_frequency=4000, order=5))

# Loop over all Microphones in the Environment and apply the
# FrequencyFilterChain to the Audio objects.
for mic in environment.get_mics():
    audio = mic.get_audio()
    frequency_filter_chain.apply(audio)
    # It is important to normalize the audio signal after applying the filters
    # to ensure that the audio signal has a maximum amplitude of 1.0.
    AudioNormalizer.normalize_audio_to_max_amplitude(audio, 1.0)

# Visualize the Audio objects of the Environment after applying the filters
wave_plot_environment(environment=environment)
spectrogram_plot_environment(environment=environment)

# Use the NoiseReducer to reduce the noise in the Audio objects.
# The NoiseReducer might lower the loudness of the sound sources
# as well, so it is important to normalize the audio signals
# after applying the NoiseReducer.
for mic in environment.get_mics():
    audio = mic.get_audio()
    NoiseReducer.reduce_noise(audio)
    AudioNormalizer.normalize_audio_to_max_amplitude(audio, 1.0)

# Visualize the Audio objects of the Environment after reducing the noise
wave_plot_environment(environment=environment)
spectrogram_plot_environment(environment=environment)

# The NMF algorithm is used to extract the sound sources from the
# Audio objects of the Microphones. The number of sound sources
# needs to be specified. The NMF algorithm is applied to the
# Audio objects of the Microphones in the Environment.
# Note: This is a computationally expensive step.
sample_rate = environment.get_sample_rate()
nmf = NonNegativeMatrixFactorization(
    number_of_sources_to_extract=n_sound_sources,
    sample_rate=sample_rate,
)
# The NMF algorithm returns a dictionary with the Microphones as keys, and the
# extracted sound sources as values.
all_sound_sources_nmf = nmf.run_for_environment(environment=environment)

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
    wave_plot_environment(environment=environment)
    spectrogram_plot_environment(environment=environment)

    # Optionally play the Audio objects of the finished processed audio (POTENTIALLY LOUD!!!)
    ### environment.get_mics()[0].get_audio().play()


# ####################
# PHASE 3 - Localize #
# ####################
print("PHASE 3 - LOCALIZE")

# To localize the sound sources, the TDOA (Time Difference of Arrival)
# between the Microphones needs to be calculated. This is done by
# either the "threshold" algorithm, where the timestamp of the peak is
# used, where a certain threshold is exceeded, or the "GCC-PHAT" algorithm
# (Generalized-Cross-Correlation with Phase Transform), where the cross-
# correlation of the signals is calculated. That means that the TDOA is
# calculated by the time shift of the signals that maximizes the cross-
# correlation of the estimated signal and the reference signal.

# If we have moving sound sources, the chunking of the audio signals needs
# to be applied. An example of this process is demonstrated in the following
# code snippet. The chunking of the audio signals is done by specifying the
# chunk duration in milliseconds.

# Note: "threshold" algorithm is used for demonstration purposes, as this
# algorithm is faster than the "GCC-PHAT" algorithm.
algorithm_choice = "threshold"
# The sources_positions list will contain the estimated positions of the
# sound sources after the multilateration step.
sources_positions = []
# This is the index of the current audio source that is being multilaterated
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

    # Chunk the audio signals by the specified duration
    environment.chunk_audio_signals_by_duration(
        chunk_duration=timedelta(milliseconds=1000)
    )

    # Multilaterate the sound source
    source_pos = environment.multilaterate(
        algorithm=algorithm_choice,
        number_of_sound_sources=1,
        threshold=0.5,
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
