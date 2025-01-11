import numpy as np
from itertools import permutations


def calculate_distance(coord1, coord2):
    """Calculate Euclidean distance between two coordinates"""
    return np.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


def get_mapped_results_accuracy(approx_source_positions, source_positions):
    result = []

    # Try all possible mappings between approx_positions and source_positions
    for mapping in permutations(range(len(approx_source_positions))):
        total_error = 0
        current_mapping = []

        # For each position in the mapping
        for result_idx, source_idx in enumerate(mapping):
            approx_dict = approx_source_positions[result_idx]
            source_dict = source_positions[source_idx]

            # Get actual positions (excluding 'sound' key)
            actual_positions = {k: v for k, v in source_dict.items() if k != "sound"}

            # Create mapping entry for this source
            source_mapping = {"source_number": source_idx + 1, "mappings": []}

            # Map each sample's approximate position to actual position
            for sample, approx_pos in approx_dict.items():
                # Find closest actual position for this sample time
                closest_time = min(
                    actual_positions.keys(), key=lambda x: abs(int(x) - int(sample))
                )
                actual_pos = actual_positions[closest_time]

                error = calculate_distance(approx_pos, actual_pos)
                total_error += error

                source_mapping["mappings"].append(
                    {
                        "sample": sample,
                        "actual": actual_pos,
                        "approximate": approx_pos,
                        "error": error,
                    }
                )

            current_mapping.append(source_mapping)

        # Keep this mapping if it has the lowest total error so far
        if not result or total_error < min_total_error:
            result = current_mapping
            min_total_error = total_error

    return result


def main():
    # Example usage:
    approx_source_positions = [
        {
            "0": (np.float64(100), np.float64(99)),
            "55125": (np.float64(105), np.float64(100)),
        },
        {
            "0": (np.float64(400), np.float64(400)),
            "55125": (np.float64(301), np.float64(399)),
        },
    ]

    source_positions = [
        {
            "sound": None,
            0: (100, 100),
            55125: (100, 100),
        },
        {
            "sound": None,
            0: (400, 400),
            55125: (300, 400),
        },
    ]

    result = get_mapped_results_accuracy(approx_source_positions, source_positions)
    print(result)


if __name__ == "__main__":
    main()
