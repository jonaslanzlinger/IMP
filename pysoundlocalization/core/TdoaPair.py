from pysoundlocalization.core.Microphone import Microphone


class TdoaPair:
    def __init__(self, mic1: Microphone, mic2: Microphone, tdoa: float) -> None:
        self.__mic1 = mic1
        self.__mic2 = mic2
        self.__tdoa = tdoa

    def __str__(self):
        return f"(TdoaPair: mic1={self.__mic1.get_name()}, mic2={self.__mic2.get_name()}, tdoa={self.__tdoa:.6f})"

    def __repr__(self):
        return str(self)

    def get_mic1(self) -> Microphone:
        return self.__mic1

    def get_mic2(self) -> Microphone:
        return self.__mic2

    def get_tdoa(self) -> float:
        return self.__tdoa
