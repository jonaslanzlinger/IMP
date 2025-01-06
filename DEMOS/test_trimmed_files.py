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
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.visualization.wave_plot import wave_plot_environment
from pysoundlocalization.visualization.spectrogram_plot import (
    spectrogram_plot_environment,
)

simulation = Simulation.create()
environment = simulation.add_environment(
    "Classroom", [(0, 0), (10.105, 0), (10.105, 11.96), (0, 11.96)]
)
mic1 = environment.add_microphone(1, 1)
mic2 = environment.add_microphone(8.61, 1)
mic3 = environment.add_microphone(8.61, 10.96)
mic4 = environment.add_microphone(1, 10.92)

mic1.set_audio(
    Audio(
        filepath="../data/06_classroom/pi1_audio_2024-11-28_15-00-00-037437.wav",
        convert_to_sample_rate=44100,
    )
)
mic1.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 37437))

mic2.set_audio(
    Audio(
        filepath="../data/06_classroom/pi2_audio_2024-11-28_15-00-00-029037.wav",
        convert_to_sample_rate=44100,
    )
)
mic2.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 29037))

mic3.set_audio(
    Audio(
        filepath="../data/06_classroom/pi3_audio_2024-11-28_15-00-00-000000.wav",
        convert_to_sample_rate=44100,
    )
)
mic3.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 0))

mic4.set_audio(
    Audio(
        filepath="../data/06_classroom/pi4_audio_2024-11-28_15-00-00-022696.wav",
        convert_to_sample_rate=44100,
    )
)
mic4.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 22696))

environment = SampleTrimmer.sync_environment(environment)

SampleTrimmer.slice_all_from_to(
    environment, timedelta(seconds=7.5), timedelta(seconds=16)
)

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1)

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=300, order=5))

for mic in environment.get_mics():
    frequency_filter_chain.apply(mic.get_audio())
    AudioNormalizer.normalize_audio_to_max_amplitude(mic.get_audio(), 1.0)

wave_plot_environment(environment=environment)
spectrogram_plot_environment(environment=environment)

for mic in environment.get_mics():
    audio = mic.get_audio()
    NoiseReducer.reduce_noise(audio)
    AudioNormalizer.normalize_audio_to_max_amplitude(audio, 1.0)

wave_plot_environment(environment=environment)
spectrogram_plot_environment(environment=environment)

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

    wave_plot_environment(environment=environment)
    spectrogram_plot_environment(environment=environment)

algorithm_choice = "threshold"

sources_positions = []

current_audio_index = 0

for i_sound_src in range(n_sound_sources):
    print(f"Multilaterating sound source {i_sound_src + 1} of {n_sound_sources}")

    for mic in environment.get_mics():
        audio = all_sound_sources_nmf[mic][i_sound_src]
        mic.set_audio(audio)

    AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1.0)

    environment.chunk_audio_signals_by_duration(
        chunk_duration=timedelta(milliseconds=1000)
    )

    source_pos = environment.multilaterate(
        algorithm=algorithm_choice,
        number_of_sound_sources=1,
        threshold=0.5,
    )

    sources_positions.append(source_pos)

# Visualize the final result
multilaterate_plot(environment, sources_positions)
