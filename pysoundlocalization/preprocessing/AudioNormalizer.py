import pyloudnorm as pyln
from pysoundlocalization.core.Environment import Environment
from pysoundlocalization.core.Audio import Audio


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
            for i, chunk in enumerate(audio.get_audio_signal_chunked()):
                peak_normalized_audio = pyln.normalize.peak(chunk, target_peak)
                audio.set_audio_signal(audio_signal=peak_normalized_audio, index=i)

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
            for i, chunk in enumerate(audio.get_audio_signal_chunked()):
                meter = pyln.Meter(audio.get_sample_rate())
                loudness = meter.integrated_loudness(chunk)
                loudness_normalized_audio = pyln.normalize.loudness(
                    chunk, loudness, target_loudness
                )
                audio.set_audio_signal(audio_signal=loudness_normalized_audio, index=i)

        return environment

    @staticmethod
    def normalize_environment_to_max_amplitude(
        environment: Environment, max_amplitude: float
    ) -> Environment:
        """
        Normalize the audios of the environment so that the maximum amplitude of all microphones matches the given value.

        Args:
            environment: Environment object
            max_amplitude: Maximum desired amplitude (e.g., 0.9 for 90% of the full scale)

        Returns:
            Environment object with normalized audio
        """
        for mic in environment.get_mics():
            audio = mic.get_audio()
            AudioNormalizer.normalize_audio_to_max_amplitude(
                audio=audio, max_amplitude=max_amplitude
            )

        return environment

    @staticmethod
    def normalize_audio_to_max_amplitude(audio: Audio, max_amplitude: float) -> Audio:
        """
        Normalize the audio so that its maximum amplitude matches the given value.

        Args:
            audio: Audio object
            max_amplitude: Maximum desired amplitude (e.g., 0.9 for 90% of the full scale)

        Returns:
            Audio object with normalized audio
        """
        for i, chunk in enumerate(audio.get_audio_signal_chunked()):
            current_max = max(abs(chunk))

            if current_max == 0:
                scale_factor = 0
            else:
                scale_factor = max_amplitude / current_max

            normalized_audio = chunk * scale_factor

            audio.set_audio_signal(audio_signal=normalized_audio, index=i)

        return audio
