from datetime import datetime, timedelta
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.visualization.environment_wave_plot import (
    environment_wave_plot,
)
from pysoundlocalization.visualization.environment_spectrogram_plot import (
    environment_spectrogram_plot,
)
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer

"""
This script demonstrates the localization of a moving clapping noise within a classroom environment.
The background noise is reduced to isolate the clapping noise.

The purpose of this demo is to show how latencies in audio signal recordings are influencing the
multilateration result. The audio signals are recorded by four Raspberry Pi's, which are not
synchronized. The audio signals are recorded with different latencies. See that the computed sound source
positions are not correct due to these latencies.
"""

simulation = Simulation.create()

environment = simulation.add_environment(
    "Classroom Simulation", [(0, 0), (10.1, 0), (10.1, 11.96), (0, 11.96)]
)

mic1 = environment.add_microphone(1, 1, name="Microphone-1")
mic2 = environment.add_microphone(9.1, 1, name="Microphone-2")
mic3 = environment.add_microphone(9.1, 10.96, name="Microphone-3")
mic4 = environment.add_microphone(1, 10.92, name="Microphone-4")

audio1_original = Audio(
    filepath="../../data/06_classroom/pi1_audio_2024-11-28_15-00-00-037437.wav"
)
mic1.set_audio(audio1_original)
mic1.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 37437))

audio2_original = Audio(
    filepath="../../data/06_classroom/pi2_audio_2024-11-28_15-00-00-029037.wav"
)
mic2.set_audio(audio2_original)
mic2.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 29037))

audio3_original = Audio(
    filepath="../../data/06_classroom/pi3_audio_2024-11-28_15-00-00-000000.wav"
)
mic3.set_audio(audio3_original)
mic3.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 0))

audio4_original = Audio(
    filepath="../../data/06_classroom/pi4_audio_2024-11-28_15-00-00-022696.wav"
)
mic4.set_audio(audio4_original)
mic4.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 22696))

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1)
SampleRateConverter.convert_all_to_lowest_sample_rate(environment)

SampleTrimmer.sync_environment(environment)
SampleTrimmer.slice_all_from_to(
    environment, timedelta(seconds=5), timedelta(seconds=10)
)

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=2000, order=5))
for mic in environment.get_mics():
    frequency_filter_chain.apply(mic.get_audio())

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1)

NoiseReducer.reduce_all_noise(environment)

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1)

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
        mic.set_audio(audio)
    AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1.0)
    environment_wave_plot(environment=environment)
    environment_spectrogram_plot(environment=environment)

algorithm_choice = "threshold"
sources_positions = []
current_audio_index = 0

for i_sound_src in range(n_sound_sources):
    print(f"Multilaterating sound source {i_sound_src + 1} of {n_sound_sources}")

    for mic in environment.get_mics():
        audio = all_sound_sources_nmf[mic][i_sound_src]
        mic.set_audio(audio)

    # Chunk the audio signals by the specified duration
    environment.chunk_audio_signals_by_duration(
        chunk_duration=timedelta(milliseconds=2000)
    )

    # Multilaterate the sound source
    source_pos = environment.localize(
        algorithm=algorithm_choice,
        threshold=0.5,
    )

    # Append the estimated position to the sources_positions list
    sources_positions.append(source_pos)

print("Computed sound source positions:")
print(sources_positions)

# Visualize the final result
multilaterate_plot(environment, sources_positions)
