import matplotlib.pyplot as plt
from pysoundlocalization.core.Environment import Environment


def environment_overlap_wave_plot(environment: Environment) -> None:
    """
    Visualizes all waves of the audio signals in the environment.

    Args:
        environment (Environment): Environment object containing the audios.
    """

    print(f"Environment Wave Plot displayed.")

    plt.rcParams["toolbar"] = "none"

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.canvas.manager.set_window_title(
        f"{environment.get_name()} - Environment Wave Plot"
    )

    # Plot audio waveforms for each microphone in the environment
    for i, mic in enumerate(environment.get_mics()):
        audio_data = mic.get_audio().get_audio_signal_unchunked()
        sample_count = mic.get_audio().get_num_samples()
        ax.plot(audio_data[:sample_count], label=f"Microphone {i + 1}")

    ax.set_title("Audio Waveforms in the Environment")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Amplitude")
    ax.legend(loc="upper right")
    ax.grid(True)

    plt.tight_layout()
    plt.show()
