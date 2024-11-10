"""Module to keep data used in LE audio log parser."""
from __future__ import annotations

import constants
import csv
import dataclasses
import datetime
import enum
import general_data
import numpy as np
import re
from typing import List, Optional, Protocol
import le_audio_constants
import le_report_data
from le_report_gen_utils import TxtReportGen, CsvReportGen
import utils


OutputResult = general_data.OutputResult
OutputFormat = general_data.OutputFormat


TASK_TYPE_2_REPORT_SECT_MAP = {
    OutputFormat.PAIR: (
        le_report_data.RS_DIALOG_TIME,
    ),
    OutputFormat.AUDIO_PATH_SWITCH_D: (
        le_report_data.RS_STOP_HFP_TIME_COST_START_TIME,
        le_report_data.RS_AUDIO_ROUTING,
        le_report_data.RS_LE_AUDIO_TIME_COST,
        le_report_data.RS_START_AUDIO_TIME,
    ),
    OutputFormat.AUDIO_PATH_TASK_12: (
        # disabled in b/321590546#comment7
        # le_report_data.RS_STOP_LE_AUDIO_TIME_COST,
        # le_report_data.RS_START_AUDIO_DATA_TIME_COST,
    ),
    OutputFormat.AUDIO_PATH_SWITCH_LE_CONV_SW_2_HFP: (
        le_report_data.RS_STOP_LE_AUDIO_TIME_COST,
        le_report_data.RS_AUDIO_ROUTING_TIME_COST,
        le_report_data.RS_HFP_TIME_COST,
        le_report_data.RS_START_AUDIO_DATA_TIME_COST),
    OutputFormat.AUDIO_PATH_SWITCH_SPEAKER_2_LE_CONV_SW: (  # task 32
        le_report_data.RS_STOP_SPEAKER_TIME_COST,
        le_report_data.RS_AUDIO_ROUTING_TIME_COST,
        le_report_data.RS_LE_AUDIO_TIME_COST,
        le_report_data.RS_START_AUDIO_DATA_TIME_COST,
    ),
    OutputFormat.AUDIO_PATH_SWITCH_SPEAKER_2_LE_MEDIA_STREAM_SW: (  # task 34
        le_report_data.RS_AUDIO_ROUTING_TIME_COST,
        le_report_data.RS_LE_AUDIO_TIME_COST,
        le_report_data.RS_START_AUDIO_DATA_TIME_COST,
    ),
    OutputFormat.AUDIO_PATH_SWITCH_HFP_2_LE_CONV_SW: (  # task 30
        le_report_data.RS_STOP_HFP_TIME_COST_START_TIME,
        le_report_data.RS_AUDIO_ROUTING,
        le_report_data.RS_LE_AUDIO_TIME_COST,
        le_report_data.RS_START_AUDIO_DATA_TIME_COST,
    ),
    OutputFormat.AUDIO_PATH_SWITCH_A2DP_2_LE_MEDIA_STREAM: (  # task 29
        le_report_data.RS_A2DP_SWITCH,
        le_report_data.RS_AUDIO_ROUTING,
        le_report_data.RS_LE_AUDIO_TIME_COST,
        le_report_data.RS_START_AUDIO_DATA,
    ),
    OutputFormat.AUDIO_PATH_SWITCH_LE_MEDIA_STREAM_SW_2_A2DP: (  # task 28
        le_report_data.RS_A2DP_SWITCH.set_section_name('Start A2DP time cost'),
        le_report_data.RS_START_AUDIO_DATA_TIME_COST,
    ),
    OutputFormat.AUDIO: (  # task 5, 26
        le_report_data.RS_CIG_SETUP_TIME,
        le_report_data.RS_CIS_SETUP_TIME,
        le_report_data.RS_ASCS_SETUP_TIME,
    ),
    OutputFormat.AUDIO_PATH_SWITCH_LE_MEDIA_STREAM_SW_2_A2DP_SW: ( # task 38
        le_report_data.RS_LE_AUDIO_TIME_COST,
        le_report_data.RS_AUDIO_ROUTING_TIME_COST,
    ),
    OutputFormat.GENERIC: (),
}


@dataclasses.dataclass
class CollectOutputResult():
  """Defines the output data collection of the log parser.

  Attributes:
    title_list: Title of output log message.
    collection: Collects all matching patterns.
    output_messages: Collects all matching patterns in output format.
  """

  title_list: List[str] = dataclasses.field(default_factory=list)
  collection: List[OutputResult] = dataclasses.field(default_factory=list)
  output_messages: List[str] = dataclasses.field(default_factory=list)
  drop_num: int = 0

  def _event_time(self, datetime_obj):
    if not datetime_obj: return '?'
    return datetime_obj.strftime(le_audio_constants.DATETIME_FMT)

  def _duration(self, start_time, end_time):
    if not start_time or not end_time:
      return '?'

    time_delta = end_time - start_time
    return str(time_delta.total_seconds())

  def text_file_format(self) -> List[str]:
    """Checks the output format used by the test results."""

    for t in range(len(self.title_list)):
      self.output_messages.append('=' * 150)
      self.output_messages.append('*' * 3 + self.title_list[t][0])
      # Prepare success rate in title section
      # e.g.: Success Rate 60.0%, total 5, success 3
      found_num = len(self.collection)
      drop_num = self.drop_num
      total_num = found_num + drop_num
      success_rate = found_num / (found_num + drop_num) * 100
      success_rate_message = (
          f'=====> Success Rate {success_rate:.01f}%, total {total_num}'
          f', success {found_num}')
      self.output_messages.append(success_rate_message)

      # Check output format
      if self.title_list[t][1] == OutputFormat.PAIR:
        # self.to_txt_file_format_for_pair_template(self.title_list[t][0])
        self.to_txt_report_by_output_type(self.title_list[t])
      elif self.title_list[t][1] == OutputFormat.AUDIO:
        # self.to_txt_file_format_for_audio_template(self.title_list[t][0])
        self.to_txt_report_by_output_type(self.title_list[t])
      elif self.title_list[t][1] == OutputFormat.GENERIC:
        self.to_txt_report_by_output_type(self.title_list[t])
      elif (
          self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_A
          or self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_B
          or self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_C
      ):
        self.to_txt_file_format_for_audio_path_switch_template(
            self.title_list[t][0]
        )
      elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_A2DP_2_LE_MEDIA_STREAM:
        self.to_txt_report_by_output_type(self.title_list[t])
      elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_LE_MEDIA_STREAM_SW_2_A2DP:
        self.to_txt_report_by_output_type(self.title_list[t])
      elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_HFP_2_LE_CONV_SW:
        self.to_txt_report_by_output_type(self.title_list[t])
      elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_LE_CONV_SW_2_HFP:
        self.to_txt_report_by_output_type(self.title_list[t])
      elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_SPEAKER_2_LE_CONV_SW:
        self.to_txt_report_by_output_type(self.title_list[t])
      elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_SPEAKER_2_LE_MEDIA_STREAM_SW:
        self.to_txt_report_by_output_type(self.title_list[t])
      elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_LE_MEDIA_STREAM_SW_2_A2DP_SW:
        self.to_txt_report_by_output_type(self.title_list[t])
      elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_TASK_12:
        self.to_txt_report_by_output_type(self.title_list[t])
      elif self.title_list[t][1] ==  OutputFormat.AUDIO_PATH_SWITCH_D:
        self.to_txt_report_by_output_type(self.title_list[t])
      else:
        self.to_txt_report_by_output_type(self.title_list[t])
        # self.to_txt_file_format(self.title_list[t][0])

  def get_title_list(self) -> List[str]:
    """Gets a list of unique titles and the output format used."""

    for output_result in self.collection:
      self.title_list.append((output_result.title, output_result.output_format))
    self.title_list = list(set(self.title_list))

  def to_txt_file_format(self, title: str) -> None:
    """The txt output format of the captured log patterns."""

    for i in range(len(self.collection)):
      if self.collection[i].title == title:
        self.output_messages.append('-' * 50 + '|' +
                                    str(self.collection[i].trial) + '|' +
                                    '-' * 50)
        self.output_messages.append('')
        for val in self.collection[i].raw_data:
          self.output_messages.append(
              val.timestamp.strftime(le_audio_constants.DATETIME_FMT) +
              val.message)
        self.output_messages.append('')
        self.output_messages.append('Event initial time:' +
                                    self.collection[i].initial_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append('Event final ime:' +
                                    self.collection[i].final_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append(
            'Event duration:' +
            str(self.collection[i].initial_to_final_duration.total_seconds()) +
            self.collection[i].final_result)
        if self.collection[i].mac_address_list:
          for item in range(len(self.collection[i].mac_address_list)):
            self.output_messages.append(
                'Mac address:' + self.collection[i].mac_address_list[item])
        else:
          self.output_messages.append('Mac address:' + '')
        self.output_messages.append('')

  def to_txt_file_format_for_pair_template(self, title: str) -> None:
    """The txt output format of the captured log patterns for pair template."""

    for output_result in self.collection:
      if output_result.title == title:
        self.output_messages.append('-' * 50 + '|' + str(output_result.trial) +
                                    '|' + '-' * 50)
        self.output_messages.append('')
        for val in output_result.raw_data:
          self.output_messages.append(
              val.timestamp.strftime(le_audio_constants.DATETIME_FMT) +
              val.messages)
        self.output_messages.append('')
        self.output_messages.append('--Section 1 - Dialog process time--')
        self.output_messages.append('Start time:' +
                                    output_result.dialog_start_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append('End time:' +
                                    output_result.dialog_end_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append(
            'Duration:' +
            str(output_result.dialog_process_duration.total_seconds()))
        self.output_messages.append('')
        self.output_messages.append('--Event time--')
        self.output_messages.append('Start time:' +
                                    output_result.event_start_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append('End time:' +
                                    output_result.event_end_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append(
            'Duration:' +
            str(output_result.start_to_end_duration.total_seconds()))
        self.output_messages.append(
            'Event duration - Dialog press duration:' +
            str(output_result.final_duration.total_seconds()) +
            output_result.event_end_result)
        # if output_result.mac_address_list:
          # for item in set(output_result.mac_address_list):
            # self.output_messages.append('Mac address:' + item)
        # else:
          # self.output_messages.append('Mac address:')
        self.output_messages.append('')

  def to_txt_file_format_for_audio_template(self, title: str) -> None:
    """The txt output format of the captured log patterns for audio template."""

    for output_result in self.collection:
      if output_result.title == title:

        self.output_messages.append('-' * 50 + '|' + str(output_result.trial) +
                                    '|' + '-' * 50)
        self.output_messages.append('')
        for val in output_result.raw_data:
          self.output_messages.append(
              val.timestamp.strftime(le_audio_constants.DATETIME_FMT) +
              val.messages)
        self.output_messages.append('')
        self.output_messages.append('--Section 1 - CIG setup time--')
        self.output_messages.append('Start time:' +
                                    output_result.cig_setup_start_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append('End time:' +
                                    output_result.cig_setup_end_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append(
            'Duration:' + str(output_result.cig_setup_duration.total_seconds()))
        self.output_messages.append('')
        self.output_messages.append('--Section 2 - CIS setup time--')
        self.output_messages.append('Start time:' +
                                    output_result.cis_setup_start_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append('End time:' +
                                    output_result.cis_setup_end_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append(
            'Duration:' + str(output_result.cis_setup_duration.total_seconds()))
        self.output_messages.append('')
        self.output_messages.append('--Section 3 - ASCS setup time--')
        self.output_messages.append('Start time:' +
                                    output_result.ascs_start_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append('End time:' +
                                    output_result.ascs_end_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append(
            'Duration:' +
            str(output_result.ascs_setup_duration.total_seconds()) +
            output_result.ascs_end_result)
        self.output_messages.append('')
        self.output_messages.append('--Event time--')
        self.output_messages.append('Start time:' +
                                    output_result.event_start_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append('End time:' +
                                    output_result.event_end_time.strftime(
                                        le_audio_constants.DATETIME_FMT))
        self.output_messages.append(
            'Duration:' +
            str(output_result.start_to_end_duration.total_seconds()) +
            output_result.event_end_result)
        self.output_messages.append('')

  def to_csv_report_by_output_type(self, csv_writer, title_info):
    """Output collected information into report as CSV format."""
    csv_report_gen = CsvReportGen(
        sections=TASK_TYPE_2_REPORT_SECT_MAP.get(title_info[1], ()))
    csv_report_gen.gen(
        csv_writer,
        report_raw_data=le_report_data.ReportRawData(
            report_title=title_info[0], collection=self.collection))

  def to_txt_report_by_output_type(self, title_info):
    """Output collected information into report as text format."""
    txt_report_gen = TxtReportGen(
        sections=TASK_TYPE_2_REPORT_SECT_MAP.get(title_info[1], ()))
    self.output_messages.extend(txt_report_gen.gen(
        report_raw_data=le_report_data.ReportRawData(
            report_title=title_info[0],
            collection=self.collection,
            drop_num=self.drop_num)))

  def to_txt_file_format_for_audio_path_switch_template(
      self, title: str
  ) -> None:
    """The txt output format of the captured log patterns for audio path switch template."""

    for output_result in self.collection:
      if output_result.title == title:
        self.output_messages.append(
            '-' * 50 + '|' + str(output_result.trial) + '|' + '-' * 50
        )
        self.output_messages.append('')
        for val in output_result.raw_data:
          self.output_messages.append(
              val.timestamp.strftime(le_audio_constants.DATETIME_FMT)
              + val.message
          )
        self.output_messages.append('')
        self.output_messages.append('--Section 1 - Stop stream--')
        self.output_messages.append(
            'Start time:'
            + output_result.event_start_time.strftime(
                le_audio_constants.DATETIME_FMT
            )
        )
        self.output_messages.append(
            'End time:'
            + output_result.audio_routing_start_time.strftime(
                le_audio_constants.DATETIME_FMT
            )
        )
        self.output_messages.append(
            'Duration:'
            + str(output_result.stream_stop_duration_in_sec)
        )
        self.output_messages.append('')
        if output_result.stream_create_start_time:
          self.output_messages.append('--Section 2 - Audio routing--')
          self.output_messages.append(
              'Start time:'
              + output_result.audio_routing_start_time.strftime(
                  le_audio_constants.DATETIME_FMT
              )
          )
          self.output_messages.append(
              'End time:'
              + output_result.stream_create_start_time.strftime(
                  le_audio_constants.DATETIME_FMT
              )
          )
          self.output_messages.append(
              'Duration:'
              + str(output_result.audio_routing_duration_in_sec)
          )
          self.output_messages.append('')
          self.output_messages.append('--Section 3 - Create audio stream--')
          self.output_messages.append(
              'Start time:'
              + output_result.stream_create_start_time.strftime(
                  le_audio_constants.DATETIME_FMT
              )
          )
          if output_result.send_audio_start_time:
            self.output_messages.append(
                'End time:'
                + output_result.send_audio_start_time.strftime(
                    le_audio_constants.DATETIME_FMT
                )
            )
            self.output_messages.append(
                'Duration:'
                + str(output_result.stream_create_duration_in_sec)
            )
            self.output_messages.append('')
            self.output_messages.append('--Section 4 - Start audio data time--')
            self.output_messages.append(
                'Start time:'
                + output_result.send_audio_start_time.strftime(
                    le_audio_constants.DATETIME_FMT
                )
            )
            self.output_messages.append(
                'End time:'
                + output_result.event_end_time.strftime(
                    le_audio_constants.DATETIME_FMT
                )
            )
            self.output_messages.append(
                'Duration:'
                + str(output_result.send_audio_duration_in_sec)
            )
            self.output_messages.append('')
          else:
            self.output_messages.append(
                'End time:'
                + output_result.event_end_time.strftime(
                    le_audio_constants.DATETIME_FMT
                )
            )
            self.output_messages.append(
                'Duration:'
                + str(output_result.stream_create_duration_in_sec)
            )
            self.output_messages.append('')
        else:
          self.output_messages.append('--Section 2 - Start audio data time--')
          self.output_messages.append(
              'Start time:'
              + output_result.audio_routing_start_time.strftime(
                  le_audio_constants.DATETIME_FMT
              )
          )
          self.output_messages.append(
              'End time:'
              + output_result.event_end_time.strftime(
                  le_audio_constants.DATETIME_FMT
              )
          )
          self.output_messages.append(
              'Duration:'
              + str(output_result.send_audio_duration_in_sec)
          )
          self.output_messages.append('')
        self.output_messages.append('--Event time--')
        self.output_messages.append(
            'Start time:'
            + output_result.event_start_time.strftime(
                le_audio_constants.DATETIME_FMT
            )
        )
        self.output_messages.append(
            'End time:'
            + output_result.event_end_time.strftime(
                le_audio_constants.DATETIME_FMT
            )
        )
        self.output_messages.append(
            'Duration:'
            + str(output_result.start_to_end_duration_in_sec)
            + output_result.event_end_result
        )
        self.output_messages.append('')

  def save_output_messages(self, output_file_path: str) -> None:
    """Saves collected output messages to given file path.

    Args:
      output_file_path: File path to save result.
    """
    with open('./{}.txt'.format(output_file_path), 'a') as fw:
      self.text_file_format()
      fw.write('\n'.join(self.output_messages))
      fw.write('\r\n')

  def save_output_messages_to_csv(self, output_file_path: str) -> None:
    """Saves collected output messages to given file path.

    Args:
      output_file_path: File path to save result.
    """
    with open(
        './{}.csv'.format(output_file_path), 'a', newline='',
        encoding='utf-8') as csv_file:

      csv_writer = csv.writer(csv_file)
      for t in range(len(self.title_list)):
        csv_writer.writerow(["'" + '=' * 150])
        csv_writer.writerow(['*' * 3 + self.title_list[t][0]])
        if self.title_list[t][1] == OutputFormat.PAIR:
          self._save_output_messages_to_csv_for_pair_template(
              self.title_list[t][0], csv_writer)
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_TASK_12:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
        elif self.title_list[t][1] == OutputFormat.AUDIO:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
          # self._save_output_messages_to_csv_for_audio_template(
          #     self.title_list[t][0], csv_writer)
        elif self.title_list[t][1] == OutputFormat.GENERIC:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_C:
          self._save_output_messages_to_csv_for_audio_path_switch_c_template(
              self.title_list[t][0], csv_writer
          )
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_A:
          # self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
          self._save_output_messages_to_csv_for_audio_path_switch_a_template(
              self.title_list[t][0], csv_writer
          )
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_B:
          self._save_output_messages_to_csv_for_audio_path_switch_b_template(
              self.title_list[t][0], csv_writer
          )
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_A2DP_2_LE_MEDIA_STREAM:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_LE_MEDIA_STREAM_SW_2_A2DP:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_HFP_2_LE_CONV_SW:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_LE_CONV_SW_2_HFP:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_SPEAKER_2_LE_CONV_SW:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_SPEAKER_2_LE_MEDIA_STREAM_SW:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
        elif self.title_list[t][1] == OutputFormat.AUDIO_PATH_SWITCH_LE_MEDIA_STREAM_SW_2_A2DP_SW:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])
        else:
          self.to_csv_report_by_output_type(csv_writer, self.title_list[t])

  def _save_output_messages_to_csv(
      self, title: str, csv_writer: object
  ) -> None:
    """Saves collected output messages to given file path.

    Args:
      title: The title of test result.
      csv_writer: CSV writer object.
    """
    csv_writer.writerow([
        'Round', 'Event initial time', 'Event final time', 'Event duration',
        'Mac address', 'Test result (Pass/Fail)'
    ])
    for i in range(len(self.collection)):
      if self.collection[i].title == title:
        csv_writer.writerow([
            str(self.collection[i].trial),
            self.collection[i].initial_time.strftime(
                le_audio_constants.DATETIME_FMT),
            self.collection[i].final_time.strftime(
                le_audio_constants.DATETIME_FMT),
            self.collection[i].initial_to_final_duration.total_seconds(),
            self.collection[i].mac_address_list, self.collection[i].final_result
        ])

  def _save_output_messages_to_csv_for_pair_template(
      self, title: str, csv_writer: object) -> None:
    """Saves collected output messages to given file path.

    Args:
      title: The title of test result.
      csv_writer: CSV writer object.
    """
    csv_writer.writerow([
        'Time interval', '', 'Section 1 - Dialog process time', '', 'Event time'
    ])
    csv_writer.writerow([
        'Round', 'Start time', 'End time', 'Duration', 'Start time', 'End time',
        'Duration', 'Event duration - Dialog press duration', 'Test result (Pass/Fail)'
    ])
    try:
      duration_list = []
      for output_result in self.collection:
        if output_result.title == title:
          csv_writer.writerow([
              str(output_result.trial),
              output_result.dialog_start_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.dialog_end_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.dialog_process_duration.total_seconds(),
              output_result.event_start_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.event_end_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.start_to_end_duration.total_seconds(),
              output_result.final_duration.total_seconds(),
              #output_result.mac_address_list,
              output_result.event_end_result
          ])
          duration_list.append(output_result.start_to_end_duration.total_seconds())

      utils.print_p95(duration_list)
    except AttributeError:
      csv_writer.writerow('')

  def _save_output_messages_to_csv_for_audio_template(
      self, title: str, csv_writer: object) -> None:
    """Saves collected output messages of audio template to given file path.

    Args:
      title: The title of test result.
      csv_writer: CSV writer object.
    """
    csv_writer.writerow([
        'Time interval', '', 'Section 1 - CIG setup time', '', '',
        'Section 2 - CIS setup time', '', '', 'Section 3 - ASCS setup time', '',
        '', 'Event time'
    ])
    csv_writer.writerow([
        'Round', 'Start time', 'End time', 'Duration', 'Start time', 'End time',
        'Duration', 'Start time', 'End time', 'Duration',
        'Test result (Pass/Fail)', 'Start time', 'End time', 'Duration',
        'Test result (Pass/Fail)'
    ])

    try:
      for output_result in self.collection:
        if output_result.title == title:
          csv_writer.writerow([
              str(output_result.trial),
              output_result.cig_setup_start_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.cig_setup_end_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.cig_setup_duration.total_seconds(),
              output_result.cis_setup_start_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.cis_setup_end_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.cis_setup_duration.total_seconds(),
              output_result.ascs_start_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.ascs_end_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.ascs_setup_duration.total_seconds(),
              output_result.ascs_end_result,
              output_result.event_start_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.event_end_time.strftime(
                  le_audio_constants.DATETIME_FMT),
              output_result.start_to_end_duration.total_seconds(),
              output_result.event_end_result,
          ])
    except AttributeError:
      csv_writer.writerow('')

  def _save_output_messages_to_csv_for_audio_path_switch_a_template(
    self, title: str, csv_writer: object) -> None:
    """Saves collected output messages to given file path.

    Args:
      title: The title of test result.
      csv_writer: CSV writer object.
    """
    csv_writer.writerow(['Time interval', '', 'Section 1 - Stop stream time', '', '', 'Section 2 - Audio routing time', '', '', 'Section 3 - Create stream time', '', '', 'Section 4 - Start audio data time', '', 'Event time'])
    csv_writer.writerow(['Round', 'Start time', 'End time', 'Duration', 'Start time', 'End time', 'Duration', 'Start time', 'End time', 'Duration', 'Start time', 'End time', 'Duration', 'Start time', 'End time', 'Duration', 'Test result (Pass/Fail)'])
    try:
      duration_list = []
      for output_result in self.collection:
        if output_result.title == title:
          csv_writer.writerow([
              str(output_result.trial),
              output_result.event_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.audio_routing_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.stream_stop_duration.total_seconds(),
              output_result.audio_routing_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.stream_create_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.audio_routing_duration.total_seconds(),
              output_result.stream_create_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.send_audio_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.stream_create_duration.total_seconds(),
              output_result.send_audio_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.event_end_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.send_audio_duration.total_seconds(),
              output_result.event_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.event_end_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.start_to_end_duration.total_seconds(),
              output_result.event_end_result
          ])
          duration_list.append(output_result.start_to_end_duration.total_seconds())

      utils.print_p95(duration_list)
    except AttributeError:
      csv_writer.writerow("")

  def _save_output_messages_to_csv_for_audio_path_switch_b_template(
    self, title: str, csv_writer: object) -> None:
    """Saves collected output messages to given file path.

    Args:
      title: The title of test result.
      csv_writer: CSV writer object.
    """
    csv_writer.writerow([
        'Time interval', '', 'Section 1 - Stop stream time', '', '', 'Section 2 - Audio routing time', '', '',
        'Section 3 - Create stream time', '', 'Event time'])
    csv_writer.writerow([
        'Round', 'Start time', 'End time', 'Duration', 'Start time', 'End time', 'Duration', 'Start time',
        'End time', 'Duration', 'Start time', 'End time', 'Duration', 'Test result (Pass/Fail)'])
    try:
      duration_list = []
      for output_result in self.collection:
        if output_result.title == title:
          csv_writer.writerow([
              str(output_result.trial),
              output_result.event_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.audio_routing_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.stream_stop_duration.total_seconds(),
              output_result.audio_routing_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.stream_create_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.audio_routing_duration.total_seconds(),
              output_result.stream_create_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.event_end_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.stream_create_duration.total_seconds(),
              output_result.event_start_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.event_end_time.strftime(le_audio_constants.DATETIME_FMT),
              output_result.start_to_end_duration.total_seconds(),
              output_result.event_end_result
            ])
          duration_list.append(output_result.start_to_end_duration.total_seconds())

      utils.print_p95(duration_list)
    except AttributeError:
      csv_writer.writerow("")

  def _save_output_messages_to_csv_for_audio_path_switch_c_template(
      self, title: str, csv_writer: object
  ) -> None:
    """Saves collected output messages to given file path.

    Args:
      title: The title of test result.
      csv_writer: CSV writer object.
    """
    csv_writer.writerow([
        'Time interval',
        '',
        'Section 1 - Stop stream time',
        '',
        '',
        'Section 2 - Start audio data time',
        '',
        'Event time',
    ])
    csv_writer.writerow([
        'Round',
        'Start time',
        'End time',
        'Duration',
        'Start time',
        'End time',
        'Duration',
        'Start time',
        'End time',
        'Duration',
        'Test result (Pass/Fail)',
    ])
    try:
      duration_list = []
      for output_result in self.collection:
        if output_result.title == title:
          csv_writer.writerow([
              str(output_result.trial),
              output_result.event_start_time.strftime(
                  le_audio_constants.DATETIME_FMT
              ),
              output_result.audio_routing_start_time.strftime(
                  le_audio_constants.DATETIME_FMT
              ),
              output_result.stream_stop_duration.total_seconds(),
              output_result.audio_routing_start_time.strftime(
                  le_audio_constants.DATETIME_FMT
              ),
              output_result.event_end_time.strftime(
                  le_audio_constants.DATETIME_FMT
              ),
              output_result.send_audio_duration.total_seconds(),
              output_result.event_start_time.strftime(
                  le_audio_constants.DATETIME_FMT
              ),
              output_result.event_end_time.strftime(
                  le_audio_constants.DATETIME_FMT
              ),
              output_result.start_to_end_duration.total_seconds(),
              output_result.event_end_result,
          ])
          duration_list.append(output_result.start_to_end_duration.total_seconds())

      utils.print_p95(duration_list)
    except AttributeError as ex:
      csv_writer.writerow('')
