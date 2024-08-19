import pandas as pd
import numpy as np
from outliers import read_and_prepare_dataframe, filter_participants_by_outliers, apply_winsorization

# Base folder for the file paths
base_folder = "/Users/freyaprein/Documents/GitHub/reutnaim_hackathon2024/"

# List of file names instead of full paths
file_names = [
    "bvp_concatenated.csv",
    "acc_concatenated.csv",
    "eda_concatenated.csv",
    "hr_concatenated.csv",
    "ibi_concatenated.csv"
]

def test_cleaning_process():
    """
    Test that the cleaning process correctly excludes all outliers and participants with too many outliers
    based on the original data's statistics.
    """
    threshold = 2.5  
    all_tests_passed = True

    for file_name in file_names:
        # Combine the base folder with the file name to create the full file path
        orig_file = base_folder + file_name
        
        original_df, timestamps = read_and_prepare_dataframe(orig_file)
        
        means = original_df.mean()
        stds = original_df.std()
        
        upper_limit = means + threshold * stds
        lower_limit = means - threshold * stds
        
        is_outlier = (original_df > upper_limit) | (original_df < lower_limit)
        outlier_percentage = is_outlier.mean() * 100
        
        participants_to_exclude = outlier_percentage[outlier_percentage > 10].index
        
        df_filtered = filter_participants_by_outliers(original_df, threshold=threshold)
        df_winsorized = apply_winsorization(df_filtered, threshold=threshold)
        
        df_winsorized.insert(0, 'Timestamp', timestamps)
        
        df_cleaned = df_winsorized.iloc[:, 1:]
        
        for participant in participants_to_exclude:
            if participant in df_cleaned.columns:
                print(f"Test failed: Participant {participant} in file {orig_file} should have been excluded.")
                all_tests_passed = False
        
        is_outlier_in_cleaned = (df_cleaned > upper_limit) | (df_cleaned < lower_limit)
        if is_outlier_in_cleaned.any().any():
            print(f"Test failed: Outliers are still present in the cleaned data for file {orig_file}.")
            all_tests_passed = False

    if all_tests_passed:
        print("All tests passed successfully.")
    else:
        print("Some tests did not pass. See above for details.")


if __name__ == "__main__":
    test_cleaning_process()
