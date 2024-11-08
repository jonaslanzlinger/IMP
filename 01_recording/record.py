import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime

# Parameters
SAMPLE_RATE = 44100  # Sample rate in Hz


def list_microphones():
    print("Available audio devices:")
    print(sd.query_devices())


def record_audio(mic_id=None, device_id=None, duration=10):
    timestamp = datetime.now()
    print(f"Recording started at: {timestamp}")

    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        device=device_id,
    )
    sd.wait()
    print("Recording complete. Saving file...")

    filename = f"output_{timestamp.strftime(f'{mic_id}_%Y-%m-%d_%H-%M-%S_%f')}.wav"

    write(filename, SAMPLE_RATE, recording)
    print(f"File saved as {filename}")


if __name__ == "__main__":
    mic_id = str(input("Enter a microphone ID to identify it later: "))

    # Manually define device for recording and duration
    list_microphones()
    device_id = int(input("Enter the device ID to use for recording: "))
    duration = int(input("Enter for how long you want to record: "))

    record_audio(mic_id=mic_id, device_id=device_id, duration=duration)
