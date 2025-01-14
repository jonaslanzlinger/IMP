import numpy as np
import matplotlib.pyplot as plt


def audio_spectrogram_plot(audio_signal: np.ndarray, sample_rate: int) -> None:
    """
    Plot the spectrogram of an audio signal.

    Args:
        audio_signal (np.ndarray): The audio signal to plot the spectrogram of.
        sample_rate (int): The sample rate of the audio signal.
    """

    print(f"Spectrogram of audio signal displayed.")

    plt.figure(figsize=(10, 6))

    plt.specgram(audio_signal, NFFT=1024, Fs=sample_rate, noverlap=512, cmap="inferno")

    plt.title("Spectrogram of Audio Signal")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [s]")

    plt.colorbar(label="Intensity [dB]")

    plt.show()
