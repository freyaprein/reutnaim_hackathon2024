import pandas as pd
from pathlib import Path
import shutil

class SubjectDataProcessor: # Class to process the data of the subjects
    def __init__(self, base_folder):
        """
        Initializes an instance of the MissingFilling class.
        Parameters:
        - base_folder (str or Path): The base folder path.
        Returns:
        - None
        """
        self.base_folder = Path(base_folder)

    # Loop through the subjects in the base folder
    def process_subjects(self): # Function to process the subjects 
        """
        Function to process the subjects.
        This function iterates over the folders in the base folder and processes the subjects that meet the following criteria:
        - The folder name starts with 'rn'.
        - The subject folder contains exactly two subfolders.
        For each subject, the function performs the following steps:
            1. Loads data from two subfolders for each CSV file type (e.g., ACC.csv, BVP.csv).
            2. Determines the time gap and fills the missing values in the recordings.
            3. Stores the filled recordings in a dictionary.
            4. Saves the filled recordings to new CSV files.
            5. Prints a message indicating the successful processing and saving of data for the subject.
        If any exception occurs during the processing of a subject, an error message is printed.
        Note: This function assumes that the base folder contains subject folders, and each subject folder contains two subfolders.
        Parameters:
        - None
        Returns:
        - None
        """
        
        for subject_folder in self.base_folder.iterdir(): # Iterate over the folders in the base folder
            if subject_folder.is_dir() and subject_folder.name.startswith('rn'):
                subfolders = [f for f in subject_folder.iterdir() if f.is_dir()]
                
                if len(subfolders) == 2: # Check if there are two subfolders
                    try:
                        combined_data = {} # Initialize a dictionary to store combined data for each CSV file type

                        csv_files = ['ACC.csv', 'BVP.csv', 'EDA.csv', 'HR.csv', 'TEMP.csv'] # Iterate over each CSV file type (e.g., ACC.csv, BVP.csv)
                        # Additional files to copy
                        additional_files = ['info.txt', 'tags.csv']
    
                        for csv_file in csv_files:
                            recording1 = pd.read_csv(subfolders[0] / csv_file, header=None) # Load the data from the first subfolder
                            recording2 = pd.read_csv(subfolders[1] / csv_file, header=None) # Load the data from the second subfolder

                            filled_recording = self.determine_time_gap_and_fill(recording1, recording2) # Determine the time gap and fill the missing values
                            
                            combined_data[csv_file] = filled_recording # Store the filled recording in the dictionary
                        
                        for csv_file, data in combined_data.items(): 
                            output_filename = f"Filled_Merged_{csv_file}" 
                            output_filepath = subject_folder / output_filename
                            self.save_in_new_csv_file(data, output_filepath) # Save the filled recording to a new CSV file
                        
                        for additional_file in additional_files:
                            additional_file_path = subject_folder / subfolders[0] / additional_file
                            if additional_file_path.exists():
                                shutil.copy(additional_file_path , subject_folder / f"Filled_Merged_{additional_file}")
                                print(f"Copied {additional_file}")
                    
                        print(f"Processed and saved data for subject: {subject_folder.name}")
                        
                    except Exception as e: # Handle exceptions
                        print(f"Error processing {subject_folder.name}: {e}")
        
                else: # Skip the subject if there are not exactly two subfolders
                    print(f"Skipping recording of {subject_folder.name} because it does not have two folders.")

    # Function to determine the time gap and fill the missing values
    def determine_time_gap_and_fill(self, recording1, recording2): 
        """
        Determines the time gap between two recordings and fills in the missing values.
        Args:
            recording1 (pandas.DataFrame): The first recording.
            recording2 (pandas.DataFrame): The second recording.
        Returns:
            pandas.DataFrame: The filled recording with the missing values.
        Raises:
            ValueError: If there is an error converting values to float or if the sampling rate is zero.
        """
        
        try: 
            timestamp1 = float(recording1.iloc[0, 0]) # Extract the timestamp from the first row
            sampling_rate1 = float(recording1.iloc[1, 0]) # Extract the sampling rate from the second row
            timestamp2 = float(recording2.iloc[0, 0]) # Extract the timestamp from the first row
        except ValueError as e: # Handle value errors
            raise ValueError(f"Error converting values to float: {e}")
        
        if sampling_rate1 == 0: # Check if the sampling rate is zero
            raise ValueError(f"Invalid sampling rate in {recording1}. Cannot be zero.")

        timestamp2 = float(recording2.iloc[0, 0]) # Extract the timestamp from the first row
        
        samples1 = len(recording1) - 2  # Count the number of data rows in the first recording and subtract the first two rows (timestamp and sampling rate)
        end1 = timestamp1 + (samples1 / sampling_rate1) # Calculate the end time of the first recording
        start2 = timestamp2 # Start time of the second recording
        
        time_gap = start2 - end1 # Calculate the time gap between the two recordings
        no_rows = int(time_gap * sampling_rate1) # Calculate the number of extra rows needed to fill the time gap

        missing_values = self.generate_dummy_rows(no_rows, recording1.iloc[2:]) # Generate dummy rows to fill the time gap

        filled_recording = self.fill_in_missing_values(recording1, recording2, missing_values) # Fill in the missing values

        return filled_recording

    def generate_dummy_rows(self, no_rows, original_data): 
        """
        Generates dummy rows with missing values based on the number of rows and the columns of the original data.
        Parameters:
        - no_rows (int): The number of rows to generate.
        - original_data (pandas.DataFrame): The original data used to determine the columns.
        Returns:
        - missing_values (pandas.DataFrame): A DataFrame with the same columns as the original data, filled with a placeholder value.
        """
        
        placeholder = 9999999999  # A large number unlikely to appear in real data
        missing_values = pd.DataFrame(placeholder, index=range(no_rows), columns=original_data.columns) # Create a DataFrame with the same columns as the original data
    
        # Debug: Check the data types of missing_values
        # print("Data types of missing_values after filling with placeholder:", missing_values.dtypes)
    
        return missing_values


    def fill_in_missing_values(self, recording1, recording2, missing_values):
        """
        Fills in missing values in a recording by replacing them with the mean value of the corresponding column.
        Args:
            recording1 (pandas.DataFrame): The first part of the recording.
            recording2 (pandas.DataFrame): The second part of the recording.
            missing_values (pandas.DataFrame): The DataFrame containing the missing values.
        Returns:
            pandas.DataFrame: The filled recording with missing values replaced by the mean value of the corresponding column.
        """
        
        recording2 = recording2.iloc[2:].reset_index(drop=True) # Delete the first two rows and reset the index
        
        filled_recording = pd.concat([recording1, missing_values, recording2], ignore_index=True)  # Concatenate recording1, missing_values, and recording2

        def replace_placeholder(col, placeholder=9999999999):
            """
            Replace the placeholder values in a column with the mean value of the non-placeholder values.
            Parameters:
            col (pandas.Series): The column containing the values to be replaced.
            placeholder (numeric, optional): The placeholder value to be replaced. Default is 9999999999.
            Returns:
            pandas.Series: The column with the placeholder values replaced by the mean value.
            """

            # Exclude the first two rows and any placeholders for the mean calculation
            excl_col = col.iloc[2:]  # Exclude the first two rows
            excl_col = excl_col[excl_col != placeholder]  # Exclude the placeholder values

            # Calculate the mean of the filtered values
            col_mean = round(excl_col.mean(), 1) # Round the mean to one decimal place
            
            # Debug: Print the mean value to replace the placeholder
            # print(f"Mean value to replace placeholder in {col.name}: {col_mean}")
            
            # Replace the placeholder values with the mean
            col = col.replace(placeholder, col_mean)
        
            return col

        filled_recording = filled_recording.apply(replace_placeholder, axis=0)

        return filled_recording

    def save_in_new_csv_file(self, filled_recording, output_filepath):
        """
        Save the filled recording DataFrame into a new CSV file.
        Parameters:
        - filled_recording (DataFrame): The filled recording DataFrame.
        - output_filepath (str): The filepath of the output CSV file.
        Returns:
        - None
        """
        # Skip the first row and save the rest of the DataFrame
        filled_recording.to_csv(output_filepath, index=False, header=False) # Save the filled recording to a new CSV file

def run_subject_data_processor(base_folder):
    """
    Function to create an instance of SubjectDataProcessor and process the subjects.
    """
    processor = SubjectDataProcessor(base_folder)
    processor.process_subjects()


# Example usage:
base_folder = '/Users/sofiakarageorgiou/Desktop/Hackathon_files_adapt_lab/individual recordings'  # Replace with your actual path
run_subject_data_processor(base_folder)
