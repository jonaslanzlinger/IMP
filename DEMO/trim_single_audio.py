from datetime import datetime, timedelta
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.SampleTrimmer import SampleTrimmer

# provide file path to the audio file
file_path = input("Enter the path to the audio file: ").strip()

# load audio file
audio = Audio(filepath=file_path)

# use SampleTrimmer to trim the audio file, here some examples:
# SampleTrimmer.trim_from_beginning(audio=audio, seconds=15)
# SampleTrimmer.trim_from_end(audio=audio, seconds=15)
# SampleTrimmer.slice_from_beginning(audio=audio, timedelta=timedelta(seconds=15, milliseconds=100))
# SampleTrimmer.slice_from_end(audio=audio, timedelta=timedelta(seconds=15, milliseconds=100))
# SampleTrimmer.slice_from_to(audio=audio, start_time=timedelta(seconds=15, milliseconds=100), end_time=timedelta(seconds=30, milliseconds=100))

# if you want to save the trimmed audio file, you can use the following code:
audio.export(output_filepath=file_path.replace(".wav", "_trimmed.wav"))
