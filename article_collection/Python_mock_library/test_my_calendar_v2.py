from datetime import datetime
import unittest
import my_calendar
from requests.exceptions import Timeout
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

  def log_request(self, url):
    # Log a fake request for test output purposes
    print(f'Making a request to {url}.')
    print('Request received!')

    # Create a new Mock to imitate a Response
    response_mock = mock.Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {
        '12/25': 'Christmas',
        '7/4': 'Independence Day',
    }
    return response_mock

  @mock.patch.object(my_calendar, 'requests', autospec=True)
  def test_get_holidays_logging(self, mock_requests):
    # Test a successful, logged request
    mock_requests.get.side_effect = self.log_request

    assert my_calendar.get_holidays()['12/25'] == 'Christmas'

  @mock.patch.object(my_calendar, 'requests', autospec=True)
  def test_get_holidays_retry(self, mock_requests):
    # Create a new Mock to imitate a Response
    response_mock = mock.Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {
        '12/25': 'Christmas',
        '7/4': 'Independence Day',
    }
    # Set the side effect of .get()
    mock_requests.get.side_effect = [Timeout, response_mock]

    # Test that the first request raises a Timeout
    with self.assertRaises(Timeout):
      my_calendar.get_holidays()

    # Now retry, expecting a successful response
    assert my_calendar.get_holidays()['12/25'] == 'Christmas'
    # Finally, assert .get() was called twice
    assert mock_requests.get.call_count == 2


if __name__ == '__main__':
    unittest.main()
