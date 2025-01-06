import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
from audio_utils import load_audio_data, play_audio
import time

audio_files = [
    "data/08_door_bell/pi1_audio.wav",
    "data/08_door_bell/pi2_audio.wav",
    "data/08_door_bell/pi3_audio.wav",
    "data/08_door_bell/pi4_audio.wav",
]

num_audio_files = len(audio_files)

audio_data = [load_audio_data(file) for file in audio_files]

min_samples = min(len(samples) for frame_rate, samples in audio_data)
sample_rate = 44100
min_duration = min_samples / sample_rate
fps = 20
interval = 1000 / fps
min_frames = int(min_duration * fps)
chunk_size = min_samples // min_frames

buffer = 5 * sample_rate
buffer_caret = buffer // 3 * 2

fig, axs = plt.subplots(num_audio_files, 1, figsize=(10, 8))
transients = [ax.plot([], [])[0] for ax in axs]

for ax in axs:
    ax.set_xlim(0, buffer)
    ax.set_ylim(-1, 1)

plot_data = [np.zeros(buffer) for _ in range(num_audio_files)]

start_time = None


def update(frame):
    global start_time
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


# Play all audio files
for audio_file in audio_files:
    audio_thread = threading.Thread(target=play_audio, args=(audio_file,))
    audio_thread.start()

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
