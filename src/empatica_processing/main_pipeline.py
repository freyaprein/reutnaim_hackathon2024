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
    
    

if __name__ == "__main__":
    main()
