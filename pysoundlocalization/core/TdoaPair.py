from pysoundlocalization.core.Microphone import Microphone


class TdoaPair:
    def __init__(self, mic1: Microphone, mic2: Microphone, tdoa: float) -> None:
        """
        Create a new TdoaPair instance.

        Args:
            mic1 (Microphone): The first microphone in the pair.
            mic2 (Microphone): The second microphone in the pair.
            tdoa (float): The time difference of arrival between the two microphones.
        """
        self.__mic1 = mic1
        self.__mic2 = mic2
        self.__tdoa = tdoa

    def __str__(self):
        """
        Return a string representation of the TdoaPair instance.

        Returns:
            str: A string representation of the TdoaPair instance.
        """
        return f"(TdoaPair: mic1={self.__mic1.get_name()}, mic2={self.__mic2.get_name()}, tdoa={self.__tdoa:.6f})"

    def __repr__(self):
        """
        Return a string representation of the TdoaPair instance.

        Returns:
            str: A string representation of the TdoaPair instance.
        """
        return str(self)

    def get_mic1(self) -> Microphone:
        """
        Return:
            Microphone: The first microphone in the pair.
        """
        return self.__mic1

    def set_mic1(self, mic1: Microphone) -> None:
        """
        Set the first microphone in the pair.

        Args:
            mic1 (Microphone): The first microphone in the pair.
        """
        self.__mic1 = mic1

    def get_mic2(self) -> Microphone:
        """
        Return:
            Microphone: The second microphone in the pair.
        """
        return self.__mic2

    def set_mic2(self, mic2: Microphone) -> None:
        """
        Set the second microphone in the pair.

        Args:
            mic2 (Microphone): The second microphone in the pair.
        """
        self.__mic2 = mic2

    def get_tdoa(self) -> float:
        """
        Return:
            float: The time difference of arrival between the two microphones.
        """
        return self.__tdoa

    def set_tdoa(self, tdoa: float) -> None:
        """
        Set the time difference of arrival between the two microphones.

        Args:
            tdoa (float): The time difference of arrival between the two microphones.
        """
        self.__tdoa = tdoa
