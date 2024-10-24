import os
import soundfile as sf
import simpleaudio as sa
import numpy as np


# TODO: Move towards a generic SoundInput wrapper class


class Audio:
    def __init__(self, filepath=None, sample_rate=None, audio_signal=None):
        """
        Initialize the Audio class with a specific audio file path.
        This class supports audio formats supported by soundfile, like WAV, FLAC, AIFF, OGG, etc.
        """
        self.filepath = filepath
        self.sample_rate = sample_rate
        self.audio_signal = audio_signal

    def load_audio_file(self):
        """
        Manually load the audio file from the filepath. May be used to re-load the file from the filepath.
        """
        if not self.filepath or not os.path.exists(self.filepath):
            raise FileNotFoundError(
                f"No valid audio file provided or file not found: {self.filepath}"
            )

        # Load the audio file using soundfile
        self.audio_signal, self.sample_rate = sf.read(self.filepath)

        return self.sample_rate, self.audio_signal

    def set_filepath(self, filepath):
        """Set the path to a new audio file."""
        self.filepath = filepath

    def get_audio_signal(self):
        """
        Return the audio signal data of the audio file.
        The audio is automatically loaded from the filepath if not done beforehand.
        """
        if self.audio_signal is None:
            self.load_audio_file()
        return self.audio_signal

    def set_audio_signal(self, audio_signal):
        """Set the audio signal data of the audio file."""
        self.audio_signal = audio_signal

    def get_sample_rate(self):
        """Return the sample rate of the audio file."""
        if self.sample_rate is None:
            raise ValueError("No audio file has been loaded yet.")
        return self.sample_rate

    '''
    def get_duration(self):
        """Return the duration of the audio file in seconds."""
        if self.audio_signal is None:
            raise ValueError("No audio file has been loaded yet.")
        return len(self.audio_signal) / self.sample_rate
    '''

    def play(self, num_channels=1, bytes_per_sample=2):
        """Play the audio file."""
        if self.audio_signal is None:
            raise ValueError("No audio file has been loaded yet.")

        # Convert the audio signal to the correct format for simpleaudio
        audio_signal = np.int16(self.audio_signal * 32767)

        play_obj = sa.play_buffer(audio_signal, num_channels, bytes_per_sample, self.sample_rate)
        play_obj.wait_done()


# TODO: def add(path, mic1): -> add a audio file by path and associate with mic1 (prior created)
# TODO: def pre_process() -> for each Audio object, we can preprocess the audio
