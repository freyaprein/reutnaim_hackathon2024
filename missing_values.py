import numpy as np
import pandas as pd
from scipy import stats
import os
import shutil

# WE NEED TO REPEAT THIS FOR EACH PHYSIOLOGICAL MEASURE SO WE NEED A FOR LOOP THAT ITERATES THORUGH EACH MEASURE AND EACH SUBJECT 
# AND IDENTIFIES SUBJECTS WITH 2 FOLDERS AND THEN RUNS THE FUNCTION BELOW
# IF THERE ARE 3 FOLDERS, RETURN WARNING
# USE TRY FUNCTION TO CATCH ERRORS
# WE NEED TO CONSIDER THAT SOME MEASURES INCLUDE MULTIPLE AXES -> E.G., ACC 

def missing_values(path):
    """
    This function takes a path as input and performs the following steps:
    1. Load two recordings from CSV files.
    2. Determine the time gap between the two recordings.
    3. Generate missing values based on the time gap.
    4. Fill in the missing values in the first recording.
    5. Save the filled recording in a new CSV file.
    Parameters:
    - path (str): The path to the directory containing the CSV files.
    Returns:
    - None
    Example usage:
    missing_values('/path/to/directory')
    """
    
    def load_data():
        # Load the data
        # Define the path to the 'individual recordings' folder
        base_folder = '/path/to/individual_recordings'  # Replace with your actual path

        # Iterate through each folder inside the 'individual recordings' folder
        for rn_folder in os.listdir(base_folder):
            rn_folder_path = os.path.join(base_folder, rn_folder)
    
        # Check if it's a directory that matches 'rn23*'
        if os.path.isdir(rn_folder_path) and rn_folder.startswith('rn23'):
            subfolders = [f for f in os.listdir(rn_folder_path) if os.path.isdir(os.path.join(rn_folder_path, f))]
            
            # If there are exactly 2 subfolders
            if len(subfolders) == 2:
                for subfolder in subfolders:
                    subfolder_path = os.path.join(rn_folder_path, subfolder)
                    
                    # Rename and copy files from the subfolder
                    for file_name in os.listdir(subfolder_path):
                        file_path = os.path.join(subfolder_path, file_name)
                        suffix = subfolder[-1]  # Assuming subfolders are named '1', '2', etc.
                        new_file_name = f"{file_name.split('.')[0]}{suffix}.{file_name.split('.')[1]}"
                        shutil.copy(file_path, os.path.join(rn_folder_path, new_file_name))
            
            # If the contents are not as expected, print a message
            else:
                print(f"Skipping {rn_folder_path}: unexpected content or structure.")

    
    def determine_time_gap(recording1, recording2):
        # Determine the time gap
        time_gap = recording2['timestamp'].iloc[0] - recording1['timestamp'].iloc[-1]
        return time_gap
    
        # NOTE: CHECK HOW WE NEED TO CALCULATE THE TIME!!!!!
        # alternative 
        # end_time_recording1 = recording1['time_column'].iloc[-1]
        # start_time_recording2 = recording2['time_column'].iloc[0]
        # time_gap = start_time_recording2 - end_time_recording1

    # GENERATE MISSING VALUES AND TAG THEM IN A SEPARATE COLUMN
    
    def generate_dummy_rows(recording1, recording2, time_gap):
        # Generate missing values
        missing_values = pd.DataFrame(columns=recording1.columns)
        for i in range(1, time_gap):
            missing_values = missing_values.append(pd.Series(), ignore_index=True)
        return missing_values
    
        # alternative
        # missing_times = pd.date_range(end_time_recording1, start_time_recording2, periods=desired_number_of_missing_points, closed='right')
        # missing_data = pd.DataFrame({'time_column': missing_times})
        
    def fill_in_missing_values(recording1, recording2, missing_values):
        # Fill in missing values
        filled_recording1 = pd.concat([recording1, missing_values, recording2], ignore_index=True)
        return filled_recording1

        # alternative
        # Add placeholder rows with NaN values
        # for col in recording1.columns:
        #     if col != 'time_column':
        #         missing_data[col] = np.nan

        # # Combine the first recording with the missing data
        # combined_data = pd.concat([recording1, missing_data], ignore_index=True)

        # # Interpolate the missing values
        # combined_data.interpolate(method='linear', inplace=True)
        
        #Concatinate recordings
        # final_combined_recording = pd.concat([combined_data, recording2], ignore_index=True)
        # return final_combined_recording
        
    def save_in_new_csv_file (filled_recording1):
        filled_recording1.to_csv('path_to_filled_recording.csv', index=False)


