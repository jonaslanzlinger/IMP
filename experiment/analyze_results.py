import numpy as np
import re


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


def extract_errors(text):
    """Extract all error values from the experiment text"""
    # Find all error values in the text
    # Convert "np.float64(X)" strings to float values
    error_pattern = r"'error': np\.float64\(([\d.]+)\)"
    errors = [float(x) for x in re.findall(error_pattern, text)]
    return np.array(errors)


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
    Reads and analyzes the experiment txt file specifically created as part of experiment.py.

    A typical txt file follows the format:
    Round 0: [{'source_number': 2, 'mappings': [{'sample': '0', 'actual': (400, 400), 'approximate': (np.float64(400.07566630995956), np.float64(399.5545727856106)), 'error': np.float64(0.45180835957470006)}, {'sample': '55125', 'actual': (300, 400), 'approximate': (np.float64(300.04389244615277), np.float64(399.4987019794673)), 'error': np.float64(0.5032159101412557)}]}, {'source_number': 1, 'mappings': [{'sample': '0', 'actual': (100, 100), 'approximate': (np.float64(100.00229926593859), np.float64(99.38170345012708)), 'error': np.float64(0.6183008250104608)}, {'sample': '55125', 'actual': (100, 100), 'approximate': (np.float64(100.04645607056848), np.float64(99.42614610171589)), 'error': np.float64(0.5757312420466145)}]}]
    Round 1: [{'source_number': 2, 'mappings': [{'sample': '0', 'actual': (400, 400), 'approximate': (np.float64(400.07566630995956), np.float64(399.5545727856106)), 'error': np.float64(0.45180835957470006)}, {'sample': '55125', 'actual': (300, 400), 'approximate': (np.float64(300.04389244615277), np.float64(399.4987019794673)), 'error': np.float64(0.5032159101412557)}]}, {'source_number': 1, 'mappings': [{'sample': '0', 'actual': (100, 100), 'approximate': (np.float64(100.00229926593859), np.float64(99.38170345012708)), 'error': np.float64(0.6183008250104608)}, {'sample': '55125', 'actual': (100, 100), 'approximate': (np.float64(100.04645607056848), np.float64(99.42614610171589)), 'error': np.float64(0.5757312420466145)}]}]

    The method extracts all values and computes key metrics, printed into the console.

    Args:
        filepath (string): Path to the experiment txt file to be loaded.

    Returns:
        dict[str, floating | complexfloating]: Statistics of the experiment file.
    """
    # Read the file
    content = read_experiment_file(filepath)
    if content is None:
        return None

    # Extract errors
    errors = extract_errors(content)

    # Calculate statistics
    stats = calculate_statistics(errors)

    # Print results
    print("\nError Statistics:")
    print(f"Mean Error: {stats['mean_error']:.6f}")
    print(f"Min Error:  {stats['min_error']:.6f}")
    print(f"Max Error:  {stats['max_error']:.6f}")
    print(f"Std Dev:    {stats['std_error']:.6f}")
    print(f"RMSE:       {stats['rmse']:.6f}")

    return stats


def main():
    """
    Analyzes the experiment file provided in the filepath.
    """
    filepath = "2025-01-11_18-21-02_experiment.txt"  # REPLACE FILEPATH WITH PATH TO EXPERIMENT FILE
    stats = analyze_experiment_file(filepath)


if __name__ == "__main__":
    main()
