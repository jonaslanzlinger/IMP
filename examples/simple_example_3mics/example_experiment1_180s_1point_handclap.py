import os
from datetime import datetime
import numpy as np

from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter

simulation = Simulation.create()
room1 = simulation.add_room("School Room", [(0, 0), (0, 10), (10, 10), (10, 0)])
mic1 = room1.add_microphone(0, 0, name="1-jonas-links")
mic2 = room1.add_microphone(1.8, 0, name="2-jonas-rechts")
mic3 = room1.add_microphone(0.9, 3.2, name="3-tibor")

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
audio1_filepath = "output_MIC1_2024-11-09_18-24-32_018020.wav"
mic1.set_audio(Audio(filepath=audio1_filepath))
mic1.set_recording_start_time(datetime(2024, 11, 9, 18, 24, 32, 18020))

audio2_filepath = "output_MIC2_2024-11-09_18-24-32_777688.wav"
mic2.set_audio(Audio(filepath=audio2_filepath))
mic2.set_recording_start_time(datetime(2024, 11, 9, 18, 24, 32, 777688))

audio3_filepath = "output_MIC3_2024-11-09_18-24-31_911530.wav"
mic3.set_audio(Audio(filepath=audio3_filepath))
mic3.set_recording_start_time(datetime(2024, 11, 9, 18, 24, 31, 911530))

# Because of system latency, the timestamps are off by a few milliseconds.
# Therefore, we concatenate some slience to the beginning of some of the audio files.
mic1.get_audio().set_audio_signal(
    np.concatenate([np.zeros(3800), mic1.get_audio().get_audio_signal()])
)
mic2.get_audio().set_audio_signal(
    np.concatenate([np.zeros(1500), mic2.get_audio().get_audio_signal()])
)

room1 = SampleTrimmer.sync_room(room1)


algorithm_choise = "threshold"

if algorithm_choise == "gcc_phat":
    tdoa_pairs = room1.compute_all_tdoa(
        sample_rate=SampleRateConverter.get_lowest_sample_rate(room1),
        print_intermediate_results=False,
    )
elif algorithm_choise == "threshold":
    tdoa_pairs = room1.compute_all_tdoa_by_threshold(debug_threshold_sample_index=True)

print(tdoa_pairs)

x, y = room1.multilaterate_sound_source(tdoa_pairs)

print(f"Approximated source position: x={x}, y={y}")

room1.add_sound_source_position(x, y)
room1.visualize()
