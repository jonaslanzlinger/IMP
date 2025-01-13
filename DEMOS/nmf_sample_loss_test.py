from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)

"""
This script tests the loss percentage of the NMF algorithm.
"""

audio = Audio("../data/07_mosquito/pi1_audio_2024-11-06_15-30-17_252158.wav")

original_num_samples = audio.get_num_samples()

nmf = NonNegativeMatrixFactorization(
    number_of_sources_to_extract=2,
    sample_rate=44100,
)

result = nmf.run_for_single_audio(audio=audio, visualize_results=False)

print(
    "Loss percentage: ", 100 - 100 * result[0].get_num_samples() / original_num_samples
)
