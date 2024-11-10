"""The observe to detect LE audio pairing test."""
import constants
import datetime
import re

import general_data
import le_audio_constants
import le_patterns

from le_audio_parsing_data import CollectOutputResult
from le_audio_parsing_data import OutputFormat
from observer.le_audio_log_observer import LeAudioLogObserver


Log = general_data.Log
_PatternEnum = general_data.PatternEnum


class PairPattern(LeAudioLogObserver):
  """The observe to detect LE audio pairing process from log for testing purpose.

  This observer is for task 1. Please refer to below link for log template:
  - go/le_audio_perf_parser_task1_log_template
  """

  def __init__(self):
    """start setup test."""
    super().__init__(
        title='***Start To Parse Log For LE Audio Pairing Information\n',
        log_pattern_dict={
            _PatternEnum.START:
                le_patterns.UserClickToConnectLe_v3(),
            _PatternEnum.END:
                le_patterns.CachedBluetoothDevice_NewProfileState2(),
        },
        event_pass_criteria_sec=le_audio_constants.PAIR_AND_CONNECT_TIME_SEC,
        ascs_pass_criteria_sec=None)
    self.start_pattern_enum = _PatternEnum.START
    self.end_pattern_enum = _PatternEnum.END
    self.start_pattern = le_patterns.UserClickToConnectLe_v3()
    self.end_pattern = le_patterns.CachedBluetoothDevice_NewProfileState2()
    self.get_end_mac_address = 0
    self.get_end_2_mac_address = 0
    self.end_mac_address_list = []
    self.end_2_mac_address_list = []

  def update_lea_config_callback(self):
    if self.lea_config.headset_type == constants.HeadsetType.Largo:
      self.captured.log_pattern_dict[_PatternEnum.CSIP_SET_COORDINATOR_STATE_MACHINE]._is_optional=True
      self.captured.log_pattern_dict[_PatternEnum.CSIP_SET_MEMBER]._is_optional=True

  def customized_reset(self) -> None:
    self.captured.mac_address_list.clear()
    self.get_end_mac_address = 0
    self.get_end_2_mac_address = 0
    self.end_mac_address_list = []
    self.end_2_mac_address_list = []

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
            line, state, self.captured, reset_func=self.set_to_default_value)

        if matcher is not None and self.captured.event_start_time:
          pass
