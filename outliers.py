import pandas as pd
from pathlib import Path
from missing_filling import base_folder
import shutil

class OutliersDataProcessor:
    def __init__(self, base_folder, threshold=2.5):
        self.base_folder = Path(base_folder)
        self.threshold = threshold
        self.recordings_path = self.base_folder / "individual recordings"
        self.clean_recordings_path = self.base_folder / "clean_individual_recordings"
        self.clean_recordings_path.mkdir(exist_ok=True)
        self.keywords = ['ACC', 'BVP', 'EDA', 'HR', 'TEMP']
        self.additional_files = ['info.txt', 'tags.csv']
        self.outlier_info = []

    def filter_out_csv(self, df):
        means = df.mean()
        std_devs = df.std()
        upper_bounds = means + self.threshold * std_devs
        lower_bounds = means - self.threshold * std_devs
        outliers = ((df > upper_bounds) | (df < lower_bounds)).sum()
        total_data_points = len(df)
        percentage_outliers = (outliers / total_data_points) * 100
        return percentage_outliers.mean()

    def save_sd_file(self, df, sd_file_path):
        means = df.mean().round(3)
        std_devs = df.std().round(3)
        upper_bounds = (means + self.threshold * std_devs).round(3)
        lower_bounds = (means - self.threshold * std_devs).round(3)

        sd_df = pd.DataFrame({
            'mean': means,
            f'-{self.threshold}SD': lower_bounds,
            f'+{self.threshold}SD': upper_bounds
        })

        sd_df.reset_index(drop=True, inplace=True)
        sd_df.to_csv(sd_file_path, index=False, header=True)
        print(f"SD file saved as {sd_file_path}")

    def winsorize_data(self, df, lower_bounds, upper_bounds):
        return df.apply(lambda x: x.clip(lower=lower_bounds[x.name], upper=upper_bounds[x.name]))

    def process_file(self, file_path, participant_folder, clean_participant_folder):
        file_name = file_path.name
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
        
        outlier_percentage = self.filter_out_csv(data_rows)
        self.outlier_info.append({
            "Participant": participant_folder.name,
            "File": file_name,
            "Outlier Percentage": f"{outlier_percentage:.1f}"
        })

        sd_file_path = clean_participant_folder / f"sd_{file_name}"
        self.save_sd_file(data_rows, sd_file_path)

        means = data_rows.mean().round(3)
        std_devs = data_rows.std().round(3)
        upper_bounds = (means + self.threshold * std_devs).round(3)
        lower_bounds = (means - self.threshold * std_devs).round(3)
        data_rows = self.winsorize_data(data_rows, lower_bounds, upper_bounds)
        
        final_df = pd.concat([first_row, second_row, data_rows], ignore_index=True)
        clean_file_path = clean_participant_folder / f"c_{file_name}"
        final_df.to_csv(clean_file_path, index=False)
        print(f"File {file_name} has been winsorized and saved as {clean_file_path}")

    def copy_additional_files(self, participant_folder, clean_participant_folder):
        for additional_file in self.additional_files:
            additional_file_path = participant_folder / additional_file
            if additional_file_path.exists():
                shutil.copy(additional_file_path, clean_participant_folder)
                print(f"Copied {additional_file} to {clean_participant_folder}")

    def process_individual_recordings(self):
        for participant_folder in self.recordings_path.iterdir():
            if participant_folder.is_dir():
                print(f"Processing participant: {participant_folder.name}")
                clean_participant_folder = self.clean_recordings_path / f"c_{participant_folder.name}"
                clean_participant_folder.mkdir(exist_ok=True)
                
                for file_path in participant_folder.glob('*.csv'):
                    if any(keyword in file_path.name for keyword in self.keywords):
                        self.process_file(file_path, participant_folder, clean_participant_folder)
                
                self.copy_additional_files(participant_folder, clean_participant_folder)
        
        self.save_outlier_info()

    def save_outlier_info(self):
        outlier_info_df = pd.DataFrame(self.outlier_info)
        outlier_info_file_path = self.base_folder / "outlier_info.csv"
        outlier_info_df.to_csv(outlier_info_file_path, index=False)
        print(f"Outlier information saved to {outlier_info_file_path}")


# Usage with base_folder from missing_filling 
processor = OutliersDataProcessor(base_folder)
processor.process_individual_recordings()
