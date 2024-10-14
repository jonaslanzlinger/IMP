# TODO
# 1. read 4 audio files
# 2. find time delay between microphones
# 3. calculate TDOA using output of gcc_phat

import numpy as np
import math
from scipy.io import wavfile
import gcc_phat

def load_wav_file(filename):
    """
    Load a wav file and return the sample rate and audio data.
    """
    sample_rate, data = wavfile.read(filename)
    return sample_rate, data

def main():
    # Load the two wav files
    sample_rate1, sig1 = load_wav_file('../audio_files/pi1_audio.wav')
    sample_rate2, sig2 = load_wav_file('../audio_files/pi2_audio.wav')

    # Ensure both signals are sampled at the same rate
    if sample_rate1 != sample_rate2:
        raise ValueError("Sample rates for the two files do not match.")

    # Shorten the longer signal to match the shorter one if necessary
    min_length = min(len(sig1), len(sig2))
    sig1 = sig1[:min_length]
    sig2 = sig2[:min_length]

    # Window function (optional)
    window = np.hanning(min_length)

    # Parameters for GCC-PHAT and sound properties
    sound_speed = 343.2  # Speed of sound in m/s
    distance = 0.14  # Distance between microphones in meters
    max_tau = distance / sound_speed  # Maximum possible time delay between microphones

    # Apply GCC-PHAT to compute the time delay (tau)
    tau, _ = gcc_phat.gcc_phat(sig1 * window, sig2 * window, fs=sample_rate1, max_tau=max_tau)

    # Compute the angle of arrival (theta)
    theta = math.asin(tau / max_tau) * 180 / math.pi

    print(f'Estimated direction of arrival (theta): {theta:.2f} degrees')

if __name__ == "__main__":
    main()