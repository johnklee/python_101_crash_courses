import unittest
import read_csv

from unittest import mock
from unittest.mock import mock_open

TEST_CSV_DATA = ['name,age', 'John,50', 'Peter,10', 'Mary,5']
TEST_INVALID_CSV_DATA = [
    'column,age', 'John,50', 'Peter,10', 'Mary,5']


class TestReadCSV(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self.test_csv_path = 'test.csv'
    self.test_invalid_csv_path = 'invalid.csv'

  def test_read_name_pass(self):
    # Test the names could be read successfully from CSV file.
    with mock.patch(
        'read_csv.open',
        mock_open(read_data='\n'.join(TEST_CSV_DATA))) as mock_file:
      names = read_csv.read_name(self.test_csv_path)

      self.assertEqual(names, ['John', 'Peter', 'Mary'])

  @mock.patch.object(read_csv, 'os')
  def test_read_name_csv_file_not_exist(self, mock_os):
    # Test if the input CSV file does not exist.
    mock_os.path.isfile.return_value = False

    with self.assertRaises(Exception):
      read_csv.read_name(self.test_csv_path)

  def test_read_name_csv_fileformat_is_not_expected(self):
    # Test if the input CSV contains the unexpected format.
    with mock.patch(
        'read_csv.open',
        mock_open(read_data='\n'.join(TEST_INVALID_CSV_DATA))) as _:
      return_value = read_csv.read_name(self.test_invalid_csv_path)

      self.assertTrue(return_value is None)


if __name__ == '__main__':
    unittest.main()
