import math

def compute_doa(tdoa, MAX_TAU):
    """
    Computes the direction of arrival (doa) of the sound considering a given microphone pair and the sound's time
    difference of arrival (tdoa) to the given microphone pair
    """
    return math.asin(tdoa / MAX_TAU) * 180 / math.pi