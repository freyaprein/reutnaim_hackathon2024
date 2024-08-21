"""Main module."""

from missing_data.missing_filling import UnusualSubjectDataProcessor
from cleaning_tagging.outliers import OutliersDataProcessor
from Visualization.vis_functions import ParticipantDataPlotter

def main():
    base_folder = "/Users/freyaprein/Desktop/Hackathon 2024 Group2 /Hackathon_files_adapt_lab"
    
    # Process subjects using UnusualSubjectDataProcessor
    processor = UnusualSubjectDataProcessor(base_folder)
    processor.process_subjects()
    
    # Process individual recordings using OutliersDataProcessor
    filter = OutliersDataProcessor(base_folder)
    filter.process_individual_recordings()
    
    # Create an instance of ParticipantDataPlotter
    plotter = ParticipantDataPlotter(base_folder)
    
    # Plot participant data and allow reinputting another participant's name
    while True:
        plotter.plot_participant_data()
        
        # Ask the user if they want to input another participant's name
        choice = input("Do you want to input another participant's ID? (yes/no): ").strip().lower()
        if choice == 'yes':
            print("Please enter the participant ID in the form '#####': ")
        else:
            print("Exiting the program.")
            break

if __name__ == "__main__":
    main()
