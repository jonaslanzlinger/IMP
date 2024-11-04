import numpy as np
import config


# TODO: think of adding z-coordinate to multilateration algorithm
def multilaterate_sound_source(tdoa_pairs: dict[tuple[tuple[float, float], tuple[float, float]], float],
                               speed_of_sound: float = config.DEFAULT_SOUND_SPEED) -> tuple[float, float]:
    """
    Approximates the sound source position given all microphone pairs and their computed TDoA values.

    Args:
        tdoa_pairs (dict): A dictionary where keys are tuples representing microphone pairs and values are the TDoA values (float) in seconds. The key consists of a tuple of two microphones that are identified by their coordinates.
        Example of dictionary tdoa_pairs: {((0.5, 1), (2.5, 1)): -58.63464131262136, ((0.5, 1), (0.5, 3)): 72.89460160061566}.
        The format of each key-value entry is: ((mic1_x, mic1_y), (mic2_x, mic2_y)): tdoa_float_value, where the key
        is ((mic1_x, mic1_y), (mic2_x, mic2_y)) and the value is the computed tdoa_float_value.

        speed_of_sound (float): Optional speed of sound in meters per second. Defaults to the value set in config.DEFAULT_SOUND_SPEED.

    Returns:
        tuple[float, float]: The estimated (x, y) coordinates of the sound source.

    Raises:
        ValueError: If fewer than two microphone pairs are provided.
    """
    if len(tdoa_pairs) < 2:
        raise ValueError("At least two microphone pairs are required to approximate the sound source.")

    Amat = np.zeros((len(tdoa_pairs), 2))
    #Amat = np.zeros((len(tdoa_pairs), 3))
    Dmat = np.zeros((len(tdoa_pairs), 1))

    for row, ((mic1_pos, mic2_pos), tdoa) in enumerate(tdoa_pairs.items()):
        # Retrieve positions of mic1 and mic2
        x0, y0 = mic1_pos
        x1, y1 = mic2_pos

        #x0, y0, z0 = mic1_pos
        #x1, y1, z1 = mic2_pos

        # Formulate the linear system based on TDoA and microphone positions
        Amat[row, 0] = 2 * (x0 - x1)
        Amat[row, 1] = 2 * (y0 - y1)
        #Amat[row, 2] = 2 * (z0 - z1)

        Dmat[row] = speed_of_sound * tdoa + (
                #(x0 ** 2 + y0 ** 2 + z0 ** 2) - (x1 ** 2 + y1 ** 2 + z1 ** 2)
                (x0 ** 2 + y0 ** 2) - (x1 ** 2 + y1 ** 2)
        )

    # Solve the least squares problem to estimate the source position
    source_position, residuals, rank, singular_values = np.linalg.lstsq(Amat, Dmat, rcond=None)

    xs, ys = source_position.flatten()

    return xs, ys