"""Holds LE common patterns."""
import datetime
import logging
import re
from typing import Callable, Optional, Protocol, Type

from constants import Color
import general_data
import le_audio_constants
import le_audio_parsing_data


Log = general_data.Log
_PatternEnum = general_data.PatternEnum
_PatternBroadcastEnum = general_data.PatternBroadcastEnum


class REPattern(general_data.Pattern):
  """Perf pattern written in RE."""

  def __init__(self, patterns: str | list[str],
               message: str | None = None,
               is_state: bool = False,
               round_check: bool = False,
               is_optional: bool = False,
               reset_signal: bool = False):
    self.log = logging.getLogger(self.__class__.__name__)
    self._is_match = False
    self._ever_match = False
    self._match_count = 0
    self._cached_count = 0
    self._patterns: list[re.Pattern] = []
    if isinstance(patterns, str):
      self._patterns.append(re.compile(patterns))
    else:
      self._patterns = [re.compile(pattern) for pattern in patterns]

    self._message = message
    self._timestamp = None
    self._cached_line = None
    self._is_state = is_state
    self._is_optional = is_optional
    self._round_check = round_check
    self._reset_signal = reset_signal
    self._last_hit_pattern: Optional[re.Pattern] = None
    if self.reset_signal:
      self._is_optional = True

  def search(self, line: str) -> Optional[re.Match]:
    self._last_hit_pattern = None
    for pattern in self._patterns:
      mth = pattern.search(line)
      if mth:
        self._last_hit_pattern = pattern
        self._is_match = True
        self._ever_match = True
        self._match_count += 1
        self._cached_count += 1
        try:
          matched_time = mth.group('time')
          if matched_time.startswith('02-29'):
            temp_time = datetime.datetime.strptime(
                matched_time[6:], le_audio_constants.TIME_FMT)
            temp_time = temp_time.replace(month=2, day=28)
            self._timestamp = temp_time
          else:
            self._timestamp = datetime.datetime.strptime(
                matched_time, le_audio_constants.DATETIME_FMT)
        except Exception as ex:
          print(f'Illegal line detected ({ex}):\n{line}\n')

        return mth

    return None

  def s(self, line: str,
        state: _PatternEnum,
        cached_output: le_audio_parsing_data.OutputResult,
        reset_func: Callable | None = None,
        set_prefix_drop_func: Callable | None = None,
        reset_before_start: bool = True,
        lazy_start_time: bool = False,
        skip_end_pattern: bool = False) -> Optional[re.Match]:
    mth = self.search(line)
    if mth:
      cached_output.raw_data.append(
          Log(timestamp=self.timestamp, message=mth.group('log')))

      if self.reset_signal or state == _PatternEnum.RESET:
        if not reset_func:
          raise Exception('Hit reset signal and no reset func is provided!')

        self.log.warning('%s: Hit reset signal!\n%s', state, line)
        reset_func()
        return None

      if state == _PatternEnum.PREFIX_DROP:
        if not set_prefix_drop_func:
          raise Exception(f'Hit {state} but not providing observer!')

        self.log.warning(Color.BOLD + 'Hit abandaned prefix pattern=%s', self)
        print(Color.YELLOW + line + Color.END)
        set_prefix_drop_func()
        return None

      if state == _PatternEnum.LOG_ERROR:
        self.log.warning(Color.BOLD + '%s: Log error discovered:', state)
        print(Color.RED + line + Color.END)

      if state in {
          _PatternEnum.START, _PatternEnum.OPTIONAL_START,
          _PatternBroadcastEnum.START}:
        if reset_before_start and \
            state in {_PatternEnum.START, _PatternEnum.OPTIONAL_START} and \
            reset_func:
          reset_func(clean_raw_log=False)

        if cached_output.event_start_time is None or not lazy_start_time:
          cached_output.event_start_time = self.timestamp
          cached_output.first_hit_start_pattern_time = datetime.datetime.now()

        self.log.info('%s: event_start_time=%s\n%s',
                       state, cached_output.event_start_time, line)
      elif state in {_PatternEnum.END, _PatternBroadcastEnum.END} \
          and not skip_end_pattern:
        cached_output.event_end_time = self.timestamp
        self.log.info('%s: event_end_time=%s\n%s\n',
                      state, cached_output.event_end_time, line)
      # else:
      #   self.log.info('%s:\n%s\n', state, line)
    return mth

  @property
  def last_hit_pattern(self) -> re.Pattern:
    return self._last_hit_pattern

  @property
  def match_count(self) -> int:
    return self._match_count

  @property
  def cached_count(self) -> int:
    return self._cached_count

  @cached_count.setter
  def cached_count(self, value):
    self._cached_count = value

  @property
  def cached_line(self) -> str:
    return self._cache_line

  @property
  def is_matched(self) -> bool:
    return self._is_match

  @property
  def is_optional(self) -> bool:
    return self._is_optional

  @property
  def is_ever_matched(self) -> bool:
    return self._ever_match

  @property
  def message(self) -> str | None:
    return self._message

  @property
  def reset_signal(self) -> bool:
    return self._reset_signal

  @property
  def round_check(self) -> bool:
    return self._round_check

  @property
  def timestamp(self) -> datetime.datetime | None:
    return self._timestamp

  def reset_cache(self):
    self._cached_count = 0
    self._cached_line = None

  def reset(self) -> bool:
    self._is_match = False
    self._cached_count = 0


class GroupREPattern(REPattern):
  """Group perf patterns."""

  def __init__(
      self, pattern_cls_list: list[Type[general_data.Pattern]],
      message: str | None = None,
      is_state: bool = False,
      round_check: bool = False,
      is_optional: bool = False,
      reset_signal: bool = False):
    _patterns: list[re.Pattern] = []
    for pattern_cls in pattern_cls_list:
      pttern_obj = pattern_cls()
      _patterns.extend(pttern_obj._patterns)

    super().__init__(
        patterns=_patterns, message=message, is_state=is_state,
        round_check=round_check, is_optional=is_optional, reset_signal=reset_signal)



class UserClickToConnectLe_v3(REPattern):
  pass


class CachedBluetoothDevice_NewProfileState2(REPattern):
  pass
