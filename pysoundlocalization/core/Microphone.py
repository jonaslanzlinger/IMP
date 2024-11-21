from pysoundlocalization.core.Audio import Audio
from datetime import datetime


class Microphone:

    def __init__(self, x: float, y: float, name: str = None):
        """
        Initialize the Microphone with a specified (x, y) position.

        Args:
            x (float): X-coordinate of the microphone position.
            y (float): Y-coordinate of the microphone position.
            name (str, optional): Name of the microphone. Defaults to "(x, y)" if not provided.
        """
        self.__x: float = x
        self.__y: float = y
        self.__name: str = name if name is not None else f"({x}, {y})"
        self.__recording_start_time: datetime | None = None
        self.__audio: Audio | None = None

    def get_name(self) -> str:
        """
        Get the name of the microphone.

        Returns:
            str: The name of the microphone.
        """
        return self.__name

    def set_name(self, name: str):
        """
        Set the name of the microphone.

        Args:
            name (str): The new name of the microphone.
        """
        self.__name = name

    def get_x(self) -> float:
        """
        Get the x-coordinate of the microphone.

        Returns:
            float: The x-coordinate of the microphone.
        """
        return self.__x

    def set_x(self, x: float):
        """
        Set the x-coordinate of the microphone.

        Args:
            x (float): The new x-coordinate of the microphone.
        """
        self.__x = x

    def get_y(self) -> float:
        """
        Get the y-coordinate of the microphone.

        Returns:
            float: The y-coordinate of the microphone.
        """
        return self.__y

    def set_y(self, y: float):
        """
        Set the y-coordinate of the microphone.

        Args:
            y (float): The new y-coordinate of the microphone.
        """
        self.__y = y

    def get_position(self) -> tuple[float, float]:
        """
        Get the (x, y) position of the microphone.

        Returns:
            tuple[float, float]: A tuple representing the microphone's position.
        """
        return self.__x, self.__y

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
        return self.__audio

    def set_audio(self, audio: Audio):
        """
        Set the audio associated with this microphone.

        Args:
            audio (Audio): The Audio object to associate with this microphone.
        """
        self.__audio = audio
