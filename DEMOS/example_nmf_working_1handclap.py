from pysoundlocalization.visualization.audio_wave_plot import audio_wave_plot
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
mic1.set_audio(audio1)

audio_file2 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC2_2024-11-07_10-30-45_474498.wav"
audio2 = Audio(filepath=audio_file2, convert_to_sample_rate=11025)
mic2.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 474498))
mic2.set_audio(audio2)

audio_file3 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC3_2024-11-07_10-30-46_550904.wav"
audio3 = Audio(filepath=audio_file3, convert_to_sample_rate=11025)
mic3.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 46, 550904))
mic3.set_audio(audio3)

audio_file4 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC4_2024-11-07_10-30-45_728052.wav"
audio4 = Audio(filepath=audio_file4, convert_to_sample_rate=11025)
mic4.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 728052))
mic4.set_audio(audio4)

SampleTrimmer.slice_all_from_to(
    environment1, timedelta(seconds=17), timedelta(seconds=20)
)

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=2000, order=5))
# frequency_filter_chain.apply(audio1)
# frequency_filter_chain.apply(audio2)
# frequency_filter_chain.apply(audio3)
# frequency_filter_chain.apply(audio4)

# TODO: when I remove noisereducer, NMF doesn't work anymore (two splits, but cannot be used)
NoiseReducer.reduce_all_noise(environment1)

###
# Showcasing different NMF methods:
# 1. Apply NMF to audio_signal of audio1
# 2. Apply NMF to audio1 directly
# 3. Apply NMF to environment (all audios associated with a mic in environment) -> this will be used for analysis here
###
nmf = NonNegativeMatrixFactorization(sample_rate=audio1.get_sample_rate())
# apply NMF to audio1_signal
audio1_signal_nmf = nmf.run_for_single_audio_signal(
    audio1.get_audio_signal_unchunked(), sample_rate=audio1.get_sample_rate()
)
audio_wave_plot(audio1_signal_nmf[0], audio1.get_sample_rate())
audio_wave_plot(audio1_signal_nmf[1], audio1.get_sample_rate())

# apply NMF to audio1
audio1_nmf_audios = nmf.run_for_single_audio(audio1)
audio_wave_plot(
    audio1_nmf_audios[0].get_audio_signal_unchunked(), audio1.get_sample_rate()
)
audio_wave_plot(
    audio1_nmf_audios[1].get_audio_signal_unchunked(), audio1.get_sample_rate()
)

all_audio_nmf = nmf.experimental_run_for_all_audio_in_environment(environment1)

for mic, audio_list in all_audio_nmf.items():
    print(f"Mic: {mic.get_name()}")
    for idx, audio in enumerate(audio_list):
        print(f"  Audio {idx + 1}: {len(audio.get_audio_signal_unchunked())} samples")
        mic.set_audio(audio, reset_recording_start_time=False)
        audio_wave_plot(
            audio.get_audio_signal_unchunked(),
            audio.get_sample_rate(),
            "nmf_environment_" + str(mic.get_name()) + "_" + str(idx + 1),
        )
        # audio.play()

# reduce noise
NoiseReducer.reduce_all_noise(environment1)

########################
# Pre-processing done! #
# Now, localize sound. #
########################

environment1 = SampleTrimmer.sync_environment(environment1)

# play
for i, mic in enumerate(environment1.get_mics()):
    print(f"MIC{i+1})")
    # mic.get_audio().play()
    # time.sleep(5)

# wait
# time.sleep(3)

environment1.chunk_audio_signals_by_duration(
    chunk_duration=timedelta(milliseconds=1000)
)

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
