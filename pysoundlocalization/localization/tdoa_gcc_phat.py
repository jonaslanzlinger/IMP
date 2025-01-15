from pysoundlocalization.core.TdoaPair import TdoaPair
from pysoundlocalization.localization.gcc_phat import gcc_phat
from itertools import combinations
import numpy as np


def get_all_tdoa_of_chunk_index_by_gcc_phat(
    environment,
    chunk_index: int = 0,
    threshold: float = 0.5,
    debug: bool = False,
) -> TdoaPair | None:
    """
    Compute TDoA for all microphone pairs in the environment.

    Args:
        environment (Environment): The environment to compute TDoA for.
        chunk_index (int): The index of the chunk to compute TDoA for.
        threshold (float): The threshold for the audio signal.
        debug (bool): Print debug information if True.

    Returns:
        list[TdoaPair] | None: A list of TdoaPair objects representing the computed TDoA for each microphone pair.
    """

    if len(environment.get_mics()) < 2:
        raise ValueError("At least two microphones are required to compute TDoA.")

    sample_rate = environment.get_lowest_sample_rate()
    max_tau = environment.get_max_tau()

    tdoa_results = []

    # Iterate over all possible pairs of microphones
    for mic1, mic2 in combinations(environment.get_mics(), 2):
        # Retrieve the audio signals from each microphone
        audio1 = mic1.get_audio().get_audio_signal(index=chunk_index)
        audio2 = mic2.get_audio().get_audio_signal(index=chunk_index)

        # Be aware that if audio signals are not the same length, the chunking can result
        # that we have different amount of chunks per mic. This can lead to problems here.
        # Therefore, make sure that audio signals have identical length in the preprocessing step.
        # Check if both microphones have valid audio signals
        if audio1 is not None and audio2 is not None:

            # If the audio signals do not contain a dominant signal, don't compute TDoA
            if np.max(np.abs(audio1)) < threshold or np.max(np.abs(audio2)) < threshold:
                if debug:
                    print(
                        f"Audio signals for mics at {mic1.get_position()} and {mic2.get_position()} do not contain a dominant signal."
                    )
                return None

            # Compute TDoA using the compute_tdoa method
            tdoa, cc = gcc_phat(
                sig=audio1, refsig=audio2, fs=sample_rate, max_tau=max_tau
            )

            tdoa_pair = TdoaPair(mic1=mic1, mic2=mic2, tdoa=tdoa)

            tdoa_results.append(tdoa_pair)

            if debug:
                print(str(tdoa_pair))

        else:
            print(
                f"Missing audio signal(s) for mics at {mic1.get_position()} and {mic2.get_position()}"
            )

    return tdoa_results
