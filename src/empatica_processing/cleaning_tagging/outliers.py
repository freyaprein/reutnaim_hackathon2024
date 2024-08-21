import pandas as pd
from pathlib import Path
import shutil


class OutliersDataProcessor:
    """
    A class to process individual recording files by filtering outliers, 
    winsorizing data, and tagging records based on provided sample rate.
    """

    def __init__(self, base_folder, threshold=2.5):
        """
        Initialize the data processor with base folder and threshold for outlier detection.

        Args:
            base_folder (str or Path): The base directory containing recordings.
            threshold (float): The threshold for outlier detection based on standard deviations.
        """
        self.base_folder = Path(base_folder)
        self.threshold = threshold
        self.recordings_path = self.base_folder / "individual recordings"
        self.clean_recordings_path = self.base_folder / "clean_individual_recordings"
        self.clean_recordings_path.mkdir(exist_ok=True)
        self.keywords = ['ACC', 'BVP', 'EDA', 'HR', 'TEMP']
        self.additional_files = ['info.txt', 'tags.csv']
        self.outlier_info = []
        print("Please wait a moment while the outliers are winsorized and the time tags are added in a new column. This may take up to a few minutes...")

    def filter_out_csv(self, df):
        """
        Calculate the percentage of outliers in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to analyze.

        Returns:
            float: The mean percentage of outliers across all columns.
        """
        means = df.mean()
        std_devs = df.std()
        upper_bounds = means + self.threshold * std_devs
        lower_bounds = means - self.threshold * std_devs
        outliers = ((df > upper_bounds) | (df < lower_bounds)).sum()
        total_data_points = len(df)
        percentage_outliers = (outliers / total_data_points) * 100
        return percentage_outliers.mean()

    def save_sd_file(self, df, sd_file_path):
        """
        Save the standard deviation (SD) information to a CSV file.

        Args:
            df (pd.DataFrame): The DataFrame for which to calculate SD.
            sd_file_path (Path): The file path to save the SD information.
        """
        means = df.mean().round(3)
        std_devs = df.std().round(3)
        upper_bounds = (means + self.threshold * std_devs).round(3)
        lower_bounds = (means - self.threshold * std_devs).round(3)

        sd_df = pd.DataFrame({
            'mean': means,
            f'-{self.threshold}SD': lower_bounds,
            f'+{self.threshold}SD': upper_bounds
        })

        # Save the SD information to a CSV file
        sd_df.reset_index(drop=True, inplace=True)
        sd_df.to_csv(sd_file_path, index=False, header=True)
        #print(f"SD file saved as {sd_file_path}")

    def winsorize_data(self, df, lower_bounds, upper_bounds):
        """
        Apply winsorization to the DataFrame to limit extreme values.

        Args:
            df (pd.DataFrame): The DataFrame to winsorize.
            lower_bounds (pd.Series): The lower bounds for each column.
            upper_bounds (pd.Series): The upper bounds for each column.

        Returns:
            pd.DataFrame: The winsorized DataFrame.
        """
        # Clip the data to stay within the specified bounds (winsorization)
        return df.apply(lambda x: x.clip(lower=lower_bounds[x.name], upper=upper_bounds[x.name]))

    def add_tags_column(self, df, tags, sample_rate):
        """
        Add a 'tags' column to the DataFrame based on provided timestamps and sample rate.

        Args:
            df (pd.DataFrame): The DataFrame to tag.
            tags (list): A list of timestamps for tagging.
            sample_rate (float): The sample rate of the recordings.

        Returns:
            pd.DataFrame: The DataFrame with an added 'tags' column.
        """
        tag0, tag1, tag2, tag3 = tags
        baseline = int(round((tag1 - tag0) * sample_rate))
        cognitive_task1 = int(round((tag2 - tag1) * sample_rate)) if tag2 is not None else None
        cognitive_task2 = int(round((tag3 - tag2) * sample_rate)) if tag3 is not None else None

        df['tags'] = ''

        df.loc[0:baseline - 1, 'tags'] = 'Baseline'

        if cognitive_task1 is not None:
            df.loc[baseline:baseline + cognitive_task1 - 1, 'tags'] = 'CognitiveTask1'

        if cognitive_task2 is not None:
            df.loc[baseline + cognitive_task1:baseline + cognitive_task1 + cognitive_task2 - 1, 'tags'] = 'CognitiveTask2'

        last_task = 'CognitiveTask2' if cognitive_task2 is not None else (
            'CognitiveTask1' if cognitive_task1 is not None else 'Baseline')
        df.loc[df['tags'] == '', 'tags'] = last_task

        return df
    def process_file(self, file_path, participant_folder, clean_participant_folder):
        """
        Process a single recording file, including outlier detection, winsorization, 
        and tagging. The processed file is saved in the cleaned recordings folder.

        Args:
            file_path (Path): The path to the file to process.
            participant_folder (Path): The folder containing the participant's data.
            clean_participant_folder (Path): The folder to save the cleaned data.
        """
        file_name = file_path.name
        #print(f"Processing...")
        #print(f"Processing file: {file_name} for participant: {participant_folder.name}")
        df = pd.read_csv(file_path, header=None)
        first_row = df.iloc[:1]
        second_row = df.iloc[1:2]
        data_rows = df.iloc[2:].reset_index(drop=True)

        tags_file = participant_folder / 'tags.csv'
        tags_df = pd.read_csv(tags_file, header=None)

        tag0 = df.iloc[0, 0]
        sample_rate = df.iloc[1, 0]
        tag1 = tags_df.iloc[0, 0] if len(tags_df) > 0 else None
        tag2 = tags_df.iloc[1, 0] if len(tags_df) > 1 else None
        tag3 = tags_df.iloc[2, 0] if len(tags_df) > 2 else None

        # Add the tags column to the data rows
        data_rows = self.add_tags_column(data_rows, [tag0, tag1, tag2, tag3], sample_rate)

        tags_column = data_rows.pop('tags')

        for column in data_rows.columns:
            if data_rows[column].isnull().any():
                if pd.api.types.is_numeric_dtype(data_rows[column]):
                    mean_value = data_rows[column].mean()
                    data_rows[column].fillna(mean_value, inplace=True)
                    print(f"Filled missing values in {column} with mean: {mean_value:.3f}")
                else:
                    print(f"Non-numeric data type found in column: {column} in file {file_name}")

        # Calculate the percentage of outliers in the data
        outlier_percentage = self.filter_out_csv(data_rows)
        self.outlier_info.append({
            "Participant": participant_folder.name,
            "File": file_name,
            "Outlier Percentage": f"{outlier_percentage:.1f}"
        })

        # Save standard deviation information
        sd_file_path = clean_participant_folder / f"sd_{file_name}"
        self.save_sd_file(data_rows, sd_file_path)

        means = data_rows.mean().round(3)
        std_devs = data_rows.std().round(3)
        upper_bounds = (means + self.threshold * std_devs).round(3)
        lower_bounds = (means - self.threshold * std_devs).round(3)
        data_rows = self.winsorize_data(data_rows, lower_bounds, upper_bounds)

        # Add the tags column back to the data
        data_rows['tags'] = tags_column

        final_df = pd.concat([first_row, second_row, data_rows], ignore_index=True)
        clean_file_path = clean_participant_folder / f"c_{file_name}"
        final_df.to_csv(clean_file_path, index=False, header=False)
        #print(f"File {file_name} has been winsorized and saved as {clean_file_path}")

    def copy_additional_files(self, participant_folder, clean_participant_folder):
        """
        Copy additional files (e.g., info.txt, tags.csv) from the participant folder 
        to the cleaned participant folder.

        Args:
            participant_folder (Path): The folder containing the participant's data.
            clean_participant_folder (Path): The folder to save the copied files.
        """
        for additional_file in self.additional_files:
            additional_file_path = participant_folder / additional_file
            if additional_file_path.exists():
                shutil.copy(additional_file_path, clean_participant_folder)
                #print(f"Copied {additional_file} to {clean_participant_folder}")

    def process_individual_recordings(self):
        """
        Process all participant folders and their recording files in the 
        base recordings directory.
        """
        for participant_folder in self.recordings_path.iterdir():
            if participant_folder.is_dir():
                #print(f"Processing participant: {participant_folder.name}")
                clean_participant_folder = self.clean_recordings_path / f"c_{participant_folder.name}"
                clean_participant_folder.mkdir(exist_ok=True)

                # Process each CSV file matching the keywords in the participant's folder
                for file_path in participant_folder.glob('*.csv'):
                    if any(keyword in file_path.name for keyword in self.keywords):
                        self.process_file(file_path, participant_folder, clean_participant_folder)

                # Copy additional files like info.txt and tags.csv
                self.copy_additional_files(participant_folder, clean_participant_folder)

        # Save the collected outlier information
        self.save_outlier_info()
        print("All individual recordings have been processed and saved to the 'clean_individual_recordings' folder.")

    def save_outlier_info(self):
        """
        Save the outlier information collected during processing to a CSV file.
        """
        outlier_info_df = pd.DataFrame(self.outlier_info)
        outlier_info_file_path = self.base_folder / "outlier_info.csv"
        outlier_info_df.to_csv(outlier_info_file_path, index=False)
        print(f"Outlier information saved to {outlier_info_file_path}")