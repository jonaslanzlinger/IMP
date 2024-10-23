import tkinter as tk
from tkinter import simpledialog, messagebox
from core.Simulation import Simulation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from core.Audio import Audio
from tkinter import filedialog
from core.Microphone import Microphone
import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Gui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sound Localization")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.root.geometry(
            f"{int(screen_width - screen_width * 0.1)}x{int(screen_height - screen_height * 0.1)}"
        )

        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20
        )

        self.new_sim_button = tk.Button(
            self.left_frame, text="New Simulation", command=self.new_simulation
        )
        self.new_sim_button.pack(pady=5)

        self.play_button = tk.Button(
            self.left_frame, text="Play", command=self.play_audio
        )
        self.play_button.pack_forget()

        self.simulation = None
        self.room = None
        self.canvas = None
        self.scale = None
        self.offset_x = None
        self.offset_y = None
        self.add_mic_button = None
        self.plot_canvas = None

        self.microphones = []

    def new_simulation(self):
        """Handle the New Simulation button click event."""

        self.simulation = Simulation.create()
        self.create_room()

    def create_room(self):
        """Create a room by asking for all vertices at once in the form [(0,0), (5,0), (5,5), (0,5)]."""

        try:
            vertices_input = simpledialog.askstring(
                "Input",
                "Enter the vertices in the form [(x1,y1), (x2,y2), ...]:",
            )

            if vertices_input is None:
                messagebox.showwarning("Cancelled", "Room creation was cancelled.")
                return

            vertices = eval(vertices_input)

            if not isinstance(vertices, list) or not all(
                isinstance(v, tuple) and len(v) == 2 for v in vertices
            ):
                raise ValueError("Invalid format")

            self.room = self.simulation.add_room(
                f"{len(vertices)}-shaped Room", vertices
            )

            self.draw_room(vertices)

            if self.add_mic_button is None:
                self.add_mic_button = tk.Button(
                    self.left_frame, text="Add Microphone", command=self.add_microphone
                )
                self.add_mic_button.pack()

        except (ValueError, SyntaxError):
            messagebox.showerror(
                "Invalid Input",
                "Please enter valid vertices in the form [(x1,y1), (x2,y2), ...].",
            )

    def draw_room(self, vertices):
        """Draw the room inside a fixed square canvas, scaled and centered with padding."""

        if self.canvas:
            self.canvas.destroy()

        canvas_size = 500
        padding = 50

        self.canvas = tk.Canvas(
            self.left_frame, bg="white", width=canvas_size, height=canvas_size
        )
        self.canvas.pack(pady=10, expand=True)

        max_x = max(x for x, y in vertices)
        max_y = max(y for x, y in vertices)

        scale_x = (canvas_size - 2 * padding) / max_x
        scale_y = (canvas_size - 2 * padding) / max_y
        self.scale = min(scale_x, scale_y)

        self.offset_x = (canvas_size - max_x * self.scale) / 2
        self.offset_y = (canvas_size - max_y * self.scale) / 2

        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]

            x1_scaled = x1 * self.scale + self.offset_x
            y1_scaled = y1 * self.scale + self.offset_y
            x2_scaled = x2 * self.scale + self.offset_x
            y2_scaled = y2 * self.scale + self.offset_y

            self.canvas.create_line(
                x1_scaled, y1_scaled, x2_scaled, y2_scaled, fill="black", width=2
            )

    def create_microphone(self):
        return {
            "microphone": None,
            "frame": None,
            "waveform_frame": None,
            "waveform_canvas": None,
            "select_button": None,
            "mute_button": None,
            "audio": None,
        }

    def add_microphone(self):
        """Ask for the x,y coordinates of the microphone and draw it on the canvas."""
        try:
            point = simpledialog.askstring(
                "Input",
                "Enter the coordinates of the microphone in the form (x,y):",
            )

            if point is None:
                messagebox.showwarning(
                    "Cancelled", "Microphone addition was cancelled."
                )
                return

            x, y = eval(point)

            microphone = self.create_microphone()
            self.microphones.append(microphone)

            microphone["microphone"] = self.room.add_microphone(x, y)

            x_scaled = x * self.scale + self.offset_x
            y_scaled = y * self.scale + self.offset_y

            self.canvas.create_oval(
                x_scaled - 5, y_scaled - 5, x_scaled + 5, y_scaled + 5, fill="green"
            )

            self.canvas.create_text(
                x_scaled, y_scaled - 10, text=f"Microphone {(x, y)}", fill="green"
            )

            self.create_microphone_control_element(microphone)

        except (ValueError, SyntaxError):
            messagebox.showerror(
                "Invalid Input", "Please enter valid coordinates for the microphone."
            )

    def create_microphone_control_element(self, microphone):
        """Create a complex control element on the right side of the GUI."""

        microphone["frame"] = tk.Frame(
            self.right_frame, padx=10, pady=10, bd=2, relief="solid"
        )
        microphone["frame"].pack(fill=tk.X)

        microphone["waveform_frame"] = tk.Frame(microphone["frame"])

        microphone["select_button"] = tk.Button(
            microphone["frame"],
            text="Audio File",
            fg="black",
            command=lambda: self.select_file(microphone),
        )
        microphone["select_button"].pack()

        microphone["mute_button"] = tk.Button(
            microphone["frame"], text="Mute", bg="white", fg="black"
        )
        microphone["mute_button"].pack()

        microphone["waveform_frame"].pack()

    def select_file(self, microphone):
        """Open a file dialog and select an audio file."""

        file_path = filedialog.askopenfilename()
        audio = Audio(filepath=file_path)
        audio.load_audio_file()
        microphone["audio"] = audio
        self.plot_waveform(microphone)

        if not self.play_button.winfo_ismapped():
            self.play_button.pack()

    def play_audio(self):
        """Play all unmuted audio files."""
        for microphone in self.microphones:
            if microphone["audio"]:
                microphone["audio"].play()

    def plot_waveform(self, microphone):
        """Plot the waveform inside the Tkinter GUI in the microphone's waveform frame."""
        audio = microphone["audio"]
        audio_signal = audio.get_audio_signal()

        if audio_signal is None or len(audio_signal) == 0:
            raise ValueError("Audio signal is empty or not loaded properly.")

        figure = plt.Figure(figsize=(10, 2), dpi=100)
        ax = figure.add_subplot(111)

        ax.plot(audio_signal)
        ax.set_title("Waveform")
        ax.set_ylabel("Amplitude")
        ax.set_xlabel("Time")

        if microphone["waveform_canvas"]:
            microphone["waveform_canvas"].get_tk_widget().destroy()

        microphone["waveform_canvas"] = FigureCanvasTkAgg(
            figure, microphone["waveform_frame"]
        )
        microphone["waveform_canvas"].get_tk_widget().pack(pady=5, expand=True)

        microphone["waveform_canvas"].draw()

    def plot_spectrogram(self):
        """Plot the spectrogram inside the Tkinter GUI."""
        audio = Audio(filepath="examples/example_audio/pi1_audio.wav")
        audio.load_audio_file()

        audio_signal = audio.get_audio_signal()
        if audio_signal is None or len(audio_signal) == 0:
            raise ValueError("Audio signal is empty or not loaded properly.")

        figure = plt.Figure(figsize=(10, 6), dpi=100)
        ax = figure.add_subplot(111)

        spec = ax.specgram(
            audio_signal, NFFT=1024, Fs=audio.sample_rate, noverlap=512, cmap="inferno"
        )
        ax.set_title("Spectrogram of Audio Signal")
        ax.set_ylabel("Frequency [Hz]")
        ax.set_xlabel("Time [s]")

        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()

        self.plot_canvas = FigureCanvasTkAgg(figure, self.right_frame)
        self.plot_canvas.get_tk_widget().pack(pady=10, expand=True)

        self.plot_canvas.draw()

    def run(self):
        """Start the Tkinter main loop."""
        self.root.mainloop()
