import numpy as np
import scipy.io.wavfile as wav
import warnings
import matplotlib.pyplot as plt

# in meters
mic_positions = np.array(
    [
        {"x": -10, "y": -10, "z": 0},
        {"x": -10, "y": 10, "z": 0},
        {"x": 10, "y": 10, "z": 0},
        {"x": 10, "y": -10, "z": 0},
    ]
)

speed_of_sound = 343  # m/s


def load_audio_data(file):
    sample_rate, samples = wav.read(file)
    return sample_rate, samples


def find_loudest_point(audio_data, sample_rate):
    max_amplitude = np.max(np.abs(audio_data))
    max_index = np.argmax(np.abs(audio_data))
    max_time = max_index / sample_rate
    return max_amplitude, max_time


audio_files = [
    "audio_files/pi1_audio.wav",
    "audio_files/pi2_audio.wav",
    "audio_files/pi3_audio.wav",
    "audio_files/pi4_audio.wav",
]

warnings.filterwarnings("ignore", category=wav.WavFileWarning)

mic_sound_peak_times = np.array([])

for file in audio_files:
    sample_rate, data = load_audio_data(file)
    max_amplitude, max_time = find_loudest_point(data, sample_rate)
    mic_sound_peak_times = np.append(mic_sound_peak_times, max_time)

print(mic_sound_peak_times)


def compute_tdoa(timestamps):
    tdoas = []
    for i in range(len(timestamps)):
        for j in range(i + 1, len(timestamps)):
            tdoas.append(timestamps[j] - timestamps[i])
    return tdoas


tdoas = compute_tdoa(mic_sound_peak_times)

def compute_distance_by_tdoa(tdoas, mic_positions):

    num_mics = len(mic_positions)

    Amat = np.zeros((num_mics - 1, 3))
    Dmat = np.zeros((num_mics - 1, 1))

    for i in range(1, num_mics):
        xi, yi, zi = mic_positions[i]["x"], mic_positions[i]["y"], mic_positions[i]["z"]
        x0, y0, z0 = mic_positions[0]["x"], mic_positions[0]["y"], mic_positions[0]["z"]

        Amat[i - 1, 0] = 2 * (x0 - xi)
        Amat[i - 1, 1] = 2 * (y0 - yi)
        Amat[i - 1, 2] = 2 * (z0 - zi)

        Dmat[i - 1] = speed_of_sound * tdoas[i - 1] + (
            (x0**2 + y0**2 + z0**2) - (xi**2 + yi**2 + zi**2)
        )

    source_position, residuals, rank, singular_values = np.linalg.lstsq(
        Amat, Dmat, rcond=None
    )

    xs, ys, zs = source_position.flatten()

    return xs, ys, zs


x, y, z = compute_distance_by_tdoa(tdoas, mic_positions)
print(f"Source position: x={x}, y={y}, z={z}")


# x, y, z = compute_distance_by_tdoa([0, 0, 0, 0, 0, 0], mic_positions)
# print(f"Source position: x={x}, y={y}, z={z}")


mic_x = [mic["x"] for mic in mic_positions]
mic_y = [mic["y"] for mic in mic_positions]

fig, ax = plt.subplots()

ax.scatter(mic_x, mic_y, color="blue", label="Microphones")
ax.scatter(x, y, color="red", label="Sound Source")
ax.set_xlabel("X (meters)")
ax.set_ylabel("Y (meters)")
ax.set_title("Microphone Positions and Estimated Sound Source (2D)")
ax.legend()

plt.show()
