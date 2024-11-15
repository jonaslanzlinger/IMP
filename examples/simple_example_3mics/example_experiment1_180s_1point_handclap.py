import os
from datetime import datetime
import numpy as np

from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot

simulation = Simulation.create()
environment1 = simulation.add_environment(
    "School Environment", [(0, 0), (0, 10), (10, 10), (10, 0)]
)
mic1 = environment1.add_microphone(0, 0, name="1-jonas-links")
mic2 = environment1.add_microphone(1.8, 0, name="2-jonas-rechts")
mic3 = environment1.add_microphone(0.9, 3.2, name="3-tibor")

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
    np.concatenate([np.zeros(3800), mic1.get_audio().get_audio_signal_by_index()])
)
mic2.get_audio().set_audio_signal(
    np.concatenate([np.zeros(1500), mic2.get_audio().get_audio_signal_by_index()])
)

environment1 = SampleTrimmer.sync_environment(environment1)

# isolate individual sound sources
# TODO: implement this in a smart way

# chunking
# for each chunk: compute tdoa, multilaterate, add sound source position to environment
# chunking the audio files
environment1.chunk_audio_signals(chunk_size=1000)
number_of_chunks = len(environment1.get_mics()[0].get_audio().get_audio_signal())

algorithm_choice = "threshold"

dict = environment1.multilaterate(
    algorithm=algorithm_choice, number_of_sound_sources=1, threshold=0.2
)

for i, object in enumerate(dict):
    print(dict[object])

multilaterate_plot(environment1, dict)
