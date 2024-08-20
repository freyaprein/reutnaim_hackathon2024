import pandas as pd
from pathlib import Path
import shutil

class SubjectDataProcessor: 
    def __init__(self, base_folder):
        self.base_folder = Path(base_folder) / "individual recordings"

    def folder_and_file_validation(self, subject_folder):
        if not subject_folder.is_dir() or not subject_folder.name.startswith('rn'):
            print(f"Skipping {subject_folder.name}. Folder must start with 'rn' and be a directory.")
            return False

        subfolders = [f for f in subject_folder.iterdir() if f.is_dir()]
        if len(subfolders) != 2:
            print(f"Skipping {subject_folder.name} because it does not have exactly two subfolders.")
            return False

        for subfolder in subfolders:
            if not any(subfolder.iterdir()):
                print(f"Warning: Subfolder {subfolder.name} in {subject_folder.name} is empty.")
                return False

            filenames = [f.name for f in subfolder.iterdir()]
            if len(filenames) != len(set(filenames)):
                print(f"Warning: Duplicate files found in {subfolder.name}.")
                return False

        return True

    def read_and_validate_csv(self, filepath, folder_name, filename):
        if not filepath.exists():
            print(f"Expected file {filename} is missing in {folder_name}.")
            return None

        data = pd.read_csv(filepath, header=None)
        if data.empty:
            print(f"File {filename} is empty in {folder_name}.")
            return None

        return data

    def process_subject_files(self, subject_folder, subfolders):
        combined_data = {}
        csv_files = ['ACC.csv', 'BVP.csv', 'EDA.csv', 'HR.csv', 'TEMP.csv', 'IBI.csv']

        for csv_file in csv_files:
            file_path1 = subfolders[0] / csv_file
            file_path2 = subfolders[1] / csv_file

            recording1 = self.read_and_validate_csv(file_path1, subject_folder.name, csv_file)
            recording2 = self.read_and_validate_csv(file_path2, subject_folder.name, csv_file)
            
            if recording1 is None or recording2 is None:
                continue

            if recording1.shape[1] != recording2.shape[1]:
                print(f"Error: Mismatched number of columns in {csv_file} for {subject_folder.name}. Skipping these files.")
                continue
            
            if csv_file == 'IBI.csv':
                # Handle IBI file
                recording1 = self.gap_handling_IBI(recording1)
                recording2 = self.gap_handling_IBI(recording2)
                filled_recording = self.determine_time_gap_and_fill_IBI(recording1, recording2)
                combined_data['IBI.csv'] = filled_recording
            else:
                # Handle other files
                filled_recording = self.determine_time_gap_and_fill(recording1, recording2)
                combined_data[csv_file] = filled_recording

        return combined_data

    def gap_handling_IBI(self, df):
        # Load the IBI data and convert to milliseconds
        df.columns = ['Timestamp', 'IBI']
        df['IBI_ms'] = df['IBI'] * 1000
        df['Time_Diff'] = df['Timestamp'].diff()

        gap_threshold = 1.0  # seconds
        gaps = df[df['Time_Diff'] > gap_threshold]

        if not gaps.empty:
            print("Detected large gaps in IBI data:")
            print(gaps[['Timestamp', 'Time_Diff']])
            df['IBI_ms'] = df['IBI_ms'].interpolate()

        df = df.drop(columns=['Time_Diff'])
        return df

    def determine_time_gap_and_fill_IBI(self, recording1, recording2):
        try:
            timestamp1 = float(recording1.iloc[0, 0])
            timestamp2 = float(recording2.iloc[0, 0])
        except ValueError as e:
            print(f"Error converting values to float: {e}")
            return None

        end1 = recording1.iloc[-1, 0] + recording1['IBI_ms'].iloc[-1]
        time_gap = timestamp2 - end1

        if time_gap < 0:
            print(f"Warning: Negative time gap found between IBI recordings in {subject_folder.name}. Skipping.")
            return None

        # Adjust timestamp of the second recording
        recording2['Timestamp'] += time_gap
        filled_recording = pd.concat([recording1, recording2], ignore_index=True)

        return filled_recording

    def process_subjects(self):
        for subject_folder in self.base_folder.iterdir():
            if not self.folder_and_file_validation(subject_folder):
                continue

            subfolders = [f for f in subject_folder.iterdir() if f.is_dir()]
            combined_data = self.process_subject_files(subject_folder, subfolders)
            if combined_data:
                self.save_combined_data(subject_folder, combined_data)
                self.copy_additional_files(subject_folder, subfolders)
                print(f"Processed and saved data for subject: {subject_folder.name}")

    def save_combined_data(self, subject_folder, combined_data):
        for csv_file, data in combined_data.items():
            output_filename = f"Filled_Merged_{csv_file}" if csv_file != 'HRV.csv' else 'HRV.csv'
            output_filepath = subject_folder / output_filename
            try:
                data.to_csv(output_filepath, index=False, header=False)
            except PermissionError:
                print(f"Warning: Unable to save {output_filename} in {subject_folder.name}. Check file permissions.")

    def copy_additional_files(self, subject_folder, subfolders):
        additional_files = ['info.txt', 'tags.csv']
        for additional_file in additional_files:
            additional_file_path = subfolders[0] / additional_file
            if additional_file_path.exists():
                shutil.copy(additional_file_path, subject_folder / additional_file)
                print(f"Copied {additional_file}.")

def run_subject_data_processor(base_folder):
    processor = SubjectDataProcessor(base_folder)
    processor.process_subjects()

# Example usage:
base_folder = '/path/to/base/folder'  # Replace with your actual path
run_subject_data_processor(base_folder)
