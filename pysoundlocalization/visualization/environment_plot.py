import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button
from matplotlib.widgets import RadioButtons
import pygame
from scipy.io.wavfile import write
import numpy as np
from matplotlib import animation
import os


def environment_plot(environment) -> None:
    """
    Visualizes the environment layout and microphones using Matplotlib.

    Args:
        environment (Environment): Environment object containing the environment layout and microphones.
    """

    plt.rcParams["toolbar"] = "none"

    fig, ax = plt.subplots(figsize=(10, 10))
    fig.canvas.manager.set_window_title(f"{environment.get_name()} - Environment Plot")
    ax.set_aspect("equal")

    polygon = patches.Polygon(
        environment.get_vertices(),
        closed=True,
        edgecolor="black",
        facecolor="none",
        linewidth=3,
    )
    ax.add_patch(polygon)
    ax.set_xlabel("Width (meters)")
    ax.set_ylabel("Height (meters)")

    ax.set_xlim(
        min(x for x, y in environment.get_vertices()) - 1,
        max(x for x, y in environment.get_vertices()) + 1,
    )
    ax.set_ylim(
        min(y for x, y in environment.get_vertices()) - 1,
        max(y for x, y in environment.get_vertices()) + 1,
    )

    if environment.get_mics():
        mic_x, mic_y = zip(*[mic.get_position() for mic in environment.get_mics()])
        ax.scatter(mic_x, mic_y, color="red", label="Microphones", marker="x", s=100)

    ax.legend(loc="upper right", bbox_to_anchor=(1.48, 0.7), borderaxespad=0.0)
    plt.show()
