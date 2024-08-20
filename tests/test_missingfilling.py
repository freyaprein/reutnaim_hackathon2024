import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch
from missing_filling import UnusualSubjectDataProcessor

@pytest.fixture
def setup_mock_data(tmp_path):
    # Create mock folder structure
    base_folder = tmp_path / "Hackathon_files_adapt_lab" / "individual recordings"
    base_folder.mkdir(parents=True, exist_ok=True)

    # Create mock subject folder
    subject_folder = base_folder / "rn12345"
    subject_folder.mkdir()

    # Create two subfolders
    subfolder1 = subject_folder / "session1"
    subfolder2 = subject_folder / "session2"
    subfolder1.mkdir()
    subfolder2.mkdir()

    # Create mock CSV data
    mock_data_1 = "0.0,1.0\n1.0,2.0\n2.0,3.0"
    mock_data_2 = "3.0,1.0\n4.0,2.0\n5.0,3.0"

    # Write mock data to CSV files
    for csv_file in ['ACC.csv', 'BVP.csv', 'EDA.csv', 'HR.csv', 'TEMP.csv']:
        with open(subfolder1 / csv_file, "w") as f:
            f.write(mock_data_1)
        with open(subfolder2 / csv_file, "w") as f:
            f.write(mock_data_2)

    # Additional files
    with open(subfolder1 / "info.txt", "w") as f:
        f.write("info text")
    with open(subfolder1 / "tags.csv", "w") as f:
        f.write("tags data")

    return base_folder

def test_folder_and_file_validation(setup_mock_data):
    print("Testing folder and file validation...")
    processor = UnusualSubjectDataProcessor(setup_mock_data)
    subject_folder = setup_mock_data / "rn12345"
    result = processor.folder_and_file_validation(subject_folder)
    assert result is True, f"Validation failed for {subject_folder}"
    print("Folder and file validation passed.")

def test_read_and_validate_csv(setup_mock_data):
    print("Testing CSV reading and validation...")
    processor = UnusualSubjectDataProcessor(setup_mock_data)
    subject_folder = setup_mock_data / "rn12345"
    subfolder1 = subject_folder / "session1"
    filepath = subfolder1 / "ACC.csv"

    # Check valid CSV file
    df = processor.read_and_validate_csv(filepath, subject_folder.name, "ACC.csv")
    assert isinstance(df, pd.DataFrame), "Failed to read valid CSV file"
    assert df.shape == (3, 2), f"Unexpected shape for CSV: {df.shape}"
    print("Valid CSV file passed.")

    # Check missing CSV file
    print("Testing missing CSV file...")
    missing_filepath = subfolder1 / "MISSING.csv"
    df = processor.read_and_validate_csv(missing_filepath, subject_folder.name, "MISSING.csv")
    assert df is None, "Missing CSV file was incorrectly processed"
    print("Missing CSV file test passed.")

    # Check empty CSV file
    print("Testing empty CSV file...")
    empty_filepath = subfolder1 / "EMPTY.csv"
    with open(empty_filepath, "w") as f:
        pass  # Write empty file
    df = processor.read_and_validate_csv(empty_filepath, subject_folder.name, "EMPTY.csv")
    assert df is None, "Empty CSV file was incorrectly processed"
    print("Empty CSV file test passed.")

def test_process_subject_files(setup_mock_data):
    print("Testing subject file processing...")
    processor = UnusualSubjectDataProcessor(setup_mock_data)
    subject_folder = setup_mock_data / "rn12345"
    subfolders = [subject_folder / "session1", subject_folder / "session2"]
    combined_data = processor.process_subject_files(subject_folder, subfolders)

    assert isinstance(combined_data, dict), "Combined data is not a dictionary"
    assert "ACC.csv" in combined_data, "ACC.csv not found in combined data"
    assert combined_data["ACC.csv"].shape == (6, 2), "Unexpected shape for combined data"
    print("Subject file processing passed.")

def test_save_combined_data(setup_mock_data):
    print("Testing saving of combined data...")
    processor = UnusualSubjectDataProcessor(setup_mock_data)
    subject_folder = setup_mock_data / "rn12345"
    combined_data = {
        "ACC.csv": pd.DataFrame([[0.0, 1.0], [1.0, 2.0], [2.0, 3.0], [3.0, 1.0], [4.0, 2.0], [5.0, 3.0]])
    }

    processor.save_combined_data(subject_folder, combined_data)
    output_file = subject_folder / "Filled_Merged_ACC.csv"
    assert output_file.exists(), "Failed to save combined data"
    print("Saving of combined data passed.")

def test_copy_additional_files(setup_mock_data):
    print("Testing copying of additional files...")
    processor = UnusualSubjectDataProcessor(setup_mock_data)
    subject_folder = setup_mock_data / "rn12345"
    subfolders = [subject_folder / "session1", subject_folder / "session2"]

    processor.copy_additional_files(subject_folder, subfolders)
    assert (subject_folder / "info.txt").exists(), "info.txt was not copied"
    assert (subject_folder / "tags.csv").exists(), "tags.csv was not copied"
    print("Copying of additional files passed.")

def test_process_subjects(setup_mock_data):
    print("Testing entire subject processing...")
    processor = UnusualSubjectDataProcessor(setup_mock_data)

    with patch.object(processor, "process_subject_files", wraps=processor.process_subject_files) as mock_process_files:
        with patch.object(processor, "save_combined_data", wraps=processor.save_combined_data) as mock_save_data:
            processor.process_subjects()
            assert mock_process_files.called, "process_subject_files was not called"
            assert mock_save_data.called, "save_combined_data was not called"
            print("Entire subject processing passed.")
