from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt



def plot_participant_data(base_path):

    # Define the path to the 'c_individual recordings_test' folder within base_path
    recordings_path = Path(base_folder) / "clean_individual_recordings"

    # Get a list of available participant IDs (folder names within the 'c_individual recordings_test' folder)
    available_ids = [folder.name[4:] for folder in recordings_path.iterdir() if folder.is_dir()]

    # Prompt the user for the participant ID
    participant_id = input("Please enter the participant ID in the form '#####': ")


    if participant_id not in available_ids:
        print(f"No rn{participant_id} folder found for participant ID: {participant_id}\n\""
              "Input format should be: ##### with no rn\n")
        return


   
    # Define the folder path based on the participant ID
    folder_name = f"clean_individual_recordings/c_rn{participant_id}"
    folder_path = base_path / folder_name

 

    # Define the file paths to the c_BVP.csv, c_HR.csv, c_EDA.csv, c_TEMP.csv, and tags.csv files
    bvp_file_path = folder_path / "c_BVP.csv"
    hr_file_path = folder_path / "c_HR.csv"
    eda_file_path = folder_path / "c_EDA.csv"
    temp_file_path = folder_path / "c_TEMP.csv"
    tags_file_path = folder_path / "tags.csv"
    sd_temp_file_path = folder_path / "sd_TEMP.csv"
    sd_bvp_file_path = folder_path / "sd_BVP.csv"
    sd_eda_file_path = folder_path / "sd_EDA.csv"
    sd_hr_file_path = folder_path / "sd_HR.csv"

    # Check if the files exist
    if not bvp_file_path.is_file() or not hr_file_path.is_file() or not eda_file_path.is_file() or not temp_file_path.is_file() or not tags_file_path.is_file():
        print(f"One or more files for participant ID {participant_id} do not exist.")
    else:
        # Load the BVP , HR, EDA, and TEMP data, skipping the first two rows of each
        bvp_data = pd.read_csv(bvp_file_path, skiprows=2, header=None)
        hr_data = pd.read_csv(hr_file_path, skiprows=2, header=None)
        eda_data = pd.read_csv(eda_file_path, skiprows=2, header=None)
        temp_data = pd.read_csv(temp_file_path, skiprows=2, header=None)
        sd_temp_data = pd.read_csv(sd_temp_file_path, header=None)

        # Load the value from starting sampling time in UTC from cell A1 of the BVP file - same value for all but HR file
        a1_value = pd.read_csv(bvp_file_path, nrows=1, header=None).iloc[0, 0]

        # Load the tags data
        tags_data = pd.read_csv(tags_file_path, header=None)

        # Subtract the starting sampling time from each tag value
        adjusted_tag_x_values = tags_data[0] - a1_value

        # Create the x-axis values
        bvp_x_values = [i * 0.015625 for i in range(len(bvp_data))]
        hr_x_values = list(range(len(hr_data)))
        eda_x_values = [i * 0.25 for i in range(len(eda_data))]
        temp_x_values = [i * 0.25 for i in range(len(temp_data))]

        # Determine the common x-axis limits
        x_min = 0
        x_max = max(bvp_x_values[-1], hr_x_values[-1], eda_x_values[-1], temp_x_values[-1])


        sdlow_temp = round(float(sd_temp_data.iloc[1, 2]), 1)
        sdhigh_temp = round(float(sd_temp_data.iloc[1, 3]), 1)



        # Create subplots with a smaller figure size
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(9, 7), sharex=True)

        # Set a single title for the entire figure
        fig.suptitle(f'Data for Participant {participant_id}', fontweight='bold', fontsize=14, y=0.95)

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
        ax4.axhline(y=sdlow_temp, color='black', linestyle='--', linewidth=1.5, label=f'C2: {sdlow_temp}')
        ax4.axhline(y=sdhigh_temp, color='black', linestyle='--', linewidth=1.5, label=f'D2: {sdhigh_temp}')
        ax4.legend(loc='upper right')

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


base_folder = Path("/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/")  # Replace with the actual path to your main folder
plot_participant_data(base_folder)