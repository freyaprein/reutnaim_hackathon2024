import pandas as pd
from pathlib import Path
import shutil

def filter_out_csv(df, threshold=2.5):
    # Calculate the mean and standard deviation for each column
    means = df.mean()
    std_devs = df.std()
    
    # Calculate the upper and lower bounds based on the threshold
    upper_bounds = means + threshold * std_devs
    lower_bounds = means - threshold * std_devs
    
    # Determine the proportion of data points that are outliers
    outliers = ((df > upper_bounds) | (df < lower_bounds)).sum()
    total_data_points = len(df)
    
    # Calculate the percentage of outliers
    percentage_outliers = (outliers / total_data_points) * 100
    
    # Debugging: Print out the calculated values
    print(f"Percentage of outliers: {percentage_outliers.mean()}%")
    
    # Check if more than 10% of the data points are outliers
    if percentage_outliers.mean() > 10:
        print("More than 10% of data points are outliers. Excluding the CSV file.")
        return False  # Exclude this CSV file
    else:
        return True  # Include this CSV file

def winsorize_data(df, threshold=2.5):
    # Calculate the mean and standard deviation for each column
    means = df.mean()
    std_devs = df.std()
    
    # Calculate the upper and lower bounds based on the threshold
    upper_bounds = means + threshold * std_devs
    lower_bounds = means - threshold * std_devs
    
    # Winsorize the data: Replace outliers with the threshold values
    df = df.apply(lambda x: x.clip(lower=lower_bounds[x.name], upper=upper_bounds[x.name]))
    
    return df

def save_sd_file(df, sd_file_path, threshold=2.5):
    # Calculate the mean and standard deviation for each column
    means = df.mean()
    std_devs = df.std()
    
    # Calculate the upper and lower bounds based on the threshold
    upper_bounds = means + threshold * std_devs
    lower_bounds = means - threshold * std_devs
    
    # Create a DataFrame to store the SD information
    sd_df = pd.DataFrame({
        'mean': means,
        f'-{threshold}SD': lower_bounds,
        f'+{threshold}SD': upper_bounds
    })
    
    # Save the SD DataFrame to a CSV file
    sd_df.to_csv(sd_file_path, index=True)
    print(f"SD file saved as {sd_file_path}")

def process_individual_recordings(individual_recordings_path):
    # Keywords to identify relevant CSV files
    keywords = ['ACC', 'BVP', 'EDA', 'HR', 'TEMP']
    
    # Additional files to copy
    additional_files = ['info.txt', 'tags.csv']

    # Path to the individual recordings folder
    recordings_path = Path(individual_recordings_path)
    
    # Path to the clean individual recordings folder
    clean_recordings_path = Path(individual_recordings_path).parent / "clean_individual_recordings"
    clean_recordings_path.mkdir(exist_ok=True)

    # Iterate through each participant's folder within the individual recordings folder
    for participant_folder in recordings_path.iterdir():
        if participant_folder.is_dir():
            print(f"Processing participant: {participant_folder.name}")
            clean_participant_folder = clean_recordings_path / f"c_{participant_folder.name}"
            clean_participant_folder.mkdir(exist_ok=True)
            
            # Iterate over all files in the participant folder
            for file_path in participant_folder.glob('*.csv'):
                file_name = file_path.name
                
                # Check if the filename contains any of the keywords
                if any(keyword in file_name for keyword in keywords):
                    print(f"Processing file: {file_name} for participant: {participant_folder.name}")
                    df = pd.read_csv(file_path)
                    
                    # Exclude the first two rows
                    df = df.iloc[2:]
                    
                    # Step 1: Handle missing values
                    for column in df.columns:
                        if df[column].isnull().any():
                            if pd.api.types.is_numeric_dtype(df[column]):
                                mean_value = df[column].mean()
                                df[column].fillna(mean_value, inplace=True)
                                print(f"Filled missing values in {column} with mean: {mean_value}")
                            else:
                                print(f"Non-numeric data type found in column: {column} in file {file_name}")
                    
                    # Step 2: Identify outliers and exclude files if necessary
                    if filter_out_csv(df):
                        # Step 3: Winsorize the data if the file is not excluded
                        df = winsorize_data(df)
                        
                        # Save the processed DataFrame to the clean folder with the 'c_' prefix
                        clean_file_path = clean_participant_folder / f"c_{file_name}"
                        df.to_csv(clean_file_path, index=False)
                        print(f"File {file_name} has been winsorized and saved as {clean_file_path}")
                        
                        # Step 4: Save the SD DataFrame to the clean folder with the 'sd_' prefix
                        sd_file_path = clean_participant_folder / f"sd_{file_name}"
                        save_sd_file(df, sd_file_path)
                    else:
                        print(f"File {file_name} for participant {participant_folder.name} has been excluded due to high outlier count.")
            
            # Copy additional files (info.txt, tags.csv) to the clean folder
            for additional_file in additional_files:
                additional_file_path = participant_folder / additional_file
                if additional_file_path.exists():
                    shutil.copy(additional_file_path, clean_participant_folder)
                    print(f"Copied {additional_file} to {clean_participant_folder}")

# Example usage:
process_individual_recordings('/Users/freyaprein/Desktop/Hackathon 2024 Group2 /Hackathon_files_adapt_lab/individual recordings')
