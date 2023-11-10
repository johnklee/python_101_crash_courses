import unittest
import read_csv

from unittest import mock


class TestReadCSV(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self.test_csv_path = 'test.csv'
    self.test_invalid_csv_path = 'invalid.csv'

  def test_read_name_pass(self):
    # Test the names could be read successfully from CSV file.
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
    return_value = read_csv.read_name(self.test_invalid_csv_path)

    self.assertTrue(return_value is None)


if __name__ == '__main__':
    unittest.main()
