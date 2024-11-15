import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pysoundlocalization.core.Environment import Environment


def multilaterate_plot(environment: Environment, dict: list[(int, int)]) -> None:
    """
    Visualizes the environment layout, microphones, and sound source positions using Matplotlib.
    The sound source positions are approximated using the multilateration algorithm, stored in the dict object.

    Args:
        environment (Environment): Environment object containing the environment layout and microphones.
        dict (object): Dictionary containing the sound source positions approximated using the multilateration algorithm.
    """

    fig, ax = plt.subplots()

    # Create a polygon representing the environment shape
    polygon = patches.Polygon(
        environment.get_vertices(),
        closed=True,
        edgecolor="black",
        facecolor="none",
        linewidth=2,
    )
    ax.add_patch(polygon)

    # Set limits based on the environment's shape
    ax.set_xlim(
        min(x for x, y in environment.get_vertices()) - 1,
        max(x for x, y in environment.get_vertices()) + 1,
    )
    ax.set_ylim(
        min(y for x, y in environment.get_vertices()) - 1,
        max(y for x, y in environment.get_vertices()) + 1,
    )

    ax.set_aspect("equal")

    # Plot microphones
    if environment.get_mics():
        mic_x, mic_y = zip(*[mic.get_position() for mic in environment.get_mics()])
        ax.scatter(mic_x, mic_y, color="red", label="Microphones")

    # Iterate through the dict entries and update the plot
    scatter_points = []
    for i, entry in enumerate(dict):

        for scatter in scatter_points:
            scatter.remove()
        scatter_points.clear()

        if dict[entry] is not None:
            x, y = dict[entry]
            scatter = ax.scatter(
                x, y, color="blue", label=f"Approximated Sound Source {i + 1}"
            )
            scatter_points.append(scatter)
            ax.legend()

        # Pause for 1 second and update the plot
        plt.pause(1)
        plt.draw()

    plt.show()

    # OLD!!! (TODO: maybe take the legend stuff from here)
    # Iterate over the dictionary containing the sound source positions
    # for i, (x, y) in enumerate(dict):
    #     ax.scatter(x, y, color="blue", label=f"Approximated Sound Source {i + 1}")

    # ax.set_xlabel("X coordinate")
    # ax.set_ylabel("Y coordinate")
    # ax.set_title(f"Environment: {environment.get_name()} with Microphones")
    # plt.legend()
    # plt.grid(True)
    # plt.show()
