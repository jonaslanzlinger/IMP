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


# Example usage:
if __name__ == "__main__":
    # Replace with your actual file path
    filepath = "2025-01-11_18-14-09_experiment.txt"
    stats = analyze_experiment_file(filepath)
