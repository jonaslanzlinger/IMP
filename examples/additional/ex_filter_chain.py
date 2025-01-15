from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from datetime import timedelta
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.HighCutFilter import HighCutFilter
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.visualization.audio_spectrogram_plot import (
    audio_spectrogram_plot,
)
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer

"""
This script shows how to apply a frequency filter chain to an audio signal.

In this example, the goal is to isolate the sine wave.
Therefore, we load an audio file, apply a low-pass filter and a low-cut filter to it, 
and reduce the noise.

To show the effect, we plot the spectrogram of the audio signal before and after the processing.
Optionally, we can play the audio signal before and after the processing (beware: LOUD).
"""

audio = Audio(
    filepath="../../data/06_classroom/pi3_audio_2024-11-28_15-00-00-000000.wav"
)
SampleTrimmer.slice_from_to(
    audio, start_time=timedelta(seconds=8), end_time=timedelta(seconds=13)
)

audio_spectrogram_plot(
    audio_signal=audio.get_audio_signal_unchunked(),
    sample_rate=audio.get_sample_rate(),
)
# play the un-processed audio (potentially LOUD!!!)
# audio.play()

frequency_filter_chain = FrequencyFilterChain()

frequency_filter_chain.add_filter(HighCutFilter(cutoff_frequency=6800, order=10))
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=5800, order=10))

frequency_filter_chain.apply(audio)

NoiseReducer.reduce_noise(audio)

AudioNormalizer.normalize_audio_to_max_amplitude(audio, 1)

audio_spectrogram_plot(
    audio_signal=audio.get_audio_signal_unchunked(),
    sample_rate=audio.get_sample_rate(),
)
# play the final processed audio (potentially LOUD!!!)
# audio.play()
