from core.Audio import Audio
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import librosa


class NonNegativeMatrixFactorization:
    def __init__(self):
        self.FRAME = 512
        self.HOP = 256
        self.SR = 44100
        self.EPSILON = 1e-10
        self.V = None
        self.K = None
        self.N = None
        self.S = 2
        self.W = None
        self.H = None
        self.cost_function = None

    def run(self, audio: Audio):

        sound_stft = librosa.stft(
            audio.get_audio_signal(),
            n_fft=self.FRAME,
            hop_length=self.HOP,
        )
        sound_sftf_magnitude = np.abs(sound_stft)
        sound_stft_angle = np.angle(sound_stft)

        self.V = sound_sftf_magnitude + self.EPSILON

        beta = 2
        self.W, self.H, self.cost_function = self.NMF(
            self.V,
            self.S,
            beta=beta,
            threshold=0.05,
            MAXITER=5000,
            display=True,
            displayEveryNiter=1000,
        )

        # After NMF, each audio source S can be expressed as a frequency mask over time
        f, axs = plt.subplots(nrows=1, ncols=self.S, figsize=(20, 5))
        filtered_spectrograms = []
        for i in range(self.S):
            axs[i].set_title(f"Frequency Mask of Audio Source s = {i+1}")
            # Filter eash source components
            WsHs = self.W[:, [i]] @ self.H[[i], :]
            filtered_spectrogram = (
                self.W[:, [i]]
                @ self.H[[i], :]
                / (self.W @ self.H + self.EPSILON)
                * self.V
            )
            # Compute the filtered spectrogram
            D = librosa.amplitude_to_db(filtered_spectrogram, ref=np.max)
            # Show the filtered spectrogram
            librosa.display.specshow(
                D,
                y_axis="hz",
                sr=self.SR,
                hop_length=self.HOP,
                x_axis="time",
                cmap=matplotlib.cm.jet,
                ax=axs[i],
            )

            filtered_spectrograms.append(filtered_spectrogram)

        reconstructed_sounds = []
        for i in range(self.S):
            reconstruct = filtered_spectrograms[i] * np.exp(1j * sound_stft_angle)
            new_sound = librosa.istft(
                reconstruct, n_fft=self.FRAME, hop_length=self.HOP
            )
            reconstructed_sounds.append(new_sound)

        # Plotting the waveform
        colors = ["r", "g", "b", "c"]
        fig, ax = plt.subplots(nrows=self.S, ncols=1, sharex=True, figsize=(10, 8))
        for i in range(self.S):
            librosa.display.waveshow(
                reconstructed_sounds[i],
                sr=self.SR,
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
            return np.sum(V / (self.W @ self.H) - math.log10(V / (self.W @ self.H)) - 1)

        if beta == 1:
            return np.sum(
                self.V * math.log10(V / (self.W @ self.H)) + (self.W @ self.H - V)
            )

        if beta == 2:
            return 1 / 2 * np.linalg.norm(self.W @ self.H - V)

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

        self.D = librosa.amplitude_to_db(self.W @ self.H, ref=np.max)

        librosa.display.specshow(
            self.W,
            y_axis="hz",
            sr=self.SR,
            hop_length=self.HOP,
            x_axis="time",
            cmap=matplotlib.cm.jet,
            ax=W_plot,
        )
        librosa.display.specshow(
            self.H,
            y_axis="hz",
            sr=self.SR,
            hop_length=self.HOP,
            x_axis="time",
            cmap=matplotlib.cm.jet,
            ax=H_plot,
        )
        librosa.display.specshow(
            self.D,
            y_axis="hz",
            sr=self.SR,
            hop_length=self.HOP,
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
        self.cost_function = []
        beta_divergence = 1

        self.K, self.N = np.shape(V)

        # Initialisation of W and H matrices : The initialization is generally random
        self.W = np.abs(np.random.normal(loc=0, scale=2.5, size=(self.K, S)))
        self.H = np.abs(np.random.normal(loc=0, scale=2.5, size=(S, self.N)))

        # Plotting the first initialization
        if display == True:
            self.plot_NMF_iter(beta, counter)

        while beta_divergence >= threshold and counter <= MAXITER:

            # Update of W and H
            self.H *= (self.W.T @ (((self.W @ self.H) ** (beta - 2)) * V)) / (
                self.W.T @ ((self.W @ self.H) ** (beta - 1)) + 10e-10
            )
            self.W *= (((self.W @ self.H) ** (beta - 2) * V) @ self.H.T) / (
                (self.W @ self.H) ** (beta - 1) @ self.H.T + 10e-10
            )

            # Compute cost function
            beta_divergence = self.divergence(V, beta=2)
            self.cost_function.append(beta_divergence)

            if display == True and counter % displayEveryNiter == 0:
                self.plot_NMF_iter(beta, counter)

            counter += 1

        if counter - 1 == MAXITER:
            print(f"Stop after {MAXITER} iterations.")
        else:
            print(f"Convergeance after {counter-1} iterations.")

        return self.W, self.H, self.cost_function
