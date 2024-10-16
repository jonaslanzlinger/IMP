import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime

# Parameters
sample_rate = 44100  # Sample rate in Hz (CD quality)
duration = 10  # Duration of the recording in seconds

def list_microphones():
    """List all available microphones and their corresponding device IDs."""
    print("Available audio devices:")
    print(sd.query_devices())


def record_audio(device_id=None):
    timestamp = datetime.now()

    # Print timestamp of recording
    print("Recording...")
    print(timestamp)

    # Record audio
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, device=device_id)
    sd.wait()  # Wait until the recording is finished
    print("Recording complete. Saving file...")

    # Save as WAV file
    filename = f"output_{timestamp.strftime("%Y-%m-%d_%H:%M:%S.%f")}.wav"  # Filename with timestamp

    write(filename, sample_rate, recording)
    print(f"File saved as {filename}")


# Run the function to start recording
if __name__ == "__main__":
    list_microphones()  # List all devices first

    # Example: Manually set the device ID (replace with the desired device ID from the list)
    # You can look at the output of list_microphones() to pick the correct device
    device_id = int(input("Enter the device ID to use for recording: "))

    record_audio(device_id=device_id)
