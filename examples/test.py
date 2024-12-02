from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from datetime import timedelta
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.preprocessing.NMF_old2 import (
    NonNegativeMatrixFactorization as NMF_old2,
)
from pysoundlocalization.core.Simulation import Simulation
from datetime import datetime

audio_file1 = "../06_versuch_classroom_syncatmic3_sinus_at_random_points/pi1_audio.wav"
audio1 = Audio(filepath=audio_file1, convert_to_sample_rate=44100)
print(audio1.get_duration())

SampleTrimmer.slice_from_to(
    audio1, start_time=timedelta(seconds=17), end_time=timedelta(seconds=28)
)

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=1000, order=5))
# frequency_filter_chain.apply(audio1)
# # frequency_filter_chain.apply(audio2)
# # frequency_filter_chain.apply(audio3)
# # frequency_filter_chain.apply(audio4)

# audio1.play()

# NoiseReducer.reduce_noise(audio=audio1)
# audio1.play()

# # audio.play()

# # spectrogram_plot(audio.get_unchuncked_audio_signal(), audio.get_sample_rate())

nmf = NMF_old2()
audio_signals_nmf = nmf.run(audio=audio1)
print(audio_signals_nmf)

for audio in audio_signals_nmf:
    newAudio = Audio.create_from_signal(audio, 44100)
    newAudio.play()


# for mic, audio_list in audio_signals_nmf.items():
#     print(f"Mic: {mic.get_name()}")
#     for idx, audio in enumerate(audio_list):
#         print(f"  Audio {idx + 1}: {len(audio.get_audio_signal_unchunked())} samples")
# #         mic.set_audio(audio, reset_recording_start_time=True)

# # audio1.play()
# # audio2.play()
# # audio3.play()
# # audio4.play()

# # reduce noise
# NoiseReducer.reduce_all_noise(environment=environment1)

# # audio1.play()
# # audio2.play()
# # audio3.play()
# # audio4.play()


# ########################
# # Pre-processing done! #
# ########################

# # TODO: multilaterate only works if sync_environment is performed before preprocessing. I don't know why.
# # environment1 = SampleTrimmer.sync_environment(environment1)

# # play
# # for i, mic in enumerate(environment1.get_mics()):
# #    print(f"(MIC{i+1})")
# # mic.get_audio().play()
# # time.sleep(5)

# # wait
# # time.sleep(3)

# environment1.chunk_audio_signals_by_duration(
#     chunk_duration=timedelta(milliseconds=1000)
# )
# number_of_chunks = len(
#     environment1.get_mics()[0].get_audio().get_audio_signal_chunked()
# )

# algorithm_choice = "threshold"

# dict = environment1.multilaterate(
#     algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.05
# )
# #
# # for i, object in enumerate(dict):
# #     print(dict[object])
# #
# # for i, mic in enumerate(environment1.get_mics()):
# #     print(
# #         f"MIC{i+1} ({mic.get_name()}) has {len(mic.get_audio().get_audio_signal_chunked())} chunks"
# #     )
# #     # play
# #     # mic.get_audio().play()
# #
# # multilaterate_plot(environment1, dict)
