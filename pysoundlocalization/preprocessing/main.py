import scipy.io.wavfile as wav
import warnings
from core.Audio import Audio
from preprocessing.FrequencyFilterChain import FrequencyFilterChain
from preprocessing.LowPassFilter import LowPassFilter

warnings.filterwarnings("ignore")

audio = Audio(filepath="preprocessing/pi1_audio.wav")
audio.load_audio_file()

frequency_filter_chain = FrequencyFilterChain()

frequency_filter_chain.add_filter(LowPassFilter(cutoff_frequency=200, order=4))

frequency_filter_chain.apply(audio)
