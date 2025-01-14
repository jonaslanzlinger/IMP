from datetime import timedelta
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.visualization.audio_wave_plot import audio_wave_plot

"""
In this example we show how to chunk audio signals.
This is used for the multilateration algorithm, where the position of
a sound source is estimated for each chunk of audio.

First we show how to chunk a single audio signal.
Then we show how to chunk all audio signals of an environment at once.
"""

#####################################
# Chunking of a single audio signal #
#####################################

audio = Audio(filepath="../data/03_classroom/pi1_audio.wav")

print("Unchunked audio:")
print(
    f"Audio Chunks: {len(audio.get_audio_signal())}, Audio signal shape: {audio.get_audio_signal().shape}"
)
audio_wave_plot(audio.get_audio_signal_unchunked(), audio.get_sample_rate())

audio.chunk_audio_signal_by_duration(chunk_duration=timedelta(milliseconds=5000))

print("Chunked audio:")
for i, chunk in enumerate(audio.get_audio_signal_chunked()):
    print(f"Chunk {i}: {len(chunk)} samples")
    audio_wave_plot(chunk, audio.get_sample_rate())


# #################################################
# Chunking of all audio signals of an environment #
# #################################################

simulation = Simulation.create()

environment = simulation.add_environment(
    "Test Environment", [(0, 0), (0, 10), (10, 10), (10, 0)]
)
mic1 = environment.add_microphone(2, 4)
mic2 = environment.add_microphone(8, 5)

mic1.set_audio(Audio(filepath="../data/03_classroom/pi1_audio.wav"))
mic2.set_audio(Audio(filepath="../data/03_classroom/pi2_audio.wav"))

environment.chunk_audio_signals_by_duration(timedelta(milliseconds=5000))
# ... or alternatively chunk by samples. This will create chunks of 1 second length:
# environment.chunk_audio_signals_by_samples(chunk_samples=44100)

print("Number of chunks in environment:")
print(f"Microphone 1: {len(mic1.get_audio().get_audio_signal_chunked())} chunks")
print(f"Microphone 2: {len(mic2.get_audio().get_audio_signal_chunked())} chunks")
