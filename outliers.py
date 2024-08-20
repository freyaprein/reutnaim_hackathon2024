
import pandas as pd
from pathlib import Path
import shutil

def filter_out_csv(df, threshold=2.5):
    means = df.mean()
    std_devs = df.std()
    upper_bounds = means + threshold * std_devs
    lower_bounds = means - threshold * std_devs
    outliers = ((df > upper_bounds) | (df < lower_bounds)).sum()
    total_data_points = len(df)
    percentage_outliers = (outliers / total_data_points) * 100
    print(f"Percentage of outliers: {percentage_outliers.mean():.3f}%")
    return percentage_outliers.mean() <= 10

def save_sd_file(df, sd_file_path, threshold=2.5):
    # Calculate the mean and standard deviation only for the actual data rows
    means = df.mean().round(3)
    std_devs = df.std().round(3)
    upper_bounds = (means + threshold * std_devs).round(3)
    lower_bounds = (means - threshold * std_devs).round(3)

    # Create the DataFrame for SD values with rounded numbers
    sd_df = pd.DataFrame({
        'mean': means,
        f'-{threshold}SD': lower_bounds,
        f'+{threshold}SD': upper_bounds
    })
    
    # Ensure that the original headers are not included in the sd_ file by saving only the computed stats
    sd_df.reset_index(drop=True, inplace=True)  # Remove any index that could carry over headers
    sd_df.to_csv(sd_file_path, index=False, header=True)
    print(f"SD file saved as {sd_file_path}")

def winsorize_data(df, lower_bounds, upper_bounds):
    return df.apply(lambda x: x.clip(lower=lower_bounds[x.name], upper=upper_bounds[x.name]))

def process_individual_recordings(base_folder):
    keywords = ['ACC', 'BVP', 'EDA', 'HR', 'TEMP']
    additional_files = ['info.txt', 'tags.csv']
    recordings_path = Path(base_folder) / "individual recordings"
    clean_recordings_path = Path(base_folder) / "clean_individual_recordings"
    clean_recordings_path.mkdir(exist_ok=True)

    for participant_folder in recordings_path.iterdir():
        if participant_folder.is_dir():
            print(f"Processing participant: {participant_folder.name}")
            clean_participant_folder = clean_recordings_path / f"c_{participant_folder.name}"
            clean_participant_folder.mkdir(exist_ok=True)
            
            for file_path in participant_folder.glob('*.csv'):
                file_name = file_path.name
                if any(keyword in file_name for keyword in keywords):
                    print(f"Processing file: {file_name} for participant: {participant_folder.name}")
                    df = pd.read_csv(file_path)
                    first_row = df.iloc[:1]
                    second_row = df.iloc[1:2]
                    data_rows = df.iloc[2:]

                    for column in data_rows.columns:
                        if data_rows[column].isnull().any():
                            if pd.api.types.is_numeric_dtype(data_rows[column]):
                                mean_value = data_rows[column].mean()
                                data_rows[column].fillna(mean_value, inplace=True)
                                print(f"Filled missing values in {column} with mean: {mean_value:.3f}")
                            else:
                                print(f"Non-numeric data type found in column: {column} in file {file_name}")
                    
                    sd_file_path = clean_participant_folder / f"sd_{file_name}"
                    save_sd_file(data_rows, sd_file_path)

                    means = data_rows.mean().round(3)
                    std_devs = data_rows.std().round(3)
                    upper_bounds = (means + 2.5 * std_devs).round(3)
                    lower_bounds = (means - 2.5 * std_devs).round(3)
                    data_rows = winsorize_data(data_rows, lower_bounds, upper_bounds)
                    
                    final_df = pd.concat([first_row, second_row, data_rows], ignore_index=True)
                    clean_file_path = clean_participant_folder / f"c_{file_name}"
                    final_df.to_csv(clean_file_path, index=False)
                    print(f"File {file_name} has been winsorized and saved as {clean_file_path}")
            
            for additional_file in additional_files:
                additional_file_path = participant_folder / additional_file
                if additional_file_path.exists():
                    shutil.copy(additional_file_path, clean_participant_folder)
                    print(f"Copied {additional_file} to {clean_participant_folder}")

# Example usage:
base_folder="/Users/freyaprein/Desktop/Hackathon 2024 Group2 /Hackathon_files_adapt_lab/"
process_individual_recordings(base_folder)
