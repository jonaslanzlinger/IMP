from datetime import datetime, timedelta
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer
from pysoundlocalization.visualization.audio_wave_plot import audio_wave_plot

filepath1 = "../08_versuch_classroom_syncatmic3_3sources/pi1_audio.wav"
filepath2 = "../08_versuch_classroom_syncatmic3_3sources/pi2_audio.wav"
filepath3 = "../08_versuch_classroom_syncatmic3_3sources/pi3_audio.wav"
filepath4 = "../08_versuch_classroom_syncatmic3_3sources/pi4_audio.wav"

for filepath in [filepath1, filepath2, filepath3, filepath4]:
    audio = Audio(filepath=filepath)
    audio_wave_plot(
        audio.get_audio_signal_unchunked(),
        audio.get_sample_rate(),
    )
    for i, sample in enumerate(audio.get_audio_signal_unchunked()):
        if sample > 0.8:
            print(i)
            SampleTrimmer.slice_from_to_samples(
                audio, i - 20000, audio.get_num_samples() - 1
            )
            audio_wave_plot(
                audio.get_audio_signal_unchunked(),
                audio.get_sample_rate(),
            )
            if audio.get_filepath() == filepath1:
                audio.export(
                    "example_audio/"
                    + "trimmed_2024-11-28_15-00-00-037437_pi1_audio.wav"
                )
            elif audio.get_filepath() == filepath2:
                audio.export(
                    "example_audio/"
                    + "trimmed_2024-11-28_15-00-00-029037_pi2_audio.wav"
                )
            elif audio.get_filepath() == filepath3:
                audio.export(
                    "example_audio/"
                    + "trimmed_2024-11-28_15-00-00-000000_pi3_audio.wav"
                )
            elif audio.get_filepath() == filepath4:
                audio.export(
                    "example_audio/"
                    + "trimmed_2024-11-28_15-00-00-022696_pi4_audio.wav"
                )
            break
    # for i, sample in enumerate(audio.get_audio_signal_unchunked()):
    #     if sample > 0.8:
    #         print(i)
    #         if audio.get_filepath() == "../08_versuch_classroom_syncatmic3_3sources/pi1_audio.wav":
    #             SampleTrimmer.slice_from_to_samples(audio, i - (20000 + 1651), )
    #         elif audio.get_filepath() == "../08_versuch_classroom_syncatmic3_3sources/pi2_audio.wav":
    #             SampleTrimmer.slice_from_to_samples(audio, i - (20000 + 1281), )
    #         elif audio.get_filepath() == "../08_versuch_classroom_syncatmic3_3sources/pi3_audio.wav":
    #             SampleTrimmer.slice_from_to_samples(audio, i - (20000 + 0), )
    #         elif audio.get_filepath() == "../08_versuch_classroom_syncatmic3_3sources/pi4_audio.wav":
    #             SampleTrimmer.slice_from_to_samples(audio, i - (20000 + 1001), )

    #         audio_wave_plot(
    #             audio.get_audio_signal_unchunked(),
    #             audio.get_sample_rate(),
    #         )
    #         print(audio.get_audio_signal_unchunked().shape)
    #         break

# audio1_offset = 20000 + 1651
# audio2_offset = 20000 + 1281
# audio3_offset = 20000 + 0
# audio4_offset = 20000 + 1001

SampleTrimmer.slice_from_beginning(audio, timedelta(seconds=15, milliseconds=100))
SampleTrimmer.slice_from_end(audio, timedelta(seconds=14, milliseconds=600))
SampleTrimmer.trim_from_beginning(audio, timedelta(milliseconds=1500))
SampleTrimmer.trim_from_end(audio, timedelta(seconds=2))
SampleTrimmer.slice_from_to(
    audio, timedelta(seconds=5, milliseconds=100), timedelta(seconds=10)
)


# Sync the audio based on known timestamps of when the respective recordings started
# Very useful as it is necessary to have perfectly synced audio to effectively compute time delays
audio1 = Audio(filepath="example_audio/pi1_audio.wav")
audio2 = Audio(filepath="example_audio/pi2_audio.wav")

audio1_timestamp = datetime(2024, 11, 8, 12, 0, 15, 0)
audio2_timestamp = datetime(2024, 11, 8, 12, 0, 17, 0)
audio_timestamps = [audio1_timestamp, audio2_timestamp]

audio_files = [audio1, audio2]

print(audio1.get_audio_signal_unchunked().shape)
print(audio2.get_audio_signal_unchunked().shape)
# TODO: currently, sync_audio has a rounding error (likely from duration) that makes it such that audio2 has just 1 sample more than audio1
SampleTrimmer.sync_audio(audio_files, audio_timestamps)

print(audio1.get_audio_signal_unchunked().shape)
print(audio2.get_audio_signal_unchunked().shape)
