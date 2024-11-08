import soundfile as sf

# Array of file paths
file_paths = [
    '../audio_files/Sandbox Experiments/Basic_Test_Mosquito/trimmed_output_MIC1_2024-11-06_15-30-17_252158.wav',
    '../audio_files/Sandbox Experiments/Basic_Test_Mosquito/trimmed_output_MIC2_2024-11-06_15-30-16_794128.wav',
    '../audio_files/Sandbox Experiments/Basic_Test_Mosquito/output_MIC3_2024-11-06_15-30-17_275815.wav',
    '../audio_files/Sandbox Experiments/Basic_Test_Mosquito/output_MIC4_2024-11-06_15-30-16_843761.wav'
]

# Iterate through each file path
for file_path in file_paths:
    try:
        # Read the .wav file
        data, sample_rate = sf.read(file_path)

        # Calculate duration in seconds
        duration_seconds = len(data) / sample_rate

        # Get the shape of the data
        shape = data.shape  # (num_samples, num_channels) if stereo, or (num_samples,) if mono

        # Print details
        print(f"File: {file_path}")
        print(f"Sample Rate: {sample_rate} Hz")
        print(f"Shape: {shape}")
        print(f"Channels: {1 if len(shape) == 1 else shape[1]}")
        print(f"Duration: {duration_seconds:.2f} seconds\n")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")