from missing_data.missing_filling import UnusualSubjectDataProcessor
from cleaning_tagging.outliers import OutliersDataProcessor
from visualization.vis_figures import ParticipantDataPlotter

def main():
    # Prompt the user to input the base folder path
    base_folder = input("Please insert the path to the folder containing the participants data folders: ").strip()
    
    # Process subjects using UnusualSubjectDataProcessor
    processor = UnusualSubjectDataProcessor(base_folder)
    processor.process_subjects()
    
    # Process individual recordings using OutliersDataProcessor
    filter = OutliersDataProcessor(base_folder)
    filter.process_individual_recordings()
    
    # Create an instance of ParticipantDataPlotter
    plotter = ParticipantDataPlotter(base_folder)
    plotter.plot_participant_data()
    
    # Plot participant data and allow reinputting another participant's name
    # while True:
    #     plotter.plot_participant_data()
        
    #     # Ask the user if they want to input another participant's name
    #     choice = input("Do you want to input another participant's ID? (yes/no): ").strip().lower()
    #     if choice == 'yes':
    #         print("Please enter the participant ID in the form '#####': ")
    #     else:
    #         print("Exiting the program.")
    #         break

if __name__ == "__main__":
    main()
