# Example to localize a sound source using 4 microphones and GCC-PHAT
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
import os

from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter

# Create a new simulation
simulation = Simulation.create()

# Define an L-shaped environment using vertices
l_shape_vertices = [(0, 0), (4.7, 0), (4.7, 2), (3, 2), (3, 4.5), (0, 4.5)]
environment1 = simulation.add_environment("L-Shaped Environment", l_shape_vertices)

# Create and add microphones with decimal coordinates
mic1 = environment1.add_microphone(0.5, 1)  # Inside the L-shaped environment
mic2 = environment1.add_microphone(2.5, 1)  # Inside the L-shaped environment
mic3 = environment1.add_microphone(0.5, 3)  # Inside the L-shaped environment
mic4 = environment1.add_microphone(2.5, 3)  # Inside the L-shaped environment

environment1.visualize()

# Add and pre-process audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
audio1_filepath = os.path.join(root, "examples", "example_audio", "pi1_audio.wav")
audio1 = Audio(filepath=audio1_filepath)
sample_rate1, audio_signal1 = audio1.load_audio_file()

# print(f"Sample Rate: {sample_rate1}")
# print(f"Audio Signal: {audio_signal1[:10]}")  # Print first 10 samples of the audio

# Associate audio with mic
mic1.set_audio(audio1)
# print(mic1.get_audio())

# Add more audio files to mics
audio2_filepath = os.path.join(root, "examples", "example_audio", "pi2_audio.wav")
mic2.set_audio(Audio(filepath=audio2_filepath))

audio3_filepath = os.path.join(root, "examples", "example_audio", "pi3_audio.wav")
mic3.set_audio(Audio(filepath=audio3_filepath))

audio4_filepath = os.path.join(root, "examples", "example_audio", "pi4_audio.wav")
mic4.set_audio(Audio(filepath=audio4_filepath))

# Ensure that all audio of the environment's microphones have the same sample rate
SampleRateConverter.convert_all_to_lowest_sample_rate(environment1)

# Define the maximum possible time delay (TDoA) of any microphone pair in the environment to improve algorithm speeds
max_tau = environment1.get_max_tau()

# Compute TDoA and DoA for mic pair 1+2
tdoa12, cc = environment1.compute_tdoa(
    audio1=mic1.get_audio().get_audio_signal(),
    audio2=mic2.get_audio().get_audio_signal(),
    sample_rate=sample_rate1,
    max_tau=max_tau,  # Optional argument, may be left out to have max_tau computed automatically
)
print(f"TDoA between mic1 and mic2: {tdoa12:.6f} seconds")

# Compute direction of arrival (DoA) of a microphone pair given their TDoA
doa = environment1.compute_doa(tdoa12)
print(f"Direction of arrival (DoA) of sound (mics 1 and 2): {doa:.6f} degrees")

# Compute all TDoA and DoA for all mic pairs
tdoa_pairs = environment1.compute_all_tdoa(
    sample_rate=sample_rate1, print_intermediate_results=True
)
print(f"TDoA for all mic pairs: {tdoa_pairs}")

doa_pairs = environment1.compute_all_doa(tdoa_pairs, print_intermediate_results=True)
print(f"DoA for all mic pairs: {doa_pairs}")

# Approximate and visualize the sound source position
x, y = environment1.multilaterate_sound_source(tdoa_pairs)
print(f"Approximated source position: x={x}, y={y}")

environment1.add_sound_source_position(x, y)
environment1.visualize()
