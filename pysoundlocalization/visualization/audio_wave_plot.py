import matplotlib.pyplot as plt
import numpy as np


def audio_wave_plot(
    audio_signal: np.ndarray, sample_rate: int, title: str = "Waveplot"
) -> None:
    """
    Plot the waveform of an audio signal.

    Args:
        audio_signal (np.ndarray): The audio signal to plot.
        sample_rate (int): The sample rate of the audio signal
        title (str): The title of the plot.
    """

    print(f"Waveplot of audio signal displayed.")

    plt.figure(figsize=(10, 6))

    timeline = np.linspace(
        0,
        len(audio_signal) / sample_rate,
        len(audio_signal),
    )

    plt.plot(timeline, audio_signal)
    plt.ylim(-1.2, 1.2)
    plt.title(title)
    plt.ylabel("Amplitude")
    plt.xlabel("Time (seconds)")

    plt.show()
