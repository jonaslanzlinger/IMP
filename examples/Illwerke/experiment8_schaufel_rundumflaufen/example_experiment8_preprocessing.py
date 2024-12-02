import os
from datetime import datetime, timedelta

from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.visualization.wave_plot import wave_plot

# Create simulation and add an environment with 4 microphones
simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Machine Environment", [(0, 0), (0, 10), (10, 10), (10, 0)]
)
mic1 = environment1.add_microphone(8.61, 2, "mic1")
mic2 = environment1.add_microphone(8.61, 5.89, "mic2")
mic3 = environment1.add_microphone(2, 5.89, "mic3")
mic4 = environment1.add_microphone(2, 2, "mic4")

# Add audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
audio1_filepath = "output_MIC1_2024-11-07_15-04-14_893209.wav"
mic1.set_audio(Audio(filepath=audio1_filepath))
mic1.set_recording_start_time(datetime(2024, 11, 7, 15, 4, 14, microsecond=893209))

audio2_filepath = "output_MIC2_2024-11-07_15-04-14_196723.wav"
mic2.set_audio(Audio(filepath=audio2_filepath))
mic2.set_recording_start_time(datetime(2024, 11, 7, 15, 4, 14, microsecond=196723))

audio3_filepath = "output_MIC3_2024-11-07_15-04-15_101837_unten.wav"
mic3.set_audio(Audio(filepath=audio3_filepath))
mic3.set_recording_start_time(datetime(2024, 11, 7, 15, 4, 15, microsecond=101837))

audio4_filepath = "output_MIC4_2024-11-07_15-04-14_633864.wav"
mic4.set_audio(Audio(filepath=audio4_filepath))
mic4.set_recording_start_time(datetime(2024, 11, 7, 15, 4, 14, microsecond=633864))

# Slice all audio to keep shorter
# TODO: use entire length for preprocessing
for mic in environment1.get_mics():
    SampleTrimmer.slice_from_to(
        mic.get_audio(),
        start_time=timedelta(seconds=12),
        end_time=timedelta(seconds=20),
    )
    # mic.get_audio().play()

# Ensure that all audio files are of same sample rate
SampleRateConverter.convert_all_to_lowest_sample_rate(environment1)

# Sync audio recordings based on their recording start timestamps
# TODO: artificially adjust samples to ensure that they actually are in sync (hardware limitation)
SampleTrimmer.sync_environment(environment1)

spectrogram_plot(
    mic1.get_audio().get_audio_signal_unchunked(),
    mic1.get_audio().get_sample_rate(),
)

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=5000, order=5))
frequency_filter_chain.apply(mic1.get_audio())
frequency_filter_chain.apply(mic2.get_audio())
frequency_filter_chain.apply(mic3.get_audio())
frequency_filter_chain.apply(mic4.get_audio())

# spectrogram_plot(
#     mic1.get_audio().get_audio_signal_unchunked(),
#     mic1.get_audio().get_sample_rate(),
# )
#
# wave_plot(
#     mic1.get_audio().get_audio_signal_unchunked(),
#     mic1.get_audio().get_sample_rate(),
# )
#
# for mic in environment1.get_mics():
#     print(mic.get_audio().get_num_samples())

# TODO: add better preprocessing to split sounds
nmf = NonNegativeMatrixFactorization(sample_rate=mic1.get_audio().get_sample_rate())
audio_signals_nmf = nmf.experimental_run_for_all_audio_in_environment(
    environment=environment1
)

# for mic, audio_list in audio_signals_nmf.items():
#     print(f"Mic: {mic.get_name()}")
#     for idx, audio in enumerate(audio_list):
#         print(f"  Audio {idx + 1}: {len(audio.get_audio_signal_unchunked())} samples")
#         # mic.set_audio(audio, reset_recording_start_time=True)
#         audio.export(f"nmf_{mic.get_name()}_{idx + 1}.wav")
