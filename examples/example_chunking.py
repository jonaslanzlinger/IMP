import os
from datetime import timedelta

from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation

# Create simulation and add an environment with 4 microphones
simulation = Simulation.create()
environment1 = simulation.add_environment(
    "Test Environment", [(0, 0), (0, 10), (10, 10), (10, 0)]
)
mic1 = environment1.add_microphone(4, 4)

# Add audio
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
audio_filepath = os.path.join(root, "examples", "example_audio", "speech_example.wav")
mic1.set_audio(Audio(filepath=audio_filepath))

print("Unchunked audio with 1 chunk:")
print(mic1.get_audio().get_audio_signal())
print(mic1.get_audio())

# Chunk audio into 1000ms chunks
mic1.get_audio().chunk_audio_signal_by_duration(
    chunk_duration=timedelta(milliseconds=1000)
)

# Alternatively chunk by desired samples per chunk (you need to be aware of the audio's sample rate)
# mic1.get_audio().chunk_audio_signal_by_samples(chunk_samples=44100)

print("Unchunked audio with 5 chunks:")
print(mic1.get_audio())

print("Printing the chunked audio as a single audio signal")
print(mic1.get_audio().get_unchunked_audio_signal())
print(mic1.get_audio().get_unchunked_audio_signal().shape)


####
# Test chunking of all audio at once via environment
####

environment2 = simulation.add_environment(
    "Test Environment 2", [(0, 0), (0, 10), (10, 10), (10, 0)]
)
mic2_1 = environment2.add_microphone(4, 4)
mic2_2 = environment2.add_microphone(2, 2)

mic2_1.set_audio(Audio(filepath=audio_filepath))
mic2_2.set_audio(Audio(filepath=audio_filepath))

environment2.chunk_audio_signals_by_duration(timedelta(milliseconds=1500))

print(mic2_1.get_audio())
print(mic2_2.get_audio())

mic2_1.set_audio(Audio(filepath=audio_filepath))
mic2_2.set_audio(Audio(filepath=audio_filepath))

environment2.chunk_audio_signals_by_samples(chunk_samples=44100)

print(mic2_1.get_audio())
print(mic2_2.get_audio())
