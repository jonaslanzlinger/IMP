import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import combinations

from algorithms.gcc_phat import gcc_phat
from algorithms.doa import compute_doa
from core.Microphone import Microphone


class Room:
    def __init__(self, name, vertices):
        self.name = name
        self.vertices = vertices  # List of (x, y) coordinates for the room's shape
        self.mics = []

    def add_microphone(self, x, y):
        if self.is_within_room(x, y):
            mic = Microphone(x, y)
            self.mics.append(mic)
            print(f"Microphone added at position ({x}, {y})")
            return mic
        else:
            print(f"Microphone at ({x}, {y}) is outside the room bounds!")

    # TODO: addAssumedSoundSource() -> add where we think the sound source is (nice for visualization)

    # TODO: Add actual check to verify that mic position is within room
    def is_within_room(self, x, y):
        return True

    # TODO: should computation methods be in room class? argument for, because you do computations on a per room basis
    # TODO: allow selection of algorithm
    def compute_tdoa(self, audio1, audio2, sample_rate, max_tau):
        """
        Computes the time difference of arrival (TDoA) of two audio signals.
        """
        return gcc_phat(audio1, audio2, fs=sample_rate, max_tau=max_tau)

    def compute_all_tdoa(self, sample_rate, max_tau):
        """Computes the time difference of arrival (TDoA) for all microphone pairs in the room"""
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
                #print(f"TDoA between mics {mic_pair}: {tdoa:.6f} seconds")
            else:
                print(f"Missing audio signals for mics at {mic1.get_position()} and {mic2.get_position()}")

        return tdoa_results

    def compute_doa(self, tdoa, max_tau):
        """
        Computes the direction of arrival (DoA) of a sound based on the time difference of arrival (TDoA) of two signals.
        """
        return compute_doa(tdoa, max_tau=max_tau)

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
