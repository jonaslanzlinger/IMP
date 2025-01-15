from pysoundlocalization.core.TdoaPair import TdoaPair
from pysoundlocalization.core.Microphone import Microphone


def get_all_tdoa_of_chunk_index_by_threshold(
    environment,
    chunk_index: int = 0,
    threshold: float = 0.5,
    debug: bool | None = False,
) -> list[TdoaPair]:
    """
    Compute TDoA for all microphone pairs in the environment based on a threshold.

    Args:
        environment (Environment): The environment to compute TDoA for.
        chunk_index (int): The index of the chunk to compute TDoA for.
        threshold (float): The threshold for the audio signal.
        debug (bool): Print debug information if True.

    Returns:
        list[TdoaPair]: A list of TdoaPair objects representing the computed TDoA for each microphone pair.
    """

    def compute_sample_index_threshold(mic: Microphone, debug: bool = False) -> int:
        for i, sample in enumerate(mic.get_audio().get_audio_signal(index=chunk_index)):
            if abs(sample) > threshold:
                if debug:
                    print(
                        f"Mic {mic.get_name()} sample index: {i} has exceeded threshold"
                    )
                return i

    tdoa_pairs = []

    for i in range(len(environment.get_mics())):
        mic1 = environment.get_mics()[i]
        mic1_sample_index = compute_sample_index_threshold(mic=mic1, debug=debug)

        if mic1_sample_index is None:
            return None

        for j in range(i + 1, len(environment.get_mics())):
            mic2 = environment.get_mics()[j]
            mic2_sample_index = compute_sample_index_threshold(mic=mic2, debug=False)

            if mic2_sample_index is None:
                return None

            tdoa_pairs.append(
                TdoaPair(
                    mic1=mic1,
                    mic2=mic2,
                    tdoa=(mic1_sample_index - mic2_sample_index)
                    / mic1.get_audio().get_sample_rate(),
                )
            )

    return tdoa_pairs
