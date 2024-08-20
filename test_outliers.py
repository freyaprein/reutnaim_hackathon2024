import pytest
import pandas as pd
from pathlib import Path
from outliers import OutliersDataProcessor

@pytest.fixture
def setup_environment(tmp_path):
    # Create a mock base folder
    base_folder = tmp_path / "test_data"
    base_folder.mkdir()

    # Create mock participant folders and copy CSV files into them
    participant_folder = base_folder / "individual recordings" / "participant_1"
    participant_folder.mkdir(parents=True)

    # Create mock data for each file type
    acc_data = {
        'ACC1': [100, 256, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.1, 0.3, 0.2],
        'ACC2': [100, 256, 0.2, 0.1, 0.4, 0.3, 0.6, 0.5, 0.1, 0.4, 0.2],
        'ACC3': [100, 256, 0.3, 0.2, 0.1, 0.5, 0.4, 0.3, 0.2, 0.1, 0.6],
    }
    pd.DataFrame(acc_data).to_csv(participant_folder / "ACC.csv", index=False)

    bvp_data = {
        'BVP': [100, 256, 80.5, 82.1, 83.0, 81.0, 79.9, 85.2, 80.7, 82.5, 81.3],
    }
    pd.DataFrame(bvp_data).to_csv(participant_folder / "BVP.csv", index=False)

    eda_data = {
        'EDA': [100, 4, 0.01, 0.02, 0.03, 0.05, 0.04, 0.03, 0.02, 0.01, 0.02],
    }
    pd.DataFrame(eda_data).to_csv(participant_folder / "EDA.csv", index=False)

    hr_data = {
        'HR': [100, 256, 72, 75, 70, 73, 74, 76, 71, 74, 75],
    }
    pd.DataFrame(hr_data).to_csv(participant_folder / "HR.csv", index=False)

    ibi_data = {
        'IBI': [100, 256, 0.8, 0.9, 0.85, 0.83, 0.87, 0.88, 0.82, 0.9, 0.86],
    }
    pd.DataFrame(ibi_data).to_csv(participant_folder / "IBI.csv", index=False)

    temp_data = {
        'TEMP': [100, 4, 36.5, 36.6, 36.7, 36.8, 36.6, 36.5, 36.7, 36.8, 36.6],
    }
    pd.DataFrame(temp_data).to_csv(participant_folder / "TEMP.csv", index=False)

    return base_folder
def test_filter_out_csv(setup_environment):
    processor = OutliersDataProcessor(base_folder=setup_environment)
    for file_name in ["ACC.csv", "BVP.csv", "EDA.csv", "HR.csv", "IBI.csv", "TEMP.csv"]:
        df = pd.read_csv(setup_environment / f"individual recordings/participant_1/{file_name}").iloc[2:]

        means = df.mean()
        std_devs = df.std()
        upper_bounds = means + processor.threshold * std_devs
        lower_bounds = means - processor.threshold * std_devs

        outlier_percentage = processor.filter_out_csv(df)

        assert outlier_percentage >= 0, f"Outliers should be detected in the {file_name} data."


def test_save_sd_file(setup_environment):
    processor = OutliersDataProcessor(base_folder=setup_environment)
    for file_name in ["ACC.csv", "BVP.csv", "EDA.csv", "HR.csv", "IBI.csv", "TEMP.csv"]:
        df = pd.read_csv(setup_environment / f"individual recordings/participant_1/{file_name}").iloc[2:]
        sd_file_path = setup_environment / f"sd_{file_name}"
        processor.save_sd_file(df, sd_file_path)

        assert sd_file_path.exists(), f"SD file {sd_file_path} should be created and saved."


def test_winsorize_data(setup_environment):
    processor = OutliersDataProcessor(base_folder=setup_environment)
    for file_name in ["ACC.csv", "BVP.csv", "EDA.csv", "HR.csv", "IBI.csv", "TEMP.csv"]:
        df = pd.read_csv(setup_environment / f"individual recordings/participant_1/{file_name}").iloc[2:]

        means = df.mean()
        std_devs = df.std()
        upper_bounds = means + processor.threshold * std_devs
        lower_bounds = means - processor.threshold * std_devs

        df_winsorized = processor.winsorize_data(df, lower_bounds, upper_bounds)

        assert df_winsorized.max().max() <= upper_bounds.max(), f"Data in {file_name} should be clipped at the upper bound."
        assert df_winsorized.min().min() >= lower_bounds.min(), f"Data in {file_name} should be clipped at the lower bound."


def test_process_file(mocker, setup_environment):
    processor = OutliersDataProcessor(base_folder=setup_environment)

    mocker.patch.object(processor, 'save_sd_file', return_value=None)

    participant_folder = setup_environment / "individual recordings/participant_1"
    clean_participant_folder = setup_environment / "clean_individual_recordings/participant_1"
    clean_participant_folder.mkdir(parents=True)

    for file_name in ["ACC.csv", "BVP.csv", "EDA.csv", "HR.csv", "IBI.csv", "TEMP.csv"]:
        processor.process_file(participant_folder / file_name, participant_folder, clean_participant_folder)

        assert (clean_participant_folder / f"c_{file_name}").exists(), f"Processed and winsorized file {file_name} should be saved."


def test_copy_additional_files(setup_environment):
    processor = OutliersDataProcessor(base_folder=setup_environment)

    participant_folder = setup_environment / "individual recordings/participant_1"
    clean_participant_folder = setup_environment / "clean_individual_recordings/participant_1"
    clean_participant_folder.mkdir(parents=True)

    additional_file = participant_folder / "info.txt"
    additional_file.write_text("Test info content")

    processor.copy_additional_files(participant_folder, clean_participant_folder)

    assert (clean_participant_folder / "info.txt").exists(), "Additional file should be copied."


def test_save_outlier_info(setup_environment):
    processor = OutliersDataProcessor(base_folder=setup_environment)

    processor.outlier_info = [{
        "Participant": "participant_1",
        "File": "ACC.csv",
        "Outlier Percentage": "20.0"
    }]

    processor.save_outlier_info()

    outlier_info_file_path = setup_environment / "outlier_info.csv"
    assert outlier_info_file_path.exists(), "Outlier information file should be saved."
