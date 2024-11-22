from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from datetime import timedelta
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.core.Simulation import Simulation
from datetime import datetime

simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Machine Environment", [(0, 0), (0, 10), (10, 10), (10, 0)]
)
mic1 = environment1.add_microphone(8.61, 2)
mic2 = environment1.add_microphone(2, 3)

audio_file1 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC1_2024-11-07_10-30-45_977581.wav"
audio1 = Audio(filepath=audio_file1, convert_to_sample_rate=11025)
mic1.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 977581))
SampleTrimmer.slice_from_to(
    audio1, start_time=timedelta(seconds=17), end_time=timedelta(seconds=20)
)
mic1.set_audio(audio1)

audio_file2 = "Illwerke/03_experiment1_1punkt_klatschen_old/first25seconds_trimmed_output_MIC2_2024-11-07_10-30-45_474498.wav"
audio2 = Audio(filepath=audio_file2, convert_to_sample_rate=11025)
mic2.set_recording_start_time(datetime(2024, 11, 7, 10, 30, 45, 474498))
SampleTrimmer.slice_from_to(
    audio2, start_time=timedelta(seconds=17), end_time=timedelta(seconds=23)
)
mic2.set_audio(audio2)

NoiseReducer.reduce_noise(audio=audio1)
NoiseReducer.reduce_noise(audio=audio2)

nmf = NonNegativeMatrixFactorization()

# Run nmf for all audio in the environment associated with a mic
# Note that the resulting splits are quite similar (or practically speaking the same) as when running nmf individually for the audio files
nmf_all_audio_from_environment = nmf.experimental_run_for_all_audio_in_environment(
    environment1
)
for mic, audio_list in nmf_all_audio_from_environment.items():
    print(f"Mic: {mic.get_name()}")
    for idx, audio in enumerate(audio_list):
        print(f"  Audio {idx + 1}: {len(audio.get_audio_signal_unchunked())} samples")
        # audio.play()

# NOTE: As audio1 is 3 seconds and Audio2 6 seconds, the sample count of the reconstructed signals is in a 1:2 proportion, as it should be.

# nmf.visualize_wave_form()
# nmf.visualize_filtered_spectrograms()
