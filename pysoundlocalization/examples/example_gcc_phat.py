# Example to localize a sound source using 4 microphones and GCC-PHAT
from core.Audio import Audio
from core.Simulation import Simulation
import os

# Create a new simulation
simulation = Simulation.create()

# Define an L-shaped room using vertices
l_shape_vertices = [(0, 0), (4.7, 0), (4.7, 2), (3, 2), (3, 4.5), (0, 4.5)]
room1 = simulation.add_room("L-Shaped Room", l_shape_vertices)

# Create and add microphones with decimal coordinates
mic1 = room1.add_microphone(0.5, 1)  # Inside the L-shaped room
mic2 = room1.add_microphone(2.5, 1)  # Inside the L-shaped room
mic3 = room1.add_microphone(0.5, 3)  # Inside the L-shaped room
mic4 = room1.add_microphone(2.5, 3)  # Inside the L-shaped room

room1.visualize()

# Add and pre-process audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
audio1_filepath = os.path.join(root, "examples", "example_audio", "pi1_audio.wav")
audio1 = Audio(filepath=audio1_filepath)
sample_rate1, audio_signal1 = audio1.load_audio_file()

# TODO: support pre-processing of audio
# print(f"Sample Rate: {sample_rate1}")
# print(f"Audio Signal: {audio_signal1[:10]}")  # Print first 10 samples of the audio

# Associate audio with mic
mic1.add_audio(audio1)
# print(mic1.get_audio())

# Add more audio files to mics
audio2_filepath = os.path.join(root, "examples", "example_audio", "pi2_audio.wav")
mic2.add_audio(Audio(filepath=audio2_filepath))

audio3_filepath = os.path.join(root, "examples", "example_audio", "pi3_audio.wav")
mic3.add_audio(Audio(filepath=audio3_filepath))

audio4_filepath = os.path.join(root, "examples", "example_audio", "pi4_audio.wav")
mic4.add_audio(Audio(filepath=audio4_filepath))

# Define the maximum possible time delay (TDoA) of any microphone pair in the room to improve algorithm speeds
max_tau = room1.get_max_tau(mic_distance=2)

# Compute TDoA and DoA for mic pair 1+2
tdoa12, cc = room1.compute_tdoa(
    audio1=mic1.get_audio().get_audio_signal(),
    audio2=mic2.get_audio().get_audio_signal(),
    sample_rate=sample_rate1,
    max_tau=max_tau
)
print(f"TDoA between mic1 and mic2: {tdoa12:.6f} seconds")

# Compute direction of arrival (DoA) of a microphone pair given their TDoA
doa = room1.compute_doa(tdoa12, max_tau=max_tau)
print(f"Direction of arrival (DoA) of sound (mics 1 and 2): {doa:.6f} degrees")

# Compute all TDoA and DoA for all mic pairs
tdoa_pairs = room1.compute_all_tdoa(sample_rate=sample_rate1, max_tau=max_tau, print_intermediate_results=True)
print(f"TDoA for all mic pairs: {tdoa_pairs}")

doa_pairs = room1.compute_all_doa(tdoa_pairs, max_tau=max_tau, print_intermediate_results=True)
print(f"DoA for all mic pairs: {doa_pairs}")

# Approximate and visualize the sound source position
x,y = room1.approximate_sound_source(tdoa_pairs)
print(f"Approximated source position: x={x}, y={y}")

room1.add_sound_source_position(x, y)
room1.visualize()