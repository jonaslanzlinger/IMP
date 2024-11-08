import os
from core.Audio import Audio
from core.Simulation import Simulation

# Create simulation and add a room with 4 microphones
simulation = Simulation.create()
room1 = simulation.add_room("Square Room", [(0, 0), (0, 4), (4, 4), (4, 0)])
mic1 = room1.add_microphone(0,0)
mic2 = room1.add_microphone(2,0)
mic3 = room1.add_microphone(2,2)
mic4 = room1.add_microphone(0,2)

# Add audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

audio1_filepath = os.path.join(root, "examples", "Basic_Test_Mosquito", "output_MIC1_2024-11-06_15-30-17_252158.wav")
mic1.add_audio(Audio(filepath=audio1_filepath, convert_to_sample_rate=44100))

audio2_filepath = os.path.join(root, "examples", "Basic_Test_Mosquito", "output_MIC2_2024-11-06_15-30-16_794128.wav")
mic2.add_audio(Audio(filepath=audio2_filepath, convert_to_sample_rate=44100))

audio3_filepath = os.path.join(root, "examples", "Basic_Test_Mosquito", "output_MIC3_2024-11-06_15-30-17_275815.wav")
mic3.add_audio(Audio(filepath=audio3_filepath, convert_to_sample_rate=44100))

audio4_filepath = os.path.join(root, "examples", "Basic_Test_Mosquito", "output_MIC4_2024-11-06_15-30-16_843761.wav")
mic4.add_audio(Audio(filepath=audio4_filepath, convert_to_sample_rate=44100))

# Compute all TDoA and DoA for all mic pairs
#TODO: Support multiple sound localizations. Currently, the mosquito sound is localized, but the handclap is ignored.
tdoa_pairs = room1.compute_all_tdoa(sample_rate=44100, print_intermediate_results=True)
print(f"TDoA for all mic pairs: {tdoa_pairs}")

# Approximate and visualize the sound source position
x,y = room1.multilaterate_sound_source(tdoa_pairs)
print(f"Approximated source position: x={x}, y={y}")

room1.add_sound_source_position(x, y)
room1.visualize()