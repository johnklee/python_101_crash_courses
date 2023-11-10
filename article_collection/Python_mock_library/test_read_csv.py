import unittest
import read_csv

from unittest import mock


class TestReadCSV(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self.test_csv_path = 'test.csv'

  @mock.patch(read_csv, 'os')
  def test_read_name_pass(self, mock_os):
    # Test the names could be read successfully from CSV file.
    pass

  def test_read_name_csv_file_not_exist(self):
    # Test if the input CSV file does not exist.
    pass

  def test_read_name_csv_fileformat_is_not_expected(self):
    # Test if the input CSV contains the unexpected format.
    pass


if __name__ == '__main__':
    unittest.main()
