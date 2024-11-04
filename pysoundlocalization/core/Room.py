import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import combinations

import numpy as np

import config
from algorithms.gcc_phat import gcc_phat
from algorithms.doa import compute_doa
from algorithms.multilateration import multilaterate_sound_source
from core.Microphone import Microphone


class Room:
    def __init__(self, name: str, vertices: list[tuple[float, float]], sound_speed: float = config.DEFAULT_SOUND_SPEED):
        """
        Initialize a Room instance with a name, vertices defining the room shape.

        Args:
            name (str): The name of the room.
            vertices (list[tuple[float, float]]): List of (x, y) coordinates defining the room's shape.
            sound_speed (float): The speed of sound in m/s. Defaults to config.DEFAULT_SOUND_SPEED.
        """
        self.sound_speed = sound_speed # Default speed of sound in m/s
        self.name = name
        self.vertices = vertices  # List of (x, y) coordinates for the room's shape
        self.mics: list[Microphone] = []
        self.sound_source_position: tuple[float, float] | None = None #TODO: create our own SoundSource class to handle multiple sound sources (assumed pos / computed pos / etc) and different colors for visualization?

    def add_microphone(self, x: float, y: float) -> Microphone | None:
        """
        Add a microphone at the specified coordinates if it is within room boundaries and not duplicated.

        Args:
            x (float): X-coordinate of the microphone position.
            y (float): Y-coordinate of the microphone position.

        Returns:
            Microphone | None: The added Microphone object if successful, otherwise None.
        """
        # Ensure that no mic already exists at given coordinates
        for mic in self.mics:
            if mic.x == x and mic.y == y:
                print(f"A microphone already exists at position ({x}, {y})")
                return None

        if self.is_within_room(x, y):
            mic = Microphone(x, y)
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
            raise ValueError("At least two microphones are required to calculate max_tau.")

        # Find the max distance between any two microphones
        max_mic_distance = max(
            np.linalg.norm(np.array(mic1.get_position()) - np.array(mic2.get_position()))
            for mic1, mic2 in combinations(self.mics, 2)
        )

        return max_mic_distance / self.sound_speed

    # TODO: should computation methods be in room class? if yes, move to separate room_computations.py file and import here?
    # TODO: allow selection of algorithm
    def compute_tdoa(self, audio1: np.ndarray, audio2: np.ndarray, sample_rate: int, max_tau: float = None) -> tuple[float, np.ndarray]:
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

    def compute_all_tdoa(self, sample_rate: int, max_tau: float = None, print_intermediate_results: bool = False) -> dict[tuple[tuple[float, float], tuple[float, float]], float] | None:
        """
        Compute TDoA for all microphone pairs in the room.

        Args:
            sample_rate (int): Sample rate of the recorded audio in Hz.
            max_tau (float): The maximum possible TDoA between the microphones, usually determined by: (mic_distance / speed_of_sound).
            print_intermediate_results (bool): Print intermediate results if True.

        Returns:
            dict[tuple[tuple[float, float], tuple[float, float]], float] | None: A dictionary where the keys are tuples representing microphone pairs (positions of the two mics),
                and the values are the computed TDoA values (in seconds). If less than two microphones are present,
                the function returns None. The key consists of a tuple of two microphones that are identified by their coordinates.
                Example of dictionary tdoa_pairs: {((0.5, 1), (2.5, 1)): -58.63464131262136, ((0.5, 1), (0.5, 3)): 72.89460160061566}.
                The format of each key-value entry is: ((mic1_x, mic1_y), (mic2_x, mic2_y)): tdoa_float_value, where the key
                is ((mic1_x, mic1_y), (mic2_x, mic2_y)) and the value is the computed tdoa_float_value.
        """
        if len(self.mics) < 2:
            print("At least two microphones are needed to compute TDoA.")
            return None

        # If max_tau is not provided via parameter, automatically compute via class method
        if max_tau is None:
            max_tau = self.get_max_tau()

        tdoa_results = {}

        # Iterate over all possible pairs of microphones
        for (mic1, mic2) in combinations(self.mics, 2):
            # Retrieve the audio signals from each microphone
            audio1 = mic1.get_audio().get_audio_signal()
            audio2 = mic2.get_audio().get_audio_signal()

            # Check if both microphones have valid audio signals
            if audio1 is not None and audio2 is not None:
                # Compute TDoA using the compute_tdoa method
                tdoa, cc = self.compute_tdoa(audio1, audio2, sample_rate, max_tau)
                mic_pair = (mic1.get_position(), mic2.get_position())


                # Store the result in a dictionary with the mic pair as the key
                tdoa_results[mic_pair] = tdoa

                if print_intermediate_results:
                    print(f"TDoA between mics {mic_pair}: {tdoa:.6f} seconds")
            else:
                print(f"Missing audio signal(s) for mics at {mic1.get_position()} and {mic2.get_position()}")

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

    def compute_all_doa(self, tdoa_pairs: dict[tuple[tuple[float, float], tuple[float, float]], float], max_tau: float = None, print_intermediate_results: bool = False) -> dict[tuple[tuple[float, float], tuple[float, float]], float]:
        """
        Computes the direction of arrival (DoA) for all microphone pairs based on their TDoA values.

        Args:
            tdoa_pairs (dict): A dictionary where keys are tuples representing microphone pairs and values are the TDoA values (float) in seconds. The key consists of a tuple of two microphones that are identified by their coordinates.
                                Example of dictionary tdoa_pairs: {((0.5, 1), (2.5, 1)): -58.63464131262136, ((0.5, 1), (0.5, 3)): 72.89460160061566}.
                                The format of each key-value entry is: ((mic1_x, mic1_y), (mic2_x, mic2_y)): tdoa_float_value, where the key
                                is ((mic1_x, mic1_y), (mic2_x, mic2_y)) and the value is the computed tdoa_float_value.
            max_tau (float): The maximum allowable time difference (in seconds) between the two signals,
                        typically determined by the distance between the microphones and the speed of sound.
            print_intermediate_results (bool): Set to true if intermediate results of computation should be printed to console. Default is false.


        Returns:
            dict[tuple[tuple[float, float], tuple[float, float]], float]: A dictionary where the keys are tuples representing microphone pairs (positions of the two mics),
                 and the values are the computed DoA values (in degrees).
        """
        doa_results = {}

        # If max_tau is not provided via parameter, automatically compute via class method
        if max_tau is None:
            max_tau = self.get_max_tau()

        for mic_pair, tdoa in tdoa_pairs.items():
            doa = self.compute_doa(tdoa, max_tau)

            # Store the computed DoA in a dictionary with the mic pair as the key
            doa_results[mic_pair] = doa

            if print_intermediate_results:
                print(f"DoA for microphone pair {mic_pair}: {doa:.2f} degrees")

        return doa_results

    def multilaterate_sound_source(self, tdoa_pairs: dict[tuple[tuple[float, float], tuple[float, float]], float]) -> tuple[float, float]:
        """
        Approximates the sound source given all microphone pairs and their computed TDoA values.

        Args:
            tdoa_pairs (dict):  A dictionary where keys are tuples representing microphone pairs and values are the TDoA values (float) in seconds. The key consists of a tuple of two microphones that are identified by their coordinates.
                                Example of dictionary tdoa_pairs: {((0.5, 1), (2.5, 1)): -58.63464131262136, ((0.5, 1), (0.5, 3)): 72.89460160061566}.
                                The format of each key-value entry is: ((mic1_x, mic1_y), (mic2_x, mic2_y)): tdoa_float_value, where the key
                                is ((mic1_x, mic1_y), (mic2_x, mic2_y)) and the value is the computed tdoa_float_value.

        Returns:
            tuple[float, float]: The estimated (x, y) coordinates of the sound source.
        """
        return multilaterate_sound_source(tdoa_pairs)

    # TODO: possibly move visualizations out of class
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

        ax.set_aspect('equal')

        # Plot microphones
        if self.mics:
            mic_x, mic_y = zip(*[mic.get_position() for mic in self.mics])
            ax.scatter(mic_x, mic_y, color="red", label="Microphones")

        if self.sound_source_position and isinstance(self.sound_source_position, tuple):
            ax.scatter(self.sound_source_position[0], self.sound_source_position[1], color="blue", label="Approximated Sound Source")

        ax.set_xlabel("X coordinate")
        ax.set_ylabel("Y coordinate")
        ax.set_title(f"Room: {self.name} with Microphones")
        plt.legend()
        plt.grid(True)
        plt.show()