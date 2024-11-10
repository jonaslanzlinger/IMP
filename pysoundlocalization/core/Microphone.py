from pysoundlocalization.core.Audio import Audio
from datetime import datetime


class Microphone:

    def __init__(self, x: float, y: float, name: str = "NoName"):
        """
        Initialize the Microphone with a specified (x, y) position.

        Args:
            x (float): X-coordinate of the microphone position.
            y (float): Y-coordinate of the microphone position.
        """
        self.name = name
        self.x = x
        self.y = y
        self.__recording_start_time: datetime | None = None

        self.audio: Audio | None = None

    def get_name(self) -> str:
        """
        Get the name of the microphone.

        Returns:
            str: The name of the microphone.
        """
        return self.name

    def set_name(self, name: str):
        """
        Set the name of the microphone.

        Args:
            name (str): The new name of the microphone.
        """
        self.name = name

    def get_position(self) -> tuple[float, float]:
        """
        Get the (x, y) position of the microphone.

        Returns:
            tuple[float, float]: A tuple representing the microphone's position.
        """
        return self.x, self.y

    def add_audio(self, audio: Audio):
        """
        Store the audio in the microphone.

        Args:
            audio (Audio): The reference to the Audio object.
        """
        self.audio = audio

    def get_audio(self) -> Audio | None:
        """
        Return the audio associated with this microphone.

        Returns:
            Audio | None: The Audio object currently referenced by this microphone,
                          containing the audio signal data and any relevant processing applied
                          to the signal. If no audio is associated, returns None.

        Note:
            The returned object is a reference to the original Audio instance.
            Any modifications made to this Audio object will affect the data
            stored in all other references to the same audio.
        """
        return self.audio

    def get_recording_start_time(self) -> datetime | None:
        """
        Get the start time of the recording.

        Returns:
            datetime | None: The start time of the recording.
        """
        return self.__recording_start_time

    def set_recording_start_time(self, start_time: datetime):
        """
        Set the start time of the recording.

        Args:
            start_time (datetime): The start time of the recording.
        """
        self.__recording_start_time = start_time
