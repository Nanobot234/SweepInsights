import pandas as pd
import os

def inspect_csv_columns(file_path):
    """
    Inspect the columns of a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        None
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return

    try:
        # Load the CSV file
        df = pd.read_csv(file_path)

        # Display the columns
        print(f"\nColumns in '{file_path}':")
        print("=" * 50)
        for column in df.columns:
            print(f"- {column}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

if __name__ == "__main__":
    # Example usage
    print("Enter the path to the CSV file:")
    file_path = input().strip()
    inspect_csv_columns(file_path)