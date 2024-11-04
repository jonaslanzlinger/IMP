from core.Room import Room
from core.Audio import Audio

class SampleRateConverter:
    """
    The SampleRateConverter takes a Room instance and applies sample rate conversions to its mic audio signals.
    """
    @staticmethod
    def get_lowest_sample_rate(room: Room) -> int:
        """
        Get the lowest sample rate from all audio files in the given room.

        Args:
            room: An instance of the Room class.

        Returns:
            int: The lowest sample rate found among the audio files in the room.
        """
        return min(mic.get_audio().get_sample_rate() for mic in room.mics if mic.get_audio() is not None)

    @staticmethod
    def convert_all_to_lowest_sample_rate(room: Room) -> None:
        """
        Convert all audio files in the given room to the lowest sample rate of any existing mic audio.

        Args:
            room: An instance of the Room class.
        """
        lowest_rate = SampleRateConverter.get_lowest_sample_rate(room)
        for mic in room.mics:
            mic.get_audio().convert_to_desired_sample_rate(lowest_rate)

    @staticmethod
    def convert_all_to_defined_sample_rate(room: Room, target_sample_rate: int) -> None:
        """
        Convert all audio files in the given room to a defined sample rate.

        Args:
            room: An instance of the Room class.
            target_sample_rate (int): The sample rate to convert to.
        """
        for mic in room.mics:
            mic.get_audio().convert_to_desired_sample_rate(target_sample_rate)

    @staticmethod
    def convert_all_to_sample_rate_of_audio_file(room: Room, audio_file: Audio) -> None:
        """
        Convert all audio files in the room to the sample rate of a specific audio file.

        Args:
            room: An instance of the Room class.
            audio_file: An audio file instance to get the sample rate from.
        """
        target_sample_rate = audio_file.get_sample_rate()
        SampleRateConverter.convert_all_to_defined_sample_rate(room, target_sample_rate)