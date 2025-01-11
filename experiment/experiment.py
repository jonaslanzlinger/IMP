from pysoundlocalization.core.Audio import Audio
from datetime import timedelta
from pysoundlocalization.preprocessing.FrequencyFilterChain import FrequencyFilterChain
from pysoundlocalization.preprocessing.LowCutFilter import LowCutFilter
from pysoundlocalization.preprocessing.NoiseReducer import NoiseReducer
from pysoundlocalization.preprocessing.NonNegativeMatrixFactorization import (
    NonNegativeMatrixFactorization,
)
from pysoundlocalization.core.Simulation import Simulation
from pysoundlocalization.visualization.multilaterate_plot import multilaterate_plot
from pysoundlocalization.visualization.wave_plot import wave_plot_environment
from pysoundlocalization.preprocessing.AudioNormalizer import AudioNormalizer
from pysoundlocalization.util.simulate_noise_util import generate_audios
from pysoundlocalization.preprocessing.SampleRateConverter import SampleRateConverter
from pysoundlocalization.preprocessing.NotchFilter import NotchFilter
from pysoundlocalization.preprocessing.HighCutFilter import HighCutFilter
from datetime import datetime
from pysoundlocalization.visualization.spectrogram_plot import (
    spectrogram_plot_environment,
)
from pysoundlocalization.visualization.wave_plot import wave_plot
import copy
import util_random_coordinates
import util_mapping_actual_approx


def run_experiment():
    # ##################
    # Global Variables #
    # ##################
    original_audios = [None, None, None, None]

    # #############
    # DEMO SCRIPT #
    # #############

    # #######################
    # PHASE 1 - ENVIRONMENT #
    # #######################
    print("PHASE 1 - ENVIRONMENT")

    # Create a Simulation: The Simulation is the main object
    # that contains all the Environments and Microphones,
    # along with the Audio objects that are used.
    simulation = Simulation.create()

    # Add an Environment to the Simulation: The Environment
    # is the object that contains the Microphones and the
    # Audio objects. The Environment is defined by a list of
    # points that represent the vertices of a polygon.
    environment = simulation.add_environment(
        "Simulation",
        [
            (0, 0),
            (600, 0),
            (600, 600),
            (0, 600),
        ],
    )

    # Add Microphones to the Environment as a 500x500m grid
    mic_1 = environment.add_microphone(50, 50)
    mic_2 = environment.add_microphone(550, 50)
    mic_3 = environment.add_microphone(550, 550)
    mic_4 = environment.add_microphone(50, 550)

    # Visualize the Environment with the Microphones
    # environment.visualize()

    # ##############################
    # PHASE 1.5 - Audio Generation #
    # ##############################
    print("PHASE 1.5 - Audio Generation")

    # Load two distinct sounds for the localization experiment
    sound_1 = Audio(filepath="../data/00_SOUND_BANK/sounds/buzzer_sound.wav")
    sound_2 = Audio(filepath="../data/00_SOUND_BANK/sounds/knock_sound.wav")

    # Normalize the audio signals to have a maximum amplitude of 1.0
    AudioNormalizer.normalize_audio_to_max_amplitude(sound_1, 1.0)
    AudioNormalizer.normalize_audio_to_max_amplitude(sound_2, 1.0)

    # Retrieve some information about the created Audio objects
    # print(f"Sound 1 duration: {sound_1.get_duration()}")
    # print(f"Sound 2 sample rate: {sound_2.get_sample_rate()}")

    # Visualize the Audio objects
    # wave_plot(
    #     audio_signal=sound_1.get_audio_signal_unchunked(),
    #     sample_rate=sound_1.get_sample_rate(),
    # )
    # wave_plot(
    #     audio_signal=sound_2.get_audio_signal_unchunked(),
    #     sample_rate=sound_2.get_sample_rate(),
    # )

    # Optionally play the Audio objects (POTENTIALLY LOUD!!!)
    ### sound_1.play()
    ### sound_2.play()

    # Ensure that all Audio objects have the same sample rate
    lowest_sample_rate = (
        SampleRateConverter.convert_list_of_audios_to_lowest_sample_rate(
            [sound_1, sound_2]
        )
    )

    RANDOM_SOURCE_A = (100, 100)  # This sound source does not move location
    RANDOM_SOURCE_B1 = (400, 400)
    RANDOM_SOURCE_B2 = (300, 400)  # This sound source moves location from B1 to B2

    # TODO: Activate randomization
    # Generate coordinate for first sound source. Remains stationary as it does not move.
    RANDOM_SOURCE_A = util_random_coordinates.get_random_coordinate(
        100, 500
    )  # This sound source does not move location

    # Generate coordinates for second sound source. Second coordinate is required as the sound moves.
    # Note that get_distant_coordinate() ensures that the coordinate is at least 150 units away.
    RANDOM_SOURCE_B1 = util_random_coordinates.get_distant_coordinate(
        RANDOM_SOURCE_A[0], RANDOM_SOURCE_A[1], 100, 500, 150
    )
    RANDOM_SOURCE_B2 = util_random_coordinates.get_distant_coordinate(
        RANDOM_SOURCE_A[0], RANDOM_SOURCE_A[1], 100, 500, 150
    )

    # Specify in this array of dictionaries the sound sources
    # and their positions in the environment. Each dictionary
    # defines one sound source. The keys of the
    # dictionaries are the sample index indicating the start
    # of the respective sound. The values are tuples with the
    # position at this sample index.
    source_positions = [
        {
            "sound": sound_1,  # None if no sound file is loaded
            int(lowest_sample_rate * 1): RANDOM_SOURCE_A,
            int(lowest_sample_rate * 6): RANDOM_SOURCE_A,
        },
        {
            "sound": sound_2,  # None if no sound file is loaded
            int(lowest_sample_rate * 1): RANDOM_SOURCE_B1,
            int(lowest_sample_rate * 6): RANDOM_SOURCE_B2,
        },
    ]

    # Additionally, add a background noise
    noise = Audio(
        filepath="../data/00_SOUND_BANK/noise/factory_sound.wav",
    )
    noise.resample_audio(lowest_sample_rate)

    # Normalize the audio signal to have a maximum amplitude of 1.0
    AudioNormalizer.normalize_audio_to_max_amplitude(noise, 1.0)

    # Visualize the noise Audio object
    # wave_plot(
    #     audio_signal=noise.get_audio_signal_unchunked(),
    #     sample_rate=noise.get_sample_rate(),
    # )

    # Retrieve some information about the created Audio objects
    # print(f"Noise duration: {noise.get_duration()}")
    # print(f"Noise sample rate: {noise.get_sample_rate()}")

    # Optionally play the Audio object (POTENTIALLY LOUD!!!)
    ### noise.play()

    # Obtain the number of sound sources, is always n=2 in this experiment.
    n_sound_sources = len(source_positions)

    # Generate the simulated audio objects
    environment = generate_audios(
        environment=environment,
        sample_rate=lowest_sample_rate,
        source_sources=source_positions,
        background_noise=noise,
        loudness_mix=[0.6, 0.6, 0.8],
        default_sound_duration=0.3,
    )

    # Visualize the Audio objects of the Environment
    # wave_plot_environment(environment=environment)
    # spectrogram_plot_environment(environment=environment)

    # Save a copy of the original Audio objects for later use
    for i, mic in enumerate(environment.get_mics()):
        original_audios[i] = copy.deepcopy(mic.get_audio())

        # Optionally play the Audio objects of the original audio (POTENTIALLY LOUD!!!)
        # original_audios[i].play()

    # ##########################
    # PHASE 2 - PRE-PROCESSING #
    # ##########################
    print("PHASE 2 - PRE-PROCESSING")

    # Filter out background noise
    frequency_filter_chain = FrequencyFilterChain()
    frequency_filter_chain.add_filter(LowCutFilter(cutoff_frequency=500, order=5))
    frequency_filter_chain.add_filter(
        NotchFilter(target_frequency=2760, quality_factor=10)
    )
    frequency_filter_chain.add_filter(HighCutFilter(cutoff_frequency=4000, order=5))

    # Loop over all Microphones in the Environment and apply the
    # FrequencyFilterChain to the Audio objects.
    for mic in environment.get_mics():
        audio = mic.get_audio()
        frequency_filter_chain.apply(audio)
        # It is important to normalize the audio signal after applying the filters
        # to ensure that the audio signal has a maximum amplitude of 1.0.
        AudioNormalizer.normalize_audio_to_max_amplitude(audio, 1.0)

    # Visualize the Audio objects of the Environment after applying the filters
    # wave_plot_environment(environment=environment)
    # spectrogram_plot_environment(environment=environment)

    # Use the NoiseReducer to reduce the noise in the Audio objects.
    for mic in environment.get_mics():
        audio = mic.get_audio()
        NoiseReducer.reduce_noise(audio)
        AudioNormalizer.normalize_audio_to_max_amplitude(audio, 1.0)

    # Visualize the Audio objects of the Environment after reducing the noise
    # wave_plot_environment(environment=environment)
    # spectrogram_plot_environment(environment=environment)

    # The NMF algorithm is used to extract the sound sources from the
    # Audio objects of the Microphones.
    sample_rate = environment.get_sample_rate()
    nmf = NonNegativeMatrixFactorization(
        number_of_sources_to_extract=n_sound_sources,
        sample_rate=sample_rate,
    )
    # The NMF algorithm returns a dictionary with the Microphones as keys, and the
    # extracted sound sources as values.
    all_sound_sources_nmf = nmf.run_for_environment(environment=environment)
    print(all_sound_sources_nmf)

    for i_sound_src in range(n_sound_sources):
        for mic in environment.get_mics():
            audio = all_sound_sources_nmf[mic][i_sound_src]
            mic.set_audio(audio)
        AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1.0)

        # Visualize the individual sound source Audio objects
        # wave_plot_environment(environment=environment)
        # spectrogram_plot_environment(environment=environment)

        # Optionally play the Audio objects of the finished processed audio (POTENTIALLY LOUD!!!)
        ### environment.get_mics()[0].get_audio().play()

    # ####################
    # PHASE 3 - Localize #
    # ####################
    print("PHASE 3 - LOCALIZE")

    algorithm_choice = "threshold"  # TODO: do for both algorithms
    # The sources_positions list will contain the estimated positions of the
    # sound sources after the multilateration step.
    approx_source_positions = []
    # This is the index of the current audio source that is being multilaterated
    current_audio_index = 0

    # Loop over all isolated sound sources, and assign them to the Microphones
    # in the Environment. Then, normalize the Environment to have a maximum
    # amplitude of 1.0. Finally, chunk the audio signals by the specified duration
    # and multilaterate the sound sources. The estimated positions are appended
    # to the sources_positions list.
    for i_sound_src in range(n_sound_sources):
        print(f"Multilaterating sound source {i_sound_src + 1} of {n_sound_sources}")

        # Load the audio signals of the sound sources into the Environment
        for mic in environment.get_mics():
            audio = all_sound_sources_nmf[mic][i_sound_src]
            mic.set_audio(audio)

        # Normalize the Environment to have a maximum amplitude of 1.0
        AudioNormalizer.normalize_environment_to_max_amplitude(environment, 1.0)

        # Chunk the audio signals by the specified duration
        environment.chunk_audio_signals_by_duration(
            chunk_duration=timedelta(milliseconds=5000)
        )

        # Multilaterate the sound source
        source_pos = environment.multilaterate(
            algorithm=algorithm_choice,
            number_of_sound_sources=1,
            threshold=0.5,
        )

        # Append the estimated position to the sources_positions list
        approx_source_positions.append(source_pos)

    print(approx_source_positions)

    # ###############
    # FINAL RESULTS #
    # ###############
    print("FINAL RESULTS")

    # Mapping approximated source_positions after NMF to the actual source_positions
    mapped_result_accuracy = util_mapping_actual_approx.get_mapped_results_accuracy(
        approx_source_positions, source_positions
    )

    # Because we want to visualize the results, with the original
    # Audio objects, we need to load the original Audio objects again
    # and assign them to the Microphones in the Environment.
    # print("Loading original Audio objects")
    # for i, mic in enumerate(environment.get_mics()):
    #     audio = original_audios[i]
    #     mic.set_audio(audio)
    #     mic.set_recording_start_time(datetime.now())
    #
    # # Visualize the final result
    # multilaterate_plot(environment, approx_source_positions)

    return mapped_result_accuracy


# 1. Create environment with microphones spaced 500x500m
# 2. create audio with background noise (sounds at 1s and 6s)
#       -> two stationary sounds (at 1s timestamp), one sound moves (at 6s timestamp)
# 3. preprocess and NMF
# 4.chunk a 10s audio into two 5s chunks (so that sounds are at 1s and 6s)
# 5. multilaterate
# 6. compute score

ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
for i in range(10):
    result = run_experiment()

    # Open the file in append mode to ensure it is created if not existing
    with open(f"{ts}_experiment.txt", "a") as file:
        file.write(f"Round {i+1}: {result}\n")
        file.flush()  # Flush the content to disk immediately

    print(f"Round {i+1}: Appended results to {ts}_experiment.txt.")
