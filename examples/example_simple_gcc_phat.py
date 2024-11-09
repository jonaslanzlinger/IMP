import os
from core.Audio import Audio
from core.Simulation import Simulation
from preprocessing.FrequencyFilterChain import FrequencyFilterChain
from preprocessing.LowPassFilter import LowPassFilter
from preprocessing.SampleRateConverter import SampleRateConverter
from visualization.spectrogram_plot import spectrogram_plot

# Create simulation and add a room with 4 microphones
simulation = Simulation.create()
room1 = simulation.add_room("Square Room", [(0, 0), (0, 4), (4, 4), (4, 0)])
mic1 = room1.add_microphone(1,1)
mic2 = room1.add_microphone(1,2)
mic3 = room1.add_microphone(2,2)
mic4 = room1.add_microphone(2,1)

# Add audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
audio_filepath = os.path.join(root, "examples", "example_audio", "pi1_audio.wav")
audio = Audio(filepath=audio_filepath)

# Add a filter
#spectrogram_plot(audio1)
frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowPassFilter(cutoff_frequency=300, order=5))
frequency_filter_chain.apply(audio)
spectrogram_plot(audio)

#Careful of potentially loud sound
#audio1.play()

# Add more audio files to mics
audio1_filepath = os.path.join(root, "examples", "example_audio", "pi1_audio.wav")
mic1.add_audio(Audio(filepath=audio1_filepath, convert_to_sample_rate=44100))

audio2_filepath = os.path.join(root, "examples", "example_audio", "pi2_audio.wav")
mic2.add_audio(Audio(filepath=audio2_filepath))

audio3_filepath = os.path.join(root, "examples", "example_audio", "pi3_audio.wav")
mic3.add_audio(Audio(filepath=audio3_filepath))

audio4_filepath = os.path.join(root, "examples", "example_audio", "pi4_audio.wav")
mic4.add_audio(Audio(filepath=audio4_filepath))

# Manually convert audio to different sample rate if needed
sample_rate = mic1.get_audio().get_sample_rate()
mic4.get_audio().convert_to_desired_sample_rate(sample_rate)

# Use the SampleRateConverter if necessary to change sample rates on the room-level
print(f"Lowest sample rate in Room: {SampleRateConverter.get_lowest_sample_rate(room1)}")
SampleRateConverter.convert_all_to_lowest_sample_rate(room1)
SampleRateConverter.convert_all_to_defined_sample_rate(room1, 44100)
SampleRateConverter.convert_all_to_sample_rate_of_audio_file(room1, audio)

# Compute all TDoA and DoA for all mic pairs
tdoa_pairs = room1.compute_all_tdoa(sample_rate=sample_rate, print_intermediate_results=True)
print(f"TDoA for all mic pairs: {tdoa_pairs}")

doa_pairs = room1.compute_all_doa(tdoa_pairs, print_intermediate_results=True)
print(f"DoA for all mic pairs: {doa_pairs}")

# Approximate and visualize the sound source position
x,y = room1.multilaterate_sound_source(tdoa_pairs)
print(f"Approximated source position: x={x}, y={y}")

room1.add_sound_source_position(x, y)
room1.visualize()
