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
    # Extract the dictionary part after 'Round X:'
    round_match = re.search(r"Round \d+: (.+)$", content)
    if not round_match:
        print("Error: Could not find Round data in the content")
        return None

    # Convert the string representation to a dictionary
    # Replace numpy float representations with regular numbers
    dict_str = round_match.group(1)
    dict_str = re.sub(r"np\.float64\(([\d.]+)\)", r"\1", dict_str)

    try:
        round_data = ast.literal_eval(dict_str)

        # Initialize dictionary to store errors for each method
        errors_by_method = {}

        # Extract errors for each method
        for method, data in round_data.items():
            errors = []
            for source in data:
                for mapping in source["mappings"]:
                    errors.append(float(mapping["error"]))
            errors_by_method[method] = np.array(errors)

        return errors_by_method

    except (ValueError, SyntaxError) as e:
        print(f"Error parsing data: {e}")
        return None


def calculate_statistics(errors):
    """Calculate various error statistics"""
    stats = {
        "mean_error": np.mean(errors),
        "min_error": np.min(errors),
        "max_error": np.max(errors),
        "std_error": np.std(errors),
        "rmse": np.sqrt(np.mean(np.square(errors))),
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
