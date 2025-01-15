from pysoundlocalization.core.TdoaPair import TdoaPair
from pysoundlocalization.core.DoaPair import DoaPair
import math


def compute_doa(tdoa: float, max_tau: float) -> float:
    """
    Computes the direction of arrival (DoA) in degrees of the sound considering a given microphone pair
    and the sound's time difference of arrival (TDoA) to the given microphone pair.

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
        raise ValueError(
            "TDoA value is out of valid range based on the maximum possible tau."
        )

    # Compute DoA in radians using the inverse sine of (TDoA / max_tau)
    doa_radians = math.asin(tdoa / max_tau)

    # Convert to degrees
    return doa_radians * 180 / math.pi


def compute_all_doa(
    tdoa_pairs: list[TdoaPair],
    max_tau: float = None,
    debug: bool = False,
) -> list[DoaPair]:
    """
    Computes the direction of arrival (DoA) for all microphone pairs based on their TDoA values.

    Args:
        tdoa_pairs (list[TdoaPair]): A list of TdoaPair objects representing the computed TDoA for each microphone pair.
        max_tau (float): The maximum allowable time difference (in seconds) between the two signals,
                    typically determined by the distance between the microphones and the speed of sound.
        debug (bool): Set to true if intermediate results of computation should be printed to console. Default is false.

    Returns:
        list[DoaPair]: A list of DoaPair objects representing the computed DoA for each microphone pair.
    """
    doa_results = []

    # Raise an error if either no TDoA pairs are provided or if no maximum tau is provided
    if not tdoa_pairs:
        raise ValueError("No TDoA pairs provided for DoA computation.")
    if max_tau is None:
        raise ValueError("No maximum tau provided for DoA computation.")

    for tdoa_pair in tdoa_pairs:
        doa = compute_doa(tdoa=tdoa_pair.get_tdoa(), max_tau=max_tau)

        doa_pair = DoaPair(
            mic1=tdoa_pair.get_mic1(), mic2=tdoa_pair.get_mic2(), doa=doa
        )
        doa_results.append(doa_pair)

        if debug:
            print(str(doa_pair))

    return doa_results
