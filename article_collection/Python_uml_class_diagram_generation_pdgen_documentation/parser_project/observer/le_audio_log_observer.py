"""Module to provide log event observer."""

import abc
import constants
import copy
import datetime
import enum
import inspect
import logging
import re
from typing import Any, Callable, List, TypeAlias

import general_data
import le_audio_constants
import le_audio_parsing_data
from le_audio_parsing_data import CollectOutputResult
from le_audio_parsing_data import OutputResult
import le_patterns


Color = constants.Color

TimeDelta = datetime.timedelta
CMP: TypeAlias = Callable[[int, int], bool]
RANGE_CMP: TypeAlias = Callable[[int, int, int], bool]
SMALLER_OR_EQUAL_CMP: CMP = lambda a, b: a <= b
LESS_OR_EQUAL_CMP = SMALLER_OR_EQUAL_CMP
LARGER_OR_EQUAL_CMP: CMP = lambda a, b: a >= b
INCLUSIVE_RANGE_COMP: RANGE_CMP = lambda a, b, c: a >= b and a <= c
EQUAL_CMP: CMP = lambda a, b: a == b

EndResult: TypeAlias = general_data.EndResult
Log = general_data.Log
_DateTime: TypeAlias = datetime.datetime
_TimeDelta: TypeAlias = datetime.timedelta
_OutputResult = le_audio_parsing_data.OutputResult
_Pattern = general_data.Pattern
_PatternEnum = general_data.PatternEnum
_BroadcastPatternEnum = general_data.PatternBroadcastEnum


class CallbackAction(enum.IntEnum):
  RESET = enum.auto()
  WAIT = enum.auto()


class Observer(abc.ABC):
  """Observer interface used to register into Publisher to accept notification of input as log event."""

  @abc.abstractmethod
  def notify(self, line: str):
    """Method to receive notification of log event from registered publisher."""

  @abc.abstractmethod
  def is_parsing_complete(self):
    """Method to check if the parsing is completed or not."""


class LeAudioLogObserver(Observer):
  """A class to provide template methods of LE audio log parser.

  Attributes:
    log: Logging object literally.
    captured: An initial data object. captured.title: Title of output log
      message.
    captured.raw_data: Logs that match the patterns.
    captured.output_list: List of output log message in output format.
    captured.log_pattern_dict: Disctionary of log patterns for events.
    captured.event_pass_criteria_sec: The time in seconds as event passing
      criteria.
    captured.ascs_pass_criteria_sec: The time in second as ascs
      passing criteria.
    captured.trial: Round of captured patterns.
    expected_lea_connection_count: This attribute is introduced since
      b/326007878 and it is used as reference of the expected number of LEA
      conversation connection.
    expected_lea_streaming_count: This attribute is introduced since
      b/326007878 and it is used as reference of the expected number of LEA
      streaming connection.
    has_prefix_drop_signal: True to drop the next caught record and reset
      itself as False then.

    **Attributes for le_audio_conversation_stream_interrupt_and_reconnect_test
    bt_stack_codec_configured_freq: Accumulated count of matching pattern to
      detect `bt stack codec configured`.
    bt_stack_qos_configured_freq: Accumulated count of matching pattern to
      detect `bt stack qos configured`.
    bt_stack_enabling_freq: Accumulated count of matching pattern to detect `bt
      stack enabling`.
    bt_stack_streaming_freq: Accumulated count of matching pattern to detect `bt
      stack streaming`.
    le_audio_profile_state: True if log pattern "le_audio_profile_state" match
      is detected, false otherwise.
    lea_config: LEA parsing configuration.
    add_cis_to_stream_sink: True if log pattern "add cis to stream sink" match
      is detected, false otherwise.
    bt_stack_enabling_ase_id: The list of ase id.
    all_freq: A list of cumulative counts.
    pattern_count_list: List of checks to verify the expected number of pattern
      matches.
    expect_end_pattern_count: Number of expected end pattern hit to start making
      record.
    expect_start_pattern_count: Number of expected start pattern hit. If the
      number of matched start pattern exceeds this setting, a reset will be
      triggered.
    drop_num: Number of times two start patterns are hit before reaching the end
      pattern, including timeouts.
    incomplete_callback: Callback to be executed when the parsing is not
      completed and there are missing patterns found.

    **Attributes for
      le_audio_path_swtich_from_le_media_stream_to_phone_speaker_test
    le_remove_iso_data_path_freq:
  """

  def __init__(
      self,
      title: str,
      log_pattern_dict: dict(),
      event_pass_criteria_sec: float,
      ascs_pass_criteria_sec: float | None = None,
      search_timeout_sec: float = constants.PATTERNS_SEARCH_TIMEOUT_SEC,
      incomplete_callback: Callable | None = None,
      lea_config: constants.LEAConfig | None = None,
  ):
    """Initial setup test."""
    self.log = logging.getLogger(self.__class__.__name__)
    log_pattern_dict[general_data.PatternEnum.LOG_ERROR] = (
        le_patterns.GeneralLogError())
    self.captured = OutputResult(
        title=title,
        log_pattern_dict=log_pattern_dict,
        raw_data=[],
        output_list=[],
        event_pass_criteria_sec=event_pass_criteria_sec,
        ascs_pass_criteria_sec=ascs_pass_criteria_sec,
        trial=0,
    )
    self._found_num = 0
    self._search_timeout_sec = search_timeout_sec
    self._task_num = -1
    self._global_raw_data: list[str] = []
    self._pattern_match_times: list[datetime.datetime] = []
    self.has_prefix_drop_signal = False
    self.pattern_count_list = []
    self.expect_end_pattern_count = 1
    self.expect_start_pattern_count = 1
    self.drop_num = 0
    self.incomplete_callback = incomplete_callback
    self._lea_config: constants.LEAConfig | None = lea_config

  def get_pattern(self, key):
    return self.captured.log_pattern_dict[key]

  @property
  def expected_lea_connection_count(self) -> int:
    return self.lea_config.connection_config

  @property
  def expected_lea_streaming_count(self) -> int:
    return self.lea_config.streaming_confg * 2

  @property
  def global_raw_data(self) -> list[str]:
    return self._global_raw_data

  @property
  def found_num(self) -> int:
    """Number of found record(s)."""
    return self._found_num

  @property
  def lea_config(self) -> constants.LEAConfig | None:
    return self._lea_config

  @lea_config.setter
  def lea_config(self, config: constants.LEAConfig):
    self._lea_config = config
    self.update_lea_config_callback()

  def update_lea_config_callback(self):
    pass

  def is_last_pattern_time_too_far(
      self, max_time_delta: TimeDelta = TimeDelta(minutes=10)) -> bool:
    """Last pattern match time stamp."""
    if len(self._pattern_match_times) > 1:
      latest_pattern_time_diff = (
          self._pattern_match_times[-1] - self._pattern_match_times[-2])
      return latest_pattern_time_diff > max_time_delta

    return False

  @property
  def task_num(self) -> int:
    """Task number."""
    return self._task_num

  @task_num.setter
  def task_num(self, task_no: int):
    self._task_num = task_no

  def notify(self, line: str) -> CollectOutputResult:
    return self.find_log_pattern(line)

  def is_parsing_complete(self):
    """Check if the parsing result is completed or not."""
    is_all_matched = True
    for pattern_type, pattern_obj in self.captured.log_pattern_dict.items():
      if isinstance(pattern_obj, str):
        self.log.warning('Old design. Skip checking!')
        return True

      if pattern_type == _PatternEnum.FOOL_PROOF or pattern_obj.is_optional:
        continue

      if not pattern_obj.is_ever_matched:
        self.log.warning(
          '%s/%s missed!',
          pattern_type, pattern_obj.__class__.__name__)
        is_all_matched = False
      else:
        self.log.info('%s Hit by %s times', pattern_type, pattern_obj.match_count)

    if not is_all_matched:
      if self.incomplete_callback:
        self.incomplete_callback(self)

      raise Exception(f'Parsing is not completed! (task num={self.task_num})')

    self.log.info('Total %s record(s) found', self._found_num)
    if self.drop_num > 0:
      self.log.warning(
          Color.BOLD + Color.ORANGE +
          'Total %s start pattern(s) being dropped!' + Color.END,
          self.drop_num)
    self.log.info('Parsing is completed! (task number=%s)', str(self.task_num))

    success_rate = (
        self._found_num / (self._found_num + self.drop_num) * 100 if self._found_num
        else 0)
    self.log.info(
          Color.BOLD + Color.GREEN +
          '\n=====> Success Rate %.1f%%, total %s, success %s' + Color.END,
          success_rate,
          self._found_num + self.drop_num, self._found_num)

  def condition_check(self, exist_property_list: list[Any] | None = None,
                      exist_property_name_list: list[str] | None = None,
                      self_property_name_list: list[str] | None = None,
                      start_end_time_check_list: list[tuple[Any, Any]] | None = None,
                      pattern_count_list: list[
                          tuple[
                              _Pattern | _PatternEnum,
                              int | tuple[int, int],
                              Callable | None],
                              str | None] | None = None,
                      self_property_name_count_list: list[
                          tuple[str, int, CMP | None]
                      ] | None = None) -> bool:
    """Check given conditions before save the collected result.

    Args:
      exist_property_list: List of values to examine if they are None or not.
      exist_property_name_list: List of property names of `self.captured` to
          examine the existence of them.
      self_property_name_list: List of properties from current object to
          examine the existence of them.
      start_end_time_check_list: List of tuple(time1, time2) to ensure that
          `time1` is occurring before `time2`.
      pattern_count_list: List of tuples to check the frequency of patterns
          being matched. The tuple will use below definition:
          - tuple[0]: Target pattern to work on.
          - tuple[1]: Number to compare with.
          - tuple[2]: Comparator used to compare the frequence of pattern
            matching with the given number in tuple[1]
          - tuple[3]: Message to show when failed in comparing condition.

    Returns:
      True iff all conditions are satisfied.
    """

    exist_property_name_list = exist_property_name_list or ['event_start_time', 'event_end_time']
    miss_property_name_list = []
    for property_name in exist_property_name_list:
      property_val = getattr(self.captured, property_name)
      if property_val is None:
        miss_property_name_list.append(property_name)

    if miss_property_name_list:
      self.log.warning('Failed to access %s', ', '.join(miss_property_name_list))
      return False

    self_property_name_list = self_property_name_list or []
    miss_property_name_list = []
    for property_name in self_property_name_list:
      property_val = getattr(self, property_name, None)
      if property_val is None:
        miss_property_name_list.append(property_name)

    if miss_property_name_list:
      self.log.warning('Failed to access %s from observer!', ', '.join(miss_property_name_list))
      return False

    exist_property_list = exist_property_list or []
    for exam_property_value in exist_property_list:
      if exam_property_value is None:
        return False

    start_end_time_check_list = start_end_time_check_list or []
    for start_time, end_time in start_end_time_check_list:
      if start_time > end_time:
        return False

    pattern_count_list = pattern_count_list or []
    for re_pattern_info, count, condition, msg in pattern_count_list:
      re_pattern = re_pattern_info
      if any([
          isinstance(re_pattern_info, _PatternEnum),
          isinstance(re_pattern_info, _BroadcastPatternEnum)]):
        re_pattern = self.captured.log_pattern_dict[re_pattern_info]

      condition = condition or EQUAL_CMP
      if isinstance(count, int):
        count = [count]

      if not condition(re_pattern.cached_count, *count):
        msg = msg or 'real count={real_count}; expected count={expect_count}'
        self.log.warning(
            'Failed on condition check of %s: %s',
            re_pattern_info,
            msg.format(real_count=re_pattern.cached_count, expect_count=count))
        return False

    self_property_name_count_list = self_property_name_count_list or []
    for self_property_name, count, cmp in self_property_name_count_list:
      cmp = cmp or EQUAL_CMP
      self_property_value = getattr(self, self_property_name, None)
      if self_property_value is None:
        self.log.warning(
            'Failed on condition check of self property as %s with value as None!',
            self_property_name)
        return False

      if not cmp(getattr(self, self_property_name, 0), count):
        self.log.warning(
            'Failed on condition check of self property as %s with value as %s',
            self_property_name, self_property_value)
        return False

    return True

  @abc.abstractmethod
  def find_log_pattern(self, line: str) -> CollectOutputResult:
    """Finds required information by parsing given log.

    Args:
      line: The line of input file to analyze.

    Returns:
      captured_messages: The matching results.
    """
    raise NotImplementedError

  def clear_timestamps(self) -> None:
    """Resets the timestamps."""
    for field_name, _ in inspect.getmembers(self.captured):
      if field_name.endswith('_time') or field_name.endswith('_duration'):
        setattr(self.captured, field_name, None)

  def append_result_info(
      self, captured_messages: List[OutputResult]
  ) -> List[OutputResult]:
    """Attaches the calculation results.

    Args:
      captured_messages: List to store the captured message.

    Returns:
      captured_messages: List to store the captured message.
    """
    if self.has_prefix_drop_signal:
      self.log.warning(
          'Drop record because of hitting prefix drop signal!')
      self.has_prefix_drop_signal = False
      self.set_to_default_value()
      return captured_messages

    self._found_num += 1
    self.log.info(f'{Color.BOLD}{Color.GREEN}===== Found (%s) ====={Color.END}', self.found_num)

    # Calculate duration of the event.
    if self.captured.event_start_time and self.captured.event_end_time:
      self.captured.start_to_end_duration = self.calc_start_to_end_duration(
          self.captured.event_start_time, self.captured.event_end_time
      )
      # Check if the result meets the pass criteria or not.
      self.captured.event_end_result = self.is_test_result_pass(
          self.captured.start_to_end_duration,
          self.captured.event_pass_criteria_sec,
      )

    if self.captured.stop_speaker_time_cost_start_time and self.captured.stop_speaker_time_cost_end_time:
      self.captured.stop_speaker_time_cost_duration = self.calc_start_to_end_duration(
          self.captured.stop_speaker_time_cost_start_time,
          self.captured.stop_speaker_time_cost_end_time,
          duration_name='stop_speaker_time_cost_duration')

    if self.captured.hfp_time_cost_end_time and self.captured.hfp_time_cost_start_time:
      self.captured.hfp_time_cost_duration = self.calc_start_to_end_duration(
          self.captured.hfp_time_cost_start_time,
          self.captured.hfp_time_cost_end_time,
          duration_name='hfp_time_cost_duration')

    if self.captured.audio_routing_time_cost_start_time and self.captured.audio_routing_time_cost_end_time:
      self.captured.audio_routing_time_cost_duration = self.calc_start_to_end_duration(
          self.captured.audio_routing_time_cost_start_time,
          self.captured.audio_routing_time_cost_end_time,
          duration_name='captured.audio_routing_time_cost_duration')

    if self.captured.audio_data_time_cost_start_time and self.captured.audio_data_time_cost_end_time:
      self.captured.audio_data_time_cost_duration = self.calc_start_to_end_duration(
          self.captured.audio_data_time_cost_start_time,
          self.captured.audio_data_time_cost_end_time,
          duration_name='audio_data_time_cost_duration')

    if self.captured.stop_le_audio_time_cost_start_time and self.captured.stop_le_audio_time_cost_end_time:
      self.captured.stop_le_audio_time_cost_duration = self.calc_start_to_end_duration(
          self.captured.stop_le_audio_time_cost_start_time,
          self.captured.stop_le_audio_time_cost_end_time,
          duration_name='stop_le_audio_time_cost_duration')

    if self.captured.stop_hfp_time_cost_start_time and self.captured.stop_hfp_time_cost_end_time:
      self.captured.stop_hfp_time_cost_duration = self.calc_start_to_end_duration(
          self.captured.stop_hfp_time_cost_start_time,
          self.captured.stop_hfp_time_cost_end_time,
          duration_name='stop_hfp_time_cost_duration')

    if self.captured.audio_routing_start_time and self.captured.audio_routing_end_time:
      self.captured.audio_routing_duration = self.calc_start_to_end_duration(
          self.captured.audio_routing_start_time, self.captured.audio_routing_end_time,
          duration_name='audio_routing_duration')

    if self.captured.a2dp_switch_start_time and self.captured.a2dp_switch_end_time:
      self.captured.a2dp_switch_duration = self.calc_start_to_end_duration(
          self.captured.a2dp_switch_start_time, self.captured.a2dp_switch_end_time)

    if self.captured.le_audio_time_cost_start_time and self.captured.le_audio_time_cost_end_time:
      self.captured.le_audio_time_cost_duration = self.calc_start_to_end_duration(
          self.captured.le_audio_time_cost_start_time, self.captured.le_audio_time_cost_end_time,
          duration_name='le_audio_time_cost')

    if self.captured.start_audio_data_start_time and self.captured.start_audio_data_end_time:
      self.captured.start_audio_data_duration = self.calc_start_to_end_duration(
          self.captured.start_audio_data_start_time, self.captured.start_audio_data_end_time,
          duration_name='start_audio_data_duration')

    if self.captured.start_audio_data_time_cost_start_time and self.captured.start_audio_data_time_cost_end_time:
      self.captured.start_audio_data_time_cost_duration = self.calc_start_to_end_duration(
          self.captured.start_audio_data_time_cost_start_time,
          self.captured.start_audio_data_time_cost_end_time,
          duration_name='start_audio_data_time_cost_duration')

    # Calculate duration of the pairing dialog press time.
    if (
        self.captured.dialog_start_time
        and self.captured.dialog_end_time
        and (self.captured.event_start_time and self.captured.event_end_time)
    ):
      self.captured.dialog_process_duration = self.calc_start_to_end_duration(
          self.captured.dialog_start_time, self.captured.dialog_end_time
      )

      self.captured.start_to_end_duration = self.calc_start_to_end_duration(
          self.captured.event_start_time, self.captured.event_end_time
      )

      self.captured.final_duration = (
          self.captured.start_to_end_duration
          - self.captured.dialog_process_duration
      )

      # Check if the result meets the pass criteria or not.
      self.captured.event_end_result = self.is_test_result_pass(
          self.captured.final_duration, self.captured.event_pass_criteria_sec
      )

    # Calculate duration of the ASCS setup.
    if self.captured.ascs_start_time and self.captured.ascs_end_time:
      self.captured.ascs_setup_duration = self.calc_start_to_end_duration(
          self.captured.ascs_start_time, self.captured.ascs_end_time
      )
      # Check if the result meets the pass criteria or not.
      self.captured.ascs_end_result = self.is_test_result_pass(
          self.captured.ascs_setup_duration,
          self.captured.ascs_pass_criteria_sec,
      )

    # Calculate duration of the CIG setup.
    if self.captured.cig_setup_start_time and self.captured.cig_setup_end_time:
      self.captured.cig_setup_duration = self.calc_start_to_end_duration(
          self.captured.cig_setup_start_time, self.captured.cig_setup_end_time
      )

    # Calculate duration of the CIS setup.
    if self.captured.cis_setup_start_time and self.captured.cis_setup_end_time:
      self.captured.cis_setup_duration = self.calc_start_to_end_duration(
          self.captured.cis_setup_start_time, self.captured.cis_setup_end_time
      )

    # Calculate duration of stop stream process.
    if self.captured.event_start_time and self.captured.audio_routing_start_time:
      self.captured.stream_stop_duration = self.calc_start_to_end_duration(
      self.captured.event_start_time, self.captured.audio_routing_start_time)

    if not self.captured.stream_create_start_time and not self.captured.send_audio_start_time:
      # Calculate duration of sending audio data process.
      if self.captured.audio_routing_start_time and self.captured.event_end_time:
        self.captured.send_audio_duration = self.calc_start_to_end_duration(
        self.captured.audio_routing_start_time, self.captured.event_end_time)
    else:
      # Calculate duration of audio routing process.
      if self.captured.audio_routing_start_time and self.captured.stream_create_start_time:
        self.captured.audio_routing_duration = self.calc_start_to_end_duration(
        self.captured.audio_routing_start_time, self.captured.stream_create_start_time,
        'audio_routing_duration', ignore_order=True)

      # Calculate duration of creating audio stream.
      if self.captured.stream_create_start_time and self.captured.send_audio_start_time:
        self.captured.stream_create_duration = self.calc_start_to_end_duration(
        self.captured.stream_create_start_time, self.captured.send_audio_start_time,
        'stream_create_duration', ignore_order=False)

        # Calculate duration of sending audio data process.
        if self.captured.send_audio_start_time and self.captured.event_end_time:
          self.captured.send_audio_duration = self.calc_start_to_end_duration(
          self.captured.send_audio_start_time , self.captured.event_end_time)

      elif self.captured.stream_create_start_time and not self.captured.send_audio_start_time and self.captured.event_end_time:
        self.captured.stream_create_duration = self.calc_start_to_end_duration(
        self.captured.stream_create_start_time, self.captured.event_end_time)

    self.captured.trial += 1
    captured_messages.append(copy.deepcopy(self.captured))
    return captured_messages

  def calc_start_to_end_duration(
      self, start_time: datetime.datetime, end_time: datetime.datetime,
      duration_name: str = 'unknown',
      ignore_order: bool = False,
  ) -> datetime.timedelta:
    """Calculates the response time.

    Args:
      start_time: Start time of a duration.
      end_time: End time of a duration.

    Returns:
      event_start_to_end_duration: Time diff between start time and end time.

    Raises:
      Exception: Either start time or end time is not ready.
    """
    if not start_time or not end_time:
      raise Exception(
          f'Failed in calculating `{duration_name}`: start time or end time is not ready!')
    if not ignore_order and start_time > end_time:
      raise Exception(
          f'Failed in calculating `{duration_name}`: start time should before end time!')

    if end_time < start_time:
        end_time, start_time = start_time, end_time

    return end_time - start_time


  def is_test_result_pass(
      self, start_to_end_duration: datetime.timedelta, pass_criteria_sec: float
  ) -> EndResult:
    """Checks if the test result meet pass criteria.

    Args:
      start_to_end_duration: Time diff between start time and end time.
      pass_criteria_sec: The seconds time in pass criteria.

    Returns:
      EndResult.Pass if the result meets given passing criteria or
      EndResult.FAIL otherwise. If passing criteria is not given,
      EndResult.TBD will be returned instead.
    """
    if pass_criteria_sec:
      return (
          EndResult.PASS
          if round(start_to_end_duration.total_seconds(), 1) <= pass_criteria_sec
          else EndResult.FAIL
      )
    return EndResult.TBD

  def save_matcher_raw_data(self, matcher: re.Match[str]) -> None:
    try:
      self._global_raw_data.append(matcher.group(0))
      matched_time = matcher.group('time')
      if matched_time.startswith('02-29'):
        temp_time = datetime.datetime.strptime(
            matched_time[6:], le_audio_constants.TIME_FMT)
        temp_time = temp_time.replace(month=2, day=28)
      else:
        temp_time = datetime.datetime.strptime(
            matched_time, le_audio_constants.DATETIME_FMT)

      self.captured.temp_time = temp_time
      self.captured.raw_data.append(
          Log(self.captured.temp_time, matcher.group('log'))
      )
      self._pattern_match_times.append(temp_time)
    except Exception as e:
      print(f'Error: matcher={matcher}')
      print(f'Error: {e}')
      raise e

  def customized_reset(self) -> None:
    """Inherited by child class for implementation of customized reset."""
    pass

  def set_prefix_drop(self):
    """Set prefix drop signal to be True."""
    self.has_prefix_drop_signal = True

  def set_to_default_value(self, clean_raw_log: bool = True) -> None:
    """Sets the attributes to the default values."""
    self.customized_reset()
    self.log.info('Reset to initial values')
    self.clear_timestamps()
    if clean_raw_log:
      self.captured.raw_data.clear()
    else:
      self.captured.raw_data = self.captured.raw_data[-1:]

    self._pattern_match_times = []
    self.bt_stack_codec_configured_freq = 0
    self.bt_stack_qos_configured_freq = 0
    self.bt_stack_enabling_freq = 0
    self.bt_stack_streaming_freq = 0
    self.le_audio_profile_state = False
    self.add_cis_to_stream_sink = False
    self.bt_stack_enabling_ase_id = []
    self.all_freq = []
    # Uses for class 'LeMediaStreamToPhoneSpeaker'
    self.le_remove_iso_data_path_freq = 0
    self.cis_set_end_freq = 0
    # Uses for class 'LeConvStreamToPhoneSpeaker'
    self.audio_encode_suspend_done = False
    self.audio_decode_suspend_done = False
    # Uses for class 'LeConvStreamToPhoneSpeaker'
    self.le_setup_iso_data_path_freq  = 0
    self.cis_setup_end_freq = 0
    self.event_start = False
    self.tbsgeneric_oncallcontrol = False
    self.bluetooth_incall_service = False
    self.count_freq = None

    # Metadata of caught record
    self.captured.first_hit_start_pattern_time = None

    #Uses for class 'LeConvStreamToHfp'
    self.captured.audio_routing_start_time = None
    self.captured.audio_routing_end_time = None
    self.captured.audio_routing_duration = None

    self.captured.stream_create_start_time = None
    self.captured.send_audio_start_time = None
    self.captured.event_end_time = None

    #Uses for class 'ClassicPairPattern'
    self.endHfp_freq = 0
    self.endA2dp_freq = 0
    self.captured.mac_address_list = []
    self.captured.event_start_time = None
    self.captured.dialog_start_time = None
    self.captured.dialog_end_time = None

    #Uses for class 'ClassicReconnectBySettingUi'
    self.get_a2dp_start = False
    self.get_hfp_start = False
    self.get_a2dp_audio = False
    self.get_hfp_audio = False
    self.endHfp_freq = 0
    self.endA2dp_freq = 0

    #Uses for class 'ReconnectBySettingUi'
    self.csip_set_info_freq = 0
    self.le_audio_enter_connecting_freq = 0
    self.create_acl_connection = 0
    self.get_end_mac_address = 0
    self.get_end_2_mac_address = 0
    self.end_mac_address_list = []
    self.end_2_mac_address_list = []

    # Task 29
    self.a2dp_switch_start_time = None
    self.a2dp_switch_end_time = None
    self.captured.le_audio_time_cost_start_time = None
    self.captured.le_audio_time_cost_end_time = None
    self.captured.start_audio_data_start_time = None
    self.captured.start_audio_data_end_time = None

    # Task 28
    self.captured.start_audio_data_time_cost_start_time = None
    self.captured.start_audio_data_time_cost_end_time = None

    # Task 30
    self.captured.stop_hfp_time_cost_start_time = None
    self.captured.stop_hfp_time_cost_end_time = None

    # Task 31
    self.captured.stop_le_audio_time_cost_start_time = None
    self.captured.stop_le_audio_time_cost_end_time = None
    self.captured.audio_routing_time_cost_start_time = None
    self.captured.audio_routing_time_cost_end_time = None
    self.captured.hfp_time_cost_start_time = None
    self.captured.hfp_time_cost_end_time = None
    self.captured.audio_data_time_cost_start_time = None
    self.captured.audio_data_time_cost_end_time = None

    # Task32
    self.captured.stop_speaker_time_cost_start_time = None
    self.captured.stop_speaker_time_cost_end_time = None

    # Others
    self.captured.event_deduct_timedelta = datetime.timedelta(seconds=0)

    # Clean cache hit of all patterns
    for _, re_pattern in self.captured.log_pattern_dict.items():
      if not isinstance(re_pattern, str):
        re_pattern.reset_cache()


class LEBroadcastLogObserver(LeAudioLogObserver):
  """A class to provide template methods of LE audio broadcast log parser.

  Attributes:
    joined_broadcast_sink_mac_set: Set to hold joined broadcast Sink MAC.
    customized_condition_check_callbacks: Callback information used to examine
      the validity of a record after matching the end pattern.
    reset_before_start: True to reset the parsing process after matching the
      start pattern.
  """

  def __init__(
      self, title, log_pattern_dict, event_pass_criteria_sec,
      ascs_pass_criteria_sec=None,
      expect_start_pattern_count=1,
      expect_end_pattern_count=1,
      reset_before_start=True,
      customized_condition_check_callbacks: list[tuple[Callable, CallbackAction]] = []):
    super().__init__(
        title=title,
        log_pattern_dict=log_pattern_dict,
        event_pass_criteria_sec=event_pass_criteria_sec,
        ascs_pass_criteria_sec=ascs_pass_criteria_sec,
    )
    self.customized_condition_check_callbacks = (
        customized_condition_check_callbacks)
    self.expect_start_pattern_count = expect_start_pattern_count
    self.expect_end_pattern_count = expect_end_pattern_count
    self.joined_broadcast_sink_mac_set = set()
    self.remove_broadcast_sink_mac_set = set()
    self.reset_before_start = reset_before_start

  def customized_reset(self):
    self.joined_broadcast_sink_mac_set.clear()
    self.remove_broadcast_sink_mac_set.clear()

  def find_log_pattern(self, line: str) -> CollectOutputResult:
    """Starts to parse logs for LE Audio pairing information.

    Args:
      line: The line of input file to analyze.

    Returns:
      captured_messages: The matching messages.
    """
    # Checks if the pair patterns matches and records the raw data.
    for state, pattern in self.captured.log_pattern_dict.items():
        matcher = pattern.s(
            line, state, self.captured, reset_func=self.set_to_default_value,
            reset_before_start=self.reset_before_start)

        if matcher is not None and self.captured.event_start_time:
          re_pattern = self.captured.log_pattern_dict[state]

          if isinstance(re_pattern, le_patterns.BroadcastDisconnectByAudioStream):
            sink_mac_addr = matcher.group('sink_mac_addr')
            if sink_mac_addr in self.remove_broadcast_sink_mac_set:
              self.log.warning(
                  'Sink MAC=%s already exists in `remove_broadcast_sink_mac_set`!'
                  ' Reset the parsing process...',
                  sink_mac_addr)
              self.set_to_default_value()
              return

            self.remove_broadcast_sink_mac_set.add(sink_mac_addr)
            self.log.info(
                'Found removed sink MAC: %s', self.remove_broadcast_sink_mac_set)

          if isinstance(re_pattern, le_patterns.BroadcastSinkNotSynced2BIS):
            synced_addr_last5_ch = matcher.group('source_mac_addr')[-5:]
            self.log.info('Found synced MAC(last 5): %s', synced_addr_last5_ch)
            for sink_mac in self.remove_broadcast_sink_mac_set:
              if sink_mac.endswith(synced_addr_last5_ch):
                self.log.info('Removing Sinking MAC=%s!', sink_mac)
                self.remove_broadcast_sink_mac_set.remove(sink_mac)
                self.log.info(
                    'Current Sink MAC set: %s',
                    self.remove_broadcast_sink_mac_set)
                break
            else:
              self.log.warning(
                  'Synced MAC=%s does not exist in source MAC set!',
                  matcher.group('source_mac_addr'))

          if isinstance(re_pattern, le_patterns.BroadcastJoinByAudioStream):
            sink_mac_addr = matcher.group('sink_mac_addr')
            if sink_mac_addr in self.joined_broadcast_sink_mac_set:
              self.log.warning(
                  'Sink MAC=%s already exists in `joined_broadcast_sink_mac_set`!'
                  ' Reset the parsing process...',
                  sink_mac_addr)
              self.set_to_default_value()
              return

            self.joined_broadcast_sink_mac_set.add(sink_mac_addr)
            self.log.info(
                'Found joined sink MAC: %s', self.joined_broadcast_sink_mac_set)

          if isinstance(re_pattern, le_patterns.BroadcastGeneralSinkSynced2BIS):
            synced_addr_last5_ch = matcher.group('source_mac_addr')[-5:]
            self.log.info('Found synced MAC(last 5): %s', synced_addr_last5_ch)
            for sink_mac in self.joined_broadcast_sink_mac_set:
              if sink_mac.endswith(synced_addr_last5_ch):
                self.log.info('Removing Sinking MAC=%s!', sink_mac)
                self.joined_broadcast_sink_mac_set.remove(sink_mac)
                self.log.info(
                    'Current Sink MAC set: %s',
                    self.joined_broadcast_sink_mac_set)
                break
            else:
              self.log.warning(
                  'Synced MAC=%s does not exist in source MAC set!',
                  matcher.group('source_mac_addr'))

          if self.expect_start_pattern_count > 0 and all([
              state in {_PatternEnum.START, _BroadcastPatternEnum.START},
              re_pattern.cached_count > self.expect_start_pattern_count]):
            self.log.warning(
                Color.ORANGE + Color.BOLD +
                'The number of START pattern appears more than expectation ' +
                'consecutively and triggers a reset process!' + Color.END)
            self.captured.event_start_time = re_pattern.timestamp
            self.captured.first_hit_start_pattern_time = datetime.datetime.now()
            re_pattern.cached_count = 1
            self.drop_num += 1
            continue

          # Gets the event end time
          if state in {_PatternEnum.END, _BroadcastPatternEnum.END}:

            for callback_ex, action_type in self.customized_condition_check_callbacks:
              if callback_ex(self):
                match action_type:
                  case CallbackAction.RESET:
                    self.log.info(
                        'Hit callback=%s and conduct resetting...',
                        callback_ex.__name__)
                    self.set_to_default_value()
                    return
                  case CallbackAction.WAIT:
                    self.log.info(
                        'Hit callback=%s and do waiting...',
                        callback_ex.__name__)
                    return
                  case _:
                    self.log.warning(
                        'Hit callback=%s with unknown action=%s!',
                        callback_ex.__name__, action_type)

            if self.expect_end_pattern_count > 1:
              if re_pattern.cached_count < self.expect_end_pattern_count:
                self.log.info(
                    f'{state} hit count({re_pattern.cached_count}) is'
                    f' less than {self.expect_end_pattern_count}. waiting...')
                continue

            # Saves results if all required logs are obtained.
            if self.condition_check(
                exist_property_name_list=[
                    'event_start_time', 'event_end_time',
                ],
                start_end_time_check_list=[
                    (self.captured.event_start_time, self.captured.event_end_time),
                ],
                pattern_count_list=self.pattern_count_list):
              captured_messages = self.append_result_info([])
              self.set_to_default_value()
              return captured_messages
            elif self.expect_end_pattern_count > 0:
              self.set_to_default_value()

    time_diff = self.captured.is_timeout(self._search_timeout_sec)
    if time_diff:
      self.log.warning(
          Color.ORANGE + Color.BOLD + 'Timeout reached after '
          f'{time_diff.total_seconds()}s (limit: {self._search_timeout_sec}s)! '
          'Resetting the searching process.' + Color.END)
      self.drop_num += 1
      self.set_to_default_value()
