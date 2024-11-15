from pysoundlocalization.core.Audio import Audio
import matplotlib.pyplot as plt
import numpy as np


def wave_plot(audio_signal: np.ndarray, sample_rate: int) -> None:
    """
    Plot the waveform of an audio signal.

    Args:
        audio_signal: np.ndarray: The audio signal to plot.
        sample_rate: int: The sample rate of the audio signal
    """
    plt.figure(figsize=(10, 6))

    timeline = np.linspace(
        0,
        len(audio_signal) / sample_rate,
        len(audio_signal),
    )

    plt.plot(timeline, audio_signal)
    plt.title("Waveform")
    plt.ylabel("Amplitude")
    plt.xlabel("Time (seconds)")

    plt.show()
