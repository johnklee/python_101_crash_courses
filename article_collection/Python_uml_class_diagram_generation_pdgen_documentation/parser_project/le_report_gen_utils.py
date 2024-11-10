"""Module to hold utility to generate performance report."""
import constants
import numpy as np
import os
import re
import utils

from typing_extensions import Protocol

from le_audio_constants import DATETIME_FMT
from le_report_data import ReportSection, ReportRawData


class ReportGen(Protocol):
  """Protocol of utility to generate performance report."""

  @property
  def sections(self):
    return self._sections

  def datetime_str(self, datetime_obj):
    return datetime_obj.strftime(DATETIME_FMT) if datetime_obj else '?'

  def duration_str(self, start_datetime_obj, end_datetime_obj,
                   pass_criteria_value: float | None = None):
    unknown_str = '?'
    if not start_datetime_obj or not end_datetime_obj:
      if pass_criteria_value:
        return f'{unknown_str}({unknown_str})'

      return unknown_str

    duration = end_datetime_obj - start_datetime_obj
    total_seconds = round(
        duration.total_seconds(),
        utils.get_round_digit())
    if pass_criteria_value is not None:
      result = 'Pass' if total_seconds <= pass_criteria_value else 'Fail'
      return f'{total_seconds}({result})'

    return str(total_seconds)

  def gen(self, report_raw_data: ReportRawData):
    ...


class CsvReportGen(ReportGen):
  """Utility to generate CSV based report."""

  def __init__(self, sections: list[ReportSection]):
    self._sections = sections

  def gen(self, csv_writer: object, report_raw_data: ReportRawData) -> list[str]:
    row = ['Time interval']
    for sect_num, report_sect in enumerate(self._sections, start=1):
      row.extend([f'Section {sect_num} - {report_sect.section_name}', '', ''])

    row.extend(['Event time info', '', '', ''])
    csv_writer.writerow(row)
    row = ['Round']
    for report_sect in self._sections:
      if report_sect.pass_criteria_name != 'none':
        row.extend(['Start time', 'End time', 'Duration', 'Test result (Pass/Fail)'])
      else:
        row.extend(['Start time', 'End time', 'Duration'])

    row.extend(['Start time', 'End time', 'Duration', 'Test result (Pass/Fail)'])
    csv_writer.writerow(row)
    duration_list = []
    try:
      for output_result in report_raw_data:
        row = [str(output_result.trial)]
        for report_sect in self._sections:
          start_datetime_obj = getattr(output_result, f'{report_sect.performance_index}_start_time')
          row.append(self.datetime_str(start_datetime_obj))
          end_datetime_obj = getattr(output_result, f'{report_sect.performance_index}_end_time')
          row.append(self.datetime_str(end_datetime_obj))
          duration_str = (
              self.duration_str(
                  start_datetime_obj, end_datetime_obj,
                  getattr(output_result, report_sect.pass_criteria_name)))

          mth = re.match(r'([.0-9]+)(\([A-Za-z]+\))', duration_str)
          if mth:
            row.append(mth.group(1))
            row.append(mth.group(2))
          else:
            row.append(duration_str)

        row.append(output_result.event_start_time.strftime(DATETIME_FMT))
        row.append(output_result.event_end_time.strftime(DATETIME_FMT))
        row.append(output_result.start_to_end_duration_in_sec)
        duration_list.append(output_result.start_to_end_duration_in_sec)
        row.append(output_result.event_end_result)
        csv_writer.writerow(row)
    except AttributeError as err:
      print(f'Somewhere went wrong while generating CSV report: {err}')
      csv_writer.writerow("")

    utils.print_p95(duration_list)


class TxtReportGen(ReportGen):
  """Utility to generate text based report."""

  def __init__(self, sections: list[ReportSection]):
    self._sections = sections

  def gen(self, report_raw_data: ReportRawData) -> list[str]:
    output_messages: list[str] = []
    for output_result in report_raw_data:
      output_messages.append(
            '-' * 50 + '|' + str(output_result.trial) + '|' + '-' * 50)
      output_messages.append('')
      for val in output_result.raw_data:
        if isinstance(val, str):
          output_messages.append(f'MESSAGE: {val}')
        else:
          output_messages.append(val.timestamp.strftime(DATETIME_FMT) + val.message)

      for sect_num, report_sect in enumerate(self._sections, start=1):
        output_messages.append('')
        output_messages.append(f'--Section {sect_num} - {report_sect.section_name}--')
        start_datetime_obj = getattr(output_result, f'{report_sect.performance_index}_start_time')
        if not start_datetime_obj:
          print(f'Failed in accessing "{report_sect.performance_index}_start_time"!')

        datetime_str = self.datetime_str(start_datetime_obj)
        output_messages.append(f'Start time:{datetime_str}')

        end_datetime_obj = getattr(output_result, f'{report_sect.performance_index}_end_time')
        if not end_datetime_obj:
          print(f'Failed in accessing "{report_sect.performance_index}_end_time"!')

        datetime_str = self.datetime_str(end_datetime_obj)
        output_messages.append(f'End time:{datetime_str}')

        duration_str =(
            self.duration_str(
                start_datetime_obj, end_datetime_obj,
                getattr(output_result, report_sect.pass_criteria_name)))
        output_messages.append(f'Duration:{duration_str}')

      output_messages.append('')
      output_messages.append('--Event time--')
      output_messages.append(
          'Start time:'
          + output_result.event_start_time.strftime(DATETIME_FMT))
      output_messages.append(
          'End time:'
          + output_result.event_end_time.strftime(DATETIME_FMT))
      output_messages.append(
          'Duration:'
          + str(output_result.start_to_end_duration_in_sec)
          + output_result.event_end_result)
      output_messages.append('')

    return output_messages
