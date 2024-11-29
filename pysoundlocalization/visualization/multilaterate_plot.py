import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pysoundlocalization.core.Environment import Environment
from matplotlib.widgets import Slider, Button
from matplotlib.widgets import RadioButtons
import pygame
from scipy.io.wavfile import write
import numpy as np
from matplotlib import animation


def multilaterate_plot(environment: Environment, data: dict) -> None:
    """
    Visualizes the environment layout, microphones, and sound source positions using Matplotlib.
    The sound source positions are approximated using the multilateration algorithm, stored in the data dictionary.

    Args:
        environment (Environment): Environment object containing the environment layout and microphones.
        data (dict): Dictionary containing the sound source positions approximated using the multilateration algorithm.
    """

    plt.rcParams["toolbar"] = "none"

    fig, ax = plt.subplots(figsize=(10, 10))
    fig.canvas.manager.set_window_title(
        f"{environment.get_name()} - Multilateration Plot"
    )
    plt.subplots_adjust(bottom=0.45, top=0.95)
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

    if environment.get_mics():
        mic_x, mic_y = zip(*[mic.get_position() for mic in environment.get_mics()])
        ax.scatter(mic_x, mic_y, color="red", label="Microphones")

    # (sound_scatter_1,) = ax.plot([], [], "bo", label="Source 1: Clap")
    # (sound_scatter_2,) = ax.plot([], [], "go", label="Source 2: Sine Wave")
    (sound_scatter,) = ax.plot([], [], "bo", label="Sound Source")

    ax.legend(loc="upper right", bbox_to_anchor=(1.48, 0.7), borderaxespad=0.0)

    menu_ax = plt.axes([0.1, 0.25, 0.8, 0.15])
    radio_items = [mic.get_name() for mic in environment.get_mics()]
    radio = RadioButtons(menu_ax, radio_items, active=0, activecolor="red")

    button_load_ax = plt.axes([0.6, 0.285, 0.125, 0.08])
    button_load = Button(button_load_ax, "Load")

    button_play_ax = plt.axes([0.75, 0.285, 0.125, 0.08])
    button_play = Button(button_play_ax, "Toggle Play")

    wave_ax = plt.axes([0.1, 0.1, 0.8, 0.15])

    global is_playing, cursor_line, animation_obj
    is_playing = False
    cursor_line = None
    animation_obj = None

    pygame.mixer.init()

    def toggle_play(event=None):

        global is_playing
        global animation_obj

        if is_playing:
            pygame.mixer.music.pause()
            is_playing = False
            if animation_obj:
                animation_obj.event_source.stop()
            return
        else:
            pygame.mixer.music.unpause()
            is_playing = True
            if animation_obj:
                animation_obj.event_source.start()

    def plot_waveform(event=None):

        global is_playing
        global cursor_line
        global animation_obj

        selected_item = radio.value_selected
        selected_audio = next(
            mic.get_audio()
            for mic in environment.get_mics()
            if mic.get_name() == selected_item
        )
        wave_ax.clear()
        wave_ax.plot(selected_audio.get_audio_signal_unchunked(), color="blue")
        wave_ax.set_xlabel("Time (samples)")
        wave_ax.set_ylabel("Amplitude")
        global cursor_line
        cursor_line = wave_ax.axvline(x=0, color="red", linestyle="--", linewidth=2)
        fig.canvas.draw_idle()

        wav_file = "temp_audio_playback.wav"
        write(
            wav_file,
            selected_audio.get_sample_rate(),
            (selected_audio.get_audio_signal_unchunked() * 32767).astype(np.int16),
        )

        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.mixer.init()

        is_playing = False

        pygame.mixer.music.load(wav_file)
        pygame.mixer.music.play()
        pygame.mixer.music.pause()

        def update_source_positions(event=None):

            global cursor_line

            playback_position_ms = pygame.mixer.music.get_pos()
            current_sample = int(
                (playback_position_ms / 1000) * selected_audio.get_sample_rate()
            )
            for key in sorted(data.keys(), key=int):
                if int(key) > current_sample:
                    break
                if data[key] is not None:
                    sound_scatter.set_data([data[key][0]], [data[key][1]])
                    fig.canvas.draw_idle()

            # HERE: Stub for having multiple sound sources
            # for key in sorted(data[0].keys(), key=int):
            #     if int(key) > current_sample:
            #         break
            #     if data[0][key] is not None:
            #         sound_scatter_1.set_data([data[0][key][0]], [data[0][key][1]])
            #         fig.canvas.draw_idle()

            # for key in sorted(data[1].keys(), key=int):
            #     if int(key) > current_sample:
            #         break
            #     if data[1][key] is not None:
            #         sound_scatter_2.set_data([data[1][key][0]], [data[1][key][1]])
            #         fig.canvas.draw_idle()

        def update_cursor(frame):

            global is_playing

            if is_playing:
                playback_position_ms = pygame.mixer.music.get_pos()
                current_sample = int(
                    (playback_position_ms / 1000) * selected_audio.get_sample_rate()
                )
                if current_sample < len(selected_audio.get_audio_signal_unchunked()):
                    cursor_line.set_xdata([current_sample])
                    fig.canvas.draw_idle()
                else:
                    cursor_line.set_xdata(
                        [len(selected_audio.get_audio_signal_unchunked()) - 1]
                    )
                    fig.canvas.draw_idle()

            update_source_positions()

        if animation_obj:
            animation_obj.event_source.stop()

        animation_obj = animation.FuncAnimation(
            fig, update_cursor, interval=100, blit=False, cache_frame_data=False
        )

    def move_cursor(event):
        if event.inaxes == wave_ax:
            cursor_line.set_xdata([event.xdata])
            fig.canvas.draw_idle()

    button_load.on_clicked(plot_waveform)
    button_play.on_clicked(toggle_play)

    fig.canvas.mpl_connect("button_press_event", move_cursor)

    plt.show()
