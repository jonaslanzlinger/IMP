import numpy as np
from pydub import AudioSegment
import simpleaudio as sa


def load_audio_data(audio_file):
    audio = AudioSegment.from_wav(audio_file)
    samples = np.array(audio.get_array_of_samples())

    # If stereo, take just one channel
    if audio.channels == 2:
        samples = samples[::2]

    return audio.frame_rate, samples


def play_audio(audio_file):
    wave_obj = sa.WaveObject.from_wave_file(audio_file)
    play_obj = wave_obj.play()
    play_obj.wait_done()
