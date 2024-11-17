import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider
from pysoundlocalization.core.Environment import Environment
import matplotlib


def multilaterate_plot(environment: Environment, data: dict) -> None:
    """
    Visualizes the environment layout, microphones, and sound source positions using Matplotlib.
    The sound source positions are approximated using the multilateration algorithm, stored in the data dictionary.

    Args:
        environment (Environment): Environment object containing the environment layout and microphones.
        data (dict): Dictionary containing the sound source positions approximated using the multilateration algorithm.
    """

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.2)
    ax.set_aspect("equal")

    polygon = patches.Polygon(
        environment.get_vertices(),
        closed=True,
        edgecolor="black",
        facecolor="none",
        linewidth=2,
    )
    ax.add_patch(polygon)

    ax.set_xlim(
        min(x for x, y in environment.get_vertices()) - 1,
        max(x for x, y in environment.get_vertices()) + 1,
    )
    ax.set_ylim(
        min(y for x, y in environment.get_vertices()) - 1,
        max(y for x, y in environment.get_vertices()) + 1,
    )

    # Plot microphones
    if environment.get_mics():
        mic_x, mic_y = zip(*[mic.get_position() for mic in environment.get_mics()])
        ax.scatter(mic_x, mic_y, color="red", label="Microphones")

    # Create a scatter plot for sound sources (empty initially)
    (sound_scatter,) = ax.plot([], [], "bo", label="Sound Source")

    ax.set_title(f"Environment: {environment.get_name()} with Microphones")
    ax.legend()

    # Add a slider for navigation
    slider_ax = plt.axes([0.2, 0.05, 0.6, 0.03])
    slider = Slider(slider_ax, "Timeline", 0, len(data) - 1, valinit=0, valstep=1)

    # Check the number of data points
    if len(data) > 1:
        # Add a slider if there are multiple data points
        slider_ax = plt.axes([0.2, 0.05, 0.6, 0.03])
        slider = Slider(slider_ax, "Timeline", 0, len(data) - 1, valinit=0, valstep=1)

        def update(val):
            idx = int(slider.val)
            entry = list(data.keys())[idx]
            position = data[entry]

            if position is not None:
                sound_scatter.set_data([position[0]], [position[1]])
            else:
                sound_scatter.set_data([], [])

            fig.canvas.draw_idle()

        slider.on_changed(update)
    else:
        # Handle a single data point
        only_entry = list(data.values())[0]
        if only_entry is not None:
            sound_scatter.set_data([only_entry[0]], [only_entry[1]])

    plt.show()
