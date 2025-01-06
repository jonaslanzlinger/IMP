import os
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowPassFilter import LowPassFilter
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot

# Create simulation and add an environment with 4 microphones
simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Square Environment", [(0, 0), (0, 4), (4, 4), (4, 0)]
)
mic1 = environment1.add_microphone(1, 1)
mic2 = environment1.add_microphone(1, 2)
mic3 = environment1.add_microphone(2, 2)
mic4 = environment1.add_microphone(2, 1)

# Add audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
audio_filepath = os.path.join(root, "examples", "example_audio", "pi1_audio.wav")
audio = Audio(filepath=audio_filepath)

# Add a filter
# spectrogram_plot(audio1)
frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowPassFilter(cutoff_frequency=300, order=5))
frequency_filter_chain.apply(audio)

spectrogram_plot(
    audio_signal=audio.get_audio_signal_unchunked(),
    sample_rate=audio.get_sample_rate(),
)

# Careful of potentially loud sound
# audio1.play()

# Add more audio files to mics
audio1_filepath = os.path.join(root, "examples", "example_audio", "pi1_audio.wav")
mic1.set_audio(Audio(filepath=audio1_filepath, convert_to_sample_rate=44100))

audio2_filepath = os.path.join(root, "examples", "example_audio", "pi2_audio.wav")
mic2.set_audio(Audio(filepath=audio2_filepath))

audio3_filepath = os.path.join(root, "examples", "example_audio", "pi3_audio.wav")
mic3.set_audio(Audio(filepath=audio3_filepath))

audio4_filepath = os.path.join(root, "examples", "example_audio", "pi4_audio.wav")
mic4.set_audio(Audio(filepath=audio4_filepath))

# Manually convert audio to different sample rate if needed
sample_rate = mic1.get_audio().get_sample_rate()
mic4.get_audio().resample_audio(target_rate=sample_rate)

# Use the SampleRateConverter if necessary to change sample rates on the environment-level
print(
    f"Lowest sample rate in Environment: {SampleRateConverter.get_lowest_sample_rate(environment1)}"
)
SampleRateConverter.convert_all_to_lowest_sample_rate(environment1)
SampleRateConverter.convert_all_to_defined_sample_rate(environment1, 44100)
SampleRateConverter.convert_all_to_sample_rate_of_audio_file(environment1, audio)

# Compute all TDoA and DoA for all mic pairs
tdoa_pairs = environment1.compute_all_tdoa_of_chunk_index_by_gcc_phat(
    chunk_index=0, threshold=0.1, debug=True
)
print(f"TDoA for all mic pairs: {tdoa_pairs}")

doa_pairs = environment1.compute_all_doa(tdoa_pairs, print_intermediate_results=True)
print(f"DoA for all mic pairs: {doa_pairs}")

algorithm_choice = "threshold"

dict = environment1.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.2
)

for i, object in enumerate(dict):
    print(dict[object])

multilaterate_plot(environment1, dict)
