from pysoundlocalization.preprocessing.IFrequencyFilter import IFrequencyFilter
from pysoundlocalization.core.Audio import Audio
from scipy.signal import butter, lfilter


class HighPassFilter(IFrequencyFilter):
    """
    A High Pass Filter class for processing audio signals by attenuating frequencies below a specified cutoff.

    Args:
        cutoff_frequency (float): The cutoff frequency for the high-pass filter in Hz.
        order (int): The order of the cutoff frequency (default is 5).
    """

    def __init__(self, cutoff_frequency: float, order: int = 5):
        self.__cutoff_frequency = cutoff_frequency
        self.__order = order

    def apply(self, audio: Audio):
        """
        Apply the high-pass filter to the given audio signal.

        Args:
            audio (Audio): The audio object to apply the filter to. The filter modifies the audio in-place.
        """
        print(
            f"Applying HighPassFilter with cutoff frequency {self.__cutoff_frequency} Hz and order {self.__order}"
        )

        """
        Nyquist Sampling Theorem: sample_rate >= 2 * max_frequency
        nyquist = 0.5 * sample_rate
        """
        nyquist = 0.5 * audio.get_sample_rate()
        normalized_cutoff = self.__cutoff_frequency / nyquist

        # Create the Butterworth filter
        b, a = butter(self.__order, normalized_cutoff, btype="high", analog=False)

        # Apply the filter to the audio signal
        audio.set_audio_signal(lfilter(b, a, audio.get_audio_signal(index=0)))

    def get_cutoff_frequency(self) -> float:
        """
        Get the cutoff frequency of the high-pass filter.

        Returns:
            float: The cutoff frequency of the high-pass filter in Hz.
        """
        return self.__cutoff_frequency

    def set_cutoff_frequency(self, cutoff_frequency: float) -> None:
        """
        Set the cutoff frequency of the high-pass filter.

        Args:
            cutoff_frequency (float): The cutoff frequency of the high-pass filter in Hz.
        """
        self.__cutoff_frequency = cutoff_frequency

    def get_order(self) -> int:
        """
        Get the order of the high-pass filter.

        Returns:
            int: The order of the high-pass filter.
        """
        return self.__order

    def set_order(self, order: int) -> None:
        """
        Set the order of the high-pass filter.

        Args:
            order (int): The order of the high-pass filter.
        """
        self.__order = order
