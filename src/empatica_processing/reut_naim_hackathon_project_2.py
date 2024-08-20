"""Main module."""

from missing_data.missing_filling import UnusualSubjectDataProcessor
from cleaning_tagging.outliers import OutliersDataProcessor
from visualization.vis_functions import ParticipantDataPlotter

def main():
    base_folder = "/Users/shiriarnon/Documents/TAU/Courses/Year_1_(23-24)/Semester_2/Python_for_neuroscience/Hackathon/Hackathon_files_adapt_lab"
    processor = UnusualSubjectDataProcessor(base_folder) # Create an instance of UnusualSubjectDataProcessor
    processor.process_subjects() # Process the subjects



if __name__ == "__main__":
    # Code here will only run if outliers.py is executed directly
    some_function()