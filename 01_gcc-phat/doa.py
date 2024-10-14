import math

def compute_doa(tdoa, max_tau):
    """
    Computes the direction of arrival (doa) of the sound considering a given microphone pair and the sound's time
    difference of arrival (tdoa) to the given microphone pair
    """
    return math.asin(tdoa / max_tau) * 180 / math.pi

def compute_all_doa(tdoas, max_tau):
    """
    Computes the direction of arrival for all microphone pairs and their prior computed time difference of arrival
    """
    for pair, tdoa in tdoas.items():
        mic_a, mic_b = pair
        theta = compute_doa(tdoa, max_tau)
        print(f"Estimated DoA (theta) between mic{mic_a + 1} and mic{mic_b + 1}: {theta:.2f} degrees")