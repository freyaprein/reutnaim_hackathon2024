import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from pathlib import Path
from io import StringIO

from missing_filling import UnusualSubjectDataProcessor  # Replace with the actual module name

class TestUnusualSubjectDataProcessor(unittest.TestCase):

    @patch('your_module_name.pd.read_csv')
    @patch('your_module_name.Path.exists')
    @patch('your_module_name.Path.iterdir')
    def test_process_subject_files_with_valid_data(self, mock_iterdir, mock_exists, mock_read_csv):
        # Mock data
        csv_data = StringIO("0,1\n1,0.5\n2,0.5")
        ibi_data = StringIO("0,1\n1,0.5")

        # Mock Path behavior
        mock_subfolder = MagicMock()
        mock_subfolder.iterdir.return_value = [Path("ACC.csv"), Path("IBI.csv")]
        mock_exists.return_value = True
        mock_iterdir.side_effect = [[mock_subfolder, mock_subfolder], mock_subfolder.iterdir.return_value]

        # Mock read_csv behavior
        def read_csv_side_effect(filepath, *args, **kwargs):
            if "IBI.csv" in str(filepath):
                return pd.read_csv(ibi_data, header=None)
            else:
                return pd.read_csv(csv_data, header=None)
        mock_read_csv.side_effect = read_csv_side_effect

        # Instantiate the processor
        processor = UnusualSubjectDataProcessor("/mock/base/folder")

        # Run the processing
        processor.process_subjects()

        # Check that the output files were created
        # Normally we would check the contents of the files, but since we're using mocks,
        # we're just verifying that the function calls occurred as expected.
        self.assertTrue(mock_read_csv.called)

    @patch('your_module_name.pd.read_csv')
    @patch('your_module_name.Path.exists')
    @patch('your_module_name.Path.iterdir')
    def test_process_subject_files_with_invalid_ibi_data(self, mock_iterdir, mock_exists, mock_read_csv):
        # Mock invalid IBI data (missing a column)
        invalid_ibi_data = StringIO("0\n1")

        # Mock Path behavior
        mock_subfolder = MagicMock()
        mock_subfolder.iterdir.return_value = [Path("IBI.csv")]
        mock_exists.return_value = True
        mock_iterdir.side_effect = [[mock_subfolder, mock_subfolder], mock_subfolder.iterdir.return_value]

        # Mock read_csv behavior to return invalid IBI data
        mock_read_csv.return_value = pd.read_csv(invalid_ibi_data, header=None)

        # Instantiate the processor
        processor = UnusualSubjectDataProcessor("/mock/base/folder")

        # Run the processing
        processor.process_subjects()

        # Check that the output files were not created due to invalid data
        self.assertTrue(mock_read_csv.called)
        self.assertEqual(processor.process_subject_files(Path("/mock/base/folder"), [mock_subfolder, mock_subfolder]), {})

    @patch('your_module_name.pd.read_csv')
    @patch('your_module_name.Path.exists')
    @patch('your_module_name.Path.iterdir')
    def test_missing_csv_file(self, mock_iterdir, mock_exists, mock_read_csv):
        # Mock Path behavior
        mock_subfolder = MagicMock()
        mock_subfolder.iterdir.return_value = [Path("ACC.csv")]
        mock_exists.side_effect = lambda x: "IBI.csv" not in str(x)
        mock_iterdir.side_effect = [[mock_subfolder, mock_subfolder], mock_subfolder.iterdir.return_value]

        # Instantiate the processor
        processor = UnusualSubjectDataProcessor("/mock/base/folder")

        # Run the processing
        processor.process_subjects()

        # Ensure that the process was skipped due to missing file
        self.assertTrue(mock_exists.called)
        self.assertFalse(mock_read_csv.called)

    # Additional tests can be added here for other edge cases

if __name__ == '__main__':
    unittest.main()
