from pysoundlocalization.core.Microphone import Microphone


class DoaPair:
    def __init__(self, mic1: Microphone, mic2: Microphone, doa: float) -> None:
        self.__mic1 = mic1
        self.__mic2 = mic2
        self.__doa = doa

    def __str__(self):
        return f"(DoaPair: mic1={self.__mic1.get_name()}, mic2={self.__mic2.get_name()}, doa={self.__doa:.2f})"

    def __repr__(self):
        return str(self)

    def get_mic1(self) -> Microphone:
        return self.__mic1

    def set_mic1(self, mic1: Microphone) -> None:
        self.__mic1 = mic1

    def get_mic2(self) -> Microphone:
        return self.__mic2

    def set_mic2(self, mic2: Microphone) -> None:
        self.__mic2 = mic2

    def get_doa(self) -> float:
        return self.__doa

    def set_doa(self, doa: float) -> None:
        self.__doa = doa
