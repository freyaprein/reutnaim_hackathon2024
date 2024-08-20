from pathlib import Path
import pandas as pd

def process_hr_files(base_folder):
    base_path = Path(base_folder)
    
    # Iterate over all folders in the base directory
    for folder in base_path.iterdir():
        if folder.is_dir() and folder.name.startswith("rn"):
            hr_file = folder / "HR.csv"
            tags_file = folder / "tags.csv"

            # Check if both HR.csv and tags.csv exist
            if hr_file.is_file() and tags_file.is_file():
                # Read the data from HR.csv and tags.csv
                hr_data = pd.read_csv(hr_file, header=None)
                tags_data = pd.read_csv(tags_file, header=None)

                # Extract the necessary values
                hr_A1 = hr_data.iloc[0, 0]
                tag_A1 = tags_data.iloc[0, 0]
                tag_A2 = tags_data.iloc[1, 0]
                tag_A3 = tags_data.iloc[2, 0]

                # Calculate the differences
                diff1 = tag_A1 - hr_A1
                diff2 = tag_A2 - hr_A1
                diff3 = tag_A3 - hr_A1


                print(f"diff1: {diff1}, diff2: {diff2}, diff3: {diff3}")


                # Initialize the time column with zeros
                time_column = [0] * len(hr_data)

                # Update the time column based on the differences, starting from row 3
                for i in range(len(hr_data)):
                    if i < diff1:
                        time_column[i] = 0
                    elif diff1 <= i < diff2:
                        time_column[i] = diff1
                    elif diff2 <= i < diff3:
                        time_column[i] = diff2
                    elif i >= diff3:
                        time_column[i] = diff3


                # Add the time column to the left of HR.csv
                hr_data.insert(0, 'time(s)', time_column)

                # Save the updated HR.csv file as HR_modified.csv
                hr_data.to_csv(folder / "HR_modified.csv", index=False, header=False)

                print(f"Processed and saved as HR_modified.csv in folder: {folder.name}")



base_path = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/individual_mini'
process_hr_files(base_path)