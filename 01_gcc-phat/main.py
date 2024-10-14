# TODO
# 1. read 4 audio files
# 2. find time delay between microphones
# 3. calculate TDOA using output of gcc_phat

# Issues
# 1. what is max_tau and why necessary? why big change in DOAs when changed from 2 to 2.5meters?

import numpy as np
import math
from scipy.io import wavfile
import gcc_phat
import multilateration
import glob
from itertools import combinations

# in meters
mic_positions = np.array(
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
    wav_filenames = glob.glob("../audio_files/*.wav")  # Load all .wav files in the directory
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

    # Parameters for GCC-PHAT and sound properties
    sound_speed = 343.2  # Speed of sound in m/s
    mic_distance = 2  # Assumed distance between microphones (can vary)
    max_tau = mic_distance / sound_speed  # Maximum possible time delay

    # Compute TDoA for all pairs of microphones
    mic_pairs = list(combinations(range(n_mics), 2))  # All unique mic pairs
    tdoas = {}  # Store TDoA results

    def compute_tdoa(sig_a, sig_b):
        return gcc_phat.gcc_phat(sig_a * window, sig_b * window, fs=sample_rate, max_tau=max_tau)

    for pair in mic_pairs:
        mic_a, mic_b = pair
        tdoa, _ = compute_tdoa(audio_signals[mic_a], audio_signals[mic_b])
        tdoas[pair] = tdoa
        print(f"TDoA between mic{mic_a + 1} and mic{mic_b + 1}: {tdoa:.6f} seconds")

    # Example: calculate angles from the TDoA for each pair
    for pair, tdoa in tdoas.items():
        mic_a, mic_b = pair
        theta = math.asin(tdoa / max_tau) * 180 / math.pi
        print(f"Estimated DoA (theta) between mic{mic_a + 1} and mic{mic_b + 1}: {theta:.2f} degrees")

    tdoas_simple = []
    for par, tdoa in tdoas.items():
        tdoas_simple.append(tdoa)

    print(tdoas_simple)

    # Further processing can involve combining the results from all pairs to get a refined estimate
    xs, ys, zs = multilateration.multilateration(tdoas_simple, mic_positions)

    print(f"Sound Localized at: ({xs},{ys},{zs})")

if __name__ == "__main__":
    main()
