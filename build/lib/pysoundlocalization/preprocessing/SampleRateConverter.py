from pysoundlocalization.core.Environment import Environment
from pysoundlocalization.core.Audio import Audio


class SampleRateConverter:
    """
    The SampleRateConverter takes an Environment instance and applies sample rate conversions to its mic audio signals.
    """

    @staticmethod
    def get_lowest_sample_rate(environment: Environment) -> int:
        """
        Get the lowest sample rate from all audio files in the given environment.

        Args:
            environment: An instance of the Environment class.

        Returns:
            int: The lowest sample rate found among the audio files in the environment.
        """
        return min(
            mic.get_audio().get_sample_rate()
            for mic in environment.get_mics()
            if mic.get_audio() is not None
        )

    @staticmethod
    def convert_all_to_lowest_sample_rate(environment: Environment) -> None:
        """
        Convert all audio files in the given environment to the lowest sample rate of any existing mic audio.

        Args:
            environment: An instance of the Environment class.
        """
        lowest_rate = SampleRateConverter.get_lowest_sample_rate(environment)
        for mic in environment.get_mics():
            mic.get_audio().convert_to_sample_rate(lowest_rate)

    @staticmethod
    def convert_all_to_defined_sample_rate(
        environment: Environment, target_sample_rate: int
    ) -> None:
        """
        Convert all audio files in the given environment to a defined sample rate.

        Args:
            environment: An instance of the Environment class.
            target_sample_rate (int): The sample rate to convert to.
        """
        for mic in environment.get_mics():
            mic.get_audio().convert_to_sample_rate(target_sample_rate)

    @staticmethod
    def convert_all_to_sample_rate_of_audio_file(
        environment: Environment, audio_file: Audio
    ) -> None:
        """
        Convert all audio files in the environment to the sample rate of a specific audio file.

        Args:
            environment: An instance of the Environment class.
            audio_file: An audio file instance to get the sample rate from.
        """
        target_sample_rate = audio_file.get_sample_rate()
        SampleRateConverter.convert_all_to_defined_sample_rate(
            environment, target_sample_rate
        )
