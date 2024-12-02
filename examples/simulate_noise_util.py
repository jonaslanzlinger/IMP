import numpy as np
from pysoundlocalization.core.Environment import Environment
from pysoundlocalization.core.Audio import Audio


def generate_microphone_audio(
    environment: Environment,
    sample_rate: int,
    source_positions: list[dict[int, tuple[float, float]]],
) -> Environment:
    """
    Helper function to generate audio signals based on an environment, and a dictionary
    containing a sample index along with the source position (x, y) for each source.

    Parameters:
    - environment (Environment): The environment containing room dimensions and microphones.
    - sample_rate (int): The sample rate of the audio signals.
    - source_positions (list[dict[int, tuple[float, float]]]):
      A list where each dictionary maps sample indices (start point) to source positions (x, y).

    Returns:
        - Environment: The environment with the generated audio signals updated.
    """
    num_mics = len(environment.get_mics())
    mic_positions = [(mic.get_x(), mic.get_y()) for mic in environment.get_mics()]

    max_sample_index = 0
    for source in source_positions:
        for start_sample_index in source.keys():
            if start_sample_index > max_sample_index:
                max_sample_index = start_sample_index

    # sine_wave_duration = 0.3
    # sawtooth_duration = 0.3

    duration = 0.3

    sounds = generate_maximally_different_sounds(
        len(source_positions), sample_rate, duration
    )

    total_samples = max_sample_index + int(duration * sample_rate)

    mic_audio = [np.zeros(total_samples) for _ in range(num_mics)]

    # t = np.linspace(
    #     0, sine_wave_duration, int(sample_rate * sine_wave_duration), endpoint=False
    # )

    # t_sine = np.linspace(
    #     0, sine_wave_duration, int(sample_rate * sine_wave_duration), endpoint=False
    # )
    # sine_wave = np.sin(2 * np.pi * 440 * t_sine)

    # t_sawtooth = np.linspace(
    #     0, sawtooth_duration, int(sample_rate * sawtooth_duration), endpoint=False
    # )
    # sawtooth_wave = 2 * (t_sawtooth % (1 / 440)) * 440 - 1

    for idx, source in enumerate(source_positions):
        for start_sample_index, (x, y) in source.items():
            for mic_index, mic_position in enumerate(mic_positions):
                mic_x, mic_y = mic_position
                distance = np.sqrt((x - mic_x) ** 2 + (y - mic_y) ** 2)
                print(f"Mic: {mic_x, mic_y}, Source: {x, y}, Distance: {distance}")

                time_delay = distance / 343.2
                sample_delay = int(sample_rate * time_delay)

                start_index = start_sample_index + sample_delay

                # if idx == 0:
                #     wave = sine_wave
                # elif idx == 1:
                #     wave = sawtooth_wave
                # else:
                #     wave = sine_wave

                wave = sounds[idx]

                if start_index + len(wave) < total_samples:
                    mic_audio[mic_index][start_index : start_index + len(wave)] += wave

    for mic, audio in zip(environment.get_mics(), mic_audio):
        audio = Audio.create_from_signal(audio, sample_rate)
        mic.set_audio(audio)

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
        lambda t, freq: np.sin(2 * np.pi * freq * t),  # Sine wave
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
