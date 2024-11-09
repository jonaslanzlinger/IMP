import warnings
from core.Audio import Audio
from preprocessing.FrequencyFilterChain import FrequencyFilterChain
from preprocessing.LowPassFilter import LowPassFilter
from visualization.spectrogram_plot import spectrogram_plot
import os

warnings.filterwarnings("ignore")
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

filepath = os.path.join(root, "examples", "example_audio", "pi1_audio.wav")
audio = Audio(filepath=filepath)
audio.load_audio_file()


spectrogram_plot(audio)

frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowPassFilter(cutoff_frequency=300, order=5))
frequency_filter_chain.apply(audio)

# audio.play()

spectrogram_plot(audio)
