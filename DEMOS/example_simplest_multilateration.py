import pysoundlocalization.core.Simulation as Simulation
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.visualization.environment_overlap_wave_plot import (
    environment_overlap_wave_plot,
)

"""
This example demonstrates the simplest multilateration possible, including
the setup of the environment, the addition of microphones, loading of audio
files and the localization of a sound source using a simple threshold
algorithm.

Note that the door bell sound is localized, while the rest of the audio
signal is ignored.
"""

simulation = Simulation.create()

environment = simulation.add_environment(
    "Door Bell Environment",
    [
        (-15, -15),
        (-15, 15),
        (15, 15),
        (15, -15),
    ],
)
environment.visualize()

mic1 = environment.add_microphone(x=-10, y=-10)
mic2 = environment.add_microphone(x=-10, y=10)
mic3 = environment.add_microphone(x=10, y=10)
mic4 = environment.add_microphone(x=10, y=-10)

# Note that those audio files are already correctly synced
mic1.set_audio(
    Audio(filepath="../data/08_door_bell/pi1_audio_2024-10-24_15-21-23_000000.wav")
)
mic2.set_audio(
    Audio(filepath="../data/08_door_bell/pi2_audio_2024-10-24_15-21-23_000000.wav")
)
mic3.set_audio(
    Audio(filepath="../data/08_door_bell/pi3_audio_2024-10-24_15-21-23_000000.wav")
)
mic4.set_audio(
    Audio(filepath="../data/08_door_bell/pi4_audio_2024-10-24_15-21-23_000000.wav")
)

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1)

environment_overlap_wave_plot(environment=environment)

# Hint: Try 'threshold' to compare with gcc_phat result.
dict = environment.localize(
    algorithm="gcc_phat",
    threshold=0.1,
)

multilaterate_plot(environment=environment, dict_list=[dict])
