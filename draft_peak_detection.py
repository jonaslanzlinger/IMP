import numpy as np
from pydub import AudioSegment
import scipy.io.wavfile as wav
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import os
import simpleaudio as sa
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from matplotlib.animation import FuncAnimation


def load_wav_pydub(wav_file):
    """Load a WAV file using pydub and convert it to a NumPy array."""
    audio = AudioSegment.from_wav(wav_file)

    # Convert audio to raw data (samples)
    samples = np.array(audio.get_array_of_samples())

    # If stereo, take only one channel
    if audio.channels == 2:
        samples = samples[::2]  # Take every second sample (left channel)

    return audio.frame_rate, samples


def find_click_timestamps(samples, sample_rate):
    """Find the timestamps of click noises in the audio."""
    # Normalize the data
    normalized_samples = samples / np.max(np.abs(samples))

    # Find peaks (representing "click" noise)
    # You may need to adjust the height and distance parameters based on your data
    peaks, _ = find_peaks(
        np.abs(normalized_samples), height=0.5, distance=sample_rate // 10
    )

    # Convert peaks to time (in seconds)
    timestamps = peaks / sample_rate
    return timestamps, peaks


# Load the audio data and convert to numpy arrays
def load_audio_data(audio_file):
    audio = AudioSegment.from_wav(audio_file)
    samples = np.array(audio.get_array_of_samples())

    # If stereo, take just one channel
    if audio.channels == 2:
        samples = samples[::2]

    return audio.frame_rate, samples


# Define the directory where the files are stored
directory = "audio_files/"

# List of audio file names
wav_files = ["pi1_audio.wav"]

timestamps = []

# Construct the full path for each file and process them
for wav_file in wav_files:
    full_path = os.path.join(directory, wav_file)
    print(full_path)
    audio_data = [load_audio_data(full_path)]
    wave_obj = sa.WaveObject.from_wave_file(full_path)
    # play_obj = wave_obj.play()
    # play_obj.wait_done()
    # timestamps = load_wav_pydub(full_path)

    # Load the audio file
    sample_rate, samples = load_wav_pydub(full_path)

    # Find the peaks and corresponding timestamps
    timestamps, peaks = find_click_timestamps(samples, sample_rate)


# Construct the full path for each file and process them
for wav_file in wav_files:
    full_path = os.path.join(directory, wav_file)
    wave_obj = sa.WaveObject.from_wave_file(full_path)
    # play_obj = wave_obj.play()
    # play_obj.wait_done()
    # timestamps = load_wav_pydub(full_path)

    # Load the audio file
    sample_rate, samples = load_wav_pydub(full_path)

    # Find the peaks and corresponding timestamps
    timestamps, peaks = find_click_timestamps(samples, sample_rate)

    # Print the timestamps
    print(f"Click noise timestamps: {timestamps}")
    play_obj = wave_obj.play()
    # Print the timestamps
    print(f"Click noise timestamps: {timestamps}")

    # Optionally, plot the waveform and detected peaks
    plt.figure(figsize=(10, 4))
    plt.plot(samples, label="Audio signal")
    plt.plot(peaks, samples[peaks], "x", label="Detected peaks")
    plt.title("Detected Click Noises")
    plt.xlabel("Sample Number")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.show()
    play_obj.wait_done()

# print(f"Timestamps for {wav_file}: {timestamps}")


# # Example usage
# wav_files = ["audio1.wav", "audio2.wav", "audio3.wav", "audio4.wav"]

# for wav_file in wav_files:
#     timestamps = find_click_timestamps(wav_file)
#     print(f"Timestamps for {wav_file}: {timestamps}")
