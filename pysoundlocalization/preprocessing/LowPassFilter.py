from preprocessing.IFrequencyFilter import IFrequencyFilter
from core.Audio import Audio
from scipy.signal import butter, lfilter


class LowPassFilter(IFrequencyFilter):
    """
    A class used to represent a Low Pass Filter.

    :param cutoff_frequency: The cutoff frequency for the low-pass filter.
    :param order: The order of the cutoff frequency (default is 5).
    """

    def __init__(self, cutoff_frequency, order=5):
        self.cutoff_frequency = cutoff_frequency
        self.order = order

    def apply(self, audio: Audio) -> Audio:
        print(
            f"Applying LowPassFilter with cutoff frequency {self.cutoff_frequency} Hz and order {self.order}"
        )

        """
        Nyquist Sampling Theorem: sample_rate >= 2 * max_frequency
        nyquist = 0.5 * sample_rate
        """
        nyquist = 0.5 * audio.sample_rate
        normalized_cutoff = self.cutoff_frequency / nyquist

        # Create the Butterworth filter
        b, a = butter(self.order, normalized_cutoff, btype="low", analog=False)

        # Apply the filter to the audio signal
        audio.audio_signal = lfilter(b, a, audio.audio_signal)
