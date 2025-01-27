import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime

"""
This script records audio from a specified microphone for a specified duration.
The audio is saved as a .wav file with a timestamp in the filename.
"""

SAMPLE_RATE = 44100


def list_microphones():
    print("Available audio devices:")
    print(sd.query_devices())


def record_audio(mic_id=None, device_id=None, duration=10):

    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        device=device_id,
        blocksize=8,
    )

    start_timestamp = datetime.now()
    sd.wait()
    end_timestamp = datetime.now()

    filename = f"pi{mic_id}_audio_{end_timestamp.strftime('%Y-%m-%d_%H-%M-%S_%f')}.wav"
    write(filename, SAMPLE_RATE, recording)
    print(f"File saved as {filename}")

    print(f"Time taken to record: {end_timestamp - start_timestamp}")


if __name__ == "__main__":
    mic_id = str(input("Enter a microphone ID to identify it later: "))

    # Manually define device for recording and duration
    list_microphones()
    device_id = int(input("Enter the device ID to use for recording: "))
    duration = int(input("Enter for how long you want to record: "))

    record_audio(mic_id=mic_id, device_id=device_id, duration=duration)
