import math
from itertools import permutations


def calculate_distance(coord1, coord2):
    """
    Calculate the Euclidean distance between two coordinates.

    Parameters:
        coord1 (tuple): First coordinate (x1, y1).
        coord2 (tuple): Second coordinate (x2, y2).

    Returns:
        float: The distance between coord1 and coord2.
    """
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


def minimize_distance_mapping(actual_source_positions, approx_source_positions):
    """
    Map approx_source_positions to actual_source_positions to minimize total distance.

    Parameters:
        actual_source_positions (list): List of dictionaries containing "RANDOM_SOURCE_XXX" coordinates.
        approx_source_positions (list): List of dictionaries containing approximation coordinates.

    Returns:
        list: Mapped result in the desired structured format.
    """
    # Extract only RANDOM_SOURCE_XXX coordinates from actual_source_positions
    actual_coordinates = []
    for source in actual_source_positions:
        actual_coordinates.append(
            [v for k, v in source.items() if isinstance(v, tuple)]
        )

    # Result storage
    mapping_results = []

    # Iterate over each approximation
    for i, approx in enumerate(approx_source_positions):
        approx_coords = list(approx.values())
        approx_samples = list(approx.keys())  # Get corresponding sample keys
        actual_coords = actual_coordinates[i]

        # Generate all possible mappings and calculate total distance
        min_distance = float("inf")
        best_mapping = None

        for perm in permutations(actual_coords):
            total_distance = sum(
                calculate_distance(approx_coords[j], perm[j])
                for j in range(len(approx_coords))
            )
            if total_distance < min_distance:
                min_distance = total_distance
                best_mapping = list(zip(approx_samples, approx_coords, perm))

        # Store the structured result
        result = {"source_number": i + 1, "mappings": []}
        for sample, approx_coord, actual_coord in best_mapping:
            error = calculate_distance(approx_coord, actual_coord)
            result["mappings"].append(
                {
                    "sample": sample,
                    "actual": actual_coord,
                    "approximate": approx_coord,
                    "error": error,
                }
            )

        mapping_results.append(result)

    return mapping_results


# Example usage
actual_source_positions = [
    {
        "sound": None,
        1: (400, 400),
        6: (300, 400),
    },
    {
        "sound": None,
        1: (100, 100),
        6: (100, 100),
    },
]

approx_source_positions = [
    {
        "0": (300.04389244615277, 399.4987019794673),
        "55125": (400.07566630995956, 399.5545727856106),
    },
    {
        "0": (100.00229926593859, 99.38170345012708),
        "55125": (100.04645607056848, 99.42614610171589),
    },
]

result = minimize_distance_mapping(actual_source_positions, approx_source_positions)
print(result)

# Print the result
for res in result:
    print(f"Source {res['source_number']}:")
    for mapping in res["mappings"]:
        print(f"  Sample: {mapping['sample']}")
        print(f"    Actual -> {mapping['actual']}")
        print(f"    Approximate -> {mapping['approximate']}")
        print(f"    Error -> {mapping['error']:.4f}")
    print()
