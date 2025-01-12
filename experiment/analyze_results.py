import numpy as np
import re
import ast


def read_experiment_file(filepath):
    """Read the experiment file and return its content"""
    try:
        with open(filepath, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def extract_errors_by_method(content):
    """Extract errors for each method from the experiment text"""
    # Initialize dictionary to store errors for each method
    errors_by_method = {"threshold": [], "gcc_phat": []}

    # Find all rounds
    rounds = content.split("Round")[
        1:
    ]  # Split by "Round" and skip the first empty element

    for round_data in rounds:
        # Clean up the round data and convert to dictionary
        round_str = round_data.split(":", 1)[
            1
        ].strip()  # Remove round number and get the dictionary part
        round_str = re.sub(
            r"np\.float64\(([\d.]+)\)", r"\1", round_str
        )  # Clean numpy values

        try:
            data = ast.literal_eval(round_str)

            # Extract errors for each method in this round
            for method in ["threshold", "gcc_phat"]:
                if method in data:
                    for source in data[method]:
                        for mapping in source["mappings"]:
                            errors_by_method[method].append(float(mapping["error"]))

        except (ValueError, SyntaxError) as e:
            print(f"Error parsing round data: {e}")
            continue

    # Convert lists to numpy arrays
    for method in errors_by_method:
        errors_by_method[method] = np.array(errors_by_method[method])

    return errors_by_method


def calculate_statistics(errors):
    """Calculate various error statistics"""
    stats = {
        "mean_error": np.mean(errors),
        "min_error": np.min(errors),
        "max_error": np.max(errors),
        "std_error": np.std(errors),
        "rmse": np.sqrt(np.mean(np.square(errors))),
        "num_samples": len(errors),
    }
    return stats


def analyze_experiment_file(filepath):
    """
    Reads and analyzes the experiment txt file with multiple methods.

    Args:
        filepath (string): Path to the experiment txt file to be loaded.

    Returns:
        dict: Statistics for each method in the experiment file.
    """
    # Read the file
    content = read_experiment_file(filepath)
    if content is None:
        return None

    # Extract errors for each method
    errors_by_method = extract_errors_by_method(content)
    if errors_by_method is None:
        return None

    # Calculate statistics for each method
    stats_by_method = {}

    print("\nError Statistics by Method:")
    print("-" * 50)

    for method, errors in errors_by_method.items():
        stats = calculate_statistics(errors)
        stats_by_method[method] = stats

        print(f"\n{method.upper()}:")
        print(f"Number of samples: {stats['num_samples']}")
        print(f"Mean Error: {stats['mean_error']:.6f}")
        print(f"Min Error:  {stats['min_error']:.6f}")
        print(f"Max Error:  {stats['max_error']:.6f}")
        print(f"Std Dev:    {stats['std_error']:.6f}")
        print(f"RMSE:       {stats['rmse']:.6f}")

    return stats_by_method


def main():
    """
    Analyzes the experiment file provided in the filepath.
    """
    # Prompt the user for the file path (eg. 2025-01-12_14-07-52_experiment_one_sound_moving.txt)
    filepath = input("Please enter the path to the experiment file: ").strip()
    analyze_experiment_file(filepath)


if __name__ == "__main__":
    main()
