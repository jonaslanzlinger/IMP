import matplotlib.pyplot as plt
from pysoundlocalization.core.Environment import Environment
import numpy as np
from matplotlib.animation import FuncAnimation
import time
import threading
import pygame
import soundfile as sf
import tempfile


def environment_play_audio_plot(environment: Environment) -> None:
    """
    Visualizes all waves of the audio signals in the environment and plays the first audio object.

    Args:
        environment (Environment): Environment object containing the audios.
    """

    print(f"Environment Play Audio Plot displayed.")

    plt.rcParams["toolbar"] = "none"

    min_samples = environment.get_min_num_samples()
    sample_rate = environment.get_sample_rate()
    min_duration = min_samples / sample_rate
    fps = 20
    interval = 1000 / fps
    min_frames = int(min_duration * fps)

    buffer = 5 * sample_rate
    buffer_caret = buffer // 3 * 2

    fig, axs = plt.subplots(4, 1, figsize=(10, 8))
    fig.canvas.manager.set_window_title(
        f"{environment.get_name()} - Environment Play Audio Plot"
    )

    transients = [ax.plot([], [])[0] for ax in axs]

    for ax in axs:
        ax.set_xlim(0, buffer)
        ax.set_ylim(-1, 1)

    plot_data = [np.zeros(buffer) for _ in range(4)]

    start_time = None

    audio_data = [
        (sample_rate, mic.get_audio().get_audio_signal_unchunked())
        for mic in environment.get_mics()
    ]

    def update(frame):
        nonlocal start_time
        if start_time is None:
            start_time = time.time()

        # Calculate the elapsed time in seconds since playback started
        elapsed_time = time.time() - start_time

        samples_played = int(elapsed_time * sample_rate)
        chunk_size = sample_rate // fps

        for i, (transient, (sr, samples)) in enumerate(zip(transients, audio_data)):
            start = samples_played
            end = start + chunk_size

            # If the end exceeds the sample length, fill with zeros
            if end > len(samples):
                end = len(samples)

            # Normalize the data between -1 and 1
            new_data = samples[start:end] / np.max(np.abs(samples))

            # Shift data in the buffer to the left by chunk_size
            plot_data[i] = np.roll(plot_data[i], -chunk_size)

            # Insert the new chunk at buffer_caret position
            plot_data[i][buffer_caret : buffer_caret + chunk_size] = new_data
            plot_data[i][buffer_caret + chunk_size :] = 0

            # Update transient data for the line
            transient.set_data(np.arange(0, buffer), plot_data[i])

        return transients

    audio = environment.get_mics()[0].get_audio()
    audio_signal = audio.get_audio_signal_unchunked()
    sample_rate = audio.get_sample_rate()

    # Save the signal as a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_audio_file:
        sf.write(temp_audio_file.name, audio_signal, sample_rate)
        audio_path = temp_audio_file.name
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)

    def on_close(event):
        """Callback to stop audio playback when the plot window is closed."""
        print("Stopping audio playback...")
        pygame.mixer.music.stop()

    # Connect the close event to the stop function
    fig.canvas.mpl_connect("close_event", on_close)

    pygame.mixer.music.play()

    # Animation function
    ani = FuncAnimation(
        fig,
        update,
        cache_frame_data=False,
        interval=interval,
        blit=True,
    )

    plt.tight_layout()
    plt.show()

    pygame.mixer.quit()
