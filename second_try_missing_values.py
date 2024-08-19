import pandas as pd
from pathlib import Path

class SubjectDataProcessor:
    def __init__(self, base_folder):
        self.base_folder = Path(base_folder)

    def process_subjects(self):
        for subject_folder in self.base_folder.iterdir():
            if subject_folder.is_dir() and subject_folder.name.startswith('rn'):
                subfolders = [f for f in subject_folder.iterdir() if f.is_dir()]
                
                if len(subfolders) == 2:
                    try:
                        # Initialize a dictionary to store combined data for each CSV file type
                        combined_data = {}

                        # Iterate over each CSV file type (e.g., ACC.csv, BVP.csv)
                        csv_files = ['ACC.csv', 'BVP.csv', 'EDA.csv', 'HR.csv', 'IBI.csv', 'TEMP.csv']
                        for csv_file in csv_files:
                            # Load data from both subfolders
                            recording1 = pd.read_csv(subfolders[0] / csv_file, header=None)
                            recording2 = pd.read_csv(subfolders[1] / csv_file, header=None)

                            # Process the data
                            filled_recording = self.determine_time_gap_and_fill(recording1, recording2)
                            
                            # Store the result in the dictionary
                            combined_data[csv_file] = filled_recording
                        
                        # Save the combined data for each CSV type
                        for csv_file, data in combined_data.items():
                            output_filename = f"Filled_Merged_{csv_file}"
                            output_filepath = subject_folder / output_filename
                            self.save_in_new_csv_file(data, output_filepath)
                        
                        print(f"Processed and saved data for subject: {subject_folder.name}")
                        
                    except Exception as e:
                        print(f"Error processing {subject_folder.name}: {e}")
        
                else:
                    print(f"Unexpected content in {subject_folder.name}. Skipping.")

    def determine_time_gap_and_fill(self, recording1, recording2):
        # Extract the timestamp and sampling rate from the first and second rows
        try:
            timestamp1 = float(recording1.iloc[0, 0])
            sampling_rate1 = float(recording1.iloc[1, 0])
            timestamp2 = float(recording2.iloc[0, 0])
        except ValueError as e:
            raise ValueError(f"Error converting values to float: {e}")
        
        if sampling_rate1 == 0:
            raise ValueError(f"Invalid sampling rate in {recording1}. Cannot be zero.")

        timestamp2 = float(recording2.iloc[0, 0])

        # Count the number of data rows in each recording
        samples1 = len(recording1) - 2  # Subtract 2 for the header and sampling rate rows

        # Calculate the end time of the first recording
        end1 = timestamp1 + (samples1 / sampling_rate1)

        # Start time of the second recording
        start2 = timestamp2

        # Calculate the time gap
        time_gap = start2 - end1

        # Calculate the number of extra rows needed
        no_rows = int(time_gap * sampling_rate1)

        # Generate the dummy rows
        missing_values = self.generate_dummy_rows(no_rows, recording1.iloc[2:])

        # Fill in the missing values
        filled_recording = self.fill_in_missing_values(recording1, recording2, missing_values)

        return filled_recording

    def generate_dummy_rows(self, no_rows, original_data):
        # Create a DataFrame with the same columns as the original data and no_rows filled with NaN
        missing_values = pd.DataFrame(pd.NA, index=range(no_rows), columns=original_data.columns)
        
        # Convert all columns to float64 to match the original data types
        missing_values = missing_values.astype('float64')
        
        # Debug: Check the data types of missing_values
        print("Data types of missing_values after conversion:", missing_values.dtypes)
        
        return missing_values


    def fill_in_missing_values(self, recording1, recording2, missing_values):
        # Delete the first two rows of recording2
        recording2 = recording2.iloc[2:].reset_index(drop=True)

        # Debug: Ensure data types are consistent before concatenation
        print("Data types of recording1 before concatenation:", recording1.dtypes)
        print("Data types of recording2 before concatenation:", recording2.dtypes)
        
        # Concatenate recording1, missing_values, and recording2
        filled_recording = pd.concat([recording1, missing_values, recording2], ignore_index=True)

        # Debug: Check the data types after concatenation
        print("Data types after concatenation:", filled_recording.dtypes)

        # Fill the NaN values in the dummy rows with the mean of each column
        filled_recording = filled_recording.apply(lambda col: col.fillna(col.mean()), axis=0)

        return filled_recording

    def save_in_new_csv_file(self, filled_recording, output_filepath):
        filled_recording.to_csv(output_filepath, index=False)


def run_subject_data_processor(base_folder):
    """
    Function to create an instance of SubjectDataProcessor and process the subjects.
    """
    processor = SubjectDataProcessor(base_folder)
    processor.process_subjects()


# Example usage:
base_folder = '/Users/sofiakarageorgiou/Desktop/Hackathon_files_adapt_lab/individual recordings'  # Replace with your actual path
run_subject_data_processor(base_folder)
