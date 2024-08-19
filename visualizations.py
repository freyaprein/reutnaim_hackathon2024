import pandas as pd
import re
import matplotlib.pyplot as plt

# Load the CSV file
mini_hr_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/mini_hr_concatenated.csv'
mini_eda_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/mini_eda_concatenated.csv'
mini_bvp_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/mini_bvp_concatenated.csv'
#acc_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/mini_acc_concatenated.csv'

hr_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/hr_concatenated.csv'
eda_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/eda_concatenated.csv'
bvp_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/bvp_concatenated.csv'


data_hr = pd.read_csv(hr_file)
data_eda = pd.read_csv(eda_file)


def add_tags_to_csv(file_path, output_path):
    # Load the CSV file, calculate the number of rows and the number of rows for each tag
    data = pd.read_csv(file_path)
    total_rows = len(data)
    third = total_rows // 3
    
    # Create the 'tags' column with the specified values
    tags = ['1000'] * third + ['2000'] * third + ['2500'] * (total_rows - 2 * third)
    
    # Insert the 'tags' column as the first column in the dataframe
    data.insert(0, 'tags', tags)
    
    # Save the modified dataframe to a new CSV file
    data.to_csv(output_path, index=False)




hr_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/hr_concatenated.csv'
tags_hr_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/hr_concatenated_with_tags_test.csv'
clean_tags_hr_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/cleaned_data/hr_concatenated_clean_with_tags_test.csv'
#add_tags_to_csv(hr_file, clean_tags_hr_file)

eda_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/eda_concatenated.csv'
tags_eda_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/eda_concatenated_with_tags_test.csv'
clean_tags_eda_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/cleaned_data/eda_concatenated_clean_with_tags_test.csv'
#add_tags_to_csv(eda_file, clean_tags_eda_file)

bvp_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/bvp_concatenated.csv'
tags_bvp_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/concatenated recordings/bvp_concatenated_with_tags_test.csv'
clean_tags_bvp_file = '/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab/cleaned_data/bvp_concatenated_clean_with_tags_test.csv'
#add_tags_to_csv(bvp_file, clean_tags_bvp_file)





def plot_participant_data(file_1, file_2, file_3, label_1, label_2, label_3):
    # Load the two CSV files
    data1 = pd.read_csv(file_1)
    data2 = pd.read_csv(file_2)
    data3 = pd.read_csv(file_3)
   #data4 = pd.read_csv(Acceleration)
    #data5 = pd.read_csv(Temperature)
    
    # Extract participant columns (excluding the time column)
    participant_columns1 = data1.columns[2:]
    participant_columns2 = data2.columns[2:]
    participant_columns3 = data3.columns[2:]

    # Extract the tags from the first file's leftmost column (assuming it's the 'tags' column)
    tags = data1['tags'].unique()
    
    # Prompt the user for input
    participant_id = input("Please enter the participant ID (e.g., rn23021): ").strip()
    
    # Find the corresponding columns in each dataframe
    column_name1 = [col for col in participant_columns1 if participant_id in col]
    column_name2 = [col for col in participant_columns2 if participant_id in col]
    column_name3 = [col for col in participant_columns3 if participant_id in col]
    
    if not column_name1 or not column_name2 or not column_name3:
        print(f"No data found for participant ID: {participant_id} in one or both files\n"
              "Input format should be: rn####\n"
              f"The possible IDs are:\nFile1: {participant_columns1}\nFile2: {participant_columns2}")
        return
    
    # Extract the time and corresponding participant data from both files
    time1 = data1['time (s)']
    time2 = data2['time (s)']
    time3 = data3['time (s)']
    participant_data1 = data1[column_name1[0]]
    participant_data2 = data2[column_name2[0]]
    participant_data3 = data3[column_name3[0]]
    
    # Plot the data with two y-axes
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color1 = 'tab:blue'
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel(f'{label_1}', color=color1)
    ax1.plot(time1, participant_data1, color=color1, marker='o', markersize=2, label='Coarse Data')
    #ax1.plot(time1, participant_data1, color=color1, marker='o', markersize=4, label=label1)
    ax1.tick_params(axis='y', labelcolor=color1)
    
    # Create a second y-axis
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel(f'{label_2}', color=color2)
    ax2.plot(time2, participant_data2, color=color2, marker='o', markersize=2, label='Fine Data')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Create a third y-axis
    ax3 = ax1.twinx()
    color3 = 'tab:green'
    ax3.set_ylabel(f'{label_3}', color=color3)
    ax3.plot(time3, participant_data3, color=color3, marker='o', markersize=2, label='Fine Data')
    ax3.tick_params(axis='y', labelcolor=color3)


    for tag in tags:
        ax1.axvline(x=tag, color='green', linestyle='--', label=f'Tag {tag}')
    

    # Avoid duplicate labels in the legend
    handles, labels = ax1.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax1.legend(unique_labels.values(), unique_labels.keys())
    
    # Title and grid
    plt.title(f"Participant {participant_id} Data Over Time")
    fig.tight_layout()
    plt.grid(True)

    # Align the x-ticks on the same scale (both axes are already aligned in seconds)
    ax1.set_xlim(min(time1.min(), time2.min()), max(time1.max(), time2.max()))
    ax2.set_xlim(min(time1.min(), time2.min()), max(time1.max(), time2.max()))
    
    plt.show()

# Example usage:
# replace with the second CSV file path
#plot_participant_data(hr_file, eda_file, bvp_file, 'HR', 'EDA', 'BVP')
plot_participant_data(clean_tags_hr_file, clean_tags_eda_file, clean_tags_bvp_file, 'HR', 'EDA', 'BVP')


