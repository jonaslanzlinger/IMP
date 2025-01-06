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

simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Classroom", [(0, 0), (10.105, 0), (10.105, 11.96), (0, 11.96)]
)
mic1 = environment1.add_microphone(1, 1)
mic2 = environment1.add_microphone(8.61, 1)
mic3 = environment1.add_microphone(8.61, 10.96)
mic4 = environment1.add_microphone(1, 10.92)

audio_file1 = "example_audio/trimmed_2024-11-28_15-00-00-037437_pi1_audio.wav"
audio1 = Audio(filepath=audio_file1, convert_to_sample_rate=44100)
mic1.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 37437))
mic1.set_audio(audio1)

audio_file2 = "example_audio/trimmed_2024-11-28_15-00-00-029037_pi2_audio.wav"
audio2 = Audio(filepath=audio_file2, convert_to_sample_rate=44100)
mic2.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 29037))
mic2.set_audio(audio2)

audio_file3 = "example_audio/trimmed_2024-11-28_15-00-00-000000_pi3_audio.wav"
audio3 = Audio(filepath=audio_file3, convert_to_sample_rate=44100)
mic3.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 0))
mic3.set_audio(audio3)

audio_file4 = "example_audio/trimmed_2024-11-28_15-00-00-022696_pi4_audio.wav"
audio4 = Audio(filepath=audio_file4, convert_to_sample_rate=44100)
mic4.set_recording_start_time(datetime(2024, 11, 28, 15, 0, 0, 22696))
mic4.set_audio(audio4)

environment1 = SampleTrimmer.sync_environment(environment1)

SampleTrimmer.slice_all_from_to(
    environment1, timedelta(seconds=7.5), timedelta(seconds=16)
)

AudioNormalizer.normalize_to_max_amplitude(environment1, 0.8)

wave_plot(
    audio1.get_audio_signal_unchunked(),
    audio1.get_sample_rate(),
)

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=2000, order=5))
# # frequency_filter_chain.apply(audio1)
# # frequency_filter_chain.apply(audio2)
# # frequency_filter_chain.apply(audio3)
# # frequency_filter_chain.apply(audio4)

# # TODO: when I remove noisereducer, NMF doesn't work anymore (two splits, but cannot be used)
# NoiseReducer.reduce_all_noise(environment1)

spectrogram_plot(
    audio1.get_audio_signal_unchunked(),
    audio1.get_sample_rate(),
)

nmf = NonNegativeMatrixFactorization(sample_rate=audio1.get_sample_rate())
all_audio_nmf = nmf.experimental_run_for_all_audio_in_environment(environment1)
print(all_audio_nmf)

for mic, audio_list in all_audio_nmf.items():
    print(f"Mic: {mic.get_name()}")
    for idx, audio in enumerate(audio_list):
        print(f"  Audio {idx + 1}: {len(audio.get_audio_signal_unchunked())} samples")
        mic.set_audio(audio, reset_recording_start_time=False)
        wave_plot(
            audio.get_audio_signal_unchunked(),
            audio.get_sample_rate(),
            "nmf_environment_" + str(mic.get_name()) + "_" + str(idx + 1),
        )
        # audio.play()

NoiseReducer.reduce_all_noise(environment1)
AudioNormalizer.normalize_to_max_amplitude(environment1, 0.8)

wave_plot(
    audio1.get_audio_signal_unchunked(),
    audio1.get_sample_rate(),
)

environment1.chunk_audio_signals_by_duration(
    chunk_duration=timedelta(milliseconds=1000)
)

algorithm_choice = "threshold"

dict = environment1.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.035
)

for i, object in enumerate(dict):
    print(dict[object])

for i, mic in enumerate(environment1.get_mics()):
    print(f"MIC{i+1} has {mic.get_audio().get_num_chunks()} chunks")
    # play
    # mic.get_audio().play()

multilaterate_plot(environment1, dict)
