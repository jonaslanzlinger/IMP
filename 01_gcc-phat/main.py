# TODO
# 1. read 4 audio files
# 2. find time delay between microphones
# 3. calculate TDOA using output of gcc_phat

import numpy as np
from scipy.io import wavfile
from gcc_phat import gcc_phat
import multilateration
import doa
import glob
import plot
from itertools import combinations

# Parameters for GCC-PHAT and sound properties
SOUND_SPEED = 343.2  # Speed of sound in m/s
MIC_DISTANCE = 2  # Assumed distance between microphones (can vary)
MAX_TAU = MIC_DISTANCE / SOUND_SPEED  # Maximum possible time delay

# There must be a matching MIC_POSITION for every wav file found in the directory.
# The first wav file corresponds to the first MIC_POSITION, and so on.
AUDIO_FILES_DIR ="../audio_files/*.wav"

# Mic positions defined in meters.
# TODO: Why -10 to 10?
MIC_POSITIONS = np.array(
    [
        {"x": -10, "y": -10, "z": 0},
        {"x": -10, "y": 10, "z": 0},
        {"x": 10, "y": 10, "z": 0},
        {"x": 10, "y": -10, "z": 0},
    ]
)

def load_wav_files():
    """
    Dynamically load all wav files from the current directory
    or any specified folder.
    """
    wav_filenames = glob.glob(AUDIO_FILES_DIR)  # Load all .wav files in the directory
    audio_signals = []
    sample_rate = None

    for filename in wav_filenames:
        sr, data = wavfile.read(filename)
        if sample_rate is None:
            sample_rate = sr
        elif sample_rate != sr:
            raise ValueError(f"Sample rate mismatch in file {filename}")

        audio_signals.append(data)

    return sample_rate, audio_signals, wav_filenames

def main():
    # Load all wav files
    sample_rate, audio_signals, filenames = load_wav_files()

    # Check if enough microphones were loaded
    n_mics = len(audio_signals)
    if n_mics < 2:
        raise ValueError("At least two microphones are required for DoA estimation.")

    print(f"Loaded {n_mics} microphone signals from files: {filenames}")

    # Ensure all signals are the same length
    min_length = min(map(len, audio_signals))
    audio_signals = [sig[:min_length] for sig in audio_signals]

    # Window function (optional)
    window = np.hanning(min_length)

    # Compute TDoA for all pairs of microphones
    mic_pairs = list(combinations(range(n_mics), 2))  # All unique mic pairs
    tdoas = {}  # Store TDoA results


    # For each microphone pair, use GCC-PHAT to compute the TDoA
    for pair in mic_pairs:
        mic_a, mic_b = pair

        sig_a = audio_signals[mic_a]
        sig_b = audio_signals[mic_b]
        tdoa, _ = gcc_phat(sig_a * window, sig_b * window, fs=sample_rate, max_tau=MAX_TAU)

        tdoas[pair] = tdoa
        print(f"TDoA between mic{mic_a + 1} and mic{mic_b + 1}: {tdoa:.6f} seconds")

    # Example: calculate angles from the TDoA for each pair
    # TODO: maybe refactor to put more into the doa.py file?
    for pair, tdoa in tdoas.items():
        mic_a, mic_b = pair
        theta = doa.compute_doa(tdoa, MAX_TAU)
        print(f"Estimated DoA (theta) between mic{mic_a + 1} and mic{mic_b + 1}: {theta:.2f} degrees")

    tdoas_simple = []
    for par, tdoa in tdoas.items():
        tdoas_simple.append(tdoa)

    # Perform multilateration to approximate the sound source using the returned time delays of GCC-PHAT
    x, y, z = multilateration.approximate_sound_source(tdoas_simple, MIC_POSITIONS)
    print(f"Source position: x={x}, y={y}, z={z}")

    # Visualize the result of the multilateration
    plot.plot_2d_multilateration_result(x, y, MIC_POSITIONS)

if __name__ == "__main__":
    main()
