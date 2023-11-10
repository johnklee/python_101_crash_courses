from datetime import datetime
import unittest
import my_calendar

from unittest import mock


class TestCalendar(unittest.TestCase):

  def setUp(self):
    # Save a couple of test days
    self.tuesday = datetime(year=2019, month=1, day=1)
    self.saturday = datetime(year=2019, month=1, day=5)

  @mock.patch.object(my_calendar, 'datetime', autospec=True)
  def test_is_weekday(self, mock_datetime):
    mock_datetime.today.return_value = self.tuesday

    self.assertTrue(my_calendar.is_weekday())

  @mock.patch.object(my_calendar, 'datetime', autospec=True)
  def test_is_not_weekday(self, mock_datetime):
    mock_datetime.today.return_value = self.saturday

    self.assertFalse(my_calendar.is_weekday())


if __name__ == '__main__':
    unittest.main()
