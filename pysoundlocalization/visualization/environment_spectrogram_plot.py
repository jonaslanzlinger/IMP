import numpy as np
import matplotlib.pyplot as plt
from pysoundlocalization.core.Environment import Environment


def environment_spectrogram_plot(environment: Environment) -> None:
    """
    Plot spectrograms of all audio signals in the given environment.

    Args:
        environment: The environment object containing microphones with audio signals.
    """

    print(f"Spectrogram of environment displayed.")

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
