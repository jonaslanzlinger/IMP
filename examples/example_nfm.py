from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from datetime import timedelta
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.visualization.spectrogram_plot import spectrogram_plot
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)

audio_file = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC3_2024-11-07_10-30-46_550904.wav"
audio = Audio(filepath=audio_file, convert_to_sample_rate=11025)
print(audio.get_duration())

SampleTrimmer.trim_from_beginning(audio, timedelta(seconds=17))
SampleTrimmer.trim_from_end(audio, timedelta(seconds=5))

print(audio.get_duration())

# spectrogram_plot(audio)

# audio.play()


frequency_filter_chain = FrequencyFilterChain()
frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=5000, order=5))
frequency_filter_chain.apply(audio)

# audio.play()

audio = NoiseReducer.reduce_noise(audio=audio)

# audio.play()

# spectrogram_plot(audio)

nmf = NonNegativeMatrixFactorization()
reconstructed_sounds = nmf.run(audio)

print(len(reconstructed_sounds))
for i in range(len(reconstructed_sounds)):
    print(f"Playing reconstructed sound {i+1}")
    audio = Audio.create_from_signal(reconstructed_sounds[i], 11025)
    audio = NoiseReducer.reduce_noise(audio=audio)
    audio.play()
