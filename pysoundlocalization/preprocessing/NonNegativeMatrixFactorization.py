"""
This script demonstrates the NMF algorithm for separating audio signals.

Original code by Zahra Benslimane (2023).
Source: https://github.com/ZahraBenslimane/SoundSourceSeparation_usingNMF

Adapted as part of a project for sound localization.
"""

from pysoundlocalization.core.Environment import Environment
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.visualization.audio_wave_plot import audio_wave_plot
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import librosa


class NonNegativeMatrixFactorization:
    def __init__(
        self,
        number_of_sources_to_extract: int = 1,
        sample_rate: int = 44100,
        frame: int = 512,
        hop: int = 256,
        epsilon: float = 1e-10,
    ):
        """
        Initialize the Non-Negative Matrix Factorization (NMF) class with user-defined or default parameters.

        Parameters:
        - number_of_sources_to_extract (int): The number of audio sources to extract (default: 1).
        - sample_rate (int): Sampling rate of the audio data, in Hz (default: 44100 Hz).
        - frame (int): Size of each audio frame for STFT (default: 512).
        - hop (int): Hop size (overlap) between frames for STFT (default: 256).
        - epsilon (float): A small constant to prevent division by zero or log errors (default: 1e-10).

        Attributes:
        - __S (int): Number of sources to extract (set from `number_of_sources_to_extract`).
        - __FRAME (int): Frame size for processing (set from `frame`).
        - __HOP (int): Hop size for processing (set from `hop`).
        - __SR (int): Sampling rate (set from `sample_rate`).
        - __EPSILON (float): Small constant for numerical stability (set from `epsilon`).
        - __V (np.ndarray): Spectrogram matrix to be factorized (initialized to None).
        - __W (np.ndarray): Basis matrix of the factorization (initialized to None).
        - __H (np.ndarray): Activation matrix of the factorization (initialized to None).
        - __D (np.ndarray): Distance or cost matrix (initialized to None).
        - __cost_function (str): Cost function for NMF optimization (initialized to None).
        - __filtered_spectrograms (list): List to store filtered spectrograms (initialized to None).
        - __reconstructed_sounds (list): List to store reconstructed audio data (initialized to None).

        This class provides flexibility for audio source separation or matrix decomposition tasks.
        """
        self.__FRAME = frame
        self.__HOP = hop
        self.__SR = sample_rate
        self.__EPSILON = epsilon
        self.__S = number_of_sources_to_extract
        self.__V = None
        self.__K = None
        self.__N = None
        self.__W = None
        self.__H = None
        self.__D = None
        self.__cost_function = None

        # Store relevant results of NFM for later access (e.g. visualizations)
        self.__filtered_spectrograms = None
        self.__reconstructed_sounds = None

    def run_for_single_audio(
        self, audio: Audio, visualize_results: bool = False
    ) -> list[Audio]:
        """
        Run NFM for a single audio file.

        Args:
            audio (Audio): The audio to run nfm for.
            visualize_results (bool): Whether to visualize intermediate results.
        """
        audio_signals = self.__run(audio=audio, visualize_results=visualize_results)
        nfm_audio = []
        for audio_signal in audio_signals:
            nfm_audio.append(
                Audio(
                    audio_signal=audio_signal,
                    sample_rate=audio.get_sample_rate(),
                )
            )
        return nfm_audio

    def run_for_single_audio_signal(
        self,
        audio_signal: np.ndarray,
        sample_rate: int,
        visualize_results: bool = False,
    ) -> list[np.ndarray]:
        """
        Run NFM for a single audio signal of type ndarray.

        Args:
            audio_signal (np.ndarray): The audio signal to run nfm for.
            sample_rate (int): Sampling rate of the audio signal, in Hz.
            visualize_results (bool): Whether to visualize intermediate results.
        """
        return self.__run(
            audio=Audio(audio_signal=audio_signal, sample_rate=sample_rate),
            visualize_results=visualize_results,
        )

    def run_for_environment(
        self, environment: Environment, visualize_results: bool = False
    ):
        """
        Runs NFM on all audio files in an environment associated with a mic while preserving the splitting order.

        NFM does not guarantee the order of the split audio, which is problematic when multiple audio signals are split
        independently of each other. This is the case in a traditional for loop that runs NFM on each audio file.

        To solve the issue, the audio files are concatenated first into a single audio file before running NFM.
        Afterward, the reconstructed sound signal is split back into its audio parts, one for each mic.

        Args:
            environment (Environment): The environment to run nfm for.
            visualize_results (bool): Whether to visualize intermediate results.

        Returns:
           A dictionary mapping each microphone to a list of updated Audio objects.
        """

        print("Running NMF for all audio signals in the environment...")

        mics = environment.get_mics()
        if not mics:
            raise ValueError("No microphones found in the environment.")

        audios = []
        reference_sample_rate = None
        reference_num_samples = None

        for mic in mics:
            audio = mic.get_audio()
            if audio is not None:
                sample_rate = audio.get_sample_rate()
                num_samples = audio.get_num_samples()

                if reference_sample_rate is None or reference_num_samples is None:
                    reference_sample_rate = sample_rate
                    reference_num_samples = num_samples
                else:
                    if sample_rate != reference_sample_rate:
                        raise ValueError(
                            f"Sample rate mismatch detected! All audio must have same sample rate."
                        )
                    if num_samples != reference_num_samples:
                        raise ValueError(
                            f"Number of samples mismatch detected! All audio must have same number of samples."
                        )
                audios.append(audio.get_audio_signal_unchunked())
            else:
                print(
                    f"Warning: No audio data found for microphone {mic.get_name()}. Skipping."
                )

        if not audios:
            raise ValueError("No valid audio data found in the environment.")

        # Run NMF on the concatenated audio signal (small trick to preserve splitting order across audio signals)
        concatenated_audio = np.concatenate(audios)

        if visualize_results:
            audio_wave_plot(
                audio_signal=concatenated_audio, sample_rate=reference_sample_rate
            )

        nmf_result = self.run_for_single_audio_signal(
            concatenated_audio, visualize_results
        )

        if visualize_results:
            for audio_signal in nmf_result:
                audio_wave_plot(
                    audio_signal=audio_signal, sample_rate=reference_sample_rate
                )

        # Split the initially concatenated signals back and add the audio to the respective mics
        # Ensures that the order of NMF splitting is the same for all mic audio.
        results = {mic: [] for mic in mics}
        for nmf_signal in nmf_result:
            # The reconstructed nmf_signal is possibly shorter than the original audio.
            # Thus, ensure that the proportion remains correct when splitting back into the respective audios for each mic.
            length_ratio = len(nmf_signal) / len(concatenated_audio)
            processed_lengths = [int(len(audio) * length_ratio) for audio in audios]
            cumulative_lengths = np.cumsum(processed_lengths)

            start_idx = 0
            for mic, end_idx in zip(mics, cumulative_lengths):
                split_signal = nmf_signal[start_idx:end_idx]
                audio_with_new_signal = Audio(
                    audio_signal=split_signal,
                    sample_rate=self.__SR,
                )
                results[mic].append(audio_with_new_signal)
                start_idx = end_idx

        print("NMF completed for all audio signals in the environment.")

        return results

    def __run(self, audio: Audio, visualize_results: bool = False):
        """
        Orchestrates the nfm algorithm.

        Args:
            audio (Audio): The audio to run nfm for.
            visualize_results (bool): Set to true if all intermediate results should be visualized.
        """
        sound_stft = librosa.stft(
            audio.get_audio_signal_unchunked(),
            n_fft=self.__FRAME,
            hop_length=self.__HOP,
        )
        sound_sftf_magnitude = np.abs(sound_stft)
        sound_stft_angle = np.angle(sound_stft)

        self.__V = sound_sftf_magnitude + self.__EPSILON

        beta = 2
        self.__W, self.__H, self.__cost_function = self.__NMF(
            V=self.__V,
            S=self.__S,
            beta=beta,
            threshold=0.05,
            MAXITER=5000,
            display=visualize_results,
            displayEveryNiter=1000,
        )

        filtered_spectrograms = self.__generate_filtered_spectrograms()
        reconstructed_sounds = self.__reconstruct_sounds(
            filtered_spectrograms=filtered_spectrograms,
            sound_stft_angle=sound_stft_angle,
        )

        if visualize_results:
            self.visualize_wave_form(reconstructed_sounds=reconstructed_sounds)
            self.visualize_filtered_spectrograms(
                filtered_spectrograms=filtered_spectrograms
            )

        return reconstructed_sounds

    def __NMF(
        self,
        V,
        S,
        beta=2,
        threshold=0.05,
        MAXITER=5000,
        display=False,
        displayEveryNiter=None,
    ):
        """
        inputs :
        --------

            V         : Mixture signal : |TFST|
            S         : The number of sources to extract
            beta      : Beta divergence considered, default=2 (Euclidean)
            threshold : Stop criterion
            MAXITER   : The number of maximum iterations, default=1000
            display   : Display plots during optimization :
            displayEveryNiter : only display last iteration


        outputs :
        ---------

            W : dictionary matrix [KxS], W>=0
            H : activation matrix [SxN], H>=0
            cost_function : the optimised cost function over iterations

        Algorithm :
        -----------

        1) Randomly initialize W and H matrices
        2) Multiplicative update of W and H
        3) Repeat step (2) until convergence or after MAXITER


        """
        counter = 0
        self.__cost_function = []
        beta_divergence = 1

        self.__K, self.__N = np.shape(V)

        # Initialisation of W and H matrices : The initialization is generally random
        self.__W = np.abs(np.random.normal(loc=0, scale=2.5, size=(self.__K, S)))
        self.__H = np.abs(np.random.normal(loc=0, scale=2.5, size=(S, self.__N)))

        # Plotting the first initialization
        if display == True:
            self._plot_NMF_iter(beta=beta, iteration=counter)

        while beta_divergence >= threshold and counter <= MAXITER:
            # Update of W and H
            self.__H *= (self.__W.T @ (((self.__W @ self.__H) ** (beta - 2)) * V)) / (
                self.__W.T @ ((self.__W @ self.__H) ** (beta - 1)) + 10e-10
            )
            self.__W *= (((self.__W @ self.__H) ** (beta - 2) * V) @ self.__H.T) / (
                (self.__W @ self.__H) ** (beta - 1) @ self.__H.T + 10e-10
            )

            # Compute cost function
            beta_divergence = self.__divergence(V=V, beta=2)
            self.__cost_function.append(beta_divergence)

            if display == True and counter % displayEveryNiter == 0:
                self._plot_NMF_iter(beta=beta, iteration=counter)

            counter += 1

        if counter - 1 == MAXITER:
            print(f"Stop after {MAXITER} iterations.")
        else:
            print(f"Convergence after {counter-1} iterations.")

        return self.__W, self.__H, self.__cost_function

    def __divergence(self, V, beta=2):
        """
        beta = 2 : Euclidean cost function
        beta = 1 : Kullback-Leibler cost function
        beta = 0 : Itakura-Saito cost function
        """
        if beta == 0:
            return np.sum(
                V / (self.__W @ self.__H) - math.log10(V / (self.__W @ self.__H)) - 1
            )

        if beta == 1:
            return np.sum(
                self.__V * math.log10(V / (self.__W @ self.__H))
                + (self.__W @ self.__H - V)
            )

        if beta == 2:
            return 1 / 2 * np.linalg.norm(self.__W @ self.__H - V)

    def __reconstruct_sounds(
        self, filtered_spectrograms: list[float], sound_stft_angle: np.ndarray
    ):
        """
        Reconstruct sounds from filtered spectrograms.

        Args:
            filtered_spectrograms (list): List of filtered spectrograms for each source.
            sound_stft_angle (ndarray): The phase angle of the original STFT.

        Returns:
            list: List of reconstructed audio signals.
        """
        reconstructed_sounds = []
        for i in range(self.__S):
            reconstruct = filtered_spectrograms[i] * np.exp(1j * sound_stft_angle)
            new_sound = librosa.istft(
                reconstruct, n_fft=self.__FRAME, hop_length=self.__HOP
            )
            reconstructed_sounds.append(new_sound)
        self.__reconstructed_sounds = reconstructed_sounds
        return reconstructed_sounds

    def __generate_filtered_spectrograms(self):
        """
        Generate filtered spectrograms for each audio source.

        Returns:
            list: A list of filtered spectrograms for each source.
        """
        filtered_spectrograms = []
        for i in range(self.__S):
            filtered_spectrogram = (
                self.__W[:, [i]]
                @ self.__H[[i], :]
                / (self.__W @ self.__H + self.__EPSILON)
                * self.__V
            )
            filtered_spectrograms.append(filtered_spectrogram)
        self.__filtered_spectrograms = filtered_spectrograms
        return filtered_spectrograms

    def visualize_filtered_spectrograms(
        self, filtered_spectrograms: list[float] | None = None
    ) -> None:
        """
        Visualize frequency masks of audio sources. Must either run NMF beforehand or provide the filtered_spectrograms.

        Args:
            filtered_spectrograms (list): List of filtered spectrograms for each source.
        """
        # Use the provided parameter if available, otherwise fall back to the stored value
        if filtered_spectrograms is None:
            if self.__filtered_spectrograms is None:
                raise ValueError(
                    "No filtered_spectrograms provided or available in object."
                )
            filtered_spectrograms = self.__filtered_spectrograms

        f, axs = plt.subplots(nrows=1, ncols=self.__S, figsize=(20, 5))
        for i, filtered_spectrogram in enumerate(filtered_spectrograms):
            axs[i].set_title(f"Frequency Mask of Audio Source s = {i + 1}")
            # Convert to decibel scale for visualization
            D = librosa.amplitude_to_db(filtered_spectrogram, ref=np.max)
            # Display the spectrogram
            librosa.display.specshow(
                D,
                y_axis="hz",
                sr=self.__SR,
                hop_length=self.__HOP,
                x_axis="time",
                cmap=matplotlib.cm.jet,
                ax=axs[i],
            )
        plt.show()

    def visualize_wave_form(
        self, reconstructed_sounds: list[np.ndarray] | None = None
    ) -> None:
        """
        Visualize waveforms of reconstructed audio signals. Must either run NMF beforehand or provide the reconstructed sounds.

        Args:
            reconstructed_sounds (list): List of reconstructed audio signals.
        """
        # Use the provided parameter if available, otherwise fall back to the stored value
        if reconstructed_sounds is None:
            if self.__reconstructed_sounds is None:
                raise ValueError(
                    "No reconstructed_sounds provided or available in the object."
                )
            reconstructed_sounds = self.__reconstructed_sounds

        colors = ["r", "g", "b", "c"]
        fig, ax = plt.subplots(nrows=self.__S, ncols=1, sharex=True, figsize=(10, 8))
        for i in range(self.__S):
            librosa.display.waveshow(
                reconstructed_sounds[i],
                sr=self.__SR,
                color=colors[i],
                ax=ax[i],
                label=f"Source {i}",
                axis="time",
            )
            ax[i].set(xlabel="Time [s]")
            ax[i].legend()
        plt.show()

    def _plot_NMF_iter(self, beta, iteration=None):

        f = plt.figure(figsize=(4, 4))
        f.suptitle(
            f"NMF Iteration {iteration}, for beta = {beta}",
            fontsize=8,
        )

        # definitions for the axes
        V_plot = plt.axes([0.35, 0.1, 1, 0.6])
        H_plot = plt.axes([0.35, 0.75, 1, 0.15])
        W_plot = plt.axes([0.1, 0.1, 0.2, 0.6])

        self.__D = librosa.amplitude_to_db(self.__W @ self.__H, ref=np.max)

        librosa.display.specshow(
            self.__W,
            y_axis="hz",
            sr=self.__SR,
            hop_length=self.__HOP,
            x_axis="time",
            cmap=matplotlib.cm.jet,
            ax=W_plot,
        )
        librosa.display.specshow(
            self.__H,
            y_axis="hz",
            sr=self.__SR,
            hop_length=self.__HOP,
            x_axis="time",
            cmap=matplotlib.cm.jet,
            ax=H_plot,
        )
        librosa.display.specshow(
            self.__D,
            y_axis="hz",
            sr=self.__SR,
            hop_length=self.__HOP,
            x_axis="time",
            cmap=matplotlib.cm.jet,
            ax=V_plot,
        )

        W_plot.set_title("Dictionnary W", fontsize=10)
        H_plot.set_title("Temporal activations H", fontsize=10)

        W_plot.axes.get_xaxis().set_visible(False)
        H_plot.axes.get_xaxis().set_visible(False)
        V_plot.axes.get_yaxis().set_visible(False)
