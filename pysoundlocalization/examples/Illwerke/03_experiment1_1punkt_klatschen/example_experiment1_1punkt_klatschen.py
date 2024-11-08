import os
from core.Audio import Audio
from core.Simulation import Simulation
from preprocessing.SampleRateConverter import SampleRateConverter

# Create simulation and add a room with 4 microphones
simulation = Simulation.create()
room1 = simulation.add_room("Machine Room", [(0, 0), (0, 10), (10, 10), (10, 0)])
mic1 = room1.add_microphone(8.61,2)
mic2 = room1.add_microphone(8.61,5.89)
mic3 = room1.add_microphone(2,5.89)
mic4 = room1.add_microphone(2,2)

# Add audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
audio1_filepath = "trimmed_output_MIC1_2024-11-07_10-30-45_977581.wav"
mic1.add_audio(Audio(filepath=audio1_filepath))

audio2_filepath = "trimmed_output_MIC2_2024-11-07_10-30-45_474498.wav"
mic2.add_audio(Audio(filepath=audio2_filepath))

audio3_filepath = "trimmed_output_MIC3_2024-11-07_10-30-46_550904.wav"
mic3.add_audio(Audio(filepath=audio3_filepath))

audio4_filepath = "trimmed_output_MIC4_2024-11-07_10-30-45_728052.wav"
mic4.add_audio(Audio(filepath=audio4_filepath))

# Ensure that all audio files are of same sample rate
SampleRateConverter.convert_all_to_lowest_sample_rate(room1)

# Compute all TDoA and DoA for all mic pairs
tdoa_pairs = room1.compute_all_tdoa(sample_rate=SampleRateConverter.get_lowest_sample_rate(room1), print_intermediate_results=True)
print(f"TDoA for all mic pairs: {tdoa_pairs}")

doa_pairs = room1.compute_all_doa(tdoa_pairs, print_intermediate_results=True)
print(f"DoA for all mic pairs: {doa_pairs}")

# Approximate and visualize the sound source position
x,y = room1.multilaterate_sound_source(tdoa_pairs)
print(f"Approximated source position: x={x}, y={y}")

room1.add_sound_source_position(x, y)
room1.visualize()