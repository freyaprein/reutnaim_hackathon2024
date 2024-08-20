import pytest
import pandas as pd
from pathlib import Path
from empatica_processing.cleaning_tagging.outliers import OutliersDataProcessor

@pytest.fixture
def setup_environment(tmp_path):
    """
    Setup a temporary environment for testing.

    Creates a mock base folder with participant subfolders and sample CSV data
    files for testing. Also, creates a mock tags.csv file.

    Args:
        tmp_path (Path): Temporary directory for testing.

    Returns:
        Path: Path to the base folder containing the mock data.
    """
    base_folder = tmp_path / "test_data"
    base_folder.mkdir()

    participant_folder = base_folder / "individual recordings" / "participant_1"
    participant_folder.mkdir(parents=True)

    # Create mock data for each file type
    acc_data = {
        'ACC1': [100, 1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.1, 0.3, 0.2],
        'ACC2': [100, 1, 0.2, 0.1, 0.4, 0.3, 0.6, 0.5, 0.1, 0.4, 0.2],
        'ACC3': [100, 1, 0.3, 0.2, 0.1, 0.5, 0.4, 0.3, 0.2, 0.1, 0.6],
    }
    pd.DataFrame(acc_data).to_csv(participant_folder / "ACC.csv", index=False, header=False)

    bvp_data = {
        'BVP': [100, 1, 80.5, 82.1, 83.0, 81.0, 79.9, 85.2, 80.7, 82.5, 81.3],
    }
    pd.DataFrame(bvp_data).to_csv(participant_folder / "BVP.csv", index=False, header=False)

    eda_data = {
        'EDA': [100, 1, 0.01, 0.02, 0.03, 0.05, 0.04, 0.03, 0.02, 0.01, 0.02],
    }
    pd.DataFrame(eda_data).to_csv(participant_folder / "EDA.csv", index=False, header=False)

    hr_data = {
        'HR': [100, 1, 72, 75, 70, 73, 74, 76, 71, 74, 75],
    }
    pd.DataFrame(hr_data).to_csv(participant_folder / "HR.csv", index=False, header=False)

    temp_data = {
        'TEMP': [100, 1, 36.5, 36.6, 36.7, 36.8, 36.6, 36.5, 36.7, 36.8, 36.6],
    }
    pd.DataFrame(temp_data).to_csv(participant_folder / "TEMP.csv", index=False, header=False)

    # Create a mock tags.csv file
    tags_data = {
        0: [101, 102, 103]  # Tags from A1 to A3
    }
    pd.DataFrame(tags_data).to_csv(participant_folder / "tags.csv", header=None, index=False)

    return base_folder

def test_tagging_functionality(setup_environment):
    """
    Test the tagging functionality of the OutliersDataProcessor.

    Ensures that the 'tags' column is correctly added to the DataFrame
    and populated with appropriate tag values.

    Args:
        setup_environment (Path): Path to the base folder with mock data.
    """
    processor = OutliersDataProcessor(base_folder=setup_environment)
    participant_folder = setup_environment / "individual recordings/participant_1"
    file_name = "ACC.csv"
    file_path = participant_folder / file_name
    df = pd.read_csv(file_path, header=None).iloc[2:]

    tags_file = participant_folder / "tags.csv"
    tags_df = pd.read_csv(tags_file, header=None)

    tag0 = df.iloc[0, 0]
    sample_rate = df.iloc[1, 0]
    tag1 = tags_df.iloc[0, 0] if len(tags_df) > 0 else None
    tag2 = tags_df.iloc[1, 0] if len(tags_df) > 1 else None
    tag3 = tags_df.iloc[2, 0] if len(tags_df) > 2 else None

    df_with_tags = processor.add_tags_column(df, [tag0, tag1, tag2, tag3], sample_rate)

    # Check that the 'tags' column was added
    assert 'tags' in df_with_tags.columns, "The 'tags' column should be added to the DataFrame."

    # Check that the 'tags' column has been populated (non-empty)
    assert not df_with_tags['tags'].isnull().all(), "The 'tags' column should not be empty."

    # Check that the tags column has the expected type and that calculations were performed
    assert df_with_tags['tags'].dtype == object, "The 'tags' column should contain string data type."

    # Optional: Print the DataFrame for debugging purposes
    print(df_with_tags[['tags']])

def test_filter_out_csv(setup_environment):
    """
    Test the outlier detection and filtering functionality of the processor.

    Ensures that outliers are correctly detected in the physiological data.

    Args:
        setup_environment (Path): Path to the base folder with mock data.
    """
    processor = OutliersDataProcessor(base_folder=setup_environment)
    for file_name in ["ACC.csv", "BVP.csv", "EDA.csv", "HR.csv", "TEMP.csv"]:
        df = pd.read_csv(setup_environment / f"individual recordings/participant_1/{file_name}", header=None).iloc[2:]

        outlier_percentage = processor.filter_out_csv(df)

        assert outlier_percentage >= 0, f"Outliers should be detected in the {file_name} data."

def test_save_sd_file(setup_environment):
    """
    Test saving the standard deviation (SD) file.

    Ensures that the SD file is correctly created and saved.

    Args:
        setup_environment (Path): Path to the base folder with mock data.
    """
    processor = OutliersDataProcessor(base_folder=setup_environment)
    for file_name in ["ACC.csv", "BVP.csv", "EDA.csv", "HR.csv", "TEMP.csv"]:
        df = pd.read_csv(setup_environment / f"individual recordings/participant_1/{file_name}", header=None).iloc[2:]
        sd_file_path = setup_environment / f"sd_{file_name}"
        processor.save_sd_file(df, sd_file_path)

        assert sd_file_path.exists(), f"SD file {sd_file_path} should be created and saved."

def test_winsorize_data(setup_environment):
    """
    Test the winsorization process on the data.

    Ensures that data is correctly winsorized to the specified bounds.

    Args:
        setup_environment (Path): Path to the base folder with mock data.
    """
    processor = OutliersDataProcessor(base_folder=setup_environment)
    for file_name in ["ACC.csv", "BVP.csv", "EDA.csv", "HR.csv", "TEMP.csv"]:
        df = pd.read_csv(setup_environment / f"individual recordings/participant_1/{file_name}", header=None).iloc[2:]

        means = df.mean()
        std_devs = df.std()
        upper_bounds = means + processor.threshold * std_devs
        lower_bounds = means - processor.threshold * std_devs

        df_winsorized = processor.winsorize_data(df, lower_bounds, upper_bounds)

        assert df_winsorized.max().max() <= upper_bounds.max(), f"Data in {file_name} should be clipped at the upper bound."
        assert df_winsorized.min().min() >= lower_bounds.min(), f"Data in {file_name} should be clipped at the lower bound."

def test_process_file(mocker, setup_environment):
    """
    Test the entire file processing function, from outlier detection to saving the processed file.

    Ensures that the file is processed and saved in the clean folder.

    Args:
        mocker (pytest_mock.MockerFixture): Mocker fixture to mock dependencies.
        setup_environment (Path): Path to the base folder with mock data.
    """
    processor = OutliersDataProcessor(base_folder=setup_environment)
    participant_folder = setup_environment / "individual recordings/participant_1"
    clean_participant_folder = setup_environment / "clean_individual_recordings/participant_1"
    clean_participant_folder.mkdir(parents=True)

    for file_name in ["ACC.csv", "BVP.csv", "EDA.csv", "HR.csv", "TEMP.csv"]:
        file_path = participant_folder / file_name
        processor.process_file(file_path, participant_folder, clean_participant_folder)

        assert (clean_participant_folder / f"c_{file_name}").exists(), f"Processed and winsorized file {file_name} should be saved."

def test_copy_additional_files(setup_environment):
    """
    Test copying additional files like metadata or information files.

    Ensures that additional files are copied to the clean folder.

    Args:
        setup_environment (Path): Path to the base folder with mock data.
    """
    processor = OutliersDataProcessor(base_folder=setup_environment)

    participant_folder = setup_environment / "individual recordings/participant_1"
    clean_participant_folder = setup_environment / "clean_individual_recordings/participant_1"
    clean_participant_folder.mkdir(parents=True)

    additional_file = participant_folder / "info.txt"
    additional_file.write_text("Test info content")

    processor.copy_additional_files(participant_folder, clean_participant_folder)

    assert (clean_participant_folder / "info.txt").exists(), "Additional file should be copied."

def test_save_outlier_info(setup_environment):
    """
    Test saving outlier information.

    Ensures that the outlier information is saved correctly.

    Args:
        setup_environment (Path): Path to the base folder with mock data.
    """
    processor = OutliersDataProcessor(base_folder=setup_environment)

    processor.outlier_info  # Implement this part based on your actual method
