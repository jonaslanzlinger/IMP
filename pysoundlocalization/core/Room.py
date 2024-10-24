import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import combinations

from algorithms.gcc_phat import gcc_phat
from algorithms.doa import compute_doa
from algorithms.multilateration import approximate_sound_source
from core.Microphone import Microphone


class Room:
    def __init__(self, name, vertices):
        self.name = name
        self.vertices = vertices  # List of (x, y) coordinates for the room's shape
        self.mics = []

    def add_microphone(self, x, y):
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

    def is_within_room(self, x, y):
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

    # TODO: should computation methods be in room class? if yes, move to separate room_computations.py file and import here?
    # TODO: allow selection of algorithm
    def compute_tdoa(self, audio1, audio2, sample_rate, max_tau):
        """
        Computes the time difference of arrival (TDoA) of two audio signals.
        """
        return gcc_phat(audio1, audio2, fs=sample_rate, max_tau=max_tau)

    def compute_all_tdoa(self, sample_rate, max_tau, print_intermediate_results=False):
        """
        Computes the time difference of arrival (TDoA) for all microphone pairs in the room.

        :param sample_rate: The sample rate of the recorded audio signals (in Hz).
        :param max_tau: The maximum allowable time difference (in seconds) between the two signals,
                    typically determined by the distance between the microphones and the speed of sound.
        :param print_intermediate_results: Set to true if intermediate results of computation should be printed to console. Default is false.

        :return: A dictionary where the keys are tuples representing microphone pairs (positions of the two mics),
             and the values are the computed TDoA values (in seconds). If less than two microphones are present,
             the function returns None.
        """
        if len(self.mics) < 2:
            print("At least two microphones are needed to compute TDoA.")
            return None

        tdoa_results = {}

        # Iterate over all possible pairs of microphones
        for (mic1, mic2) in combinations(self.mics, 2):
            # Retrieve the audio signals from each microphone
            audio1 = mic1.get_recorded_audio()
            audio2 = mic2.get_recorded_audio()

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

    def compute_doa(self, tdoa, max_tau):
        """
        Computes the direction of arrival (DoA) of a sound based on the time difference of arrival (TDoA) of two signals.
        """
        return compute_doa(tdoa, max_tau=max_tau)

    def compute_all_doa(self, tdoa_pairs, max_tau, print_intermediate_results=False):
        """
        Computes the direction of arrival (DoA) for all microphone pairs based on their TDoA values.

        :param tdoa_pairs: A dictionary where the keys are tuples representing microphone pairs (positions of the two mics),
                             and the values are the computed TDoA values (in seconds).
        :param max_tau: The maximum allowable time difference (in seconds) between the two signals,
                        typically determined by the distance between the microphones and the speed of sound.
        :param print_intermediate_results: Set to true if intermediate results of computation should be printed to console. Default is false.

        :return: A dictionary where the keys are tuples representing microphone pairs (positions of the two mics),
                 and the values are the computed DoA values (in degrees).
        """
        doa_results = {}

        for mic_pair, tdoa in tdoa_pairs.items():
            doa = self.compute_doa(tdoa, max_tau)

            # Store the computed DoA in a dictionary with the mic pair as the key
            doa_results[mic_pair] = doa

            # TODO: use parameter to define whether intermediate results should be printed or not?
            if print_intermediate_results:
                print(f"DoA for microphone pair {mic_pair}: {doa:.2f} degrees")

        return doa_results

    def approximate_sound_source(self, tdoa_pairs):
        """
        Approximates the sound source given all microphone pairs and their computed TDoA values.

        :param tdoa_pairs: A dictionary where the keys are tuples representing microphone pairs (positions of the two mics),
                         and the values are the computed TDoA values (in seconds).
        :return: The estimated (x, y) coordinates of the sound source.
        """
        return approximate_sound_source(tdoa_pairs)


    # TODO: possibly move visualizations out of class
    def visualize(self):
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

        # Plot microphones
        if self.mics:
            mic_x, mic_y = zip(*[mic.get_position() for mic in self.mics])
            ax.scatter(mic_x, mic_y, color="red", label="Microphones")

        ax.set_xlabel("X coordinate")
        ax.set_ylabel("Y coordinate")
        ax.set_title(f"Room: {self.name} with Microphones")
        plt.legend()
        plt.grid(True)
        plt.show()
