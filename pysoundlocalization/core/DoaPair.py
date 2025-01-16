from pysoundlocalization.core.Microphone import Microphone


class DoaPair:
    def __init__(self, mic1: Microphone, mic2: Microphone, doa: float) -> None:
        """
        DoaPair class represents a pair of microphones and the direction of arrival (DOA) of the sound source.

        Args:
            mic1 (Microphone): The first microphone.
            mic2 (Microphone): The second microphone.
            doa (float): The direction of arrival (DOA) of the sound source.
        """
        self.__mic1 = mic1
        self.__mic2 = mic2
        self.__doa = doa

    def __str__(self):
        """
        Returns:
            str: A string representation of the DoaPair object.
        """
        return f"(DoaPair: mic1={self.__mic1.get_name()}, mic2={self.__mic2.get_name()}, doa={self.__doa:.2f})"

    def __repr__(self):
        """
        Returns:
            str: A string representation of the DoaPair object.
        """
        return str(self)

    def get_mic1(self) -> Microphone:
        """
        Returns:
            Microphone: The first microphone.
        """
        return self.__mic1

    def set_mic1(self, mic1: Microphone) -> None:
        """
        Args:
            mic1 (Microphone): The first microphone.
        """
        self.__mic1 = mic1

    def get_mic2(self) -> Microphone:
        """
        Returns:
            Microphone: The second microphone.
        """
        return self.__mic2

    def set_mic2(self, mic2: Microphone) -> None:
        """
        Args:
            mic2 (Microphone): The second microphone.
        """
        self.__mic2 = mic2

    def get_doa(self) -> float:
        """
        Returns:
            float: The direction of arrival (DOA) of the sound source.
        """
        return self.__doa

    def set_doa(self, doa: float) -> None:
        """
        Args:
            doa (float): The direction of arrival (DOA) of the sound source.
        """
        self.__doa = doa
