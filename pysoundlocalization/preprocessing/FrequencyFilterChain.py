from preprocessing.IFrequencyFilter import IFrequencyFilter
from core.Audio import Audio
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np


class FrequencyFilterChain(IFrequencyFilter):
    def __init__(self):
        self.filters = []

    def apply(self, audio: Audio) -> Audio:
        for filter in self.filters:
            filter.apply(audio)

    def add_filter(self, filter: IFrequencyFilter):
        self.filters.append(filter)

    def remove_filter(self, filter: IFrequencyFilter):
        self.filters.remove(filter)
