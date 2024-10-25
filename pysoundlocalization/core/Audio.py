import os
import soundfile as sf
import simpleaudio as sa
import numpy as np


# TODO: Move towards a generic SoundInput wrapper class
class Audio:
    def __init__(self, filepath: str | None = None, sample_rate: int | None = None, audio_signal: np.ndarray | None = None):
        """
        Initialize the Audio class with a specific audio file path.
        This class supports audio formats supported by soundfile, like WAV, FLAC, AIFF, OGG, etc.

        Args:
            filepath (str | None): Path to the audio file.
            sample_rate (int | None): Sampling rate of the audio signal in Hz. May also be set by loading the audio from the filepath.
            audio_signal (np.ndarray | None): Pre-loaded audio signal data as a numpy array. May also be set by loading the audio from the filepath.
        """
        self.load_audio_file(filepath)
        self.filepath = filepath

    def load_audio_file(self, filepath: str = None) -> tuple[int, np.ndarray]:
        """
        Manually load the audio file from the filepath. May be used to re-load the file from the filepath.

        Returns:
            tuple[int, np.ndarray]: A tuple containing the sample rate (Hz) and audio signal (numpy array).

        Raises:
            FileNotFoundError: If no valid file path is provided or the file does not exist.
        """
        if filepath is None:
            filepath = self.filepath

        if not filepath or not os.path.exists(filepath):
            raise FileNotFoundError(
                f"No valid audio file provided or file not found: {filepath}"
            )

        # Load the audio file using soundfile
        self.audio_signal, self.sample_rate = sf.read(filepath)

        return self.sample_rate, self.audio_signal

    def get_audio_signal(self) -> np.ndarray:
        """
        Return the audio signal data of the audio file.
        The audio is automatically loaded from the filepath if not audio_signal is empty.

        Returns:
            np.ndarray: The audio signal data as a numpy array.

        Raises:
            FileNotFoundError: If the audio file needs to be loaded but the file path is not set.
        """
        if self.audio_signal is None:
            self.load_audio_file()
        return self.audio_signal

    def set_audio_signal(self, audio_signal: np.ndarray) -> None:
        """
        Set the audio signal data of the audio file.

        Args:
            audio_signal (np.ndarray): The audio signal data as a numpy array.
        """
        self.audio_signal = audio_signal

    def get_sample_rate(self) -> int:
        """
        Return the sample rate of the audio file.

        Returns:
            int: The sample rate in Hz.

        Raises:
            ValueError: If the sample rate has not been set or loaded.
        """
        if self.sample_rate is None:
            self.load_audio_file()
        return self.sample_rate

    def get_duration(self) -> float:
        """
        Return the duration of the audio file in seconds.

        Returns:
            float: Duration of the audio file in seconds.

        Raises:
            ValueError: If the audio signal has not been loaded yet.
        """
        if self.audio_signal is None:
            self.load_audio_file()
        return len(self.audio_signal) / self.sample_rate

    def play(self, num_channels: int = 1, bytes_per_sample: int = 2) -> None:
        """
        Play the audio file using simpleaudio.

        Args:
            num_channels (int): Number of audio channels. Default is 1 (mono).
            bytes_per_sample (int): Number of bytes per sample. Default is 2 (16-bit audio).

        Raises:
            ValueError: If the audio signal has not been loaded yet.
        """
        if self.audio_signal is None:
            self.load_audio_file()

        # Convert the audio signal to the correct format for simpleaudio
        audio_signal = np.int16(self.audio_signal * 32767)

        play_obj = sa.play_buffer(audio_signal, num_channels, bytes_per_sample, self.sample_rate)
        play_obj.wait_done()