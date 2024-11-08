import numpy as np
from core.Audio import Audio
import noisereduce as nr


class NoiseReducer:

    @staticmethod
    def reduce_noise(audio: Audio, noise_sample: np.ndarray = None) -> Audio:
        """
        Reduces the noise from the audio signal using the noise sample.

        Args:
            audio (Audio): The audio object containing the audio signal to reduce the noise from.
            noise_sample (np.ndarray): The noise sample to reduce from the audio signal.

        Returns:
            Audio: The audio object with the noise reduced audio signal.
        """
        audio_sound = audio.get_audio_signal()
        sr = audio.get_sample_rate()

        noise_sample = None
        if noise_sample is None:
            noise_sample = audio_sound[0 : int(sr * 1)]

        audio_sound = nr.reduce_noise(y=audio_sound, sr=sr, y_noise=noise_sample)
        audio.set_audio_signal(audio_sound)
        return audio
