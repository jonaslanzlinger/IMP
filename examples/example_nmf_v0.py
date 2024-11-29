from build.lib.pysoundlocalization.visualization.wave_plot import wave_plot
from examples.example_simple_gcc_phat import sample_rate
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from datetime import timedelta
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.core.Simulation import Simulation
import numpy as np
from datetime import datetime
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
import time

simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Machine Environment", [(0, 0), (0, 10), (10, 10), (10, 0)]
)
mic1 = environment1.add_microphone(8.61, 2)
mic2 = environment1.add_microphone(8.61, 5.89)
mic3 = environment1.add_microphone(2, 5.89)
mic4 = environment1.add_microphone(2, 2)

audio_file1 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC1_2024-11-07_10-30-45_977581.wav"
audio1 = Audio(filepath=audio_file1, convert_to_sample_rate=11025)
mic1.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 977581))
print(audio1.get_duration())

SampleTrimmer.trim_from_beginning(audio1, timedelta(seconds=17))
SampleTrimmer.trim_from_end(audio1, timedelta(seconds=5))

audio_file2 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC2_2024-11-07_10-30-45_474498.wav"
audio2 = Audio(filepath=audio_file2, convert_to_sample_rate=11025)
mic2.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 474498))
print(audio2.get_duration())

SampleTrimmer.trim_from_beginning(audio2, timedelta(seconds=17))
SampleTrimmer.trim_from_end(audio2, timedelta(seconds=5))

audio_file3 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC3_2024-11-07_10-30-46_550904.wav"
audio3 = Audio(filepath=audio_file3, convert_to_sample_rate=11025)
mic3.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 46, 550904))
print(audio3.get_duration())

SampleTrimmer.trim_from_beginning(audio3, timedelta(seconds=17))
SampleTrimmer.trim_from_end(audio3, timedelta(seconds=5))

audio_file4 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC4_2024-11-07_10-30-45_728052.wav"
audio4 = Audio(filepath=audio_file4, convert_to_sample_rate=11025)
mic4.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 728052))
print(audio4.get_duration())

SampleTrimmer.trim_from_beginning(audio4, timedelta(seconds=17))
SampleTrimmer.trim_from_end(audio4, timedelta(seconds=5))


# spectrogram_plot(
#     audio_signal=audio.get_audio_signal_unchunked(),
#     sample_rate=audio.get_sample_rate(),
# )

# audio.play()


frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=2000, order=5))
# frequency_filter_chain.apply(audio1)
# frequency_filter_chain.apply(audio2)
# frequency_filter_chain.apply(audio3)
# frequency_filter_chain.apply(audio4)

# audio.play()

# TODO: when I remove noisereducer, NMF doesn't work anymore (two splits, but cannot be used)
# audio1 = NoiseReducer.reduce_noise(audio=audio1)
# audio2 = NoiseReducer.reduce_noise(audio=audio2)
# audio3 = NoiseReducer.reduce_noise(audio=audio3)
# audio4 = NoiseReducer.reduce_noise(audio=audio4)

# audio.play()

# spectrogram_plot(audio.get_audio_signal_unchunked(), audio.get_sample_rate())

# concatenate all 4 audio signals (audio.get_audio_signal_unchunked() is the first audio signal)
audio_signal_concatenated = np.concatenate(
    [
        audio1.get_audio_signal_unchunked(),
        audio2.get_audio_signal_unchunked(),
        audio3.get_audio_signal_unchunked(),
        audio4.get_audio_signal_unchunked(),
    ],
    axis=0,
)

audio_concatinated = Audio.create_from_signal(audio_signal_concatenated, 11025)
print(audio_concatinated.get_duration())
# audio_concatinated.play()

######
# IMPORTANT: WE'RE USING THE NMF_old2.py HERE, AND NOT THE OPTIMIZED NMF class!!!
######
nmf = NonNegativeMatrixFactorization(sample_rate=audio1.get_sample_rate())
# audio_signal_concatinated_nmf = nmf.run(audio_concatinated)
audio_signal_concatinated_nmf = nmf.run_for_single_audio_signal(
    audio_signal_concatenated, sample_rate=audio1.get_sample_rate()
)

print("nmf audio")
print(audio_signal_concatinated_nmf)

wave_plot(audio_signal_concatinated_nmf[0], audio1.get_sample_rate())
wave_plot(audio_signal_concatinated_nmf[1], audio1.get_sample_rate())


for i, audio_concatinated_source_signal in enumerate(audio_signal_concatinated_nmf):
    new_audio1_signal = audio_concatinated_source_signal[
        0 : len(audio1.get_audio_signal_unchunked())
    ]
    new_audio2_signal = audio_concatinated_source_signal[
        len(audio1.get_audio_signal_unchunked()) : len(
            audio1.get_audio_signal_unchunked()
        )
        + len(audio2.get_audio_signal_unchunked())
    ]
    new_audio3_signal = audio_concatinated_source_signal[
        len(audio1.get_audio_signal_unchunked())
        + len(audio2.get_audio_signal_unchunked()) : len(
            audio1.get_audio_signal_unchunked()
        )
        + len(audio2.get_audio_signal_unchunked())
        + len(audio3.get_audio_signal_unchunked())
    ]
    new_audio4_signal = audio_concatinated_source_signal[
        len(audio1.get_audio_signal_unchunked())
        + len(audio2.get_audio_signal_unchunked())
        + len(audio3.get_audio_signal_unchunked()) : len(
            audio1.get_audio_signal_unchunked()
        )
        + len(audio2.get_audio_signal_unchunked())
        + len(audio3.get_audio_signal_unchunked())
        + len(audio4.get_audio_signal_unchunked())
    ]
    audio1.set_audio_signal(audio_signal=new_audio1_signal, index=0)
    audio2.set_audio_signal(audio_signal=new_audio2_signal, index=0)
    audio3.set_audio_signal(audio_signal=new_audio3_signal, index=0)
    audio4.set_audio_signal(audio_signal=new_audio4_signal, index=0)
    break

# audio1.play()
# audio2.play()
# audio3.play()
# audio4.play()

# reduce noise
audio1 = NoiseReducer.reduce_noise(audio=audio1)
audio2 = NoiseReducer.reduce_noise(audio=audio2)
audio3 = NoiseReducer.reduce_noise(audio=audio3)
audio4 = NoiseReducer.reduce_noise(audio=audio4)

# audio1.play()
# audio2.play()
# audio3.play()
# audio4.play()

mic1.set_audio(audio1)
mic2.set_audio(audio2)
mic3.set_audio(audio3)
mic4.set_audio(audio4)

########################
# Pre-processing done! #
########################


environment1 = SampleTrimmer.sync_environment(environment1)

# play
for i, mic in enumerate(environment1.get_mics()):
    print(f"MIC{i+1})")
    # mic.get_audio().play()
    # time.sleep(5)

# wait
# time.sleep(3)

environment1.chunk_audio_signals(chunk_size=1000)
number_of_chunks = len(environment1.get_mics()[0].get_audio().get_audio_signal())

algorithm_choice = "threshold"

dict = environment1.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.05
)

for i, object in enumerate(dict):
    print(dict[object])

for i, mic in enumerate(environment1.get_mics()):
    print(f"MIC{i+1} has {len(mic.get_audio().get_audio_signal())} chunks")
    # play
    # mic.get_audio().play()

multilaterate_plot(environment1, dict)
