import pandas as pd
from pathlib import Path
import shutil

class UnusualSubjectDataProcessor: 
    def __init__(self, base_folder):
        """
        Initializes an instance of the UnusualSubjectDataProcessor class.
        Parameters:
        - base_folder (str or Path): The base folder path.
        Returns:
        - None
        """
        self.base_folder = Path(base_folder) / "individual recordings"  # Navigate to "individual recordings"

    def folder_and_file_validation(self, subject_folder):
        """
        Validates the subject folder, its subfolders, and the files within them.
        Parameters:
        - subject_folder (Path): The path to the subject folder.
        Returns:
        - bool: True if the folder and files are valid, False otherwise.
        """
        if not subject_folder.is_dir() or not subject_folder.name.startswith('rn'): # Check if the folder is a directory and starts with 'rn'
            print(f"Skipping {subject_folder.name}. Folder must start with 'rn' and be a directory.")
            return False

        subfolders = [f for f in subject_folder.iterdir() if f.is_dir()] # Check if the subject folder has exactly two subfolders
        if len(subfolders) != 2:
            print(f"Skipping {subject_folder.name} because it does not have exactly two subfolders.")
            return False

        for subfolder in subfolders: # Check if the subfolders are not empty and do not contain duplicate files
            if not any(subfolder.iterdir()):
                print(f"Warning: Subfolder {subfolder.name} in {subject_folder.name} is empty.")
                return False

            filenames = [f.name for f in subfolder.iterdir()]
            if len(filenames) != len(set(filenames)):
                print(f"Warning: Duplicate files found in {subfolder.name} of {subject_folder.name}.")
                return False

        return True

    def read_and_validate_csv(self, filepath, folder_name, filename):
        """
        Reads a CSV file and performs basic validation.
        Parameters:
        - filepath (Path): The path to the CSV file.
        - folder_name (str): The name of the folder containing the file.
        - filename (str): The name of the CSV file.
        Returns:
        - pd.DataFrame or None: The DataFrame if valid, None otherwise.
        """
        if not filepath.exists(): # Check if the file exists
            print(f"Expected file {filename} is missing in {folder_name}.")
            return None

        data = pd.read_csv(filepath, header=None) # Check if the file is empty
        if data.empty: 
            print(f"File {filename} is empty in {folder_name}.")
            return None

        return data

    def process_subject_files(self, subject_folder, subfolders):
        """
        Processes the CSV files in the subject subfolders after validation.
        Parameters:
        - subject_folder (Path): The path to the subject folder.
        - subfolders (list of Path): List of subfolder paths.
        Returns:
        - dict: Dictionary containing the filled recordings, or None if validation fails.
        """
        combined_data = {}
        csv_files = ['ACC.csv', 'BVP.csv', 'EDA.csv', 'HR.csv', 'TEMP.csv']

        for csv_file in csv_files: # Process each CSV file
            file_path1 = subfolders[0] / csv_file
            file_path2 = subfolders[1] / csv_file

            recording1 = self.read_and_validate_csv(file_path1, subject_folder.name, csv_file)
            recording2 = self.read_and_validate_csv(file_path2, subject_folder.name, csv_file)
            
            if recording1 is None or recording2 is None: # Skip if any of the files are invalid
                continue

            if recording1.shape[1] != recording2.shape[1]: # Check for mismatched number of columns
                print(f"Error: Mismatched number of columns in {csv_file} for {subject_folder.name}. Skipping these files.")
                continue

            sampling_rate1 = float(recording1.iloc[1, 0]) # Check for negative sampling rates
            sampling_rate2 = float(recording2.iloc[1, 0])
            if sampling_rate1 <= 0 or sampling_rate2 <= 0:
                print(f"Error: Negative or zero sampling rate found in {csv_file} for {subject_folder.name}. Skipping these files.")
                continue

            filled_recording = self.determine_time_gap_and_fill(recording1, recording2, subject_folder) # Fill in missing values
            combined_data[csv_file] = filled_recording

        return combined_data

    def process_subjects(self):
        """
        Processes all subject folders in the base folder.
        Returns:
        - None
        """
        for subject_folder in self.base_folder.iterdir():
            if not self.folder_and_file_validation(subject_folder):
                continue

            subfolders = [f for f in subject_folder.iterdir() if f.is_dir()] 
            combined_data = self.process_subject_files(subject_folder, subfolders)
            if combined_data:
                self.save_combined_data(subject_folder, combined_data) 
                self.copy_additional_files(subject_folder, subfolders) 

                print(f"Processed and saved data for subject: {subject_folder.name}")

    def determine_time_gap_and_fill(self, recording1, recording2, subject_folder):
        """
        Determines the time gap between two recordings and fills in the missing values.
        Parameters:
        - recording1 (pd.DataFrame): The first recording.
        - recording2 (pd.DataFrame): The second recording.
        Returns:
        - pd.DataFrame: The filled recording with the missing values.
        """
        try: # Extract timestamps and sampling rates
            timestamp1 = float(recording1.iloc[0, 0])
            sampling_rate1 = float(recording1.iloc[1, 0])
            timestamp2 = float(recording2.iloc[0, 0])
        except ValueError as e: # Handle errors in converting values to float
            print(f"Error converting values to float: {e}")
            return None

        end1 = timestamp1 + (len(recording1) - 2) / sampling_rate1 # Calculate the end time of the first recording
        start2 = timestamp2 # Calculate the start time of the second recording
        time_gap = start2 - end1 # Calculate the time gap between the two recordings

        if time_gap < 0: # Check for negative time gaps
            print(f"Warning: Negative time gap found between recordings in {subject_folder.name}. Skipping.")
            return None

        no_rows = int(time_gap * sampling_rate1) # Calculate the number of rows to generate
        missing_values = self.generate_dummy_rows(no_rows, recording1.iloc[2:]) # Generate dummy rows with missing values
        filled_recording = self.fill_in_missing_values(recording1, recording2, missing_values) # Fill in missing values

        return filled_recording

    def generate_dummy_rows(self, no_rows, original_data):
        """
        Generates dummy rows with missing values based on the number of rows and the columns of the original data.
        Parameters:
        - no_rows (int): The number of rows to generate.
        - original_data (pd.DataFrame): The original data used to determine the columns.
        Returns:
        - pd.DataFrame: A DataFrame with the same columns as the original data, filled with a placeholder value.
        """
        placeholder = 9999999999 # Placeholder value for missing data
        if placeholder in original_data.values: # Check if the placeholder value already exists in the original data
            print(f"Placeholder value {placeholder} already exists in the original data. Please choose a different placeholder.")
            return None

        missing_values = pd.DataFrame(placeholder, index=range(no_rows), columns=original_data.columns) # Create a DataFrame with missing values
        return missing_values

    def fill_in_missing_values(self, recording1, recording2, missing_values):
        """
        Fills in missing values in a recording by replacing them with the mean value of the corresponding column.
        Parameters:
        - recording1 (pd.DataFrame): The first part of the recording.
        - recording2 (pd.DataFrame): The second part of the recording.
        - missing_values (pd.DataFrame): The DataFrame containing the missing values.
        Returns:
        - pd.DataFrame: The filled recording with missing values replaced by the mean value of the corresponding column.
        """
        if missing_values is None: # Check if missing values are generated
            return None

        recording2 = recording2.iloc[2:].reset_index(drop=True) # Reset the index of the second recording
        filled_recording = pd.concat([recording1, missing_values, recording2], ignore_index=True) # Concatenate the recordings

        filled_recording = filled_recording.apply(self.replace_placeholder, axis=0) # Replace the placeholder values with the mean value 
        return filled_recording

    def replace_placeholder(self, col, placeholder=9999999999):
        """
        Replace the placeholder values in a column with the mean value of the non-placeholder values.
        Parameters:
        - col (pd.Series): The column containing the values to be replaced.
        - placeholder (numeric, optional): The placeholder value to be replaced. Default is 9999999999.
        Returns:
        - pd.Series: The column with the placeholder values replaced by the mean value.
        """
        excl_col = col.iloc[2:] # Exclude the first two rows (timestamps and sampling rates)
        excl_col = excl_col[excl_col != placeholder] # Exclude the placeholder values
        col_mean = round(excl_col.mean(), 1) if not excl_col.empty else placeholder # Calculate the mean value
        col = col.replace(placeholder, col_mean) # Replace the placeholder values with the mean value
        return col

    def save_combined_data(self, subject_folder, combined_data):
        """
        Saves the combined data for each CSV type to new CSV files.
        Parameters:
        - subject_folder (Path): The path to the subject folder.
        - combined_data (dict): The dictionary containing the filled recordings.
        Returns:
        - None
        """
        for csv_file, data in combined_data.items(): # Save the filled recordings to new CSV files
            output_filename = f"Filled_Merged_{csv_file}" # Create the output filename
            output_filepath = subject_folder / output_filename # Create the output filepath
            try: 
                data.to_csv(output_filepath, index=False, header=False)
            except PermissionError: # Handle permission errors
                print(f"Warning: Unable to save {output_filename} in {subject_folder.name}. Check file permissions.")

    def copy_additional_files(self, subject_folder, subfolders):
        """
        Copies additional files (info.txt, tags.csv) from the first subfolder to the subject folder.
        Parameters:
        - subject_folder (Path): The path to the subject folder.
        - subfolders (list of Path): List of subfolder paths.
        Returns:
        - None
        """
        additional_files = ['info.txt', 'tags.csv'] # Additional files to copy to the subject folder
        for additional_file in additional_files:
            additional_file_path = subfolders[0] / additional_file
            if additional_file_path.exists():
                shutil.copy(additional_file_path, subject_folder / additional_file)
                print(f"Copied {additional_file}.")

def run_subject_data_processor(base_folder):
    """
    Function to create an instance of UnusualSubjectDataProcessor and process the subjects.
    """
    processor = UnusualSubjectDataProcessor(base_folder) # Create an instance of UnusualSubjectDataProcessor
    processor.process_subjects() # Process the subjects

# # Example usage:
# base_folder = '/Users/sofiakarageorgiou/Desktop/Hackathon_files_adapt_lab'  # Replace with your actual path
# run_subject_data_processor(base_folder) # Run the subject data processor

#base_folder = "/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab"
#run_subject_data_processor(base_folder)