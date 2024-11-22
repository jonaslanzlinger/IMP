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
mic1 = environment1.add_microphone(8.61, 2, "mic1")
mic2 = environment1.add_microphone(8.61, 5.89, "mic2")
mic3 = environment1.add_microphone(2, 5.89, "mic3")
mic4 = environment1.add_microphone(2, 2, "mic4")

audio_file1 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC1_2024-11-07_10-30-45_977581.wav"
audio1 = Audio(filepath=audio_file1, convert_to_sample_rate=11025)
mic1.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 977581))
mic1.set_audio(audio1)
print(audio1.get_duration())

audio_file2 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC2_2024-11-07_10-30-45_474498.wav"
audio2 = Audio(filepath=audio_file2, convert_to_sample_rate=11025)
mic2.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 474498))
mic2.set_audio(audio2)
print(audio2.get_duration())

audio_file3 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC3_2024-11-07_10-30-46_550904.wav"
audio3 = Audio(filepath=audio_file3, convert_to_sample_rate=11025)
mic3.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 46, 550904))
mic3.set_audio(audio3)
print(audio3.get_duration())

audio_file4 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC4_2024-11-07_10-30-45_728052.wav"
audio4 = Audio(filepath=audio_file4, convert_to_sample_rate=11025)
mic4.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 728052))
mic4.set_audio(audio4)
print(audio4.get_duration())

SampleTrimmer.slice_from_to(
    audio1, start_time=timedelta(seconds=17), end_time=timedelta(seconds=20)
)
SampleTrimmer.slice_from_to(
    audio2, start_time=timedelta(seconds=17), end_time=timedelta(seconds=20)
)
SampleTrimmer.slice_from_to(
    audio3, start_time=timedelta(seconds=17), end_time=timedelta(seconds=20)
)
SampleTrimmer.slice_from_to(
    audio4, start_time=timedelta(seconds=17), end_time=timedelta(seconds=20)
)

# spectrogram_plot(
#     audio_signal=audio.get_unchuncked_audio_signal(),
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

NoiseReducer.reduce_noise(audio=mic1.get_audio())
NoiseReducer.reduce_noise(audio=mic2.get_audio())
NoiseReducer.reduce_noise(audio=mic3.get_audio())
NoiseReducer.reduce_noise(audio=mic4.get_audio())

# audio.play()

# spectrogram_plot(audio.get_unchuncked_audio_signal(), audio.get_sample_rate())

# TODO: IMPORTANT: nmf returns a signal that is slighly shorter than the original concatenated signal.
nmf = NonNegativeMatrixFactorization()
audio_signals_nmf = nmf.experimental_run_for_all_audio_in_environment(
    environment=environment1
)

for mic, audio_list in audio_signals_nmf.items():
    print(f"Mic: {mic.get_name()}")
    for idx, audio in enumerate(audio_list):
        print(f"  Audio {idx + 1}: {len(audio.get_unchunked_audio_signal())} samples")
        # TODO: currently, the audio objectes returned from NMF only have the audio_signal and other parameters are missing, like sample_rate. That means that mic.set_audio(audio) does not work really.
        mic.get_audio().set_audio_signal(audio.get_unchunked_audio_signal())

# audio1.play()
# audio2.play()
# audio3.play()
# audio4.play()

# reduce noise
NoiseReducer.reduce_noise(audio=mic1.get_audio())
NoiseReducer.reduce_noise(audio=mic2.get_audio())
NoiseReducer.reduce_noise(audio=mic3.get_audio())
NoiseReducer.reduce_noise(audio=mic4.get_audio())

# audio1.play()
# audio2.play()
# audio3.play()
# audio4.play()


########################
# Pre-processing done! #
########################

print("a")

environment1 = SampleTrimmer.sync_environment(environment1)

print("b")
# play
for i, mic in enumerate(environment1.get_mics()):
    print(f"MIC{i+1})")
    # mic.get_audio().play()
    # time.sleep(5)

print("c")
# wait
# time.sleep(3)

environment1.chunk_audio_signals_by_duration(
    chunk_duration=timedelta(milliseconds=1000)
)
number_of_chunks = len(environment1.get_mics()[0].get_audio().get_audio_signal())

algorithm_choice = "threshold"

dict = environment1.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.05
)

for i, object in enumerate(dict):
    print(dict[object])

for i, mic in enumerate(environment1.get_mics()):
    print(
        f"MIC{i+1} ({mic.get_name()}) has {len(mic.get_audio().get_audio_signal())} chunks"
    )
    # play
    # mic.get_audio().play()

multilaterate_plot(environment1, dict)
