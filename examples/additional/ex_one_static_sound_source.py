from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from datetime import timedelta
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.core.Simulation import Simulation
from datetime import datetime
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.visualization.audio_spectrogram_plot import (
    audio_spectrogram_plot,
)
from pysoundlocalization.visualization.audio_wave_plot import audio_wave_plot

"""
This script demonstrates the localization of a synthetic clap sound within
a water pump environment. The background noise is reduced to isolate the clap noise.

Note, uncomment respective parts to visualize the audio signals and spectrograms at
different stages of the preprocessing part.
"""

# #############
# DEMO SCRIPT #
# #############

# #######################
# PHASE 1 - ENVIRONMENT #
# #######################
print("PHASE 1 - ENVIRONMENT")

simulation = Simulation.create()

environment = simulation.add_environment(
    name="Pump Environment",
    vertices=[
        (0, 2),
        (0, 12),
        (5, 12),
        (5, 14),
        (10, 14),
        (10, 12),
        (20, 12),
        (20, 0),
        (13, 0),
        (13, 2),
        (10, 2),
        (10, 0),
        (5, 0),
        (5, 2),
    ],
)
environment.visualize()

mic1 = environment.add_microphone(x=10.61, y=5)
mic2 = environment.add_microphone(x=10.61, y=8.89)
mic3 = environment.add_microphone(x=4, y=8.89)
mic4 = environment.add_microphone(x=4, y=5)

mic1.set_audio(
    audio=Audio(filepath="../../data/10_pump/pi1_audio_2024-11-07_10-30-45_977581.wav")
)
mic1.set_recording_start_time(start_time=datetime(2024, 11, 7, 10, 30, 45, 977581))

mic2.set_audio(
    audio=Audio(filepath="../../data/10_pump/pi2_audio_2024-11-07_10-30-45_474498.wav")
)
mic2.set_recording_start_time(start_time=datetime(2024, 11, 7, 10, 30, 45, 474498))

mic3.set_audio(
    audio=Audio(filepath="../../data/10_pump/pi3_audio_2024-11-07_10-30-46_550904.wav")
)
mic3.set_recording_start_time(start_time=datetime(2024, 11, 7, 10, 30, 46, 550904))

mic4.set_audio(
    audio=Audio(filepath="../../data/10_pump/pi4_audio_2024-11-07_10-30-45_728052.wav")
)
mic4.set_recording_start_time(start_time=datetime(2024, 11, 7, 10, 30, 45, 728052))

# ##########################
# PHASE 2 - PRE-PROCESSING #
# ##########################
print("PHASE 2 - PRE-PROCESSING")

# Bring all audio files to the same sample rate
SampleRateConverter.convert_all_to_lowest_sample_rate(environment=environment)

# for mic in environment.get_mics():
#     audio = mic.get_audio()
#     audio_wave_plot(
#         audio_signal=audio.get_audio_signal(), sample_rate=audio.get_sample_rate()
#     )
#     audio_spectrogram_plot(
#         audio_signal=audio.get_audio_signal(), sample_rate=audio.get_sample_rate()
#     )
#     audio.play()

SampleTrimmer.sync_environment(environment=environment)
# Isolate the part of the audio signal where the clap sound is present
SampleTrimmer.slice_all_from_to(
    environment=environment,
    start_time=timedelta(seconds=15),
    end_time=timedelta(seconds=20),
)

# Apply a low cut filter to remove low frequency noise of the water pump
frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(filter=LowCutFilter(cutoff_frequency=2000, order=5))
for mic in environment.get_mics():
    frequency_filter_chain.apply(audio=mic.get_audio())

# for mic in environment.get_mics():
#     audio = mic.get_audio()
#     audio_wave_plot(
#         audio_signal=audio.get_audio_signal(), sample_rate=audio.get_sample_rate()
#     )
#     audio_spectrogram_plot(
#         audio_signal=audio.get_audio_signal(), sample_rate=audio.get_sample_rate()
#     )
#     audio.play()

# Reduce noise to further isolate the clap sound
NoiseReducer.reduce_all_noise(environment=environment)

# Normalize the audio signals to the maximum amplitude of 1.0 to ensure
# peak amplitude consistency.
AudioNormalizer.normalize_environment_to_max_amplitude(
    environment=environment, max_amplitude=1.0
)

# for mic in environment.get_mics():
# audio = mic.get_audio()
# audio_wave_plot(
#     audio_signal=audio.get_audio_signal(), sample_rate=audio.get_sample_rate()
# )
# audio_spectrogram_plot(
#     audio_signal=audio.get_audio_signal(), sample_rate=audio.get_sample_rate()
# )
# audio.play()

# ####################
# PHASE 3 - Localize #
# ####################
print("PHASE 3 - LOCALIZE")

algorithm_choice = "threshold"
all_dicts = []
result_dict = environment.localize(algorithm=algorithm_choice, threshold=0.75)
all_dicts.append(result_dict)

# ###############
# FINAL RESULTS #
# ###############
print("FINAL RESULTS")

# for i, object in enumerate(all_dicts):
#     print(dict[object])

multilaterate_plot(environment=environment, dict_list=all_dicts)
