#-------
# Used to verify whether there's a problem with the rewritten multilateration algorithm used in the library,
# by comparing it to the initial algorithm here.
#
# FINDING: the algorithm in the pysoundlocalization library seems correct as the resulting x,y is the same here


import numpy as np
from matplotlib import pyplot as plt

# in meters
mic_positions = np.array(
    [
        {"x": 8.61, "y": 2, "z": 0},
        {"x": 8.61, "y": 5.89, "z": 0},
        {"x": 2, "y": 5.89, "z": 0},
        {"x": 2, "y": 2, "z": 0},
    ]
)

speed_of_sound = 343  # m/s

# pairs: 1,2 + 1,3 + 1,4 + 2,3 + 2,4 + 3,4
# where pair 1,2 would be (8.61,2) and (8.61,5.89)
tdoas = [
    np.float64(0.0001403061224489796),
    np.float64(0.00011621315192743764),
    np.float64(-0.014426020408163265),
    np.float64(-0.00020833333333333335),
    np.float64(0.0002990362811791383),
    np.float64(0.02145124716553288)
]

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
                (x0 ** 2 + y0 ** 2 + z0 ** 2) - (xi ** 2 + yi ** 2 + zi ** 2)
        )

    source_position, residuals, rank, singular_values = np.linalg.lstsq(
        Amat, Dmat, rcond=None
    )

    xs, ys, zs = source_position.flatten()

    return xs, ys, zs


x, y, z = compute_distance_by_tdoa(tdoas, mic_positions)
print(f"Source position: x={x}, y={y}, z={z}")


# VISUALIZE

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

# Initialize subplots
fig, axs = plt.subplots(3, 1, figsize=(12, 16))

# Plot 1: Microphone positions and sound source
ax1 = axs[0]
ax1.scatter(mic_x, mic_y, color="blue", label="Microphones")
ax1.scatter(x, y, color="red", label="Sound Source")
ax1.set_xlabel("X (meters)")
ax1.set_ylabel("Y (meters)")
ax1.set_title("Microphone Positions and Estimated Sound Source (2D)")
ax1.legend()