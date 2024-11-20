import os
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
audio1_filepath = os.path.join(root, "examples", "example_audio", "speech_example.wav")
mic1.set_audio(Audio(filepath=audio1_filepath))

print("Unchunked audio with 1 chunk:")
print(mic1.get_audio().get_audio_signal())  # TODO: fix duration = Nones

# Chunk audio into 1000ms chunks
mic1.get_audio().chunk_audio_signal(chunk_size=1000)

print("Unchunked audio with 5 chunks:")
print(mic1.get_audio())

print("Printing the chunked audio as a single audio signal")
print(mic1.get_audio().get_unchuncked_audio_signal())
print(mic1.get_audio().get_unchuncked_audio_signal().shape)
