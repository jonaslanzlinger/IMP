from datetime import timedelta, datetime

from core.Room import Room
from core.Audio import Audio

class SampleTrimmer:

    #TODO: not just seconds, but duration with H:MM:SS.sss
    @staticmethod
    def trim_from_beginning(audio: Audio, seconds: int):
        """
        Trim the specified number of seconds from the beginning of the audio signal.

        Args:
            audio (Audio): The audio object to be trimmed.
            seconds (int): The number of seconds to trim from the beginning.
        """
        # Calculate the number of samples to trim
        samples_to_trim = int(seconds * audio.sample_rate)

        # Trim the audio signal
        audio.audio_signal = audio.audio_signal[samples_to_trim:]

        return audio

    @staticmethod
    def trim_from_end(audio: Audio, seconds: int):
        """
        Trim the specified number of seconds from the end of the audio signal.

        Args:
            audio (Audio): The audio object to be trimmed.
            seconds (int): The number of seconds to trim from the end.
        """
        # Calculate the number of samples to trim
        samples_to_trim = int(seconds * audio.sample_rate)

        # Trim the audio signal
        audio.audio_signal = audio.audio_signal[:-samples_to_trim]

        return audio

    @staticmethod
    def slice_from_beginning(audio: Audio, seconds: int):
        """
        Keep only the first X seconds from the beginning of the audio signal.

        Args:
            audio (Audio): The audio object to be trimmed.
            seconds (int): The duration in seconds to keep from the beginning.
        """
        # Calculate the number of samples to keep
        samples_to_keep = int(seconds * audio.sample_rate)

        # Keep the specified portion of the audio signal
        audio.audio_signal = audio.audio_signal[:samples_to_keep]

        return audio

    @staticmethod
    def slice_from_end(audio: Audio, seconds: int):
        """
        Keep only the last X seconds of the end of the audio signal.

        Args:
            audio (Audio): The audio object to be trimmed.
            seconds (int): The number of seconds from the end of the audio to keep.
        """
        # Calculate the number of samples to keep
        samples_to_keep = int(seconds * audio.sample_rate)

        # Keep only the last X seconds of the audio signal
        audio.audio_signal = audio.audio_signal[-samples_to_keep:]

        return audio

    @staticmethod
    def slice_from_to(audio: Audio, start_seconds: int, end_seconds: int):
        """
        Slice the audio signal to keep only the part between the start and end timestamps.

        Args:
            audio (Audio): The audio object to be sliced.
            start_seconds (int): The start timestamp in seconds.
            end_seconds (int): The end timestamp in seconds.

        Returns:
            Audio: The sliced audio object containing the portion between start and end timestamps.
        """
        # Calculate the start and end sample indices
        start_sample = int(start_seconds * audio.sample_rate)
        end_sample = int(end_seconds * audio.sample_rate)

        # Slice the audio signal between start and end samples
        audio.audio_signal = audio.audio_signal[start_sample:end_sample]

        return audio

    @staticmethod
    def sync_audio(audio_files: list[Audio], start_times: list[datetime]):
        """
        Synchronize the audio files to start and end at the same timestamp. Concretely, it slices all audio to start
        at the latest start timestamp (effectively synchronizing the audio, but possibly losing the beginning of
        some audio) and trims the end of the recordings, if necessary, to make the audio files to have equal length.

        Consider multiple audio files of any length. To ensure accurate computation of time delays (ie. to perform sound localization),
        it must be ensured that all audio files are in sync. If for example one audio recording was started late, the computation
        of time delays will be faulty.

        Note that audio files having the same length does not necessarily mean that they're in sync. One audio recording
        could have been started early/late, which makes accurate time delay computations impossible.

        If timestamps of when recordings started are available, the method slices all audio files to the latest start timestamp
        (syncing the actual start of recordings) and trims the end to make them of equal length.

        Args:
            audio_files (list): List of Audio objects to be synchronized.
            start_times (list): Corresponding start times (timestamps) for each audio file.

        Returns:
            list: List of synchronized Audio objects.
        """
        if len(audio_files) != len(start_times):
            raise ValueError("The number of audio files and start times must match.")

        # Find the latest start timestamp and the earliest end timestamp
        latest_start = max(start_times)
        earliest_end = min(
            start_time + timedelta(milliseconds=audio.get_duration() * 1000)
            for start_time, audio in zip(start_times, audio_files)
        )

        # Calculate the synchronization window duration
        sync_duration_s = int((earliest_end - latest_start).total_seconds())

        for audio, start_time in zip(audio_files, start_times):
            # Calculate the offset for trimming
            offset_s = int((latest_start - start_time).total_seconds())

            # Trim or pad the audio file accordingly
            # TODO: currently bugged because .slice_from_to can only consider full seconds
            SampleTrimmer.slice_from_to(audio, offset_s, offset_s + sync_duration_s)