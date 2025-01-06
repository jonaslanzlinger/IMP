from datetime import datetime, timedelta
import numpy as np

from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.visualization.environment_plot import environment_plot
from pysoundlocalization.visualization.environment_play_audio_plot import (
    environment_play_audio_plot,
)
from pysoundlocalization.visualization.environment_wave_plot import (
    environment_wave_plot,
)
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot

simulation = Simulation.create()

environment = simulation.add_environment(
    "School Environment", [(0, 0), (0, 5), (5, 5), (5, 0)]
)

mic1 = environment.add_microphone(1, 1)
mic2 = environment.add_microphone(2.8, 1)
mic3 = environment.add_microphone(1.9, 4.2)

# Note: The audio files are already synced correctly.
mic1.set_audio(
    Audio(
        filepath="../data/09_three_microphones/pi1_audio_2024-11-09_18-24-32_104187.wav"
    )
)
mic1.set_recording_start_time(datetime(2024, 11, 9, 18, 24, 32, 104187))

mic2.set_audio(
    Audio(
        filepath="../data/09_three_microphones/pi2_audio_2024-11-09_18-24-32_811701.wav"
    )
)
mic2.set_recording_start_time(datetime(2024, 11, 9, 18, 24, 32, 811701))

mic3.set_audio(
    Audio(
        filepath="../data/09_three_microphones/pi3_audio_2024-11-09_18-24-31_911530.wav"
    )
)
mic3.set_recording_start_time(datetime(2024, 11, 9, 18, 24, 31, 911530))

environment = SampleTrimmer.sync_environment(environment)

dict = environment.multilaterate(
    algorithm="threshold", number_of_sound_sources=1, threshold=0.2
)

print(dict)

environment_plot(environment)
environment_play_audio_plot(environment)
environment_wave_plot(environment)
multilaterate_plot(environment, [dict])
