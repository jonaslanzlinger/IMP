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
    doa_degrees = doa_radians * 180 / math.pi

    return doa_degrees


'''
def compute_all_doa(tdoas, max_tau):
    """
    Computes the direction of arrival for all microphone pairs and their prior computed time difference of arrival
    """
    for pair, tdoa in tdoas.items():
        mic_a, mic_b = pair
        theta = compute_doa(tdoa, max_tau)
        print(f"Estimated DoA (theta) between mic{mic_a + 1} and mic{mic_b + 1}: {theta:.2f} degrees")
'''