from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from datetime import timedelta
from pysoundlocalization.core.Simulation import Simulation
from datetime import datetime
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter

simulation = Simulation.create()

environment = simulation.add_environment(
    "Test Environment",
    [
        (0, 0),
        (100, 0),
        (100, 100),
        (0, 100),
    ],
)
# environment.visualize()

mic1 = environment.add_microphone(x=1, y=1)
mic2 = environment.add_microphone(x=99, y=1)
mic3 = environment.add_microphone(x=99, y=99)
mic4 = environment.add_microphone(x=1, y=99)
# environment.visualize()

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
