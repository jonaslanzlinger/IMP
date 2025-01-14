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

simulation = Simulation.create()

environment = simulation.add_environment(
    "Pump Environment",
    [
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

mic1 = environment.add_microphone(10.61, 5)
mic2 = environment.add_microphone(10.61, 8.89)
mic3 = environment.add_microphone(4, 8.89)
mic4 = environment.add_microphone(4, 5)

mic1.set_audio(
    Audio(filepath="../data/10_pump/pi1_audio_2024-11-07_10-30-45_977581.wav")
)
mic1.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 977581))

mic2.set_audio(
    Audio(filepath="../data/10_pump/pi2_audio_2024-11-07_10-30-45_474498.wav")
)
mic2.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 474498))

mic3.set_audio(
    Audio(filepath="../data/10_pump/pi3_audio_2024-11-07_10-30-46_550904.wav")
)
mic3.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 46, 550904))

mic4.set_audio(
    Audio(filepath="../data/10_pump/pi4_audio_2024-11-07_10-30-45_728052.wav")
)
mic4.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 728052))

for mic in environment.get_mics():
    audio = mic.get_audio()
    # audio_wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio_spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)

for mic in environment.get_mics():
    audio = mic.get_audio()
    # audio_wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio_spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
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
    # audio_wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio_spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio.play()

NoiseReducer.reduce_all_noise(environment)

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)

for mic in environment.get_mics():
    audio = mic.get_audio()
    # audio_wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    # audio_spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
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
