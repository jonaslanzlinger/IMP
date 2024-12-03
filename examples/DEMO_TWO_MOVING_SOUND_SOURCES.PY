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
from pysoundlocalization.visualization.wave_plot import wave_plot_environment
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.util.simulate_noise_util import generate_audios
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.preprocessing.NotchFilter import NotchFilter
from pysoundlocalization.preprocessing.HighCutFilter import HighCutFilter
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.visualization.wave_plot import wave_plot
from datetime import datetime
from pysoundlocalization.visualization.spectrogram_plot import (
    spectrogram_plot_environment,
)

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

mic_1 = environment.add_microphone(5, 15)
mic_2 = environment.add_microphone(95, 15)
mic_3 = environment.add_microphone(95, 95)
mic_4 = environment.add_microphone(5, 95)

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

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1.0)

# EXPORT THE AUDIOS TO WAV FILES
# original_audio1 = mic_1.get_audio()
# original_audio1.export("audio_1.wav")
# original_audio2 = mic_2.get_audio()
# original_audio2.export("audio_2.wav")
# original_audio3 = mic_3.get_audio()
# original_audio3.export("audio_3.wav")
# original_audio4 = mic_4.get_audio()
# original_audio4.export("audio_4.wav")

# The following commented code is needed in case the audio files are loaded instead of generated

# for i, mic in enumerate(environment.get_mics()):
#     audio = Audio(filepath=f"audio_{i+1}.wav")
#     mic.set_audio(audio)
#     mic.set_recording_start_time(datetime.now())

# SampleRateConverter.convert_all_to_lowest_sample_rate(environment)
# SampleTrimmer.sync_environment(environment)

wave_plot_environment(environment=environment)
spectrogram_plot_environment(environment=environment)

frequency_filter_chain = FrequencyFilterChain()

frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=500, order=5))
frequency_filter_chain.add_filter(NotchFilter(target_frequency=2760, quality_factor=10))
frequency_filter_chain.add_filter(HighCutFilter(cutoff_frequency=4000, order=5))

for mic in environment.get_mics():
    frequency_filter_chain.apply(mic.get_audio())
    AudioNormalizer.normalize_audio_to_max_amplitude(mic.get_audio(), 1.0)

# wave_plot_environment(environment=environment)
# spectrogram_plot_environment(environment=environment)

for mic in environment.get_mics():
    NoiseReducer.reduce_noise(mic.get_audio())
    AudioNormalizer.normalize_audio_to_max_amplitude(mic.get_audio(), 1.0)

# wave_plot_environment(environment=environment)
# spectrogram_plot_environment(environment=environment)

n_sound_sources = 2
sample_rate = environment.get_sample_rate()

nmf = NonNegativeMatrixFactorization(
    number_of_sources_to_extract=n_sound_sources,
    sample_rate=sample_rate,
)
all_sound_sources_nmf = nmf.run_for_environment(environment=environment)

for i_sound_src in range(n_sound_sources):
    for mic in environment.get_mics():
        audio = all_sound_sources_nmf[mic][i_sound_src]
        mic.set_audio(audio)

    AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1.0)

    # wave_plot_environment(environment=environment)
    # spectrogram_plot_environment(environment=environment)

algorithm_choice = "threshold"
sources_positions = []
current_audio_index = 0

for i_sound_src in range(n_sound_sources):
    for mic in environment.get_mics():
        audio = all_sound_sources_nmf[mic][i_sound_src]
        mic.set_audio(audio)

    AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1.0)

    environment.chunk_audio_signals_by_duration(
        chunk_duration=timedelta(milliseconds=500)
    )

    source_pos = environment.multilaterate(
        algorithm=algorithm_choice,
        number_of_sound_sources=1,
        threshold=0.5,
    )
    sources_positions.append(source_pos)

for i, mic in enumerate(environment.get_mics()):
    audio = Audio(filepath=f"audio_{i+1}.wav")
    mic.set_audio(audio)
    mic.set_recording_start_time(datetime.now())

multilaterate_plot(environment, sources_positions)
