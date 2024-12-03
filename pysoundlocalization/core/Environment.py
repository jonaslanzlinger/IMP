from datetime import timedelta

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import combinations

import numpy as np

import pysoundlocalization.config as config
from pysoundlocalization.algorithms.gcc_phat import gcc_phat
from pysoundlocalization.algorithms.doa import compute_doa
from pysoundlocalization.algorithms.multilateration import multilaterate_by_tdoa_pairs
from pysoundlocalization.core.Microphone import Microphone
from pysoundlocalization.core.TdoaPair import TdoaPair
from pysoundlocalization.core.DoaPair import DoaPair


class Environment:
    def __init__(
        self,
        name: str,
        vertices: list[tuple[float, float]],
        sound_speed: float = config.DEFAULT_SOUND_SPEED,
    ):
        """
        Initialize an Environment instance with a name, vertices defining the environment shape.

        Args:
            name (str): The name of the environment.
            vertices (list[tuple[float, float]]): List of (x, y) coordinates defining the environment's shape.
            sound_speed (float): The speed of sound in m/s. Defaults to config.DEFAULT_SOUND_SPEED.
        """
        self.__sound_speed = sound_speed  # Default speed of sound in m/s
        self.__name = name
        self.__vertices = (
            vertices  # List of (x, y) coordinates for the environment's shape
        )
        self.__mics: list[Microphone] = []
        self.__sound_source_position: tuple[float, float] | None = (
            None  # TODO: create our own SoundSource class to handle multiple sound sources (assumed pos / computed pos / etc) and different colors for visualization?
        )

    def add_microphone(
        self, x: float, y: float, name: str | None = None
    ) -> Microphone | None:
        """
        Add a microphone at the specified coordinates if it is within environment boundaries and not duplicated.

        Args:
            x (float): X-coordinate of the microphone position.
            y (float): Y-coordinate of the microphone position.
            name (str): The name of the microphone.

        Returns:
            Microphone | None: The added Microphone object if successful, otherwise None.
        """
        # Ensure that no mic already exists at given coordinates
        for mic in self.__mics:
            if mic.get_x == x and mic.get_y == y:
                print(f"A microphone already exists at position ({x}, {y})")
                return None

        if self.is_within_environment(x, y):
            mic = Microphone(x, y, name)
            self.__mics.append(mic)
            print(f"Microphone added at position ({x}, {y})")
            return mic
        else:
            print(f"Microphone at ({x}, {y}) is outside the environment bounds!")

    # TODO: addAssumedSoundSource() -> add where we think the sound source is (nice for visualization)
    def add_sound_source_position(self, x: float, y: float) -> None:
        """
        Add coordinates of sound source

        Args:
            x (float): X-coordinate of the sound source.
            y (float): Y-coordinate of the sound source.
        """
        self.__sound_source_position = (x, y)

    def is_within_environment(self, x: float, y: float) -> bool:
        """
        Check if a point (x, y) is inside the environment's polygon defined by its vertices.

        Implementation of the ray-casting algorithm to solve the point-in-polygon problem.

        Args:
            x (float): X-coordinate of the point to check.
            y (float): Y-coordinate of the point to check.

        Returns:
            bool: True if the point is inside the polygon, False otherwise.
        """
        num_vertices = len(self.__vertices)
        inside = False

        # Iterate over each edge of the polygon
        for i in range(num_vertices):
            # Get current vertex and the next vertex (wrapping around at the end)
            x1, y1 = self.__vertices[i]
            x2, y2 = self.__vertices[(i + 1) % num_vertices]

            # Check if the ray crosses the edge
            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside

        return inside

    def get_max_tau(self) -> float:
        """
        Calculate the maximum time delay (tau) based on the distance between microphones and the sound speed.

        Returns:
            float: Maximum time delay (tau) in seconds.
        """
        if len(self.__mics) < 2:
            raise ValueError(
                "At least two microphones are required to calculate max_tau."
            )

        # Find the max distance between any two microphones
        max_mic_distance = max(
            np.linalg.norm(
                np.array(mic1.get_position()) - np.array(mic2.get_position())
            )
            for mic1, mic2 in combinations(self.__mics, 2)
        )

        return max_mic_distance / self.__sound_speed

    def get_lowest_sample_rate(self) -> int:
        """
        Get the lowest sample rate of all microphones in the environment.

        Returns:
            int: The lowest sample rate of all microphones.
        """
        return min(mic.get_audio().get_sample_rate() for mic in self.__mics)

    def get_sample_rate(self) -> int:
        """
        Get the sample rate of the environment. If there are different
        sample rates for the microphones, an exception is raised.

        Returns:
            int: The sample rate of the environment.
        """
        sample_rates = [mic.get_audio().get_sample_rate() for mic in self.__mics]
        if len(set(sample_rates)) > 1:
            raise ValueError(
                "Different sample rates for microphones in the environment."
            )
        return sample_rates[0]

    def chunk_audio_signals_by_duration(
        self, chunk_duration: timedelta | None = timedelta(milliseconds=1000)
    ) -> None:
        """
        Chunk the audio signals of all microphones into chunks of a specified duration.

        Args:
            chunk_duration (timedelta | None): The duration of each chunk. Defaults to 1000 ms.
        """
        for mic in self.__mics:
            mic.get_audio().chunk_audio_signal_by_duration(
                chunk_duration=chunk_duration
            )

    def chunk_audio_signals_by_samples(self, chunk_samples: int) -> None:
        """
        Chunk the audio signals of all microphones into chunks of specified number of samples.

        Args:
            chunk_samples (int): The number of samples in each chunk. The sample rate of the audio defines how many samples are in a given timeframe.
        """
        for mic in self.__mics:
            mic.get_audio().chunk_audio_signal_by_samples(chunk_samples=chunk_samples)

    def multilaterate(
        self,
        algorithm: str = "threshold",
        number_of_sound_sources: int = 1,
        threshold: float | None = 0.5,
    ) -> dict:
        """
        Approximates the sound source given the algorithm and number of sound sources that shall be approximated.

        Args:
            algorithm (str): The algorithm to use for computing the TDoA values.
            number_of_sound_sources (int): The number of sound sources to approximate.

        Returns:
            TODO: dict: A dictionary containing the estimated (x, y) coordinates of the sound sources.
        """

        number_of_chunks = len(
            self.get_mics()[0].get_audio().get_audio_signal_chunked()
        )

        # Get chunk size in samples
        chunk_size = int(
            self.get_mics()[0].get_audio().get_num_samples() / number_of_chunks
        )

        dict = {}
        for i in range(number_of_chunks):

            if algorithm == "gcc_phat":
                tdoa_pairs_of_chunk = self.compute_all_tdoa_of_chunk_index_by_gcc_phat(
                    chunk_index=i,
                    threshold=threshold,
                    debug=False,
                )
            elif algorithm == "threshold":
                tdoa_pairs_of_chunk = self.compute_all_tdoa_of_chunk_index_by_threshold(
                    chunk_index=i, threshold=threshold, debug=True
                )

            if tdoa_pairs_of_chunk is None:
                dict[f"{i * chunk_size}"] = tdoa_pairs_of_chunk
                continue

            sound_source_position = multilaterate_by_tdoa_pairs(tdoa_pairs_of_chunk)

            dict[f"{i * chunk_size}"] = sound_source_position

        return dict

    # TODO: should computation methods be in environment class? if yes, move to separate environment_computations.py file and import here?
    # TODO: allow selection of algorithm
    def compute_tdoa(
        self,
        audio1: np.ndarray,
        audio2: np.ndarray,
        sample_rate: int,
        max_tau: float = None,
    ) -> tuple[float, np.ndarray]:
        """
        Computes the time difference of arrival (TDoA) of two audio signals.

        Args:
            audio1 (np.ndarray): Audio signal from the first microphone.
            audio2 (np.ndarray): Audio signal from the second microphone.
            sample_rate (int): Sample rate of the audio in Hz.
            max_tau (float): Maximum allowable time delay.

        Returns:
            tuple[float, np.ndarray]: The estimated time delay and cross-correlation result.
        """
        # If max_tau is not provided via parameter, automatically compute via class method
        if max_tau is None:
            max_tau = self.get_max_tau()

        return gcc_phat(audio1, audio2, fs=sample_rate, max_tau=max_tau)

    def compute_all_tdoa_of_chunk_index_by_threshold(
        self, chunk_index: int = 0, threshold: float = 0.5, debug: bool | None = False
    ) -> list[TdoaPair]:
        """
        Compute TDoA for all microphone pairs in the environment based on a threshold.

        Args:
            chunk_index (int): The index of the chunk to compute TDoA for.
            threshold (float): The threshold for the audio signal.
            debug (bool): Print debug information if True.

        Returns:
            list[TdoaPair]: A list of TdoaPair objects representing the computed TDoA for each microphone pair.
        """

        def compute_sample_index_threshold(mic: Microphone, debug: bool = False) -> int:
            for i, sample in enumerate(
                mic.get_audio().get_audio_signal(index=chunk_index)
            ):
                if abs(sample) > threshold:
                    if debug:
                        print(
                            f"Mic {mic.get_name()} sample index: {i} has exceeded threshold"
                        )
                    return i

        tdoa_pairs = []

        for i in range(len(self.__mics)):
            mic1 = self.__mics[i]
            mic1_sample_index = compute_sample_index_threshold(mic1, debug=debug)

            if mic1_sample_index is None:
                return None

            for j in range(i + 1, len(self.__mics)):
                mic2 = self.__mics[j]
                mic2_sample_index = compute_sample_index_threshold(mic2, debug=False)

                if mic2_sample_index is None:
                    return None

                tdoa_pairs.append(
                    TdoaPair(
                        mic1,
                        mic2,
                        (mic1_sample_index - mic2_sample_index)
                        / mic1.get_audio().get_sample_rate(),
                    )
                )

        return tdoa_pairs

    def compute_all_tdoa_of_chunk_index_by_gcc_phat(
        self,
        chunk_index: int = 0,
        threshold: float = 0.5,
        debug: bool = False,
    ) -> TdoaPair | None:
        """
        Compute TDoA for all microphone pairs in the environment.

        Args:
            chunk_index (int): The index of the chunk to compute TDoA for.
            threshold (float): The threshold for the audio signal.
            debug (bool): Print debug information if True.

        Returns:
            list[TdoaPair] | None: A list of TdoaPair objects representing the computed TDoA for each microphone pair.
        """

        from pysoundlocalization.preprocessing.SampleRateConverter import (
            SampleRateConverter,
        )

        sample_rate = SampleRateConverter.get_lowest_sample_rate(self)

        if len(self.__mics) < 2:
            print("At least two microphones are needed to compute TDoA.")
            return None

        max_tau = self.get_max_tau()

        tdoa_results = []

        # Iterate over all possible pairs of microphones
        for mic1, mic2 in combinations(self.__mics, 2):
            # Retrieve the audio signals from each microphone
            audio1 = mic1.get_audio().get_audio_signal(index=chunk_index)
            audio2 = mic2.get_audio().get_audio_signal(index=chunk_index)

            # TODO: be aware that if audio signals are not the same length, the chunking can result
            # that we have different amount of chunks per mic. This can lead to problems here!!!
            # Check if both microphones have valid audio signals
            if audio1 is not None and audio2 is not None:

                # If the audio signals do not contain a dominant signal, don't compute TDoA
                if (
                    np.max(np.abs(audio1)) < threshold
                    or np.max(np.abs(audio2)) < threshold
                ):
                    if debug:
                        print(
                            f"Audio signals for mics at {mic1.get_position()} and {mic2.get_position()} do not contain a dominant signal."
                        )
                    return None

                # Compute TDoA using the compute_tdoa method
                tdoa, cc = self.compute_tdoa(audio1, audio2, sample_rate, max_tau)

                tdoa_pair = TdoaPair(mic1, mic2, tdoa)
                tdoa_results.append(tdoa_pair)

                if debug:
                    print(str(tdoa_pair))

            else:
                print(
                    f"Missing audio signal(s) for mics at {mic1.get_position()} and {mic2.get_position()}"
                )

        return tdoa_results

    def compute_doa(self, tdoa: float, max_tau: float = None) -> float:
        """
        Computes the direction of arrival (DoA) of a sound based on the time difference of arrival (TDoA) of two signals.

        Args:
            tdoa (float): Time difference of arrival.
            max_tau (float): Maximum allowable time delay.

        Returns:
            float: The direction of arrival in degrees.
        """
        # If max_tau is not provided via parameter, automatically compute via class method
        if max_tau is None:
            max_tau = self.get_max_tau()

        return compute_doa(tdoa, max_tau=max_tau)

    def compute_all_doa(
        self,
        tdoa_pairs: list[TdoaPair],
        max_tau: float = None,
        print_intermediate_results: bool = False,
    ) -> list[DoaPair]:
        """
        Computes the direction of arrival (DoA) for all microphone pairs based on their TDoA values.

        Args:
            tdoa_pairs (list[TdoaPair]): A list of TdoaPair objects representing the computed TDoA for each microphone pair.
            max_tau (float): The maximum allowable time difference (in seconds) between the two signals,
                        typically determined by the distance between the microphones and the speed of sound.
            print_intermediate_results (bool): Set to true if intermediate results of computation should be printed to console. Default is false.


        Returns:
            list[DoaPair]: A list of DoaPair objects representing the computed DoA for each microphone pair.
        """
        doa_results = []

        # If max_tau is not provided via parameter, automatically compute via class method
        if max_tau is None:
            max_tau = self.get_max_tau()

        # for mic_pair, tdoa in tdoa_pairs.items():
        for tdoa_pair in tdoa_pairs:
            doa = self.compute_doa(tdoa_pair.get_tdoa(), max_tau)

            doa_pair = DoaPair(tdoa_pair.get_mic1(), tdoa_pair.get_mic2(), doa)
            doa_results.append(doa_pair)

            if print_intermediate_results:
                print(str(doa_pair))

        return doa_results

    # TODO: Needed?
    def visualize(self) -> None:
        """
        Visualizes the environment layout, microphones, and sound source positions using Matplotlib.
        """
        fig, ax = plt.subplots()

        # Create a polygon representing the environment shape
        polygon = patches.Polygon(
            self.__vertices,
            closed=True,
            edgecolor="black",
            facecolor="none",
            linewidth=2,
        )
        ax.add_patch(polygon)

        # Set limits based on the environment's shape
        ax.set_xlim(
            min(x for x, y in self.__vertices) - 1,
            max(x for x, y in self.__vertices) + 1,
        )
        ax.set_ylim(
            min(y for x, y in self.__vertices) - 1,
            max(y for x, y in self.__vertices) + 1,
        )

        ax.set_aspect("equal")

        # Plot microphones
        if self.__mics:
            mic_x, mic_y = zip(*[mic.get_position() for mic in self.__mics])
            ax.scatter(mic_x, mic_y, color="red", label="Microphones")

        if self.__sound_source_position and isinstance(
            self.__sound_source_position, tuple
        ):
            ax.scatter(
                self.__sound_source_position[0],
                self.__sound_source_position[1],
                color="blue",
                label="Approximated Sound Source",
            )

        ax.set_xlabel("X coordinate")
        ax.set_ylabel("Y coordinate")
        ax.set_title(f"Environment: {self.__name} with Microphones")
        plt.legend()
        plt.grid(True)
        plt.show()

    def get_sound_speed(self) -> float:
        """
        Get the speed of sound in the environment.

        Returns:
            float: The speed of sound in m/s.
        """
        return self.__sound_speed

    def set_sound_speed(self, speed: float) -> None:
        """
        Set the speed of sound in the environment.

        Args:
            speed (float): The speed of sound in m/s.
        """
        self.__sound_speed = speed

    def get_name(self) -> str:
        """
        Get the name of the environment.

        Returns:
            str: The name of the environment.
        """
        return self.__name

    def set_name(self, name: str) -> None:
        """
        Set the name of the environment.

        Args:
            name (str): The name of the environment.
        """
        self.__name = name

    def get_vertices(self) -> list[tuple[float, float]]:
        """
        Get the vertices of the environment.

        Returns:
            list[tuple[float, float]]: List of (x, y) coordinates defining the environment's shape.
        """
        return self.__vertices

    def set_vertices(self, vertices: list[tuple[float, float]]) -> None:
        """
        Set the vertices of the environment.

        Args:
            vertices (list[tuple[float, float]]): List of (x, y) coordinates defining the environment's shape.
        """
        self.__vertices = vertices

    def get_mics(self) -> list[Microphone]:
        """
        Get the microphones in the environment.

        Returns:
            list[Microphone]: List of Microphone objects in the environment.
        """
        return self.__mics

    def set_mics(self, mics: list[Microphone]) -> None:
        """
        Set the microphones in the environment.

        Args:
            mics (list[Microphone]): List of Microphone objects in the environment.
        """
        self.__mics = mics

    # TODO: Needed?
    def get_sound_source_position(self) -> tuple[float, float] | None:
        """
        Get the coordinates of the sound source.

        Returns:
            tuple[float, float] | None: The (x, y) coordinates of the sound source if available, otherwise None.
        """
        return self.__sound_source_position

    # TODO: Needed?
    def set_sound_source_position(
        self, sound_source_position: tuple[float, float]
    ) -> None:
        """
        Set the coordinates of the sound source.

        Args:
            sound_source_position (tuple[float, float]): The (x, y) coordinates of the sound source.
        """
        self.__sound_source_position = sound_source_position
