import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import FastICA
from pysoundlocalization.core.Audio import Audio

"""
In this example, we will demonstrate how to use FastICA to separate two sound sources from a mixed audio signal.
We will mix a speech signal with a sinusoidal noise signal and then use FastICA to separate the two sources.
"""

speech_audio = Audio(filepath="../../data/00_SOUND_BANK/noise/meteo_speaker.wav")
speech_audio.load_audio_file()
speech_signal = speech_audio.get_audio_signal_unchunked()
speech_sample_rate = speech_audio.get_sample_rate()

noise_frequency = 2500
noise_amplitude = 0.05
noise_sample_rate = speech_sample_rate
noise_time_array = np.linspace(
    0, len(speech_signal) / speech_sample_rate, len(speech_signal), endpoint=False
)
noise_signal = noise_amplitude * np.sin(2 * np.pi * noise_frequency * noise_time_array)
noise_audio = Audio.create_from_signal(
    audio_signal=noise_signal, sample_rate=noise_sample_rate
)

combined_signal = speech_signal + noise_signal

combined_audio = Audio.create_from_signal(
    audio_signal=combined_signal, sample_rate=speech_sample_rate
)

# combined_audio.play()

signalSummation = np.c_[
    speech_audio.get_audio_signal_unchunked(),
    noise_audio.get_audio_signal_unchunked(),
]

ica = FastICA(
    n_components=2
)  # n_components denotes the number of sound sources in the mixed audio signal
sources = ica.fit_transform(signalSummation)

plt.figure(figsize=(10, 6))

# Plot original mixed signals (True Sources)
plt.subplot(2, 1, 1)
plt.title("Mixed Signals (True Sources)")
for i, sig in enumerate(signalSummation.T):
    plt.plot(sig, label=f"Signal {i+1}")
plt.legend()
plt.xlabel("Samples")
plt.ylabel("Amplitude")

# Plot ICA recovered signals
plt.subplot(2, 1, 2)
plt.title("ICA Recovered Signals")
for i, sig in enumerate(sources.T):
    plt.plot(sig, label=f"Recovered Source {i+1}")
plt.legend()
plt.xlabel("Samples")
plt.ylabel("Amplitude")

plt.tight_layout()
plt.show()

speech_source = sources[:, 0]
noise_source = sources[:, 1]

speech_audio = Audio.create_from_signal(
    audio_signal=speech_source, sample_rate=speech_sample_rate
)
noise_audio = Audio.create_from_signal(
    audio_signal=noise_source, sample_rate=speech_sample_rate
)

#############################################
# WARNING: LOUD!!!
# ###########################################

# speech_audio.play()
# noise_audio.play()

# ###########################################
