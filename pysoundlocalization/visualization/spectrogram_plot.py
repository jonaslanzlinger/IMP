import numpy as np
import matplotlib.pyplot as plt
from pysoundlocalization.core.Environment import Environment


def spectrogram_plot(audio_signal: np.ndarray, sample_rate: int) -> None:
    """
    Plot the spectrogram of an audio signal.

    Args:
        audio_signal (np.ndarray): The audio signal to plot the spectrogram of.
        sample_rate (int): The sample rate of the audio signal.
    """

    plt.figure(figsize=(10, 6))

    plt.specgram(audio_signal, NFFT=1024, Fs=sample_rate, noverlap=512, cmap="inferno")

    plt.title("Spectrogram of Audio Signal")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [s]")

    plt.colorbar(label="Intensity [dB]")

    plt.show()

    print(f"Spectrogram of audio signal displayed.")


def spectrogram_plot_environment(environment: Environment) -> None:
    """
    Plot spectrograms of all audio signals in the given environment.

    Args:
        environment: The environment object containing microphones with audio signals.
    """
    mics = environment.get_mics()

    num_mics = len(mics)
    plt.figure(figsize=(10, 2 * num_mics))

    for i, mic in enumerate(mics):
        audio_signal = mic.get_audio().get_audio_signal_unchunked()

        plt.subplot(num_mics, 1, i + 1)
        plt.specgram(
            audio_signal,
            NFFT=1024,
            Fs=mic.get_audio().get_sample_rate(),
            noverlap=512,
            cmap="inferno",
        )
        plt.ylabel("Frequency [Hz]")
        plt.xlabel("Time [s]")

        plt.colorbar(label="Intensity [dB]")

    plt.gcf().canvas.manager.set_window_title("Environment all Spectrograms")
    plt.tight_layout()
    plt.show()

    print(f"Spectrogram of environment displayed.")
