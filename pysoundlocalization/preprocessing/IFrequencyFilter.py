from abc import ABC, abstractmethod
from core.Audio import Audio


class IFrequencyFilter(ABC):

    @abstractmethod
    def apply(self, audio: Audio) -> Audio:
        pass
