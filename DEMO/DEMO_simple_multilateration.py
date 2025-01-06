import numpy as np
import scipy.io.wavfile as wav
import warnings
import matplotlib.pyplot as plt
import pysoundlocalization.core.Simulation as Simulation
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from datetime import datetime, timedelta
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.config import DEFAULT_SOUND_SPEED
from pysoundlocalization.core.Environment import Environment
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.visualization.environment_wave_plot import (
    environment_wave_plot,
)

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

mic1.set_audio(Audio(filepath="../data/08_door_bell/pi1_audio.wav"))
mic2.set_audio(Audio(filepath="../data/08_door_bell/pi2_audio.wav"))
mic3.set_audio(Audio(filepath="../data/08_door_bell/pi3_audio.wav"))
mic4.set_audio(Audio(filepath="../data/08_door_bell/pi4_audio.wav"))

AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1)

environment_wave_plot(environment)

dict = environment.multilaterate(
    algorithm="threshold",
    number_of_sound_sources=1,
    threshold=0.1,
)

multilaterate_plot(environment, [dict])
