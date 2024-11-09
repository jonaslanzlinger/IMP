from pysoundlocalization.preprocessing.IFrequencyFilter import IFrequencyFilter
from pysoundlocalization.core.Audio import Audio


class FrequencyFilterChain(IFrequencyFilter):
    def __init__(self) -> None:
        """
        Initialize an empty chain of frequency filters.
        """
        self.filters: list[IFrequencyFilter] = []

    def apply(self, audio: Audio) -> None:
        """
        Apply each filter in the chain to the given audio object.

        Args:
            audio (Audio): The audio object to process with each filter.
        """
        for filter in self.filters:
            filter.apply(audio)

    def add_filter(self, filter: IFrequencyFilter) -> None:
        """
        Add a filter to the chain.

        Args:
            filter (IFrequencyFilter): The filter to add to the chain.
        """
        self.filters.append(filter)

    def remove_filter(self, filter: IFrequencyFilter) -> None:
        """
        Remove a filter from the chain.

        Args:
            filter (IFrequencyFilter): The filter to remove from the chain.

        Raises:
            ValueError: If the filter is not in the chain.
        """
        self.filters.remove(filter)
