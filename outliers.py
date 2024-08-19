import pandas as pd
import numpy as np

def read_and_prepare_dataframe(file_path):
    """
    Reads a CSV file into a DataFrame, removes the timestamp column, and converts data to numeric format.

    Parameters:
    file_path (str): The path to the CSV file.

    Returns:
    pd.DataFrame: DataFrame with the timestamp column removed and participant data.
    pd.Series: Series containing the timestamp data.
    """
    df = pd.read_csv(file_path, header=0, low_memory=False)
    timestamps = df.iloc[:, 0]
    participant_ids = df.columns[1:]
    df = df.iloc[:, 1:]
    df.columns = participant_ids
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.dropna(axis=1, how='all')
    data_type = df.dtypes.unique()
    print(f"Data types in {file_path}: {data_type}")
    return df, timestamps

def filter_participants_by_outliers(df, threshold=2.5):
    """
    Filters out participants who have more than 10% of their data identified as outliers.

    Parameters:
    df (pd.DataFrame): The DataFrame containing participant data.
    threshold (float): The threshold in standard deviations for identifying outliers.

    Returns:
    pd.DataFrame: DataFrame with participants with excessive outliers removed.
    """
    means = df.mean()
    stds = df.std()
    upper_limit = means + threshold * stds
    lower_limit = means - threshold * stds
    is_outlier = (df > upper_limit) | (df < lower_limit)
    outlier_percentage = is_outlier.mean() * 100
    participants_to_exclude = outlier_percentage[outlier_percentage > 10].index
    df_filtered = df.drop(columns=participants_to_exclude)
    return df_filtered

def apply_winsorization(df, threshold=2.5):
    """
    Applies Winsorization to the DataFrame, limiting extreme values to a specified threshold.

    Parameters:
    df (pd.DataFrame): The DataFrame containing participant data.
    threshold (float): The threshold in standard deviations for Winsorization.

    Returns:
    pd.DataFrame: DataFrame with extreme values limited according to the Winsorization threshold.
    """
    means = df.mean()
    stds = df.std()
    upper_limit = means + threshold * stds
    lower_limit = means - threshold * stds
    df_winsorized = df.clip(lower=lower_limit, upper=upper_limit, axis=1)
    return df_winsorized

def process_files(base_folder, file_names, output_dir):
    """
    Processes a list of CSV files by reading, filtering outliers, applying Winsorization, and saving cleaned data.

    Parameters:
    base_folder (str): The base folder where the CSV files are located.
    file_names (list of str): List of file names to be processed.
    output_dir (str): Directory where the processed CSV files will be saved.

    Returns:
    None
    """
    if not output_dir.endswith('/'):
        output_dir += '/'

    if not base_folder.endswith('/'):
        base_folder += '/'

    for file_name in file_names:
        file_path = base_folder + file_name
        df, timestamps = read_and_prepare_dataframe(file_path)
        df_filtered = filter_participants_by_outliers(df)
        df_winsorized = apply_winsorization(df_filtered)
        df_winsorized.insert(0, 'Timestamp', timestamps)
        output_path = output_dir + "cleaned_" + file_name
        df_winsorized.to_csv(output_path, index=False)

base_folder = '/Users/freyaprein/Documents/GitHub/reutnaim_hackathon2024'
file_names = [
    'bvp_concatenated.csv',
    'acc_concatenated.csv',
    'eda_concatenated.csv',
    'hr_concatenated.csv',
    'ibi_concatenated.csv'
]

output_dir = base_folder + '/cleaned_files'

process_files(base_folder, file_names, output_dir)
