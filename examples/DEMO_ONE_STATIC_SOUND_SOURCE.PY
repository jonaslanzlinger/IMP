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

simulation = Simulation.create()

environment = simulation.add_environment(
    "Illwerke - Rodundwerk II", [(0, 0), (10, 0), (10, 10), (0, 10)]
)

mic1 = environment.add_microphone(7.61, 1)
mic2 = environment.add_microphone(7.61, 4.89)
mic3 = environment.add_microphone(1, 4.89)
mic4 = environment.add_microphone(1, 1)

mic1.set_audio(Audio(filepath="illwerke_MIC1_2024-11-07_10-30-45_977581.wav"))
mic1.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 0))
SampleTrimmer.trim_from_beginning(mic1.get_audio(), timedelta(microseconds=300499))
SampleTrimmer.trim_from_beginning(mic1.get_audio(), timedelta(microseconds=16681))

mic2.set_audio(Audio(filepath="illwerke_MIC2_2024-11-07_10-30-45_474498.wav"))
mic2.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 0))
SampleTrimmer.trim_from_beginning(mic2.get_audio(), timedelta(microseconds=16681))

mic3.set_audio(Audio(filepath="illwerke_MIC3_2024-11-07_10-30-46_550904.wav"))
mic3.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 0))
SampleTrimmer.trim_from_beginning(mic3.get_audio(), timedelta(microseconds=20593))
SampleTrimmer.trim_from_beginning(mic3.get_audio(), timedelta(microseconds=326916))

mic4.set_audio(Audio(filepath="illwerke_MIC4_2024-11-07_10-30-45_728052.wav"))
mic4.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 0))
SampleTrimmer.trim_from_beginning(mic4.get_audio(), timedelta(microseconds=326916))

for mic in environment.get_mics():
    audio = mic.get_audio()
    # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)

for mic in environment.get_mics():
    audio = mic.get_audio()
    # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()


SampleRateConverter.convert_all_to_lowest_sample_rate(environment)

SampleTrimmer.sync_environment(environment)
SampleTrimmer.slice_all_from_to(
    environment, timedelta(seconds=15), timedelta(seconds=20)
)

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=2000, order=5))
for mic in environment.get_mics():
    frequency_filter_chain.apply(mic.get_audio())

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)

for mic in environment.get_mics():
    audio = mic.get_audio()
    # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()

NoiseReducer.reduce_all_noise(environment)

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)

for mic in environment.get_mics():
    audio = mic.get_audio()
    # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()

algorithm_choice = "threshold"
all_dicts = []
result_dict = environment.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.75
)
all_dicts.append(result_dict)

for i, object in enumerate(all_dicts):
    print(dict[object])

multilaterate_plot(environment, all_dicts)
