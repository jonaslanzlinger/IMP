from pysoundlocalization.preprocessing.IFrequencyFilter import IFrequencyFilter
from pysoundlocalization.core.Audio import Audio
from scipy.signal import butter, lfilter


class LowCutFilter(IFrequencyFilter):
    """
    A Low Cut Filter class for processing audio signals by attenuating frequencies below a specified cutoff.

    Args:
        cutoff_frequency (float): The cutoff frequency for the low-cut filter in Hz.
        order (int): The order of the cutoff frequency (default is 5).
    """

    def __init__(self, cutoff_frequency: float, order: int = 5):
        self.cutoff_frequency = cutoff_frequency
        self.order = order

    def apply(self, audio: Audio):
        """
        Apply the low-cut filter to the given audio signal.

        Args:
            audio (Audio): The audio object to apply the filter to. The filter modifies the audio in-place.
        """
        print(
            f"Applying LowCutFilter with cutoff frequency {self.cutoff_frequency} Hz and order {self.order}"
        )

        """
        Nyquist Sampling Theorem: sample_rate >= 2 * max_frequency
        nyquist = 0.5 * sample_rate
        """
        nyquist = 0.5 * audio.get_sample_rate()
        normalized_cutoff = self.cutoff_frequency / nyquist

        # Create the Butterworth filter
        b, a = butter(self.order, normalized_cutoff, btype="high", analog=False)

        # Apply the filter to the audio signal
        audio.set_audio_signal(lfilter(b, a, audio.get_audio_signal()))
