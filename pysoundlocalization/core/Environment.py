from datetime import timedelta
from itertools import combinations
import numpy as np
import pysoundlocalization.config as config
from pysoundlocalization.localization.multilateration import multilaterate_by_tdoa_pairs
from pysoundlocalization.core.Microphone import Microphone
from pysoundlocalization.visualization.environment_plot import environment_plot
from pysoundlocalization.localization.tdoa_gcc_phat import (
    get_all_tdoa_of_chunk_index_by_gcc_phat,
)
from pysoundlocalization.localization.tdoa_threshold import (
    get_all_tdoa_of_chunk_index_by_threshold,
)


class Environment:
    def __init__(
        self,
        name: str,
        vertices: list[tuple[float, float]],
        sound_speed: float = config.DEFAULT_SOUND_SPEED,
    ):
        """
        Initialize an Environment instance with a name, vertices defining the environment shape.

        Args:
            name (str): The name of the environment.
            vertices (list[tuple[float, float]]): List of (x, y) coordinates defining the environment's shape.
            sound_speed (float): The speed of sound in m/s. Defaults to config.DEFAULT_SOUND_SPEED.
        """
        self.__sound_speed = sound_speed
        self.__name = name
        self.__vertices = (
            vertices  # List of (x, y) coordinates for the environment's shape
        )
        self.__mics: list[Microphone] = []
        self.__sound_source_position: tuple[float, float] | None = None

    def add_microphone(
        self, x: float, y: float, name: str | None = None
    ) -> Microphone | None:
        """
        Add a microphone at the specified coordinates if it is within environment boundaries and not duplicated.

        Args:
            x (float): X-coordinate of the microphone position.
            y (float): Y-coordinate of the microphone position.
            name (str): The name of the microphone.

        Returns:
            Microphone | None: The added Microphone object if successful, otherwise None.
        """
        # Ensure that no mic already exists at given coordinates
        for mic in self.__mics:
            if mic.get_x == x and mic.get_y == y:
                print(f"A microphone already exists at position ({x}, {y})")
                return None

        if self.is_within_environment(x=x, y=y):
            mic = Microphone(x=x, y=y, name=name)
            self.__mics.append(mic)
            print(f"Microphone added at position ({x}, {y})")
            return mic
        else:
            print(f"Microphone at ({x}, {y}) is outside the environment bounds!")

    def add_sound_source_position(self, x: float, y: float) -> None:
        """
        Add coordinates of measured sound source. To goal is to estimate this position.

        Args:
            x (float): X-coordinate of the sound source.
            y (float): Y-coordinate of the sound source.
        """
        self.__sound_source_position = (x, y)

    def is_within_environment(self, x: float, y: float) -> bool:
        """
        Check if a point (x, y) is inside the environment's polygon defined by its vertices.

        Implementation of the ray-casting algorithm to solve the point-in-polygon problem.

        Args:
            x (float): X-coordinate of the point to check.
            y (float): Y-coordinate of the point to check.

        Returns:
            bool: True if the point is inside the polygon, False otherwise.
        """
        num_vertices = len(self.__vertices)
        inside = False

        # Iterate over each edge of the polygon
        for i in range(num_vertices):
            # Get current vertex and the next vertex (wrapping around at the end)
            x1, y1 = self.__vertices[i]
            x2, y2 = self.__vertices[(i + 1) % num_vertices]

            # Check if the ray crosses the edge
            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside

        return inside

    def get_max_tau(self) -> float:
        """
        Calculate the maximum time delay (tau) based on the distance between microphones and the sound speed.

        Returns:
            float: Maximum time delay (tau) in seconds.
        """
        if len(self.__mics) < 2:
            raise ValueError(
                "At least two microphones are required to calculate max_tau."
            )

        # Find the max distance between any two microphones
        max_mic_distance = max(
            np.linalg.norm(
                np.array(mic1.get_position()) - np.array(mic2.get_position())
            )
            for mic1, mic2 in combinations(self.__mics, 2)
        )

        return max_mic_distance / self.__sound_speed

    def get_lowest_sample_rate(self) -> int:
        """
        Get the lowest sample rate of all microphones in the environment.

        Returns:
            int: The lowest sample rate of all microphones in the environment.
        """
        return min(mic.get_audio().get_sample_rate() for mic in self.__mics)

    def get_min_num_samples(self) -> int:
        """
        Get the minimum number of samples of all audios in the environment.

        Returns:
            int: The minimum number of samples of all audios in the environment.
        """
        return min(mic.get_audio().get_num_samples() for mic in self.__mics)

    def get_sample_rate(self) -> int:
        """
        Get the sample rate of the environment. If there are different
        sample rates for the microphones, an exception is raised.

        Returns:
            int: The sample rate of the environment.
        """
        sample_rates = [mic.get_audio().get_sample_rate() for mic in self.__mics]
        if len(set(sample_rates)) > 1:
            raise ValueError(
                "Different sample rates for microphones in the environment."
            )
        return sample_rates[0]

    def chunk_audio_signals_by_duration(
        self, chunk_duration: timedelta | None = timedelta(milliseconds=1000)
    ) -> None:
        """
        Chunk the audio signals of all microphones into chunks of a specified duration.

        Args:
            chunk_duration (timedelta | None): The duration of each chunk. Defaults to 1000 ms.
        """
        for mic in self.__mics:
            mic.get_audio().chunk_audio_signal_by_duration(
                chunk_duration=chunk_duration
            )

    def chunk_audio_signals_by_samples(self, chunk_samples: int) -> None:
        """
        Chunk the audio signals of all microphones into chunks of specified number of samples.

        Args:
            chunk_samples (int): The number of samples in each chunk. The sample rate of the audio defines how many samples are in a given timeframe.
        """
        for mic in self.__mics:
            mic.get_audio().chunk_audio_signal_by_samples(chunk_samples=chunk_samples)

    def localize(
        self,
        algorithm: str = "threshold",
        threshold: float | None = 0.5,
        debug: bool | None = False,
    ) -> dict:
        """
        Localizes the sound source of the loaded audio signals.

        Args:
            algorithm (str): The algorithm to use for computing the TDoA values.
            threshold (float): The threshold for the audio signal.
            debug (bool): Print debug information if True.

        Returns:
            dict: A dictionary containing the estimated (x, y) coordinates at given sample indices of the sound source
        """

        # To localize, at least two microphones are needed
        if len(self.get_mics()) < 2:
            raise ValueError("At least two microphones are needed to localize.")

        num_chunks = len(self.get_mics()[0].get_audio().get_audio_signal_chunked())
        chunk_size = int(self.get_mics()[0].get_audio().get_num_samples() / num_chunks)

        dict = {}
        for i in range(num_chunks):
            tdoa_pairs_of_chunk = None

            if algorithm == "gcc_phat":
                tdoa_pairs_of_chunk = get_all_tdoa_of_chunk_index_by_gcc_phat(
                    environment=self, chunk_index=i, threshold=threshold, debug=debug
                )
            elif algorithm == "threshold":
                tdoa_pairs_of_chunk = get_all_tdoa_of_chunk_index_by_threshold(
                    environment=self, chunk_index=i, threshold=threshold, debug=debug
                )

            if tdoa_pairs_of_chunk is None:
                dict[f"{i * chunk_size}"] = None
                continue

            sound_source_position = multilaterate_by_tdoa_pairs(
                tdoa_pairs=tdoa_pairs_of_chunk
            )

            dict[f"{i * chunk_size}"] = sound_source_position

        return dict

    def visualize(self) -> None:
        """
        Visualizes the environment layout, and microphones using Matplotlib.
        """
        environment_plot(environment=self)

    def get_sound_speed(self) -> float:
        """
        Get the speed of sound in the environment.

        Returns:
            float: The speed of sound in m/s of the environment.
        """
        return self.__sound_speed

    def set_sound_speed(self, speed: float) -> None:
        """
        Set the speed of sound in the environment.

        Args:
            speed (float): The speed of sound in m/s.
        """
        self.__sound_speed = speed

    def get_name(self) -> str:
        """
        Get the name of the environment.

        Returns:
            str: The name of the environment.
        """
        return self.__name

    def set_name(self, name: str) -> None:
        """
        Set the name of the environment.

        Args:
            name (str): The name of the environment.
        """
        self.__name = name

    def get_vertices(self) -> list[tuple[float, float]]:
        """
        Get the vertices of the environment.

        Returns:
            list[tuple[float, float]]: List of (x, y) coordinates defining the environment's shape.
        """
        return self.__vertices

    def set_vertices(self, vertices: list[tuple[float, float]]) -> None:
        """
        Set the vertices of the environment.

        Args:
            vertices (list[tuple[float, float]]): List of (x, y) coordinates defining the environment's shape.
        """
        self.__vertices = vertices

    def get_mics(self) -> list[Microphone]:
        """
        Get the microphones in the environment.

        Returns:
            list[Microphone]: List of Microphone objects in the environment.
        """
        return self.__mics

    def set_mics(self, mics: list[Microphone]) -> None:
        """
        Set the microphones in the environment.

        Args:
            mics (list[Microphone]): List of Microphone objects in the environment.
        """
        self.__mics = mics

    def get_sound_source_position(self) -> tuple[float, float] | None:
        """
        Get the coordinates of the measured sound source.

        Returns:
            tuple[float, float] | None: The (x, y) coordinates of the measured sound source if available, otherwise None.
        """
        return self.__sound_source_position

    def set_sound_source_position(
        self, sound_source_position: tuple[float, float]
    ) -> None:
        """
        Set the coordinates of the measured sound source.

        Args:
            sound_source_position (tuple[float, float]): The (x, y) coordinates of the measured sound source.
        """
        self.__sound_source_position = sound_source_position
