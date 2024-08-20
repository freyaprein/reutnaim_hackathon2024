import pandas as pd
import numpy as np
from pathlib import Path

class IBIhandling:
    def __init__(self, base_folder):
        self.base_folder = Path(base_folder)

    def ibi_handling(self):
        # Iterate through each participant's folder within the base folder
        for participant_folder in self.base_folder.glob('rn23*'):  # Assuming participant folders start with 'rn23'
            if participant_folder.is_dir():
                ibi_file = participant_folder / 'IBI.csv'  # Assuming the IBI file is named 'IBI.csv'
                if ibi_file.exists():
                    df = pd.read_csv(ibi_file)
                    handled_df = self.gap_handling(df)
                    HRV = self.calculate_HRV(handled_df)
                    self.save_HRV(handled_df, HRV, participant_folder)

    def gap_handling(self, df):
        # Convert the IBI from seconds to milliseconds for HRV calculations
        df['IBI_ms'] = df['IBI'] * 1000

        # Calculate the time differences between consecutive timestamps
        df['Time_Diff'] = df['Timestamp'].diff()

        # Define a threshold for detecting large gaps (e.g., 1 second)
        gap_threshold = 1.5  # seconds

        # Identify rows where the time difference exceeds the threshold
        gaps = df[df['Time_Diff'] > gap_threshold]

        if not gaps.empty:
            print(f"Detected large gaps in the data for {df['Timestamp'][0]} at the following timestamps:")
            print(gaps[['Timestamp', 'Time_Diff']])

            # Interpolate missing data across gaps
            df['IBI_ms'] = df['IBI_ms'].interpolate()

            # If you prefer to remove rows with large gaps instead of interpolation, uncomment the line below
            # df = df[df['Time_Diff'] <= gap_threshold]

        # Drop the Time_Diff column as it's no longer needed
        df = df.drop(columns=['Time_Diff'])

        return df

    def calculate_HRV(self, df):
        # Calculate RMSSD (Root Mean Square of Successive Differences)
        diffs = np.diff(df['IBI_ms'])
        squared_diffs = np.square(diffs)
        rmssd = np.sqrt(np.mean(squared_diffs))

        print(f'Calculated RMSSD: {rmssd} ms')

        return rmssd

    def save_HRV(self, df, HRV, participant_folder):
        # Save the HRV and cleaned data to a new CSV file
        df['RMSSD'] = HRV  # Adding the RMSSD value to the dataframe if needed
        HRV_file = participant_folder / 'HRV.csv'
        df.to_csv(HRV_file, index=False)
        print(f'HRV data saved to {HRV_file}')

# Usage Example
base_folder_path = 'C:\Users\denis\Downloads\Hackathon_files_adapt_lab.zip\Hackathon_files_adapt_lab\individual recordings'  # Replace with the path to your base folder
handler = IBIhandling(base_folder_path)
handler.ibi_handling()



