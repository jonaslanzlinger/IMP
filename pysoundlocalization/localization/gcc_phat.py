"""
This script demonstrates the GCC-PHAT algorithm for estimating time delays between signals.

Original code by Yihui Xiong (2017), licensed under the Apache License, Version 2.0.
Source: https://github.com/xiongyihui/tdoa/blob/master/gcc_phat.py
License: https://www.apache.org/licenses/LICENSE-2.0

Adapted as part of a project for sound localization.
"""

import numpy as np


def gcc_phat(
    sig: np.ndarray,
    refsig: np.ndarray,
    fs: int = 1,
    max_tau: float | None = None,
    interp: int = 16,
) -> tuple[float, np.ndarray]:
    """
    Computes the time delay estimation (tau) between a signal `sig` and a reference signal `refsig`
    using the Generalized Cross Correlation - Phase Transform (GCC-PHAT) method.

    Args:
        sig (np.ndarray): The input signal.
        refsig (np.ndarray): The reference signal to compare against.
        fs (int): The sampling rate of the signals in Hz. Defaults to 1.
        max_tau (float | None): Maximum allowable time delay in seconds. Limits the search window. Defaults to None.
        interp (int): Interpolation factor to improve precision. Defaults to 16.

    Returns:
        tuple[float, np.ndarray]: A tuple containing:
            - tau (float): The estimated time delay between the signals in seconds.
            - cc (np.ndarray): The cross-correlation result array.
    """
    # make sure the length for the FFT is larger or equal than len(sig) + len(refsig)
    n = sig.shape[0] + refsig.shape[0]

    # Generalized Cross Correlation Phase Transform
    SIG = np.fft.rfft(sig, n=n)
    REFSIG = np.fft.rfft(refsig, n=n)
    R = SIG * np.conj(REFSIG)

    cc = np.fft.irfft(R / np.abs(R), n=(interp * n))

    max_shift = int(interp * n / 2)
    if max_tau:
        max_shift = np.minimum(int(interp * fs * max_tau), max_shift)

    cc = np.concatenate((cc[-max_shift:], cc[: max_shift + 1]))

    # find max cross correlation index
    shift = np.argmax(cc) - max_shift

    # Sometimes, there is a 180-degree phase difference between the two microphones.
    # shift = np.argmax(np.abs(cc)) - max_shift

    tau = shift / float(interp * fs)

    return tau, cc


def main():
    """
    Simple demonstration of estimating the time offset (or delay) between two signals using the
    Generalized Cross-Correlation with Phase Transform (GCC-PHAT) algorithm
    """
    refsig = np.linspace(1, 10, 10)

    for i in range(0, 10):
        sig = np.concatenate((np.linspace(0, 0, i), refsig, np.linspace(0, 0, 10 - i)))
        offset, _ = gcc_phat(sig, refsig)
        print(offset)


if __name__ == "__main__":
    main()
