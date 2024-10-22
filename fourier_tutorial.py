# https://medium.com/@ongzhixuan/frequency-analysis-of-audio-signals-with-fourier-transform-f89ac113a2b4
# https://medium.com/@ongzhixuan/exploring-the-short-time-fourier-transform-analyzing-time-varying-audio-signals-98157d1b9a12

import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft


duration = 1
sampling_rate = 1024
num_samples = duration * sampling_rate

t = np.linspace(0, duration, num_samples, endpoint=False)

frequencies = [50, 120, 200]
amplitudes = [1, 0.5, 0.3]
signal = sum(
    amplitude * np.sin(2 * np.pi * frequency * t)
    for frequency, amplitude in zip(frequencies, amplitudes)
)

noise_level = 0.15
noise = noise_level * np.random.normal(0, 1, num_samples)
mystery_signal = signal + noise

plt.plot(t, mystery_signal)
plt.title("Mystery Signal")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.show()

mystery_signal_fft = fft(mystery_signal)

amplitude_spectrum = np.abs(mystery_signal_fft)

amplitude_spectrum = amplitude_spectrum / np.max(amplitude_spectrum)

freqs = np.fft.fftfreq(num_samples, 1 / sampling_rate)

plt.plot(freqs[: num_samples // 2], amplitude_spectrum[: num_samples // 2])
plt.xlabel("Frequency [Hz]")
plt.ylabel("Normalized Amplitude")
plt.title("Amplitude Spectrum of the Mystery Signal")
plt.show()

threshold = 0.2
dominant_freq_indices = np.where(amplitude_spectrum[: num_samples // 2] >= threshold)
dominant_freqs = freqs[dominant_freq_indices]

print("Dominant Frequencies: ", dominant_freqs)
