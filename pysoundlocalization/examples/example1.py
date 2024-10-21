# Example to localize a sound source using 4 microphones and GCC-PHAT
from pysoundlocalization.core.Simulation import Simulation


simulation = Simulation.create()

# Define an L-shaped room using vertices
l_shape_vertices = [(0, 0), (4.7, 0), (4.7, 2), (3, 2), (3, 4.5), (0, 4.5)]
room1 = simulation.add_room("L-Shaped Room", l_shape_vertices)

# Create and add microphones with decimal coordinates
room1.add_microphone(1.2, 2.5)  # Inside the L-shaped room
room1.add_microphone(2.6, 3.6784849)  # Inside the L-shaped room

room1.visualize()