import numpy as np
from scipy.signal import butter, filtfilt
import librosa
import librosa.display
from pysoundlocalization.core.Audio import Audio
import warnings
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot
from pysoundlocalization.visualization.wave_plot import wave_plot
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowPassFilter import LowPassFilter
import os

warnings.filterwarnings("ignore")
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

speech_filepath = os.path.join(root, "examples", "example_audio", "speech_example.wav")
speech_audio = Audio(filepath=speech_filepath)
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
noise_audio = Audio(audio_signal=noise_signal, sample_rate=noise_sample_rate)

combined_signal = speech_signal + noise_signal

combined_audio = Audio(audio_signal=combined_signal, sample_rate=speech_sample_rate)

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowPassFilter(cutoff_frequency=1500, order=5))
# frequency_filter_chain.apply(combined_audio)

spectrogram_plot(
    combined_audio.get_audio_signal_unchunked(), combined_audio.get_sample_rate()
)

# combined_audio.play()


def stft(signal, window_size, hop_length):
    return librosa.stft(signal, n_fft=window_size, hop_length=hop_length)


window_size = 2048
hop_length = 512
stft_matrix = stft(combined_audio.get_audio_signal_unchunked(), window_size, hop_length)

magnitude_spectrogram = np.abs(stft_matrix)
print(f"Magnitude spectrogram shape: {magnitude_spectrogram.shape}")

dominant_freqs = []
for i in range(magnitude_spectrogram.shape[1]):
    mag_frame = magnitude_spectrogram[:, i]
    top_freq_indices = np.argsort(mag_frame)[-3:]
    freqs = librosa.fft_frequencies(
        sr=speech_audio.get_sample_rate(), n_fft=window_size
    )
    dominant_freqs.append(freqs[top_freq_indices])

dominant_freqs = np.array(dominant_freqs)
print(f"Dominant frequencies across frames:\n{dominant_freqs}")


def notch_filter(audio: Audio, freq) -> Audio:
    nyquist = 0.5 * audio.get_sample_rate()
    norm_freq = freq / nyquist
    b, a = butter(2, [norm_freq - 0.01, norm_freq + 0.01], btype="bandstop")
    filtered_signal = filtfilt(b, a, audio.get_audio_signal_unchunked())
    filtered_audio = Audio(
        audio_signal=filtered_signal, sample_rate=audio.get_sample_rate()
    )
    return filtered_audio


filtered_audio = notch_filter(combined_audio, noise_frequency)

# filtered_audio.play()

wave_plot(filtered_audio.get_audio_signal_unchunked(), filtered_audio.get_sample_rate())
