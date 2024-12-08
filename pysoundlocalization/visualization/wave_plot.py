from pysoundlocalization.core.Audio import Audio
import matplotlib.pyplot as plt
import numpy as np
from pysoundlocalization.core.Environment import Environment


def wave_plot(
    audio_signal: np.ndarray, sample_rate: int, title: str = "Waveplot"
) -> None:
    """
    Plot the waveform of an audio signal.

    Args:
        audio_signal (np.ndarray): The audio signal to plot.
        sample_rate (int): The sample rate of the audio signal
        title (str): The title of the plot.
    """
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


def wave_plot_environment(environment: Environment) -> None:
    """
    Plot the waveforms of all audio signals in the given environment.

    Args:
        environment: The environment object containing microphones with audio signals.
    """
    mics = environment.get_mics()

    num_mics = len(mics)
    plt.figure(figsize=(10, 2 * num_mics))

    for i, mic in enumerate(mics):
        audio_signal = mic.get_audio().get_audio_signal_unchunked()

        timeline = np.linspace(
            0,
            len(audio_signal) / mic.get_audio().get_sample_rate(),
            len(audio_signal),
        )

        plt.subplot(num_mics, 1, i + 1)
        plt.plot(timeline, audio_signal)
        plt.ylim(-1.2, 1.2)
        plt.ylabel("Amplitude")
        plt.xlabel("Time (seconds)")

    plt.gcf().canvas.manager.set_window_title("Environment all Waveplots")
    plt.tight_layout()
    plt.show()
