"""LE audio log parser main program."""

import argparse
import constants
import dataclasses
from dotenv import load_dotenv
import logging
import os
import sys

import le_audio_log_event_publisher
from observer.le_audio_log_observer import LeAudioLogObserver
from observer.le_audio_pairing_test import PairPattern


load_dotenv()
Color = constants.Color
TitleStyle = Color.BOLD + Color.YELLOW + Color.UNDERLINE
logging.basicConfig(
    format='%(asctime)s %(levelname)-4s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%H:%M:%S', level=logging.DEBUG)


@dataclasses.dataclass(frozen=True)
class LEParserTask:
  task_id: int
  observer_cls: LeAudioLogObserver
  description: str


ParserTaskInfo = {
    1: LEParserTask(1, PairPattern, 'Generic: Pair and connection'),
}


def check_value_in_test_case_options():
  """Checks if given `tc_no` exist in predefined test cases options."""
  if int(tc_no) in ParserTaskInfo:
      return True

  return False


def select_parser_task_info():
  """Prints perf parser task information."""
  item_2_task_id = {
      1:   1,
      2:   2,
      3:  37,
      4:   3,
      5:   4,
      6:   5,
      7:  26,
      8:  24,
      9:  23,
     10:  42,
     11:  27,
     12:  25,
     13:   7,
     14:  36,
     15:  23,
     16:   8,
     17:  40,
     18:   9,
     19:  39,
     20:  10,
     21:  35,
     22:  11,
     23:  34,
     24:  12,
     25:  33,
     26:  13,
     27:  33,
     28:  14,
     29:  28,
     30:  15,
     31:  29,
     32:  16,
     33:  38,
     34:  17,
     35:  29,
     36:  18,
     37:  31,
     38:  19,
     39:  30,
     40:  20,
     41:  22,
     42:  42,
  }
  print(TitleStyle + '\n\t=== Performance - Connection ===' + Color.END)
  print('\t  1. Generic: Pair and connection')
  print('\t  2. Generic: Reconnect - Turn off/on DUT BT')
  print('\t  3. Generic: Reconnect by TA')
  print('\t  4. Media streaming: One earbud dropping the connection and reconnection')
  print('\t  5. Call conversation: One earbud dropping the connection and reconnection')
  print(TitleStyle + '\n\t=== Performance - Media/Call control ===' + Color.END)
  print('\t  6. Media Control: Play music from LE Audio device (HW)')
  print('\t  7. Media Control: Play music from LE Audio device (SW)')
  print('\t  8. Media Control: Pause music from LE Audio device')
  print('\t  9. Media Control: Volume control from LE Audio device')
  print('\t 10. Call Control: Incoming call from LE audio device (HW)')
  print('\t 11. Call Control: Incoming call from LE audio device (SW)')
  print('\t 12. Call Control: End call from LE Audio devices')
  print('\t 13. Call Control: Outgoing call from DUT (HW)')
  print('\t 14. Call Control: Outgoing call from DUT (SW)')
  print('\t 15. Call Control: Volume control from LE Audio device')
  print(TitleStyle + '\n\t=== Performance - Content type switching ===' + Color.END)
  print('\t 16. Stream interrupted by incoming call: LE media stream -> LE conversation stream')
  print('\t 17. Stream interrupted by incoming call: LE media stream -> LE conversation stream (SW)')  # New
  print('\t 18. Stream resume back after call end with LE audio device: LE conversation stream -> LE media stream')
  print('\t 19. Stream resume back after call end with LE audio device: LE conversation stream -> LE media stream (SW)')  # New
  print(TitleStyle + '\n\t=== Performance - Audio path switching ===' + Color.END)
  print('\t 20. Media streaming: LE media stream -> DUT speaker (HW)')
  print('\t 21. Media streaming: LE media stream -> DUT speaker (SW)')
  print('\t 22. Media streaming: DUT speaker -> LE media stream (HW)')
  print('\t 23. Media streaming: DUT speaker -> LE media stream (SW)')
  print('\t 24. Call conversation: LE conversation stream -> DUT speaker (HW)')
  print('\t 25. Call conversation: LE conversation stream -> DUT speaker (SW)')
  print('\t 26. Call conversation: DUT speaker -> LE conversation stream (HW)')
  print('\t 27. Call conversation: DUT speaker -> LE conversation stream (SW)')
  print(TitleStyle + '\n\t=== Performance - Multi-connections with BR/EDR device ===' + Color.END)
  print('\t 28. Media streaming: LE media stream (HW) -> A2dp HW offload')
  print('\t 29. Media streaming: LE media stream (SW) -> A2dp HW offload')
  print('\t 30. Media streaming: A2dp HW offload -> LE media stream (HW)')
  print('\t 31. Media streaming: A2dp HW offload -> LE media stream (SW)')
  print('\t 32. Media streaming: LE media stream -> A2dp SW encode')
  print('\t 33. Media streaming: LE media stream (SW) -> A2dp SW encode')
  print('\t 34. Media streaming: A2dp SW encode -> LE media stream (HW)')
  print('\t 35. Media streaming: A2dp SW encode -> LE media stream (SW)')
  print('\t 36. Call conversation: LE conversation stream (HW) -> HFP')
  print('\t 37. Call conversation: LE conversation stream (SW) -> HFP')
  print('\t 38. Call conversation: HFP -> LE conversation stream (HW)')
  print('\t 39. Call conversation: HFP -> LE conversation stream (SW)')
  print(TitleStyle + '\n\t=== Others ===' + Color.END)
  print('\t 40. Generic: Reconnect - disconnect/connect from phone setting UI')

  tc_no = int(input('\nInput a test case number: '))
  task_id = item_2_task_id[tc_no]
  log.info(f'Executing parser task-{task_id}...')
  return task_id


def print_perf_test_case_options():
  """Prints performance test case options."""
  le_audio_new_task_nums = {
      23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36}
  print('\n+++ LE Audio performance test case +++\n')
  for task_id, task_info in ParserTaskInfo.items():
    if task_id <= 20 or task_id in le_audio_new_task_nums:
      print(f'{task_id:>3} : {task_info.description}')

  print('\n+++ Classic performance test case +++\n')
  for option in test_case_options:
    if task_id > 20 and task_id not in le_audio_new_task_nums:
      print(f'{task_id:>3} : {task_info.description}')

  print('=====================================\n')


if __name__ == '__main__':
  log = logging.getLogger(__name__)

  parser = argparse.ArgumentParser()
  parser.add_argument('logcat_filename', type=str, nargs='?')
  parser.add_argument('result_filename', type=str, nargs='?')
  parser.add_argument('tc_no', type=str, nargs='?')
  args = parser.parse_args()
  logcat_filename = args.logcat_filename
  result_filename = args.result_filename
  headset_type_str = os.getenv('HEADSET_TYPE', None)
  tc_no = args.tc_no
  log.info('tc_no=%s', tc_no)

  while not headset_type_str:
    print('\n===== Select headset type =====')
    supported_headset_num = len(constants.HeadsetType)
    headset_options = list(enumerate(constants.HeadsetType, 1))
    for opt_num, headset_type in headset_options:
      print(f'\t{opt_num}) {headset_type}')
    selected_option = input(
        f'Input option (1-{supported_headset_num}): ')
    try:
      headset_type_str = headset_options[int(selected_option) - 1][1]
    except Exception as ex:
      logging.warning(
          f'Something went wrong with option="{selected_option}": {ex}')

  headset_type = constants.HeadsetType.from_str(headset_type_str)
  print(f'Headset type="{headset_type}" is selected...')

  if not logcat_filename:
    logcat_filename = input('Input a logcat filename: ')

  if not os.path.isfile(logcat_filename) and not logcat_filename.startswith('device:'):
    log.error('Input logcat file=%s does not exist!\n', logcat_filename)
    sys.exit(1)

  if not result_filename:
    result_filename = input('Input a result filename: ')

  if not tc_no:
    # print_perf_test_case_options()
    tc_no = select_parser_task_info()
    # tc_no = int(input('Input a test case number: '))

  if not check_value_in_test_case_options():
    log.error('Invalid test case option=%s!\n', tc_no)
    sys.exit(1)

  # Initialization
  log_gr = le_audio_log_event_publisher.LogEventPublisher()

  registered_observer_count = 0  # pylint: disable=invalid-name
  tc_no = int(tc_no)
  task_info = ParserTaskInfo[tc_no]
  parser_clz = task_info.observer_cls
  parser_object = parser_clz()
  parser_object.lea_config = constants.LEAConfig.from_headset_type(headset_type)
  parser_object.task_num = tc_no
  log_gr.register_observer(parser_object)
  log.debug('Registered observer %s...(tc_no=%s)', parser_object, task_info.task_id)
  registered_observer_count += 1

  log.info('Total %s observer(s) being registered!',
           registered_observer_count)

  # Parsing
  # log_gr.convert_to_utf8(input_file_path=logcat_filename)
  log_gr.start_to_search(
      input_file_path=logcat_filename, output_file_path=result_filename)
