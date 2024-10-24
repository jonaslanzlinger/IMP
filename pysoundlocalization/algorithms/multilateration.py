import numpy as np

# TODO: move somewhere else
SPEED_OF_SOUND = 343  # meters per second (constant for air at room temperature)


def approximate_sound_source(tdoa_pairs):
    """
    Approximates the sound source given all microphone pairs and their computed TDoA values.

    :param tdoa_pairs: A dictionary where the keys are tuples representing microphone pairs (positions of the two mics),
                         and the values are the computed TDoA values (in seconds).
    :return: The estimated (x, y) coordinates of the sound source.
    """
    if len(tdoa_pairs) < 2:
        raise ValueError("At least two microphone pairs are required to approximate the sound source.")

    Amat = np.zeros((len(tdoa_pairs), 2))
    #Amat = np.zeros((len(tdoa_pairs), 3)) #TODO: only if z is included
    Dmat = np.zeros((len(tdoa_pairs), 1))

    for row, ((mic1_pos, mic2_pos), tdoa) in enumerate(tdoa_pairs.items()):
        # Retrieve positions of mic1 and mic2
        x0, y0 = mic1_pos
        x1, y1 = mic2_pos

        # TODO: add z as well?
        #x0, y0, z0 = mic1_pos
        #x1, y1, z1 = mic2_pos

        # Formulate the linear system based on TDoA and microphone positions
        Amat[row, 0] = 2 * (x0 - x1)
        Amat[row, 1] = 2 * (y0 - y1)
        #Amat[row, 2] = 2 * (z0 - z1)

        Dmat[row] = SPEED_OF_SOUND * tdoa + (
                #(x0 ** 2 + y0 ** 2 + z0 ** 2) - (x1 ** 2 + y1 ** 2 + z1 ** 2)
                (x0 ** 2 + y0 ** 2) - (x1 ** 2 + y1 ** 2)
        )

    # Solve the least squares problem to estimate the source position
    source_position, residuals, rank, singular_values = np.linalg.lstsq(Amat, Dmat, rcond=None)

    xs, ys = source_position.flatten()

    return xs, ys