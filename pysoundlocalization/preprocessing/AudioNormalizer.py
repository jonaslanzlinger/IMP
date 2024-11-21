import soundfile as sf
import pyloudnorm as pyln
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Environment import Environment


class AudioNormalizer:

    @staticmethod
    def peak_normalize(environment: Environment, target_peak: float) -> Environment:
        """
        Normalize the audio to the target peak level.

        Args:
            environment: Environment object
            target_peak: Target peak level in dB

        Returns:
            Environment object with normalized audio
        """
        for mic in environment.get_mics():
            audio = mic.get_audio()
            for i, chunk in enumerate(audio.get_audio_signal()):
                peak_normalized_audio = pyln.normalize.peak(chunk, target_peak)
                audio.set_audio_signal(peak_normalized_audio, i)

        return environment

    @staticmethod
    def loudness_normalize(
        environment: Environment, target_loudness: float
    ) -> Environment:
        """
        Normalize the audio to the target loudness level.

        Args:
            environment: Environment object
            target_loudness: Target loudness level in dB

        Returns:
            Environment object with normalized audio
        """
        for mic in environment.get_mics():
            audio = mic.get_audio()
            for i, chunk in enumerate(audio.get_audio_signal()):
                meter = pyln.Meter(audio.get_sample_rate())
                loudness = meter.integrated_loudness(chunk)
                loudness_normalized_audio = pyln.normalize.loudness(
                    chunk, loudness, target_loudness
                )
                audio.set_audio_signal(loudness_normalized_audio, i)

        return environment