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

simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Simulation", [(0, 0), (100, 0), (150, 50), (100, 100), (0, 100)]
)
mic1 = environment1.add_microphone(10, 10)
mic2 = environment1.add_microphone(90, 10)
mic3 = environment1.add_microphone(90, 90)
mic4 = environment1.add_microphone(10, 90)

sound1 = Audio(filepath="buzzer.wav")
sound2 = Audio(filepath="hammer.wav")
print(f"Sound 1 duration: {sound1.get_sample_rate()}")
print(f"Sound 2 duration: {sound2.get_sample_rate()}")
lowest_sample_rate = SampleRateConverter.convert_list_of_audios_to_lowest_sample_rate(
    [sound1, sound2]
)
source_positions = [
    {
        "sound": sound1,
        int(lowest_sample_rate * 1): (40, 80),
        int(lowest_sample_rate * 2.5): (40, 80),
        int(lowest_sample_rate * 4.1): (40, 80),
        int(lowest_sample_rate * 5.5): (40, 80),
        int(lowest_sample_rate * 7): (40, 80),
    },
    {
        "sound": sound2,
        int(lowest_sample_rate * 1.6): (75, 20),
        int(lowest_sample_rate * 2.0): (85, 27),
        int(lowest_sample_rate * 3.1): (98, 34),
        int(lowest_sample_rate * 3.6): (105, 41),
        int(lowest_sample_rate * 4.5): (112, 49),
        int(lowest_sample_rate * 5.0): (122, 55),
        int(lowest_sample_rate * 6.0): (130, 60),
    },
]
n_sound_sources = len(source_positions)

audio_background_noise = Audio(filepath="factory.wav")
print(f"Background noise duration: {audio_background_noise.get_duration()}")

environment1 = generate_audios(
    environment=environment1,
    sample_rate=lowest_sample_rate,
    source_sources=source_positions,
    background_noise=audio_background_noise,
    loudness_mix=[0.3, 0.3, 1.0],
    default_sound_duration=0.3,
)

AudioNormalizer.normalize_environment_to_max_amplitude(environment1, 0.8)

original_audio1 = mic1.get_audio()
original_audio2 = mic2.get_audio()
original_audio3 = mic3.get_audio()
original_audio4 = mic4.get_audio()

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=300, order=5))
for mic in environment1.get_mics():
    frequency_filter_chain.apply(mic.get_audio())

for mic in environment1.get_mics():
    NoiseReducer.reduce_noise(mic.get_audio())

nmf = NonNegativeMatrixFactorization(
    number_of_sources_to_extract=n_sound_sources,
    sample_rate=environment1.get_mics()[0].get_audio().get_sample_rate(),
)
all_sound_sources_nmf = nmf.experimental_run_for_all_audio_in_environment(environment1)

algorithm_choice = "threshold"
all_multilaterations = []
current_audio_index = 0

for i_sound_src in range(n_sound_sources):
    for mic in environment1.get_mics():
        mic.set_audio(all_sound_sources_nmf[mic][i_sound_src])
    # for mic in environment.get_mics():
    #     audio = mic.get_audio()
    #     # wave_plot(audio.get_audio_signal(), audio.get_sample_rate())
    #     # spectrogram_plot(audio.get_audio_signal(), audio.get_sample_rate())
    #     # audio.play()
    AudioNormalizer.normalize_environment_to_max_amplitude(environment1, 0.8)
    environment1.chunk_audio_signals_by_duration(
        chunk_duration=timedelta(milliseconds=1000)
    )
    result_dict = environment1.multilaterate(
        algorithm=algorithm_choice,
        number_of_sound_sources=n_sound_sources,
        threshold=0.3,
    )
    all_multilaterations.append(result_dict)

# Reset audio to original audio
mic1.set_audio(original_audio1)
mic2.set_audio(original_audio2)
mic3.set_audio(original_audio3)
mic4.set_audio(original_audio4)

multilaterate_plot(environment1, all_multilaterations)
