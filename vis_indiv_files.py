from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Prompt the user for the participant ID
participant_id = input("Please enter the participant ID in the form '#####': ")

# Define the folder path based on the participant ID
folder_name = f"c_rn{participant_id}"
base_path = Path("/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/c_individual recordings_test")  # Replace with the actual path to your main folder
folder_path = base_path / folder_name

# Define the file paths to the c_BVP.csv, c_HR.csv, c_EDA.csv, and c_TEMP.csv files
bvp_file_path = folder_path / "c_BVP.csv"
hr_file_path = folder_path / "c_HR.csv"
eda_file_path = folder_path / "c_EDA.csv"
temp_file_path = folder_path / "c_TEMP.csv"

# Check if the files exist
if not bvp_file_path.is_file() or not hr_file_path.is_file() or not eda_file_path.is_file() or not temp_file_path.is_file():
    print(f"One or more files for participant ID {participant_id} do not exist.")
else:
    # Load the BVP data, skipping the first two rows
    bvp_data = pd.read_csv(bvp_file_path, skiprows=2, header=None)

    # Load the HR data, skipping the first two rows
    hr_data = pd.read_csv(hr_file_path, skiprows=2, header=None)

    # Load the EDA data, skipping the first two rows
    eda_data = pd.read_csv(eda_file_path, skiprows=2, header=None)

    # Load the TEMP data, skipping the first two rows
    temp_data = pd.read_csv(temp_file_path, skiprows=2, header=None)

    # Create the x-axis values
    bvp_x_values = [i * 0.015625 for i in range(len(bvp_data))]
    hr_x_values = list(range(len(hr_data)))
    eda_x_values = [i * 0.25 for i in range(len(eda_data))]
    temp_x_values = [i * 0.25 for i in range(len(temp_data))]

    # Determine the common x-axis limits
    x_min = 0
    x_max = max(bvp_x_values[-1], hr_x_values[-1], eda_x_values[-1], temp_x_values[-1])

    # Create subplots with a smaller figure size
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(8, 8), sharex=True)

    # Plot BVP data in the first subplot
    ax1.plot(bvp_x_values, bvp_data[0], color='blue')
    ax1.set_ylabel('BVP Value')
    ax1.set_title(f'BVP Data for Participant {participant_id}')
    ax1.grid(True)

    # Plot HR data in the second subplot
    ax2.plot(hr_x_values, hr_data[0], color='red')
    ax2.set_ylabel('HR Value')
    ax2.set_title(f'HR Data for Participant {participant_id}')
    ax2.grid(True)

    # Plot EDA data in the third subplot
    ax3.plot(eda_x_values, eda_data[0], color='green')
    ax3.set_ylabel('EDA Value')
    ax3.set_title(f'EDA Data for Participant {participant_id}')
    ax3.grid(True)

    # Plot TEMP data in the fourth subplot
    ax4.plot(temp_x_values, temp_data[0], color='purple')
    ax4.set_ylabel('TEMP Value')
    ax4.set_xlabel('Time (s)')
    ax4.set_title(f'TEMP Data for Participant {participant_id}')
    ax4.grid(True)

    # Set the x-axis limits to be the same for all subplots
    ax1.set_xlim(x_min, x_max)
    ax2.set_xlim(x_min, x_max)
    ax3.set_xlim(x_min, x_max)
    ax4.set_xlim(x_min, x_max)

    # Adjust layout
    plt.tight_layout()

    # Show the plot
    plt.show()
