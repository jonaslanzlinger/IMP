from pysoundlocalization.core.Audio import Audio
from datetime import timedelta
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
import time
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.util.simulate_noise_util import generate_audios
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.preprocessing.NotchFilter import NotchFilter
from pysoundlocalization.preprocessing.HighCutFilter import HighCutFilter

simulation = Simulation.create()

environment = simulation.add_environment(
    "Simulation",
    [
        (0, 10),
        (50, 0),
        (100, 10),
        (100, 25),
        (110, 25),
        (110, 85),
        (100, 85),
        (100, 100),
        (0, 100),
    ],
)


mic1 = environment.add_microphone(5, 15)
mic2 = environment.add_microphone(95, 15)
mic3 = environment.add_microphone(95, 95)
mic4 = environment.add_microphone(5, 95)

buzzer = Audio(filepath="buzzer_sound.wav")
knock = Audio(filepath="knock_sound.wav")
# print(f"Sound 1 duration: {buzzer.get_sample_rate()}")
# print(f"Sound 2 duration: {knock.get_sample_rate()}")
lowest_sample_rate = SampleRateConverter.convert_list_of_audios_to_lowest_sample_rate(
    [buzzer, knock]
)
source_positions = [
    {
        "sound": buzzer,
        int(lowest_sample_rate * 1): (50, 85),
        int(lowest_sample_rate * 3): (50, 85),
        int(lowest_sample_rate * 5): (50, 85),
        int(lowest_sample_rate * 7): (50, 85),
    },
    {
        "sound": knock,
        int(lowest_sample_rate * 1.5): (10, 50),
        int(lowest_sample_rate * 2.3): (25, 50),
        int(lowest_sample_rate * 3.7): (40, 50),
        int(lowest_sample_rate * 4.2): (55, 50),
        int(lowest_sample_rate * 4.6): (70, 50),
        int(lowest_sample_rate * 5.5): (85, 50),
        int(lowest_sample_rate * 6.0): (100, 50),
    },
]

n_sound_sources = len(source_positions)

factory_sound_audio = Audio(
    filepath="factory_sound.wav", convert_to_sample_rate=lowest_sample_rate
)
# factory_sound_audio.play()
# print(f"Background noise duration: {factory_sound_audio.get_duration()}")
# print(f"sample rate: {factory_sound_audio.get_sample_rate()}")

environment = generate_audios(
    environment=environment,
    sample_rate=lowest_sample_rate,
    source_sources=source_positions,
    background_noise=factory_sound_audio,
    loudness_mix=[0.3, 0.3, 1.0],
    default_sound_duration=0.3,
)

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)

original_audio1 = mic1.get_audio()
original_audio2 = mic2.get_audio()
original_audio3 = mic3.get_audio()
original_audio4 = mic4.get_audio()
# original_audio1.play()

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=500, order=5))
frequency_filter_chain.add_filter(NotchFilter(target_frequency=2760, quality_factor=10))
frequency_filter_chain.add_filter(HighCutFilter(cutoff_frequency=4000, order=5))
for mic in environment.get_mics():
    frequency_filter_chain.apply(mic.get_audio())

for mic in environment.get_mics():
    NoiseReducer.reduce_noise(mic.get_audio())

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1.0)

nmf = NonNegativeMatrixFactorization(
    number_of_sources_to_extract=n_sound_sources,
    sample_rate=environment.get_mics()[0].get_audio().get_sample_rate(),
)
all_sound_sources_nmf = nmf.experimental_run_for_all_audio_in_environment(environment)

algorithm_choice = "threshold"
all_multilaterations = []
current_audio_index = 0

for i_sound_src in range(n_sound_sources):
    for mic in environment.get_mics():
        mic.set_audio(all_sound_sources_nmf[mic][i_sound_src])
    # for mic in environment.get_mics():
    #     audio = mic.get_audio()
    #     # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    #     # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    #     # audio.play()
    AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.8)
    environment.chunk_audio_signals_by_duration(
        chunk_duration=timedelta(milliseconds=1000)
    )
    result_dict = environment.multilaterate(
        algorithm=algorithm_choice,
        number_of_sound_sources=n_sound_sources,
        threshold=0.5,
    )
    all_multilaterations.append(result_dict)
    # environment.get_mics()[0].get_audio().play()

# Reset audio to original audio
mic1.set_audio(original_audio1)
mic2.set_audio(original_audio2)
mic3.set_audio(original_audio3)
mic4.set_audio(original_audio4)

multilaterate_plot(environment, all_multilaterations)
