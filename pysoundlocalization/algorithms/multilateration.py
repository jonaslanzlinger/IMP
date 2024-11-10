import numpy as np
import pysoundlocalization.config as config
from pysoundlocalization.core.TdoaPair import TdoaPair
from scipy.optimize import least_squares


# TODO: think of adding z-coordinate to multilateration algorithm
def multilaterate_sound_source(
    tdoa_pairs: TdoaPair,
    speed_of_sound: float = config.DEFAULT_SOUND_SPEED,
) -> tuple[float, float]:
    """
    Approximates the sound source position given all microphone pairs and their computed TDoA values.

    Args:
        tdoa_pairs (list[TdoaPair]): A list of TdoaPair objects representing the TDoA values between microphone pairs.
        speed_of_sound (float): Optional speed of sound in meters per second. Defaults to the value set in config.DEFAULT_SOUND_SPEED.

    Returns:
        tuple[float, float]: The estimated (x, y) coordinates of the sound source.

    Raises:
        ValueError: If fewer than two microphone pairs are provided.
    """
    if len(tdoa_pairs) < 2:
        raise ValueError(
            "At least two microphone pairs are required to approximate the sound source."
        )

    # Convert TDOA times to distance differences in meters
    tdoa_distances = [
        (
            tdoa_pair.get_mic1(),
            tdoa_pair.get_mic2(),
            tdoa_pair.get_tdoa() * speed_of_sound,
        )
        for tdoa_pair in tdoa_pairs
    ]

    # Define the system of equations based on the hyperbolic equations for TDOA
    def multilateration_fn(initial_guess):
        """Function to minimize for multilateration."""
        px, py = initial_guess
        equations = []
        for mic1, mic2, d in tdoa_distances:
            x1, y1 = mic1.get_position()
            x2, y2 = mic2.get_position()
            dist1 = np.sqrt((px - x1) ** 2 + (py - y1) ** 2)
            dist2 = np.sqrt((px - x2) ** 2 + (py - y2) ** 2)
            equations.append(dist1 - dist2 - d)
        return equations

    # Initial guess (e.g., center of the mic positions or any reasonable point)
    # Or any reasonable starting point in your coordinate system
    initial_guess = [0, 0]
    for mic1, mic2, d in tdoa_distances:
        x1, y1 = mic1.get_position()
        x2, y2 = mic2.get_position()
        initial_guess[0] += (x1 + x2) / 2
        initial_guess[1] += (y1 + y2) / 2
    initial_guess[0] /= len(tdoa_distances)
    initial_guess[1] /= len(tdoa_distances)

    print("Initial guess:", initial_guess)

    # Solve using least squares optimization
    result = least_squares(multilateration_fn, initial_guess)

    source_position = result.x

    xs, ys = source_position

    return xs, ys
