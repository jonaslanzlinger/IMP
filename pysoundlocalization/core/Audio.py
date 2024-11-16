import librosa
import numpy as np
import os
import soundfile as sf
import sounddevice as sd


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
        self.__filepath = filepath
        self.__convert_to_sample_rate = convert_to_sample_rate
        self.__audio_signal = [audio_signal]
        self.__sample_rate = sample_rate
        if audio_signal is not None and sample_rate is not None:
            self.__duration = len(audio_signal) / sample_rate
        elif audio_signal is None and sample_rate is None:
            self.__duration = None
            self.load_audio_file(filepath)

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
        chunks = len(self.__audio_signal)
        return f"Audio(filepath={self.__filepath}, sample_rate={self.__sample_rate}, chunks={chunks}, duration={self.__duration}s, audio_signal={self.__audio_signal})"

    def load_audio_file(self, filepath: str = None) -> tuple[int, list[np.ndarray]]:
        """
        Manually load the audio file from the filepath. May be used to re-load the file from the filepath.

        Returns:
            tuple[int, np.ndarray]: A tuple containing the sample rate (Hz) and audio signal (numpy array).

        Raises:
            FileNotFoundError: If no valid file path is provided or the file does not exist.
        """
        if filepath is None:
            filepath = self.__filepath

        if not filepath or not os.path.exists(filepath):
            raise FileNotFoundError(
                f"No valid audio file provided or file not found: {filepath}"
            )

        # Load the audio file using soundfile
        audio_signal, self.__sample_rate = sf.read(filepath)
        self.__audio_signal = [audio_signal]

        # If desired sample rate is provided, convert audio to new sample rate
        if (
            self.__convert_to_sample_rate is not None
            and self.__sample_rate != self.__convert_to_sample_rate
        ):
            self.__audio_signal = self.resample_audio()
            self.__sample_rate = self.__convert_to_sample_rate

        return self.__sample_rate, self.__audio_signal

    def resample_audio(self, target_rate: int | None = None) -> list[np.ndarray]:
        """
        Resamples the audio signal to the desired sampling rate.

        Args:
            target_rate (int): The desired sampling rate of the resampled audio signal
        """

        if target_rate is None:
            target_rate = self.__convert_to_sample_rate

        if self.__sample_rate == target_rate:
            return self.__audio_signal

        self.__audio_signal = [
            librosa.resample(signal, orig_sr=self.__sample_rate, target_sr=target_rate)
            for signal in self.__audio_signal
        ]

        self.__sample_rate = self.__convert_to_sample_rate

        return self.__audio_signal

    def convert_to_sample_rate(
        self, target_sample_rate: int
    ) -> tuple[int, list[np.ndarray]]:
        """
        Converts the audio to the desired sample rate.

        Args:
            target_sample_rate (int): The desired sample rate of the converted audio signal.

        Returns:
            tuple[int, np.ndarray]: The converted sample rate (Hz) and audio signal (numpy array).
        """
        if self.__sample_rate != target_sample_rate:
            self.__audio_signal = self.resample_audio(target_sample_rate)
            self.__sample_rate = target_sample_rate
        return self.__sample_rate, self.__audio_signal

    def chunk_audio_signal(self, chunk_size: int | None = 1000) -> None:
        """
        Chunk the audio signal into chunks of a specific duration.

        Args:
            chunk_size (int): The duration of each audio chunk in milliseconds.
        """

        if len(self.__audio_signal) > 1:
            raise ValueError("Audio signal is already chunked. Cannot chunk it again.")

        chunk_in_samples = int(self.__sample_rate * chunk_size / 1000)
        chunks = []
        for i in range(0, len(self.__audio_signal[0]), chunk_in_samples):
            next_chunk = self.__audio_signal[0][i : i + chunk_in_samples]
            if len(next_chunk) == chunk_in_samples:
                chunks.append(next_chunk)
            else:
                chunks.append(
                    np.pad(next_chunk, (0, chunk_in_samples - len(next_chunk)))
                )

        self.__audio_signal = chunks

    def get_filepath(self) -> str:
        """
        Return the file path of the audio file.

        Returns:
            str: The file path of the audio file.
        """
        return self.__filepath

    def get_audio_signal_by_index(self, index: int | None = 0) -> np.ndarray:
        """
        Return the audio signal data of the audio file at a specific index.

        Args:
            index (int): The index of the audio signal in the list of audio signals.

        Returns:
            np.ndarray: The audio signal data as a numpy array.
        """
        if self.__audio_signal is None:
            self.load_audio_file()

        return self.__audio_signal[index]

    def get_audio_signal(self) -> list[np.ndarray]:
        """
        Return the list of audio signal data of the audio file.

        Returns:
            list[np.ndarray]: The list of audio signal data as numpy arrays.
        """
        if self.__audio_signal is None:
            self.load_audio_file()

        return self.__audio_signal

    def set_audio_signal(self, audio_signal: np.ndarray, index: int | None = 0) -> None:
        """
        Set the audio signal data of the audio file.

        Args:
            audio_signal (np.ndarray): The audio signal data as a numpy array.
            index (int): The index of the audio signal in the list of audio signals.
        """
        self.__audio_signal[index] = audio_signal

    def get_sample_rate(self) -> int:
        """
        Return the sample rate of the audio file.

        Returns:
            int: The sample rate in Hz.

        Raises:
            ValueError: If the sample rate has not been set or loaded.
        """
        if self.__sample_rate is None:
            self.load_audio_file()
        return self.__sample_rate

    def get_duration(self) -> float:
        """
        Return the duration of the audio file in seconds.

        Returns:
            float: Duration of the audio file in seconds.

        Raises:
            ValueError: If the audio signal has not been loaded yet.
        """
        if self.__audio_signal is None:
            self.load_audio_file()

        self.__duration = 0

        for i in range(len(self.__audio_signal)):
            self.__duration = (
                self.__duration + len(self.__audio_signal[i]) / self.__sample_rate
            )

        return self.__duration

    def play(self) -> None:
        """
        Play the audio file using sounddevice.

        Raises:
            ValueError: If the audio signal has not been loaded yet.
        """
        if self.__audio_signal is None:
            self.load_audio_file()

        for chunk in self.__audio_signal:
            sd.play(chunk, self.__sample_rate)
            sd.wait()
