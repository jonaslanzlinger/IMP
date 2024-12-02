import numpy as np
from pysoundlocalization.core.Environment import Environment
from pysoundlocalization.core.Audio import Audio
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.config import DEFAULT_SOUND_SPEED


def generate_audios(
    environment: Environment,
    sample_rate: int,
    source_sources: list[dict[int, tuple[float, float]]],
    background_noise: Audio | None = None,
    loudness_mix: list[float] | None = None,
    default_sound_duration: float = 0.3,
) -> Environment:
    """
    Helper function to generate audio signals based on an environment, and a dictionary
    containing a sample index along with the source position (x, y) for each source.

    Parameters:
    - environment (Environment): The environment containing room dimensions and microphones.
    - sample_rate (int): The sample rate of the audio signals.
    - source_sources (list[dict[int, tuple[float, float]]]):
        A list where each dictionary maps sample indices (start point) to source positions (x, y).
    - background_noise np.ndarray | None: Background noise to add to the audio signals.
    - loudness_mix (list[float] | None): List of loudness values to mix the audio signals with.
    - default_sound_duration (float): The default duration of the generated audio signals.

    Returns:
        - Environment: The environment with the generated audio signals updated.
    """

    # Count the number of source positions that do not have a custom audio signal
    n_default_sounds = 0
    for source in source_sources:
        if source["sound"] is None:
            n_default_sounds += 1

    default_sounds = []
    if n_default_sounds > 0:
        default_sounds = generate_maximally_different_sounds(
            n_default_sounds, sample_rate, default_sound_duration
        )

    for source in source_sources:
        if source["sound"] is None:
            source["sound"] = Audio.create_from_signal(
                default_sounds.pop(0), sample_rate
            )

    num_mics = len(environment.get_mics())
    mic_positions = [(mic.get_x(), mic.get_y()) for mic in environment.get_mics()]

    max_sample_index = 0
    for source in source_sources:
        for start_sample_index in (key for key in source.keys() if key != "sound"):
            if start_sample_index > max_sample_index:
                max_sample_index = start_sample_index

    # Compute max delay for the furthest possible distances in the environment
    environment_vertices = environment.get_vertices()
    x_coords = [vertex[0] for vertex in environment_vertices]
    y_coords = [vertex[1] for vertex in environment_vertices]
    max_distance = np.sqrt(
        (max(x_coords) - min(x_coords)) ** 2 + (max(y_coords) - min(y_coords)) ** 2
    )
    max_delay = max_distance / DEFAULT_SOUND_SPEED
    max_delay_samples = int(sample_rate * max_delay)

    max_delay = max_distance / DEFAULT_SOUND_SPEED
    max_delay_samples = int(sample_rate * max_delay)

    # max_sample_index + longest duration in samples + max delay in samples
    total_samples = (
        max_sample_index + int(default_sound_duration * sample_rate) + max_delay_samples
    )

    mic_audio = [np.zeros(total_samples) for _ in range(num_mics)]

    # Default loudness mix if not provided
    if loudness_mix is None:
        loudness_mix = [1.0] * (len(source_sources) + (1 if background_noise else 0))

    if len(loudness_mix) != len(source_sources) + (1 if background_noise else 0):
        raise ValueError(
            "Length of loudness_mix must match number of sources + background noise."
        )

    for idx, source in enumerate(source_sources):
        for start_sample_index, (x, y) in (
            (key, value) for key, value in source.items() if key != "sound"
        ):
            for mic_index, mic_position in enumerate(mic_positions):
                mic_x, mic_y = mic_position
                distance = np.sqrt((x - mic_x) ** 2 + (y - mic_y) ** 2)

                time_delay = distance / DEFAULT_SOUND_SPEED
                sample_delay = int(sample_rate * time_delay)

                start_index = start_sample_index + sample_delay

                wave = source["sound"].get_audio_signal_unchunked() * loudness_mix[idx]

                if start_index + len(wave) <= total_samples:
                    mic_audio[mic_index][start_index : start_index + len(wave)] += wave

    # Add background noise
    if background_noise is not None:
        background_noise_signal = background_noise.get_audio_signal_unchunked()
        bg_noise_repeated = np.tile(
            background_noise_signal,
            int(np.ceil(total_samples / len(background_noise_signal))),
        )[:total_samples]

        bg_noise_repeated *= loudness_mix[-1]

        for mic_index in range(num_mics):
            mic_audio[mic_index] += bg_noise_repeated

    # Clip audio signals to [-1, 1]
    for mic_index in range(num_mics):
        mic_audio[mic_index] = np.clip(mic_audio[mic_index], -1.0, 1.0)

    # Set audio signals to microphones
    for mic, audio in zip(environment.get_mics(), mic_audio):
        audio = Audio.create_from_signal(audio, sample_rate)
        mic.set_audio(audio)

    # Normalize audio signals to prevent very loud audio signals
    AudioNormalizer.normalize_environment_to_max_amplitude(environment, 0.5)

    return environment


def generate_maximally_different_sounds(N, sample_rate, duration):
    """
    Generate N maximally different sounds.

    Args:
        N (int): Number of distinct sounds to generate.
        sample_rate (int): Sampling rate in Hz.
        duration (float): Duration of each sound in seconds.

    Returns:
        list[np.ndarray]: List of generated sound waveforms.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    signal_generators = [
        lambda t, freq: np.sin(2 * np.pi * (2 * freq) * t),  # Sine wave
        lambda t, freq: 2 * (t % (1 / freq)) * freq - 1,  # Sawtooth wave
        lambda t, freq: np.sign(np.sin(2 * np.pi * freq * t)),  # Square wave
        lambda t, freq: 2 * np.abs(2 * (t % (1 / freq)) * freq - 1)
        - 1,  # Triangle wave
        lambda t, _: np.random.uniform(-1, 1, len(t)),  # White noise
    ]

    frequencies = np.logspace(np.log10(100), np.log10(1000), N)

    sounds = []
    for i in range(N):
        signal_type = signal_generators[i % len(signal_generators)]
        freq = frequencies[i]
        sound = signal_type(t, freq)
        sounds.append(sound)

    return sounds
