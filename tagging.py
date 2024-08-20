from pathlib import Path
import pandas as pd

def process_all_files(base_folder):
    base_path = Path(base_folder)
    
    # Iterate over all folders in the base directory
    for folder in base_path.iterdir():
        if folder.is_dir() and folder.name.startswith("rn"):
            hr_file = folder / "HR.csv"
            bvp_file = folder / "BVP.csv"
            temp_file = folder / "TEMP.csv"
            eda_file = folder / "EDA.csv"
            tags_file = folder / "tags.csv"

            # Check if all required files exist
            if hr_file.is_file() and bvp_file.is_file() and temp_file.is_file() and eda_file.is_file() and tags_file.is_file():
                # Read the data from HR.csv, BVP.csv, TEMP.csv, EDA.csv, and tags.csv
                hr_data = pd.read_csv(hr_file, header=None)
                bvp_data = pd.read_csv(bvp_file, header=None)
                temp_data = pd.read_csv(temp_file, header=None)
                eda_data = pd.read_csv(eda_file, header=None)
                tags_data = pd.read_csv(tags_file, header=None)

                # Extract the necessary values from tags.csv
                tag_A1 = tags_data.iloc[0, 0]
                tag_A2 = tags_data.iloc[1, 0]
                tag_A3 = tags_data.iloc[2, 0]

                # Extract the necessary values from each file and calculate the differences, multiplied by A2
                hr_A1 = hr_data.iloc[0, 0]
                hr_A2 = hr_data.iloc[1, 0]
                hr_diff1 = (tag_A1 - hr_A1) * hr_A2
                hr_diff2 = (tag_A2 - hr_A1) * hr_A2
                hr_diff3 = (tag_A3 - hr_A1) * hr_A2

                bvp_A1 = bvp_data.iloc[0, 0]
                bvp_A2 = bvp_data.iloc[1, 0]
                bvp_diff1 = (tag_A1 - bvp_A1) * bvp_A2
                bvp_diff2 = (tag_A2 - bvp_A1) * bvp_A2
                bvp_diff3 = (tag_A3 - bvp_A1) * bvp_A2

                temp_A1 = temp_data.iloc[0, 0]
                temp_A2 = temp_data.iloc[1, 0]
                temp_diff1 = (tag_A1 - temp_A1) * temp_A2
                temp_diff2 = (tag_A2 - temp_A1) * temp_A2
                temp_diff3 = (tag_A3 - temp_A1) * temp_A2

                eda_A1 = eda_data.iloc[0, 0]
                eda_A2 = eda_data.iloc[1, 0]
                eda_diff1 = (tag_A1 - eda_A1) * eda_A2
                eda_diff2 = (tag_A2 - eda_A1) * eda_A2
                eda_diff3 = (tag_A3 - eda_A1) * eda_A2

                # Print the differences for debugging
                print(f"Processing {folder.name}:")
                print(f"HR: diff1={hr_diff1}, diff2={hr_diff2}, diff3={hr_diff3}")
                print(f"BVP: diff1={bvp_diff1}, diff2={bvp_diff2}, diff3={bvp_diff3}")
                print(f"TEMP: diff1={temp_diff1}, diff2={temp_diff2}, diff3={temp_diff3}")
                print(f"EDA: diff1={eda_diff1}, diff2={eda_diff2}, diff3={eda_diff3}")

                # Initialize the time columns with zeros
                time_column_hr = [0] * len(hr_data)
                time_column_bvp = [0] * len(bvp_data)
                time_column_temp = [0] * len(temp_data)
                time_column_eda = [0] * len(eda_data)

                # Update the time column for HR based on the differences, starting from row 3
                for i in range(2, len(hr_data)):
                    if i < hr_diff1:
                        time_column_hr[i] = 0
                    elif hr_diff1 <= i < hr_diff2:
                        time_column_hr[i] = hr_diff1
                    elif hr_diff2 <= i < hr_diff3:
                        time_column_hr[i] = hr_diff2
                    elif i >= hr_diff3:
                        time_column_hr[i] = hr_diff3

                # Update the time column for BVP based on the differences, starting from row 3
                for i in range(2, len(bvp_data)):
                    if i < bvp_diff1:
                        time_column_bvp[i] = 0
                    elif bvp_diff1 <= i < bvp_diff2:
                        time_column_bvp[i] = bvp_diff1
                    elif bvp_diff2 <= i < bvp_diff3:
                        time_column_bvp[i] = bvp_diff2
                    elif i >= bvp_diff3:
                        time_column_bvp[i] = bvp_diff3

                # Update the time column for TEMP based on the differences, starting from row 3
                for i in range(2, len(temp_data)):
                    if i < temp_diff1:
                        time_column_temp[i] = 0
                    elif temp_diff1 <= i < temp_diff2:
                        time_column_temp[i] = temp_diff1
                    elif temp_diff2 <= i < temp_diff3:
                        time_column_temp[i] = temp_diff2
                    elif i >= temp_diff3:
                        time_column_temp[i] = temp_diff3

                # Update the time column for EDA based on the differences, starting from row 3
                for i in range(2, len(eda_data)):
                    if i < eda_diff1:
                        time_column_eda[i] = 0
                    elif eda_diff1 <= i < eda_diff2:
                        time_column_eda[i] = eda_diff1
                    elif eda_diff2 <= i < eda_diff3:
                        time_column_eda[i] = eda_diff2
                    elif i >= eda_diff3:
                        time_column_eda[i] = eda_diff3

                # Add the time columns to the left of each file
                hr_data.insert(0, 'time(s)', time_column_hr)
                bvp_data.insert(0, 'time(s)', time_column_bvp)
                temp_data.insert(0, 'time(s)', time_column_temp)
                eda_data.insert(0, 'time(s)', time_column_eda)

                # Save the updated files as modified versions
                hr_data.to_csv(folder / "HR_modified.csv", index=False, header=False)
                bvp_data.to_csv(folder / "BVP_modified.csv", index=False, header=False)
                temp_data.to_csv(folder / "TEMP_modified.csv", index=False, header=False)
                eda_data.to_csv(folder / "EDA_modified.csv", index=False, header=False)

                print(f"Processed and saved modified files in folder: {folder.name}")



base_path = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/individual_mini'
process_all_files(base_path)