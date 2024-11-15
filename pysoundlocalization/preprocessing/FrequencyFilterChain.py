from pysoundlocalization.preprocessing.IFrequencyFilter import IFrequencyFilter
from pysoundlocalization.core.Audio import Audio


class FrequencyFilterChain(IFrequencyFilter):
    def __init__(self) -> None:
        """
        Initialize an empty chain of frequency filters.
        """
        self.__filters: list[IFrequencyFilter] = []

    def apply(self, audio: Audio) -> None:
        """
        Apply each filter in the chain to the given audio object.

        Args:
            audio (Audio): The audio object to process with each filter.
        """
        if len(audio.get_audio_signal()) > 1:
            raise ValueError("Audio signal can not be chunked during pre-processing.")

        for filter in self.__filters:
            filter.apply(audio)

    def add_filter(self, filter: IFrequencyFilter) -> None:
        """
        Add a filter to the chain.

        Args:
            filter (IFrequencyFilter): The filter to add to the chain.
        """
        self.__filters.append(filter)

    def remove_filter(self, filter: IFrequencyFilter) -> None:
        """
        Remove a filter from the chain.

        Args:
            filter (IFrequencyFilter): The filter to remove from the chain.

        Raises:
            ValueError: If the filter is not in the chain.
        """
        self.__filters.remove(filter)

    def get_filters(self) -> list[IFrequencyFilter]:
        """
        Get all filters in the chain.

        Returns:
            list[IFrequencyFilter]: A list of all filters in the chain.
        """
        return self.__filters
