import numpy as np

SPEED_OF_SOUND = 343  # m/s

def approximate_sound_source(tdoas, mic_positions):
    num_mics = len(mic_positions)

    Amat = np.zeros((num_mics - 1, 3))
    Dmat = np.zeros((num_mics - 1, 1))

    for i in range(1, num_mics):
        xi, yi, zi = mic_positions[i]["x"], mic_positions[i]["y"], mic_positions[i]["z"]
        x0, y0, z0 = mic_positions[0]["x"], mic_positions[0]["y"], mic_positions[0]["z"]

        Amat[i - 1, 0] = 2 * (x0 - xi)
        Amat[i - 1, 1] = 2 * (y0 - yi)
        Amat[i - 1, 2] = 2 * (z0 - zi)

        Dmat[i - 1] = SPEED_OF_SOUND * tdoas[i - 1] + (
                (x0 ** 2 + y0 ** 2 + z0 ** 2) - (xi ** 2 + yi ** 2 + zi ** 2)
        )

    source_position, residuals, rank, singular_values = np.linalg.lstsq(
        Amat, Dmat, rcond=None
    )

    xs, ys, zs = source_position.flatten()

    return xs, ys, zs