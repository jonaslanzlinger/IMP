from abc import ABC, abstractmethod
from core.Audio import Audio


class IFrequencyFilter(ABC):
    """
    Interface for frequency filter classes, providing a method to apply a filter to an Audio object.
    """
    @abstractmethod
    def apply(self, audio: Audio) -> Audio:
        """
        Apply the filter to the given Audio object.

        Args:
            audio (Audio): The audio object to apply the filter to.

        Returns:
            Audio: The processed audio object after applying the filter.
        """
        pass
