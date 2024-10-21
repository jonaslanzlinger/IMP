import matplotlib.pyplot as plt
import matplotlib.patches as patches

from pysoundlocalization.algorithms.gcc_phat import gcc_phat
from pysoundlocalization.core.Microphone import Microphone


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
    def compute_tdoa(self, mic1, mic2, sample_rate, max_tau):
        return gcc_phat(mic1, mic2, fs=sample_rate, max_tau=max_tau)

    # TODO: possibly move visualizations out of class
    def visualize(self):
        fig, ax = plt.subplots()

        # Create a polygon representing the room shape
        polygon = patches.Polygon(self.vertices, closed=True, edgecolor='black', facecolor='none', linewidth=2)
        ax.add_patch(polygon)

        # Set limits based on the room's shape
        ax.set_xlim(min(x for x, y in self.vertices) - 1, max(x for x, y in self.vertices) + 1)
        ax.set_ylim(min(y for x, y in self.vertices) - 1, max(y for x, y in self.vertices) + 1)

        # Plot microphones
        if self.mics:
            mic_x, mic_y = zip(*[mic.get_position() for mic in self.mics])
            ax.scatter(mic_x, mic_y, color='red', label='Microphones')

        ax.set_xlabel('X coordinate')
        ax.set_ylabel('Y coordinate')
        ax.set_title(f'Room: {self.name} with Microphones')
        plt.legend()
        plt.grid(True)
        plt.show()