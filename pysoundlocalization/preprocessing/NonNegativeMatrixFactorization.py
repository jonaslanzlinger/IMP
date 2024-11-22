from pysoundlocalization.core.Environment import Environment
from pysoundlocalization.core.Audio import Audio
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import librosa


class NonNegativeMatrixFactorization:
    def __init__(self):
        self.__FRAME = 512
        self.__HOP = 256
        self.__SR = 44100
        self.__EPSILON = 1e-10
        self.__V = None
        self.__K = None
        self.__N = None
        self.__S = 2
        self.__W = None
        self.__H = None
        self.__D = None
        self.__cost_function = None

    def run_for_single_audio(self, audio: Audio):
        """
        Run NFM for a single audio file.

        Args:
            audio (Audio): The audio to run nfm for.
        """
        return self.__run(audio)

    def run_for_single_audio_signal(self, audio_signal: np.ndarray):
        """
        Run NFM for a single audio signal of type ndarray.

        Args:
            audio_signal (np.ndarray): The audio signal to run nfm for.
        """
        return self.__run(Audio(audio_signal=audio_signal))

    def experimental_run_for_all_audio_in_environment(self, environment: Environment):
        """
        This method is experimental and may change in the future. Method requires advanced understanding and should not be used unless the behaviour is understood.

        Runs NFM on all audio files in an environment associated with a mic while preserving the splitting order.

        NFM does not guarantee the order of the split audio, which is problematic when multiple audio signals are split
        independently of each other. This is the case in a traditional for loop that runs NFM on each audio file.

        To solve the issue, the audio files are concatenated first into a single audio file before running NFM.
        Afterward, the reconstructed sound signal is split back into its audio parts, one for each mic.

        Args:
            environment (Environment): The environment to run nfm for.

        Returns:
           A dictionary mapping each microphone to a list of updated Audio objects.
        """
        mics = environment.get_mics()
        if not mics:
            raise ValueError("No microphones found in the environment.")

        # Collect relevant audio signals in environment and their lengths
        # TODO: all checks before doing the splitting, like do all audio have same sample rate, start timestamp, etc
        audios = []
        mic_audio_lengths = []
        for mic in mics:
            audio = mic.get_audio()
            if audio is not None:
                audio_signal = audio.get_unchunked_audio_signal()
                audios.append(audio_signal)
                mic_audio_lengths.append(len(audio_signal))
            else:
                print(
                    f"Warning: No audio data found for microphone {mic.get_name()}. Skipping."
                )

        if not audios:
            raise ValueError("No valid audio data found in the environment.")

        # Run NMF on the concatenated audio signal (small trick to preserve splitting order across audio signals)
        nmf_result = self.run_for_single_audio_signal(np.concatenate(audios))

        # Iterate through nmf_result, which returns a list of reconstructed_sounds
        # split first reconstructed sound and give one split to each mic respectively. repeat for the second.
        # Initialize results dictionary to store the split audio for each mic
        results = {mic: [] for mic in mics}
        cumulative_lengths = np.cumsum(mic_audio_lengths)
        # print(cumulative_lengths)
        # print(nmf_result[0])
        # print(nmf_result[1])
        # print(len(nmf_result[0]))
        # print(len(nmf_result[1]))

        # Iterate through the NMF results and split each reconstructed sound for each microphone
        for source_signal in nmf_result:
            start_idx = 0
            for mic, end_idx in zip(mics, cumulative_lengths):
                split_signal = source_signal[start_idx:end_idx]
                results[mic].append(Audio(audio_signal=split_signal))
                start_idx = end_idx

        return results

    def __run(self, audio: Audio):

        sound_stft = librosa.stft(
            audio.get_unchunked_audio_signal(),
            n_fft=self.__FRAME,
            hop_length=self.__HOP,
        )
        sound_sftf_magnitude = np.abs(sound_stft)
        sound_stft_angle = np.angle(sound_stft)

        self.__V = sound_sftf_magnitude + self.__EPSILON

        beta = 2
        self.__W, self.__H, self.__cost_function = self.NMF(
            self.__V,
            self.__S,
            beta=beta,
            threshold=0.05,
            MAXITER=5000,
            display=True,
            displayEveryNiter=1000,
        )

        # After NMF, each audio source S can be expressed as a frequency mask over time
        f, axs = plt.subplots(nrows=1, ncols=self.__S, figsize=(20, 5))
        filtered_spectrograms = []
        for i in range(self.__S):
            axs[i].set_title(f"Frequency Mask of Audio Source s = {i+1}")
            # Filter eash source components
            WsHs = self.__W[:, [i]] @ self.__H[[i], :]
            filtered_spectrogram = (
                self.__W[:, [i]]
                @ self.__H[[i], :]
                / (self.__W @ self.__H + self.__EPSILON)
                * self.__V
            )
            # Compute the filtered spectrogram
            D = librosa.amplitude_to_db(filtered_spectrogram, ref=np.max)
            # Show the filtered spectrogram
            librosa.display.specshow(
                D,
                y_axis="hz",
                sr=self.__SR,
                hop_length=self.__HOP,
                x_axis="time",
                cmap=matplotlib.cm.jet,
                ax=axs[i],
            )

            filtered_spectrograms.append(filtered_spectrogram)

        reconstructed_sounds = []
        for i in range(self.__S):
            reconstruct = filtered_spectrograms[i] * np.exp(1j * sound_stft_angle)
            new_sound = librosa.istft(
                reconstruct, n_fft=self.__FRAME, hop_length=self.__HOP
            )
            reconstructed_sounds.append(new_sound)

        # Plotting the waveform
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

        return reconstructed_sounds

    def divergence(self, V, beta=2):
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

    def plot_NMF_iter(self, beta, iteration=None):

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

    def NMF(
        self,
        V,
        S,
        beta=2,
        threshold=0.05,
        MAXITER=5000,
        display=True,
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
            self.plot_NMF_iter(beta, counter)

        while beta_divergence >= threshold and counter <= MAXITER:

            # Update of W and H
            self.__H *= (self.__W.T @ (((self.__W @ self.__H) ** (beta - 2)) * V)) / (
                self.__W.T @ ((self.__W @ self.__H) ** (beta - 1)) + 10e-10
            )
            self.__W *= (((self.__W @ self.__H) ** (beta - 2) * V) @ self.__H.T) / (
                (self.__W @ self.__H) ** (beta - 1) @ self.__H.T + 10e-10
            )

            # Compute cost function
            beta_divergence = self.divergence(V, beta=2)
            self.__cost_function.append(beta_divergence)

            if display == True and counter % displayEveryNiter == 0:
                self.plot_NMF_iter(beta, counter)

            counter += 1

        if counter - 1 == MAXITER:
            print(f"Stop after {MAXITER} iterations.")
        else:
            print(f"Convergeance after {counter-1} iterations.")

        return self.__W, self.__H, self.__cost_function
