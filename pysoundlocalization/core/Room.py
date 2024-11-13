import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import combinations

import numpy as np

import pysoundlocalization.config as config
from pysoundlocalization.algorithms.gcc_phat import gcc_phat
from pysoundlocalization.algorithms.doa import compute_doa
from pysoundlocalization.algorithms.multilateration import multilaterate_sound_source
from pysoundlocalization.core.Microphone import Microphone
from pysoundlocalization.core.TdoaPair import TdoaPair
from pysoundlocalization.core.DoaPair import DoaPair


class Room:
    def __init__(
        self,
        name: str,
        vertices: list[tuple[float, float]],
        sound_speed: float = config.DEFAULT_SOUND_SPEED,
    ):
        """
        Initialize a Room instance with a name, vertices defining the room shape.

        Args:
            name (str): The name of the room.
            vertices (list[tuple[float, float]]): List of (x, y) coordinates defining the room's shape.
            sound_speed (float): The speed of sound in m/s. Defaults to config.DEFAULT_SOUND_SPEED.
        """
        self.__sound_speed = sound_speed  # Default speed of sound in m/s
        self.__name = name
        self.vertices = vertices  # List of (x, y) coordinates for the room's shape
        self.mics: list[Microphone] = []
        self.sound_source_position: tuple[float, float] | None = (
            None  # TODO: create our own SoundSource class to handle multiple sound sources (assumed pos / computed pos / etc) and different colors for visualization?
        )

    def add_microphone(
        self, x: float, y: float, name: str | None = None
    ) -> Microphone | None:
        """
        Add a microphone at the specified coordinates if it is within room boundaries and not duplicated.

        Args:
            x (float): X-coordinate of the microphone position.
            y (float): Y-coordinate of the microphone position.
            name (str): The name of the microphone.

        Returns:
            Microphone | None: The added Microphone object if successful, otherwise None.
        """
        # Ensure that no mic already exists at given coordinates
        for mic in self.mics:
            if mic.x == x and mic.y == y:
                print(f"A microphone already exists at position ({x}, {y})")
                return None

        if self.is_within_room(x, y):
            mic = Microphone(x, y, name)
            self.mics.append(mic)
            print(f"Microphone added at position ({x}, {y})")
            return mic
        else:
            print(f"Microphone at ({x}, {y}) is outside the room bounds!")

    # TODO: addAssumedSoundSource() -> add where we think the sound source is (nice for visualization)
    def add_sound_source_position(self, x: float, y: float) -> None:
        """
        Add coordinates of sound source

        Args:
            x (float): X-coordinate of the sound source.
            y (float): Y-coordinate of the sound source.
        """
        self.sound_source_position = (x, y)

    def is_within_room(self, x: float, y: float) -> bool:
        """
        Check if a point (x, y) is inside the room's polygon defined by its vertices.

        Implementation of the ray-casting algorithm to solve the point-in-polygon problem.

        Args:
            x (float): X-coordinate of the point to check.
            y (float): Y-coordinate of the point to check.

        Returns:
            bool: True if the point is inside the polygon, False otherwise.
        """
        num_vertices = len(self.vertices)
        inside = False

        # Iterate over each edge of the polygon
        for i in range(num_vertices):
            # Get current vertex and the next vertex (wrapping around at the end)
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % num_vertices]

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
        if len(self.mics) < 2:
            raise ValueError(
                "At least two microphones are required to calculate max_tau."
            )

        # Find the max distance between any two microphones
        max_mic_distance = max(
            np.linalg.norm(
                np.array(mic1.get_position()) - np.array(mic2.get_position())
            )
            for mic1, mic2 in combinations(self.mics, 2)
        )

        return max_mic_distance / self.__sound_speed

    # TODO: should computation methods be in room class? if yes, move to separate room_computations.py file and import here?
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

    def compute_all_tdoa_by_threshold(
        self, debug_threshold_sample_index: bool = False
    ) -> list[TdoaPair]:
        """
        Compute TDoA for all microphone pairs in the room based on a threshold.

        Returns:
            list[TdoaPair]: A list of TdoaPair objects representing the computed TDoA for each microphone pair.
        """

        def compute_sample_index_threshold(mic: Microphone, debug: bool = False) -> int:
            threshold = 0.3
            for i, sample in enumerate(mic.get_audio().audio_signal):
                if abs(sample) > threshold:
                    if debug:
                        print(
                            f"Mic {mic.get_name()} sample index: {i} has exceeded threshold"
                        )
                    return i

        tdoa_pairs = []

        for i in range(len(self.mics)):
            mic1 = self.mics[i]
            mic1_sample_index = compute_sample_index_threshold(
                mic1, debug=debug_threshold_sample_index
            )
            for j in range(i + 1, len(self.mics)):
                mic2 = self.mics[j]
                mic2_sample_index = compute_sample_index_threshold(mic2, debug=False)
                tdoa_pairs.append(
                    TdoaPair(
                        mic1,
                        mic2,
                        abs(mic2_sample_index - mic1_sample_index)
                        / mic1.get_audio().get_sample_rate(),
                    )
                )

        return tdoa_pairs

    def compute_all_tdoa(
        self,
        sample_rate: int,
        max_tau: float = None,
        print_intermediate_results: bool = False,
    ) -> TdoaPair | None:
        """
        Compute TDoA for all microphone pairs in the room.

        Args:
            sample_rate (int): Sample rate of the recorded audio in Hz.
            max_tau (float): The maximum possible TDoA between the microphones, usually determined by: (mic_distance / speed_of_sound).
            print_intermediate_results (bool): Print intermediate results if True.

        Returns:
            list[TdoaPair] | None: A list of TdoaPair objects representing the computed TDoA for each microphone pair.
        """
        if len(self.mics) < 2:
            print("At least two microphones are needed to compute TDoA.")
            return None

        # If max_tau is not provided via parameter, automatically compute via class method
        if max_tau is None:
            max_tau = self.get_max_tau()

        tdoa_results = []

        # Iterate over all possible pairs of microphones
        for mic1, mic2 in combinations(self.mics, 2):
            # Retrieve the audio signals from each microphone
            audio1 = mic1.get_audio().get_audio_signal()
            audio2 = mic2.get_audio().get_audio_signal()

            # Check if both microphones have valid audio signals
            if audio1 is not None and audio2 is not None:
                # Compute TDoA using the compute_tdoa method
                tdoa, cc = self.compute_tdoa(audio1, audio2, sample_rate, max_tau)

                tdoa_pair = TdoaPair(mic1, mic2, tdoa)
                tdoa_results.append(tdoa_pair)

                if print_intermediate_results:
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

    def multilaterate_sound_source(
        self, tdoa_pairs: list[TdoaPair]
    ) -> tuple[float, float]:
        """
        Approximates the sound source given all microphone pairs and their computed TDoA values.

        Args:
            tdoa_pairs (list[TdoaPair]): A list of TdoaPair objects representing the computed TDoA for each microphone pair

        Returns:
            tuple[float, float]: The estimated (x, y) coordinates of the sound source.
        """
        return multilaterate_sound_source(tdoa_pairs)

    def visualize(self) -> None:
        """
        Visualizes the room layout, microphones, and sound source positions using Matplotlib.
        """
        fig, ax = plt.subplots()

        # Create a polygon representing the room shape
        polygon = patches.Polygon(
            self.vertices, closed=True, edgecolor="black", facecolor="none", linewidth=2
        )
        ax.add_patch(polygon)

        # Set limits based on the room's shape
        ax.set_xlim(
            min(x for x, y in self.vertices) - 1, max(x for x, y in self.vertices) + 1
        )
        ax.set_ylim(
            min(y for x, y in self.vertices) - 1, max(y for x, y in self.vertices) + 1
        )

        ax.set_aspect("equal")

        # Plot microphones
        if self.mics:
            mic_x, mic_y = zip(*[mic.get_position() for mic in self.mics])
            ax.scatter(mic_x, mic_y, color="red", label="Microphones")

        if self.sound_source_position and isinstance(self.sound_source_position, tuple):
            ax.scatter(
                self.sound_source_position[0],
                self.sound_source_position[1],
                color="blue",
                label="Approximated Sound Source",
            )

        ax.set_xlabel("X coordinate")
        ax.set_ylabel("Y coordinate")
        ax.set_title(f"Room: {self.__name} with Microphones")
        plt.legend()
        plt.grid(True)
        plt.show()

    def get_sound_speed(self) -> float:
        """
        Get the speed of sound in the room.

        Returns:
            float: The speed of sound in m/s.
        """
        return self.__sound_speed

    def set_sound_speed(self, speed: float) -> None:
        """
        Set the speed of sound in the room.

        Args:
            speed (float): The speed of sound in m/s.
        """
        self.__sound_speed = speed

    def get_name(self) -> str:
        """
        Get the name of the room.

        Returns:
            str: The name of the room.
        """
        return self.__name

    def set_name(self, name: str) -> None:
        """
        Set the name of the room.

        Args:
            name (str): The name of the room.
        """
        self.__name = name
