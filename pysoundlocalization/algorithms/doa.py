import math


def compute_doa(tdoa, max_tau):
    """
    Computes the direction of arrival (DoA) in degrees of the sound considering a given microphone pair
    and the sound's time difference of arrival (TDoA) to the given microphone pair.

    :param tdoa: Time difference of arrival between the two microphones (in seconds).
    :param max_tau: The maximum possible TDoA between the microphones.
    :return: The DoA in degrees.
    """
    if abs(tdoa) > max_tau:
        raise ValueError("TDoA value is out of valid range based on the maximum possible tau.")

    # Compute DoA in radians using the inverse sine of (TDoA / max_tau)
    doa_radians = math.asin(tdoa / max_tau)

    # Convert to degrees
    return doa_radians * 180 / math.pi