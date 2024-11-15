import os
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot

# Create simulation and add an environment with 4 microphones
simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Square Environment", [(0, 0), (0, 4), (4, 4), (4, 0)]
)
mic1 = environment1.add_microphone(0, 0)
mic2 = environment1.add_microphone(2, 0)
mic3 = environment1.add_microphone(2, 2)
mic4 = environment1.add_microphone(0, 2)

# Add audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

audio1_filepath = "trimmed_output_MIC1_2024-11-06_15-30-17_252158.wav"
mic1.set_audio(Audio(filepath=audio1_filepath, convert_to_sample_rate=44100))

audio2_filepath = "trimmed_output_MIC2_2024-11-06_15-30-16_794128.wav"
mic2.set_audio(Audio(filepath=audio2_filepath, convert_to_sample_rate=44100))

audio3_filepath = "trimmed_output_MIC3_2024-11-06_15-30-17_275815.wav"
mic3.set_audio(Audio(filepath=audio3_filepath, convert_to_sample_rate=44100))

audio4_filepath = "trimmed_output_MIC4_2024-11-06_15-30-16_843761.wav"
mic4.set_audio(Audio(filepath=audio4_filepath, convert_to_sample_rate=44100))

# Compute all TDoA and DoA for all mic pairs
# TODO: Support multiple sound localizations. Currently, the mosquito sound is localized, but the handclap is ignored.

algorithm_choice = "threshold"

dict = environment1.multilaterate(algorithm=algorithm_choice, number_of_sound_sources=1)

for i, object in enumerate(dict):
    print(dict[object])

multilaterate_plot(environment1, dict)


# tdoa_pairs = environment1.compute_all_tdoa(print_intermediate_results=True)
# print(f"TDoA for all mic pairs: {tdoa_pairs}")

# # Approximate and visualize the sound source position
# x, y = environment1.multilaterate_sound_source(tdoa_pairs)
# print(f"Approximated source position: x={x}, y={y}")

# environment1.add_sound_source_position(x, y)
# environment1.visualize()
