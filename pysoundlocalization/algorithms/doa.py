import math


def compute_doa(tdoa, max_tau):
    """
    Computes the direction of arrival (DoA) in degrees of the sound considering a given microphone pair
    and the sound's time difference of arrival (TDoA) to the given microphone pair.

    :param tdoa: Time difference of arrival between the two microphones (in seconds).
    :param max_tau: The maximum possible TDoA between the microphones.
    :return: The DoA in degrees.

    Args:
        tdoa (float): Time difference of arrival between the two microphones (in seconds).
        max_tau (float): The maximum possible TDoA between the microphones, usually determined by: (mic_distance / speed_of_sound).
        For example, if distance between microphones is 2 meters and speed of sound is 343.2 m/s, then max_tau = 2 / 343.2.

    Returns:
        float: The computed DoA in degrees.

    Raises:
        ValueError: If the absolute value of TDoA exceeds the maximum allowable TDoA (max_tau).
    """
    if abs(tdoa) > max_tau:
        raise ValueError("TDoA value is out of valid range based on the maximum possible tau.")

    # Compute DoA in radians using the inverse sine of (TDoA / max_tau)
    doa_radians = math.asin(tdoa / max_tau)

    # Convert to degrees
    return doa_radians * 180 / math.pi