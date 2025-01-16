from pysoundlocalization.preprocessing.IFrequencyFilter import IFrequencyFilter
from pysoundlocalization.core.Audio import Audio
from scipy.signal import iirnotch, lfilter


class NotchFilter(IFrequencyFilter):
    """
    A Notch Filter class for attenuating a specific frequency in an audio signal.

    Args:
        target_frequency (float): The frequency to cancel out in Hz.
        quality_factor (float): The quality factor (Q), which controls the bandwidth of the notch filter.
    """

    def __init__(self, target_frequency: float, quality_factor: float = 30.0):
        self.__target_frequency = target_frequency
        self.__quality_factor = quality_factor

    def apply(self, audio: Audio):
        """
        Apply the notch filter to the given audio signal.

        Args:
            audio (Audio): The audio object to apply the filter to. The filter modifies the audio in-place.
        """
        print(
            f"Applying NotchFilter to remove {self.__target_frequency} Hz with quality factor {self.__quality_factor}"
        )

        # Get the sample rate and compute the normalized frequency
        sample_rate = audio.get_sample_rate()
        normalized_frequency = self.__target_frequency / (0.5 * sample_rate)

        # Create the notch filter coefficients
        b, a = iirnotch(normalized_frequency, self.__quality_factor)

        # Apply the filter to the audio signal
        audio.set_audio_signal(
            audio_signal=lfilter(b, a, audio.get_audio_signal(index=0))
        )

    def get_target_frequency(self) -> float:
        """
        Get the target frequency of the notch filter.

        Returns:
            float: The target frequency of the notch filter in Hz.
        """
        return self.__target_frequency

    def set_target_frequency(self, target_frequency: float) -> None:
        """
        Set the target frequency of the notch filter.

        Args:
            target_frequency (float): The target frequency of the notch filter in Hz.
        """
        self.__target_frequency = target_frequency

    def get_quality_factor(self) -> float:
        """
        Get the quality factor of the notch filter.

        Returns:
            float: The quality factor of the notch filter.
        """
        return self.__quality_factor

    def set_quality_factor(self, quality_factor: float) -> None:
        """
        Set the quality factor of the notch filter.

        Args:
            quality_factor (float): The quality factor of the notch filter.
        """
        self.__quality_factor = quality_factor
