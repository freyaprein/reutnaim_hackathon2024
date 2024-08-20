import pandas as pd
from pathlib import Path

def calculate_sample_rate(file_path):
    df = pd.read_csv(file_path, nrows=1)
    sample_rate = df.iloc[0, 0]
    return sample_rate

def calculate_tag_differences(tags):
    diffs = []
    for i in range(1, len(tags)):
        diffs.append(tags[i] - tags[i - 1])
    return diffs

def process_csv_files(workspace_folder):
    workspace_path = Path(workspace_folder)
    
    # Iterate through all participant folders
    for participant_folder in workspace_path.iterdir():
        if participant_folder.is_dir():
            # Look for the tags.csv file in each participant folder
            tags_file_path = participant_folder / 'tags.csv'
            if not tags_file_path.exists():
                print(f"No tags.csv found in {participant_folder}")
                continue
            
            tags_df = pd.read_csv(tags_file_path, header=None)

            # Identify the row where 'UTC' is found in the first column
            utc_row = tags_df[tags_df[0] == 'UTC']
            if utc_row.empty:
                print(f"'UTC' not found in {tags_file_path}")
                continue

            # Extract the tag values from the identified row
            utc_tags = utc_row.iloc[0, 1:4].dropna().values
            if len(utc_tags) < 2:
                print(f"Not enough tags found in {tags_file_path}")
                continue
            
            # Calculate differences between tags
            tag_diffs = calculate_tag_differences(utc_tags)
            
            # Process each CSV file with ACC, EDA, BVP, HR, TEMP, or TAG in the name
            for csv_file in participant_folder.glob("**/*[ACC|EDA|BVP|HR|TEMP|tag]*.csv"):
                sample_rate = calculate_sample_rate(csv_file)
                
                # Multiply differences by the sample rate
                scaled_diffs = [diff * sample_rate for diff in tag_diffs]
                
                # Load the original data, skipping the first row
                data_df = pd.read_csv(csv_file, skiprows=1)
                
                # Create the new column based on the tag differences
                new_col = []
                for i in range(len(data_df)):
                    if i < scaled_diffs[0]:
                        new_col.append(scaled_diffs[0])
                    elif len(scaled_diffs) > 1 and i < scaled_diffs[0] + scaled_diffs[1]:
                        new_col.append(scaled_diffs[1])
                    elif len(scaled_diffs) > 2 and i < scaled_diffs[0] + scaled_diffs[1] + scaled_diffs[2]:
                        new_col.append(scaled_diffs[2])
                    else:
                        new_col.append(None)
                
                # Add the new column to the DataFrame
                data_df['diff_tag'] = [None] + new_col[1:]
                
                # Save the updated DataFrame back to the file
                data_df.to_csv(csv_file, index=False)
                print(f"Processed and updated {csv_file.name}")

# Call the function with the path to your workspace containing the CLEAN participant folders
process_csv_files("/Users/freyaprein/Desktop/Hackathon 2024 Group2 /Hackathon_files_adapt_lab/clean_individual_recordings")
