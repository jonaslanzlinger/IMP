from pysoundlocalization.core.Audio import Audio
import matplotlib.pyplot as plt
import numpy as np


def wave_plot(audio: Audio) -> None:
    """
    Plot the waveform of an audio signal.

    Args:
        audio (Audio): Audio object containing the audio signal to plot.
    """
    plt.figure(figsize=(10, 6))

    timeline = np.linspace(
        0,
        len(audio.get_audio_signal_chunked()) / audio.get_sample_rate(),
        len(audio.get_audio_signal_chunked()),
    )

    plt.plot(timeline, audio.get_audio_signal_chunked())
    plt.title("Waveform")
    plt.ylabel("Amplitude")
    plt.xlabel("Time (seconds)")

    plt.show()
