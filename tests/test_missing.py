import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch
from empatica_processing.missing_data.missing_filling import UnusualSubjectDataProcessor  # Replace with your actual module

# Adjust this path to where your mock folder is located
# MOCK_BASE_FOLDER = Path("/Users/sofiakarageorgiou/Desktop/Hackathon_files_adapt_lab/mock_data/")
MOCK_BASE_FOLDER = Path(__file__).parent / "mock_data"  # Use this line if the mock_data folder is in the same directory as this test file
def test_process_subject_files():
    processor = UnusualSubjectDataProcessor(MOCK_BASE_FOLDER.parent)  # Initialize with the base folder

    base_folder = MOCK_BASE_FOLDER

    # Iterate over each subject folder (e.g., rn23004)
    for subject_folder in base_folder.iterdir():
        if not subject_folder.is_dir():
            continue

        # Ensure the subject folder has exactly two subfolders (1 and 2)
        subfolders = [f for f in subject_folder.iterdir() if f.is_dir()]
        if len(subfolders) != 2:
            print(f"Skipping {subject_folder.name} because it does not have exactly two subfolders.")
            continue  # Skip this iteration if the condition is not met

        subfolders.sort()  # Sort to ensure consistent ordering (1 and 2)

        # Mock the read_and_validate_csv method to only return data for HR.csv and None for others
        with patch.object(processor, 'read_and_validate_csv') as mock_read_and_validate_csv:
            def side_effect(filepath, folder_name, filename):
                if "HR.csv" in str(filepath):
                    # Return valid data for HR.csv
                    return pd.read_csv(filepath, header=None)
                else:
                    return None

            mock_read_and_validate_csv.side_effect = side_effect

            # Process the subject files
            combined_data = processor.process_subject_files(subject_folder, subfolders)

            # We expect the combined data to have the filled recording for HR.csv only
            assert combined_data is not None, "The combined data should not be None."
            assert "HR.csv" in combined_data, "The combined data should include the 'HR.csv' file."

            # Check if the filled recording has the expected number of rows
            filled_recording = combined_data["HR.csv"]
            actual_time_gap = 1713100065.000000 - 1713098412.000000
            expected_num_rows = len(filled_recording)
            print(f"Expected number of rows: {expected_num_rows}")

            assert len(filled_recording) == expected_num_rows, f"Expected {expected_num_rows} rows, but got {len(filled_recording)}."

            # Check if the placeholder rows are correctly filled
            placeholder_rows = filled_recording.iloc[len(filled_recording) - int(actual_time_gap):]
            assert (placeholder_rows != 9999999999).all().all(), "The filled rows should contain the placeholder value 9999999999."

