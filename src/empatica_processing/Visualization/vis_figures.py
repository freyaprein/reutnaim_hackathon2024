from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


class ParticipantDataPlotter:
    """
    A class to load, process, and plot physiological data for individual participants.
    """

    def __init__(self, base_folder):
        """
        Initialize the ParticipantDataPlotter with the base folder containing the data.

        Args:
            base_folder (str): The path to the base folder containing participant data.
        """
        self.base_folder = Path(base_folder)
        self.recordings_path = self.base_folder / "clean_individual_recordings"
        self.participant_id = None
        self.folder_path = None
        print("Please wait a moment while all participant's figures are generated and saved. This may take up to a few minutes...")

    def load_data(self, file_path, skiprows=2):
        """
        Load CSV data, skipping the specified number of rows.

        Args:
            file_path (Path): The path to the CSV file.
            skiprows (int): Number of rows to skip at the beginning of the file.

        Returns:
            pd.DataFrame: The loaded data as a pandas DataFrame.
        """
        return pd.read_csv(file_path, skiprows=skiprows, header=None)
    
    def get_data_file_path(self, base_file_path):
        """
        Determine whether to use the standard or filled/merged data file.

        Args:
            base_file_path (Path): The base path to the standard data file.

        Returns:
            Path: The path to the data file to be used.
        """
        merged_file_path = base_file_path.with_name(f"c_Filled_Merged_{base_file_path.stem[2:]}.csv")
        if merged_file_path.exists():
            return merged_file_path
        else:
            return base_file_path

    def calculate_x_values(self, data_length, increment):
        """
        Generate x-axis values based on data length and time increment.

        Args:
            data_length (int): The number of data points.
            increment (float): The time increment between data points.

        Returns:
            list: A list of x-axis values.
        """
        return [i * increment for i in range(data_length)]

    def check_threshold_exceedance(self, label, data, sdlow, sdhigh):
        """
        Check if any values exceed the standard deviation thresholds, starting from row 3.

        Args:
            label (str): The label for the data (e.g., 'BVP', 'HR').
            data (pd.Series): The data series to check.
            sdlow (float): The lower standard deviation threshold.
            sdhigh (float): The upper standard deviation threshold.
        """
        data_to_check = data[2:]  # Ignore the first two rows of data
        if any(data_to_check < sdlow):
            return
            #print(f"{label} data goes below the lower standard deviation threshold starting from row 3.")
        if any(data_to_check > sdhigh):
            return
            # print(f"{label} data goes above the upper standard deviation threshold starting from row 3.")

    def plot_data(self, ax, x_values, data, color, ylabel, sdlow=None, sdhigh=None):
        """
        Plot data on a given axis with optional standard deviation lines.

        Args:
            ax (matplotlib.axes.Axes): The axis to plot the data on.
            x_values (list): The x-axis values.
            data (pd.Series): The data series to plot.
            color (str): The color of the plot line.
            ylabel (str): The label for the y-axis.
            sdlow (float, optional): The lower standard deviation threshold. Defaults to None.
            sdhigh (float, optional): The upper standard deviation threshold. Defaults to None.
        """
        ax.plot(x_values, data[0], color=color)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        if sdlow is not None and sdhigh is not None:
            ax.axhline(y=sdlow, color='black', linestyle='--', linewidth=1.5, label=f'sd_low: {sdlow}')
            ax.axhline(y=sdhigh, color='black', linestyle='--', linewidth=1.5, label=f'sd_high: {sdhigh}')
            ax.legend(loc='upper right')

    def load_sd_values(self, sd_file_path, file_label):
        """
        Load standard deviation values from the provided file.

        Args:
            sd_file_path (Path): The path to the standard deviation file.
            file_label (str): The label for the data file (e.g., 'TEMP', 'BVP').

        Returns:
            tuple: A tuple containing the lower and upper standard deviation thresholds.
        """
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


    def get_sd_file_path(self, base_file_path):
        """
        Determine whether to use the standard or filled/merged SD file.

        Args:
            base_file_path (Path): The base path to the standard SD file.

        Returns:
            Path: The path to the SD file to be used.
        """
        merged_file_path = base_file_path.with_name(f"sd_Filled_Merged_{base_file_path.stem[3:]}.csv")
        if merged_file_path.exists():
            return merged_file_path
        else:
            return base_file_path


    def plot_participant_data(self):
        """
        Load and plot data for each participant, save the figures, then prompt the user to input a participant ID to display the figure.
        """
        available_ids = [folder.name[4:] for folder in self.recordings_path.iterdir() if folder.is_dir()]

        for participant_id in available_ids:
            self.participant_id = participant_id
            self.folder_path = self.recordings_path / f"c_rn{self.participant_id}"
            
            bvp_file_path = self.get_data_file_path(self.folder_path / "c_BVP.csv")
            hr_file_path = self.get_data_file_path(self.folder_path / "c_HR.csv")
            eda_file_path = self.get_data_file_path(self.folder_path / "c_EDA.csv")
            temp_file_path = self.get_data_file_path(self.folder_path / "c_TEMP.csv")
            tags_file_path = self.folder_path / "tags.csv"
            
            sd_temp_file_path = self.get_sd_file_path(self.folder_path / "sd_TEMP.csv")
            sd_bvp_file_path = self.get_sd_file_path(self.folder_path / "sd_BVP.csv")
            sd_eda_file_path = self.get_sd_file_path(self.folder_path / "sd_EDA.csv")
            sd_hr_file_path = self.get_sd_file_path(self.folder_path / "sd_HR.csv")

            # Check if all required files exist
            if not all(file.is_file() for file in [bvp_file_path, hr_file_path, eda_file_path, temp_file_path, tags_file_path]):
                print(f"One or more files for participant ID {self.participant_id} do not exist.")
                continue

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

            # Save the figure
            save_path = self.folder_path / f"participant_{self.participant_id}_plot.png"
            plt.savefig(save_path)
            #print(f"Figure saved for participant {self.participant_id} at {save_path}")

            # Close the figure to free memory
            plt.close(fig)
        
        print("All individual figures have been generated and saved to the each participant's folder in the 'clean_individual_recordings' folder.")


