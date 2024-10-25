from core.Audio import Audio
import matplotlib.pyplot as plt


def spectrogram_plot(audio: Audio) -> None:
    """
    Plot the spectrogram of an audio signal.

    Args:
        audio (Audio): Audio object containing the audio signal to plot.
    """
    sample_rate = audio.sample_rate
    audio_signal = audio.get_audio_signal()

    plt.figure(figsize=(10, 6))

    plt.specgram(audio_signal, NFFT=1024, Fs=sample_rate, noverlap=512, cmap="inferno")

    plt.title("Spectrogram of Audio Signal")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [s]")

    plt.colorbar(label="Intensity [dB]")

    plt.show()
