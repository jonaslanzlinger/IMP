from datetime import timedelta, datetime
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Room import Room


class SampleTrimmer:

    @staticmethod
    def trim_from_beginning(audio: Audio, time_delta: timedelta):
        """
        Trim the specified timedelta (duration) from the beginning of the audio signal.

        Args:
            audio (Audio): The audio object to be trimmed.
            time_delta (timedelta): The time duration to trim from the beginning. Use format timedelta(days=5, seconds=5, milliseconds=5, ...)
        """
        # Convert the timedelta to seconds (including microseconds and milliseconds)
        seconds_to_trim = time_delta.total_seconds()

        # Calculate the number of samples to trim
        samples_to_trim = int(seconds_to_trim * audio.sample_rate)

        # Trim the audio signal
        audio.audio_signal = audio.audio_signal[samples_to_trim:]

        return audio

    @staticmethod
    def trim_from_end(audio: Audio, time_delta: timedelta):
        """
        Trim the specified number of seconds from the end of the audio signal.

        Args:
            audio (Audio): The audio object to be trimmed.
            time_delta (int): The time duration to trim from the end. Use format timedelta(days=5, seconds=5, milliseconds=5, ...)
        """
        # Convert the timedelta to seconds (including milliseconds and microseconds)
        seconds_to_trim = time_delta.total_seconds()

        # Calculate the number of samples to trim
        samples_to_trim = int(seconds_to_trim * audio.sample_rate)

        # Trim the audio signal
        audio.audio_signal = audio.audio_signal[:-samples_to_trim]

        return audio

    @staticmethod
    def slice_from_beginning(audio: Audio, time_delta: timedelta):
        """
        Keep only the first specified time duration from the beginning of the audio signal.

        Args:
            audio (Audio): The audio object to be sliced.
            time_delta (timedelta): The duration to keep from the beginning. Use format timedelta(days=5, seconds=5, milliseconds=5, ...)
        """
        # Convert the timedelta to seconds (including milliseconds and microseconds)
        seconds_to_keep = time_delta.total_seconds()

        # Calculate the number of samples to keep
        samples_to_keep = int(seconds_to_keep * audio.sample_rate)

        # Keep the specified portion of the audio signal
        audio.audio_signal = audio.audio_signal[:samples_to_keep]

        return audio

    @staticmethod
    def slice_from_end(audio: Audio, time_delta: timedelta):
        """
        Keep only the specified time duration from the end of the audio signal.

        Args:
            audio (Audio): The audio object to be trimmed.
            time_delta (timedelta): The duration to keep from the end of the audio signal. Use format timedelta(days=5, seconds=5, milliseconds=5, ...)
        """
        # Convert the timedelta to seconds (including milliseconds and microseconds)
        seconds_to_keep = time_delta.total_seconds()

        # Calculate the number of samples to keep
        samples_to_keep = int(seconds_to_keep * audio.sample_rate)

        # Keep only the specified duration from the end of the audio signal
        audio.audio_signal = audio.audio_signal[-samples_to_keep:]

        return audio

    @staticmethod
    def slice_from_to(audio: Audio, start_time: timedelta, end_time: timedelta):
        """
        Slice the audio signal to keep only the part between the start and end timestamps.

        Args:
            audio (Audio): The audio object to be sliced.
            start_time (timedelta): The start timestamp as a timedelta. Use format timedelta(days=5, seconds=5, milliseconds=5, ...)
            end_time (timedelta): The end timestamp as a timedelta. Use format timedelta(days=5, seconds=5, milliseconds=5, ...)

        Returns:
            Audio: The sliced audio object containing the portion between start and end timestamps.
        """
        # Convert the timedeltas to seconds
        start_seconds = start_time.total_seconds()
        end_seconds = end_time.total_seconds()

        # Calculate the start and end sample indices
        start_sample = int(start_seconds * audio.sample_rate)
        end_sample = int(end_seconds * audio.sample_rate)

        # Slice the audio signal between start and end samples
        audio.audio_signal = audio.audio_signal[start_sample:end_sample]

        return audio

    @staticmethod
    def slice_all_from_to(room: Room, start_time: timedelta, end_time: timedelta):
        """
        Slice all audio signals in room (associated with a mic) to keep only the part between the start and end timestamps.

        Args:
            room (Room): The room to slice all audio signals from.
            start_time (timedelta): The start timestamp as a timedelta. Use format timedelta(days=5, seconds=5, milliseconds=5, ...)
            end_time (timedelta): The end timestamp as a timedelta. Use format timedelta(days=5, seconds=5, milliseconds=5, ...)

        Returns:
            Room: The room with all audio signals sliced.
        """
        for mic in room.mics:
            SampleTrimmer.slice_from_to(mic.get_audio(), start_time, end_time)
        return room

    @staticmethod
    def sync_room(room: Room) -> Room | None:

        if len(room.mics) == 0:
            raise ValueError("Room has no microphones.")

        list_audio = []
        list_start_times = []

        for mic in room.mics:

            if mic.get_audio() is None:
                raise ValueError(f"MIC {mic.get_name()} has no audio signal.")
            if mic.get_recording_start_time() is None:
                raise ValueError(f"MIC {mic.get_name()} has no recording start time.")

            list_audio.append(mic.get_audio())
            list_start_times.append(mic.get_recording_start_time())

        SampleTrimmer.sync_audio(list_audio, list_start_times)

        return room

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
            start_time + timedelta(seconds=audio.get_duration())
            for start_time, audio in zip(start_times, audio_files)
        )

        # Calculate the synchronization duration as a timedelta
        sync_duration = earliest_end - latest_start

        for audio, start_time in zip(audio_files, start_times):
            # Calculate the offset for trimming as a timedelta
            offset = latest_start - start_time

            # Trim or pad the audio file accordingly using timedelta precision
            SampleTrimmer.slice_from_to(audio, offset, offset + sync_duration)

        return audio_files
