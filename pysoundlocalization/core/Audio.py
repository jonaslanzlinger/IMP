import librosa
import numpy as np
import os
import soundfile as sf
import simpleaudio as sa
import sounddevice as sd
from scipy.io import wavfile


# TODO: Move towards a generic SoundInput wrapper class?
class Audio:
    def __init__(
        self,
        filepath: str | None = None,
        convert_to_sample_rate: int = None,
        audio_signal: np.ndarray = None,
        sample_rate: int = None,
    ):
        """
        Initialize the Audio class with a specific audio file path.
        This class supports audio formats supported by soundfile, like WAV, FLAC, AIFF, OGG, etc.

        Args:
            filepath (str | None): Path to the audio file.
            convert_to_sample_rate (int | None): Desired sampling rate of the audio signal in Hz to which the audio will be converted.
        """
        self.audio_signal = audio_signal
        self.sample_rate = sample_rate
        if audio_signal is None and sample_rate is None:
            self.convert_to_sample_rate = convert_to_sample_rate
            self.load_audio_file(filepath)
            self.filepath = filepath

    @classmethod
    def create_from_signal(cls, audio_signal: np.ndarray, sample_rate: int) -> "Audio":
        """
        Create an Audio object from an audio signal and sample rate.

        Args:
            audio_signal (np.ndarray): The audio signal data as a numpy array.
            sample_rate (int): The sample rate in Hz.

        Returns:
            Audio: The audio object with the provided audio signal and sample rate.
        """
        return cls(audio_signal=audio_signal, sample_rate=sample_rate)

    def __str__(self):
        shape = self.audio_signal.shape
        return f"Audio(filepath={self.filepath}, sample_rate={self.sample_rate}, shape={shape}, channels={1 if len(shape) == 1 else shape[1]}, duration={self.get_duration()}s, audio_signal={self.audio_signal})"

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

        # If desired sample rate is provided, convert audio to new sample rate
        if (
            self.convert_to_sample_rate is not None
            and self.sample_rate != self.convert_to_sample_rate
        ):
            self.audio_signal = self.resample_audio(
                self.audio_signal, self.sample_rate, self.convert_to_sample_rate
            )
            self.sample_rate = self.convert_to_sample_rate

        return self.sample_rate, self.audio_signal

    def resample_audio(
        self, audio_signal: np.ndarray, original_rate: int, target_rate: int
    ) -> np.ndarray:
        """
        Resamples the audio signal to the desired sampling rate.

        Args:
            audio_signal (np.ndarray): The audio signal to be resampled.
            original_rate (int): The original sample rate of the audio signal.
            target_rate (int): The desired sample rate of the audio signal.

        Returns:
            np.ndarray: The resampled audio signal.
        """
        if original_rate == target_rate:
            return audio_signal
        return librosa.resample(
            audio_signal, orig_sr=original_rate, target_sr=target_rate
        )

    def convert_to_desired_sample_rate(
        self, desired_sample_rate: int
    ) -> tuple[int, np.ndarray]:
        """
        Converts the audio to the desired sample rate.

        Args:
            desired_sample_rate (int): The desired sample rate of the converted audio signal.

        Returns:
            tuple[int, np.ndarray]: The converted sample rate (Hz) and audio signal (numpy array).
        """
        if self.sample_rate != desired_sample_rate:
            self.audio_signal = self.resample_audio(
                self.audio_signal, self.sample_rate, desired_sample_rate
            )
            self.sample_rate = desired_sample_rate
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

    def play(self) -> None:
        """
        Play the audio file using sounddevice.

        Raises:
            ValueError: If the audio signal has not been loaded yet.
        """
        if self.audio_signal is None:
            self.load_audio_file()

        sd.play(self.audio_signal, self.sample_rate)
        sd.wait()
