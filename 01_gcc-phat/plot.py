import matplotlib.pyplot as plt


def plot_2d_multilateration_result(x, y, MIC_POSITIONS):
    mic_x = [mic["x"] for mic in MIC_POSITIONS]
    mic_y = [mic["y"] for mic in MIC_POSITIONS]

    fig, ax = plt.subplots()

    ax.scatter(mic_x, mic_y, color="blue", label="Microphones")
    ax.scatter(x, y, color="red", label="Sound Source")
    ax.set_xlabel("X (meters)")
    ax.set_ylabel("Y (meters)")
    ax.set_title("Microphone Positions and Estimated Sound Source (2D)")
    ax.legend()

    plt.show()
