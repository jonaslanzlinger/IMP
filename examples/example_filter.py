import warnings
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowPassFilter import LowPassFilter
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot
import os

warnings.filterwarnings("ignore")
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

filepath = os.path.join(root, "examples", "example_audio", "pi1_audio.wav")
audio = Audio(filepath=filepath)
audio.load_audio_file()


spectrogram_plot(
    audio_signal=audio.get_unchunked_audio_signal(),
    sample_rate=audio.get_sample_rate(),
)
print(audio.get_unchunked_audio_signal())
frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowPassFilter(cutoff_frequency=300, order=5))
frequency_filter_chain.apply(audio)

print(audio.get_unchunked_audio_signal())
# audio.play()

spectrogram_plot(
    audio_signal=audio.get_unchunked_audio_signal(),
    sample_rate=audio.get_sample_rate(),
)
