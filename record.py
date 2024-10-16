import sounddevice as sd
from scipy.io.wavfile import write

# Parameters
sample_rate = 44100  # Sample rate in Hz (CD quality)
duration = 60  # Duration of the recording in seconds
filename = "output.wav"  # File name for the output


def record_audio():
    print("Recording...")
    # Record audio
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()  # Wait until the recording is finished
    print("Recording complete. Saving file...")

    # Save as WAV file
    write(filename, sample_rate, recording)
    print(f"File saved as {filename}")


# Run the function to start recording
if __name__ == "__main__":
    record_audio()