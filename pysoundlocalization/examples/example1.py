# Example to localize a sound source using 4 microphones and GCC-PHAT
from core.Audio import Audio
from core.Simulation import Simulation
import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

simulation = Simulation.create()

# Define an L-shaped room using vertices
l_shape_vertices = [(0, 0), (4.7, 0), (4.7, 2), (3, 2), (3, 4.5), (0, 4.5)]
room1 = simulation.add_room("L-Shaped Room", l_shape_vertices)

# Create and add microphones with decimal coordinates
mic1 = room1.add_microphone(0.9, 3)  # Inside the L-shaped room
mic2 = room1.add_microphone(2.4, 3.284849)  # Inside the L-shaped room
mic3 = room1.add_microphone(1, 1)  # Inside the L-shaped room
mic4 = room1.add_microphone(2.5, 1.5)  # Inside the L-shaped room

room1.visualize()

# Add and pre-process audio
audio1_filepath = os.path.join(root, "examples", "example_audio", "pi1_audio.wav")
audio1 = Audio(filepath=audio1_filepath)
sample_rate1, audio_signal1 = audio1.load_audio_file()

# TODO: support pre-processing of audio
# print(f"Sample Rate: {sample_rate1}")
# print(f"Audio Signal: {audio_signal1[:10]}")  # Print first 10 samples of the audio

# Associate audio with mic
mic1.add_recorded_audio(audio_signal1)
# print(mic2.get_recorded_audio())

# Add more audio files to mics
audio2_filepath = os.path.join(root, "examples", "example_audio", "pi2_audio.wav")
mic2.add_recorded_audio(Audio(filepath=audio2_filepath).get_audio_signal())

audio3_filepath = os.path.join(root, "examples", "example_audio", "pi3_audio.wav")
mic3.add_recorded_audio(Audio(filepath=audio3_filepath).get_audio_signal())

audio4_filepath = os.path.join(root, "examples", "example_audio", "pi4_audio.wav")
mic4.add_recorded_audio(Audio(filepath=audio4_filepath).get_audio_signal())

# TODO: add MAX_TAU via variables instead of 2/343.2 -> max_tau = MIC_DISTANCE / sound_speed  # Maximum possible time delay
max_distance = 2
speed_sound = 343.3
max_tau = max_distance / speed_sound

# Compute TDoA and DoA for mic pair 1+2
tdoa12, cc = room1.compute_tdoa(
    audio1=mic1.get_recorded_audio(),
    audio2=mic2.get_recorded_audio(),
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


