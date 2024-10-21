# Example to localize a sound source using 4 microphones and GCC-PHAT
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Simulation import Simulation


simulation = Simulation.create()

# Define an L-shaped room using vertices
l_shape_vertices = [(0, 0), (4.7, 0), (4.7, 2), (3, 2), (3, 4.5), (0, 4.5)]
room1 = simulation.add_room("L-Shaped Room", l_shape_vertices)

# Create and add microphones with decimal coordinates
mic1 = room1.add_microphone(1.2, 2.5)  # Inside the L-shaped room
mic2 = room1.add_microphone(2.6, 3.6784849)  # Inside the L-shaped room

room1.visualize()

#Add and pre-process audio
audio1 = Audio(filepath='example_audio/pi1_audio.wav')
sample_rate1, audio_signal1 = audio1.load_audio_file()

# TODO: support pre-processing of audio
#print(f"Sample Rate: {sample_rate1}")
#print(f"Audio Signal: {audio_signal1[:10]}")  # Print first 10 samples of the audio

#Associate audio with mic
mic1.add_recorded_audio(audio_signal1)

#TODO: It is weird that we have to use load_audio_file() before we  can use get_audio_signal(). Maybe get_audio_signal() should load the audio if not already done?
audio2 = Audio(filepath='example_audio/pi2_audio.wav')
audio2.load_audio_file()
mic2.add_recorded_audio(audio2.get_audio_signal())
#print(mic2.get_recorded_audio())

# TODO: add MAX_TAU via variables instead of 2/343.2 -> max_tau = MIC_DISTANCE / sound_speed  # Maximum possible time delay
tdoa12, cc = room1.compute_tdoa(mic1.get_recorded_audio(), mic2.get_recorded_audio(), sample_rate1, 2/343.2)
print(f"TDoA between mic1 and mic2: {tdoa12:.6f} seconds")

# Compute DOA from Room
# room1.getDOA(...)

#print(mic1.get_position())