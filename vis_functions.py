from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

class ParticipantDataPlotter:
    def __init__(self, base_folder):
        self.base_folder = Path(base_folder)
        self.recordings_path = self.base_folder / "clean_individual_recordings"
        self.participant_id = None
        self.folder_path = None

    def load_data(self, file_path, skiprows=2):
        """Load CSV data, skipping the specified number of rows."""
        return pd.read_csv(file_path, skiprows=skiprows, header=None)

    def calculate_x_values(self, data_length, increment):
        """Generate x-axis values based on data length and time increment."""
        return [i * increment for i in range(data_length)]

    def check_threshold_exceedance(self, label, data, sdlow, sdhigh):
        """Check if any values exceed the standard deviation thresholds, starting from row 3."""
        data_to_check = data[2:]
        if any(data_to_check < sdlow):
            print(f"{label} data goes below the lower standard deviation threshold starting from row 3.")
        if any(data_to_check > sdhigh):
            print(f"{label} data goes above the upper standard deviation threshold starting from row 3.")

    def plot_data(self, ax, x_values, data, color, ylabel, sdlow=None, sdhigh=None):
        """Plot data on a given axis with standard deviation lines."""
        ax.plot(x_values, data[0], color=color)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        if sdlow is not None and sdhigh is not None:
            ax.axhline(y=sdlow, color='black', linestyle='--', linewidth=1.5, label=f'sd_low: {sdlow}')
            ax.axhline(y=sdhigh, color='black', linestyle='--', linewidth=1.5, label=f'sd_high: {sdhigh}')
            ax.legend(loc='upper right')

    def load_sd_values(self, sd_file_path, file_label):
        """Load standard deviation values from the provided file."""
        try:
            sd_data = pd.read_csv(sd_file_path, header=None)
            if len(sd_data) >= 2 and sd_data.shape[1] >= 3:
                sdlow = round(float(sd_data.iloc[1, 1]), 1)  # B2
                sdhigh = round(float(sd_data.iloc[1, 2]), 1)  # C2
                return sdlow, sdhigh
            else:
                raise ValueError(f"{file_label} file does not have the expected structure.")
        except Exception as e:
            print(f"Error loading {file_label} standard deviation values: {e}")
            return None, None

    def plot_participant_data(self):
        available_ids = [folder.name[4:] for folder in self.recordings_path.iterdir() if folder.is_dir()]

        self.participant_id = input("Please enter the participant ID in the form '#####': ")
        if self.participant_id not in available_ids:
            print(f"No rn{self.participant_id} folder found for participant ID: {self.participant_id}\n"
                  "Input format should be: ##### with no rn\n")
            return

        self.folder_path = self.recordings_path / f"c_rn{self.participant_id}"

        # Define file paths
        bvp_file_path = self.folder_path / "c_BVP.csv"
        hr_file_path = self.folder_path / "c_HR.csv"
        eda_file_path = self.folder_path / "c_EDA.csv"
        temp_file_path = self.folder_path / "c_TEMP.csv"
        tags_file_path = self.folder_path / "tags.csv"
        sd_temp_file_path = self.folder_path / "sd_TEMP.csv"
        sd_bvp_file_path = self.folder_path / "sd_BVP.csv"
        sd_eda_file_path = self.folder_path / "sd_EDA.csv"
        sd_hr_file_path = self.folder_path / "sd_HR.csv"

        if not all(file.is_file() for file in [bvp_file_path, hr_file_path, eda_file_path, temp_file_path, tags_file_path]):
            print(f"One or more files for participant ID {self.participant_id} do not exist.")
            return

        # Load data
        bvp_data = self.load_data(bvp_file_path)
        hr_data = self.load_data(hr_file_path)
        eda_data = self.load_data(eda_file_path)
        temp_data = self.load_data(temp_file_path)
        
        # Load standard deviation data
        sdlow_temp, sdhigh_temp = self.load_sd_values(sd_temp_file_path, "TEMP")
        sdlow_bvp, sdhigh_bvp = self.load_sd_values(sd_bvp_file_path, "BVP")
        sdlow_eda, sdhigh_eda = self.load_sd_values(sd_eda_file_path, "EDA")
        sdlow_hr, sdhigh_hr = self.load_sd_values(sd_hr_file_path, "HR")

        # Create x-axis values
        bvp_x_values = self.calculate_x_values(len(bvp_data), 0.015625)
        hr_x_values = self.calculate_x_values(len(hr_data), 1)  # HR is typically in 1-second increments
        eda_x_values = self.calculate_x_values(len(eda_data), 0.25)
        temp_x_values = self.calculate_x_values(len(temp_data), 0.25)

        # Check if any values exceed the standard deviation thresholds
        if sdlow_bvp is not None and sdhigh_bvp is not None:
            self.check_threshold_exceedance("BVP", bvp_data[0], sdlow_bvp, sdhigh_bvp)
        if sdlow_hr is not None and sdhigh_hr is not None:
            self.check_threshold_exceedance("HR", hr_data[0], sdlow_hr, sdhigh_hr)
        if sdlow_eda is not None and sdhigh_eda is not None:
            self.check_threshold_exceedance("EDA", eda_data[0], sdlow_eda, sdhigh_eda)
        if sdlow_temp is not None and sdhigh_temp is not None:
            self.check_threshold_exceedance("TEMP", temp_data[0], sdlow_temp, sdhigh_temp)

        # Create subplots
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(9, 7), sharex=True)
        fig.suptitle(f'Data for Participant {self.participant_id}', fontweight='bold', fontsize=14, y=0.95)

        # Plot data
        self.plot_data(ax1, bvp_x_values, bvp_data, color='blue', ylabel='BVP Value', sdlow=sdlow_bvp, sdhigh=sdhigh_bvp)
        self.plot_data(ax2, hr_x_values, hr_data, color='red', ylabel='HR Value', sdlow=sdlow_hr, sdhigh=sdhigh_hr)
        self.plot_data(ax3, eda_x_values, eda_data, color='green', ylabel='EDA Value', sdlow=sdlow_eda, sdhigh=sdhigh_eda)
        self.plot_data(ax4, temp_x_values, temp_data, color='purple', ylabel='TEMP Value', sdlow=sdlow_temp, sdhigh=sdhigh_temp)
        ax4.set_xlabel('Time (s)')

        # Plot vertical lines for tags on all subplots and add labels on the topmost plot
        a1_value = pd.read_csv(bvp_file_path, nrows=1, header=None).iloc[0, 0]
        tags_data = pd.read_csv(tags_file_path, header=None)
        adjusted_tag_x_values = tags_data[0] - a1_value

        for tag_x in adjusted_tag_x_values:
            ax1.axvline(x=tag_x, color='black', linestyle='--', linewidth=1.2)
            ax1.text(tag_x, max(bvp_data[0]) * 1.15, f'{tag_x:.2f}', ha='center', va='bottom', fontsize=8, color='black')
            ax2.axvline(x=tag_x, color='black', linestyle='--', linewidth=1.2)
            ax3.axvline(x=tag_x, color='black', linestyle='--', linewidth=1.2)
            ax4.axvline(x=tag_x, color='black', linestyle='--', linewidth=1.2)

        ax1.set_xlim(0, max(bvp_x_values[-1], hr_x_values[-1], eda_x_values[-1], temp_x_values[-1]))

        # Adjust layout to make room for the title
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()

# Example usage
base_folder = "/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/"  # Replace with the actual path to your main folder
plotter = ParticipantDataPlotter(base_folder)
plotter.plot_participant_data()

