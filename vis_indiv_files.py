from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Prompt the user for the participant ID
participant_id = input("Please enter the participant ID in the form '#####': ")

# Define the folder path based on the participant ID
folder_name = f"c_rn{participant_id}"
base_path = Path("/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/c_individual recordings_test")  # Replace with the actual path to your main folder
folder_path = base_path / folder_name


# Define the file paths to the c_BVP.csv, c_HR.csv, c_EDA.csv, c_TEMP.csv, and tags.csv files
bvp_file_path = folder_path / "c_BVP.csv"
hr_file_path = folder_path / "c_HR.csv"
eda_file_path = folder_path / "c_EDA.csv"
temp_file_path = folder_path / "c_TEMP.csv"
tags_file_path = folder_path / "tags.csv"

# Check if the files exist
if not bvp_file_path.is_file() or not hr_file_path.is_file() or not eda_file_path.is_file() or not temp_file_path.is_file() or not tags_file_path.is_file():
    print(f"One or more files for participant ID {participant_id} do not exist.")
else:
    # Load the BVP data, skipping the first two rows
    bvp_data = pd.read_csv(bvp_file_path, skiprows=2, header=None)

    # Load the value from cell A1 of the BVP file
    a1_value = pd.read_csv(bvp_file_path, nrows=1, header=None).iloc[0, 0]

    # Load the HR data, skipping the first two rows
    hr_data = pd.read_csv(hr_file_path, skiprows=2, header=None)

    # Load the EDA data, skipping the first two rows
    eda_data = pd.read_csv(eda_file_path, skiprows=2, header=None)

    # Load the TEMP data, skipping the first two rows
    temp_data = pd.read_csv(temp_file_path, skiprows=2, header=None)

    # Load the tags data
    tags_data = pd.read_csv(tags_file_path, header=None)

    # Subtract the A1 value from each tag value
    adjusted_tag_x_values = tags_data[0] - a1_value

    # Create the x-axis values
    bvp_x_values = [i * 0.015625 for i in range(len(bvp_data))]
    hr_x_values = list(range(len(hr_data)))
    eda_x_values = [i * 0.25 for i in range(len(eda_data))]
    temp_x_values = [i * 0.25 for i in range(len(temp_data))]

    # Determine the common x-axis limits
    x_min = 0
    x_max = max(bvp_x_values[-1], hr_x_values[-1], eda_x_values[-1], temp_x_values[-1])

    # Create subplots with a smaller figure size
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 8), sharex=True)

    # Set a single title for the entire figure
    fig.suptitle(f'Data for Participant {participant_id}', fontsize=14, y=0.95)

    # Plot BVP data in the first subplot
    ax1.plot(bvp_x_values, bvp_data[0], color='blue')
    ax1.set_ylabel('BVP Value')
    ax1.grid(True)

    # Plot HR data in the second subplot
    ax2.plot(hr_x_values, hr_data[0], color='red')
    ax2.set_ylabel('HR Value')
    ax2.grid(True)

    # Plot EDA data in the third subplot
    ax3.plot(eda_x_values, eda_data[0], color='green')
    ax3.set_ylabel('EDA Value')
    ax3.grid(True)

    # Plot TEMP data in the fourth subplot
    ax4.plot(temp_x_values, temp_data[0], color='purple')
    ax4.set_ylabel('TEMP Value')
    ax4.set_xlabel('Time (s)')
    ax4.grid(True)

    # Plot adjusted vertical lines for tags on all subplots and add labels on the topmost plot
    for tag_x in adjusted_tag_x_values:
        ax1.axvline(x=tag_x, color='black', linestyle='--', linewidth=1.2)
        ax1.text(tag_x, max(bvp_data[0]) * 1.15, f'{tag_x:.2f}', ha='center', va='bottom', fontsize=8, color='black')
        ax2.axvline(x=tag_x, color='black', linestyle='--', linewidth=1.2)
        ax3.axvline(x=tag_x, color='black', linestyle='--', linewidth=1.2)
        ax4.axvline(x=tag_x, color='black', linestyle='--', linewidth=1.2)

    # Set the x-axis limits to be the same for all subplots
    ax1.set_xlim(x_min, x_max)
    ax2.set_xlim(x_min, x_max)
    ax3.set_xlim(x_min, x_max)
    ax4.set_xlim(x_min, x_max)

    # Adjust layout to make room for the title
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Show the plot
    plt.show()
