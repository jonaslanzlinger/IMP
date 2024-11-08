from scipy.io import wavfile

# Array of file paths
# TODO: define audio files to verify their properties (e.g. whether their lengths align)
file_paths = [
    '../audio_files/Sandbox Experiments/Basic_Test_Mosquito/trimmed_output_MIC1_2024-11-06_15-30-16_794128.wav',
    '../audio_files/Sandbox Experiments/Basic_Test_Mosquito/trimmed_output_MIC2_2024-11-06_15-30-17_275815.wav',
    '../audio_files/Sandbox Experiments/Basic_Test_Mosquito/trimmed_output_MIC3_2024-11-06_15-30-16_843761.wav',
    '../audio_files/Sandbox Experiments/Basic_Test_Mosquito/trimmed_output_MIC4_2024-11-06_15-30-17_252158.wav'
]

# Iterate through each file path
for file_path in file_paths:
    try:
        # Read the .wav file
        sample_rate, data = wavfile.read(file_path)

        # Get the shape of the data
        shape = data.shape  # This will be (num_samples, num_channels) if stereo, or (num_samples,) if mono

        # Print the details
        print(f"File: {file_path}")
        print(f"Sample Rate: {sample_rate} Hz")
        print(f"Shape: {shape}")
        print(f"Channels: {1 if len(shape) == 1 else shape[1]}")
        print(f"Duration: {shape[0] / sample_rate:.2f} seconds\n")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")