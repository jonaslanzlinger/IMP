from datetime import timedelta, datetime
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.core.Environment import Environment


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
        samples_to_trim = int(seconds_to_trim * audio.get_sample_rate())

        # Trim the audio signal
        audio.set_audio_signal(audio.get_audio_signal(index=0)[samples_to_trim:])

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
        samples_to_trim = int(seconds_to_trim * audio.get_sample_rate())

        # Trim the audio signal
        audio.set_audio_signal(audio.get_audio_signal(index=0)[:-samples_to_trim])

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
        samples_to_keep = int(seconds_to_keep * audio.get_sample_rate())

        # Keep the specified portion of the audio signal
        audio.set_audio_signal(audio.get_audio_signal(index=0)[:samples_to_keep])

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
        samples_to_keep = int(seconds_to_keep * audio.get_sample_rate())

        # Keep only the specified duration from the end of the audio signal
        audio.set_audio_signal(audio.get_audio_signal(index=0)[-samples_to_keep:])

        return audio

    # TODO: we still sometimes have sample discrepancies of 1-2 samples after syncing from duration float conversion
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
        start_sample = int(round(start_seconds * audio.get_sample_rate()))
        end_sample = int(round(end_seconds * audio.get_sample_rate()))

        # Ensure the indices are within the bounds of the audio signal
        total_samples = audio.get_num_samples()
        start_sample = max(0, min(start_sample, total_samples))
        end_sample = max(0, min(end_sample, total_samples))

        # Slice the audio signal between start and end samples
        audio.set_audio_signal(
            audio.get_audio_signal_unchunked()[start_sample:end_sample]
        )

        return audio

    @staticmethod
    # TODO: currently not used!
    def slice_from_to_samples(audio: Audio, start_sample: int, end_sample: int):
        # Ensure the indices are within the bounds of the audio signal
        total_samples = audio.get_num_samples()
        start_sample = max(0, min(start_sample, total_samples))
        end_sample = max(0, min(end_sample, total_samples))

        # Slice the audio signal between start and end samples
        audio.set_audio_signal(
            audio.get_audio_signal_unchunked()[start_sample:end_sample]
        )

        return audio

    @staticmethod
    def slice_all_from_to(
        environment: Environment, start_time: timedelta, end_time: timedelta
    ):
        """
        Slice all audio signals in environment (associated with a mic) to keep only the part between the start and end timestamps.

        Args:
            environment (Environment): The environment to slice all audio signals from.
            start_time (timedelta): The start timestamp as a timedelta. Use format timedelta(days=5, seconds=5, milliseconds=5, ...)
            end_time (timedelta): The end timestamp as a timedelta. Use format timedelta(days=5, seconds=5, milliseconds=5, ...)

        Returns:
            Environment: The environment with all audio signals sliced.
        """
        list_audio = []
        for mic in environment.get_mics():
            SampleTrimmer.slice_from_to(mic.get_audio(), start_time, end_time)
            list_audio.append(mic.get_audio())
        SampleTrimmer.ensure_synced_audio(list_audio)
        return environment

    @staticmethod
    def sync_environment(environment: Environment) -> Environment | None:

        if len(environment.get_mics()) == 0:
            raise ValueError("Environment has no microphones.")

        for mic in environment.get_mics():
            if len(mic.get_audio().get_audio_signal_chunked()) > 1:
                raise ValueError(
                    "Audio signal is chunked. Can not sync environmnet on chunked audio."
                )

        list_audio = []
        list_start_times = []

        for mic in environment.get_mics():
            if mic.get_audio() is None:
                raise ValueError(f"MIC {mic.get_name()} has no audio signal.")
            if mic.get_recording_start_time() is None:
                raise ValueError(f"MIC {mic.get_name()} has no recording start time.")

            list_audio.append(mic.get_audio())
            list_start_times.append(mic.get_recording_start_time())

        SampleTrimmer.sync_audio(list_audio, list_start_times)

        return environment

    @staticmethod
    def sync_audio(list_audio: list[Audio], start_times: list[datetime]):
        """
        Synchronize the audio objects to start and end at the same timestamp. Concretely, it slices all audio to start
        at the latest start timestamp (effectively synchronizing the audio, but possibly losing the beginning of
        some audio) and trims the end of the recordings, if necessary, to make the audio objects to have equal length.

        Consider multiple audio objects of any length. To ensure accurate computation of time delays (ie. to perform sound localization),
        it must be ensured that all audio objects are in sync. If for example one audio recording was started late, the computation
        of time delays will be faulty.

        Note that audio objects having the same length does not necessarily mean that they're in sync. One audio recording
        could have been started early/late, which makes accurate time delay computations impossible.

        If timestamps of when recordings started are available, the method slices all audio objects to the latest start timestamp
        (syncing the actual start of recordings) and trims the end to make them of equal length.

        Args:
            list_audio (list): List of Audio objects to synchronize.
            start_times (list): Corresponding start times (timestamps) for each audio object.

        Returns:
            list: List of synchronized Audio objects.
        """
        if len(list_audio) != len(start_times):
            raise ValueError("The number of audio objects and start times must match.")

        # Find the latest start timestamp and the earliest end timestamp
        latest_start = max(start_times)
        earliest_end = min(
            start_time + timedelta(seconds=audio.get_duration())
            for start_time, audio in zip(start_times, list_audio)
        )

        # Calculate the synchronization duration as a timedelta
        sync_duration = earliest_end - latest_start

        for audio, start_time in zip(list_audio, start_times):
            # Calculate the offset for trimming as a timedelta
            offset = latest_start - start_time
            # Trim or pad the audio file accordingly using timedelta precision
            SampleTrimmer.slice_from_to(audio, offset, offset + sync_duration)

        SampleTrimmer.ensure_synced_audio(list_audio)

        return list_audio

    @staticmethod
    def ensure_synced_audio(list_audio: list[Audio]) -> list[Audio]:
        # If all audio has the same sample count, return list unchanged
        sample_counts = [audio.get_num_samples() for audio in list_audio]
        if all(sample_count == sample_counts[0] for sample_count in sample_counts):
            return list_audio

        # TODO: usually this is only 1-2 samples due to float precision, but what if it's more? how to handle?
        # Else, trim all audios to match the lowest sample count
        min_sample_count = min(sample_counts)
        for audio in list_audio:
            signal = audio.get_audio_signal_unchunked()
            trimmed_signal = signal[:min_sample_count]
            audio.set_audio_signal(trimmed_signal)

            # Print the number of samples trimmed
            trimmed_count = audio.get_num_samples() - min_sample_count
            print(f"Trimmed {trimmed_count} samples from audio to ensure sync: {audio}")

        return list_audio
