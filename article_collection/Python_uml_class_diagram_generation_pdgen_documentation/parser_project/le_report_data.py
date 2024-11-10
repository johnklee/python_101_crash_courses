"""Module to hold raw data used to generate report."""
from __future__ import annotations

import dataclasses
from general_data import OutputResult


@dataclasses.dataclass(frozen=True)
class ReportSection:
  section_name: str
  performance_index: str
  pass_criteria_name: str = 'none'

  def set_section_name(self, name) -> ReportSection:
    return ReportSection(
        section_name = name, performance_index = self.performance_index)

RS_START_AUDIO_TIME = ReportSection(
    section_name='Start audio data time cost',
    performance_index='start_audio_data')


RS_DIALOG_TIME = ReportSection(
    section_name='Dialog process time',
    performance_index='dialog')


RS_ASCS_SETUP_TIME = ReportSection(
    section_name='ASCS setup time',
    performance_index='ascs',
    pass_criteria_name='ascs_pass_criteria_sec')


RS_CIS_SETUP_TIME = ReportSection(
    section_name='CIS setup time',
    performance_index='cis_setup')


RS_CIG_SETUP_TIME = ReportSection(
    section_name='CIG setup time',
    performance_index='cig_setup')


RS_A2DP_SWITCH = ReportSection(
    section_name='A2DP time cost',
    performance_index='a2dp_switch')


RS_START_AUDIO_DATA = ReportSection(
    section_name='Start audio data time cost',
    performance_index='start_audio_data')


RS_AUDIO_ROUTING = ReportSection(
    section_name='Audio routing time cost',
    performance_index='audio_routing')


RS_STOP_HFP_TIME_COST_START_TIME = ReportSection(
    section_name='Stop HFP time cost',
    performance_index='stop_hfp_time_cost')


RS_LE_AUDIO_TIME_COST = ReportSection(
    section_name='LE audio time cost',
    performance_index='le_audio_time_cost')


RS_STOP_SPEAKER_TIME_COST = ReportSection(
    section_name='Stop speaker time cost',
    performance_index='stop_speaker_time_cost')


RS_STOP_LE_AUDIO_TIME_COST = ReportSection(
    section_name='Stop LE audio time cost',
    performance_index='stop_le_audio_time_cost')


RS_AUDIO_ROUTING_TIME_COST = ReportSection(
    section_name='Audio routing time cost',
    performance_index='audio_routing_time_cost')


RS_HFP_TIME_COST = ReportSection(
    section_name='HFP time cost',
    performance_index='hfp_time_cost')


RS_START_AUDIO_DATA_TIME_COST = ReportSection(
    section_name='Start audio data time cost',
    performance_index='start_audio_data_time_cost')


@dataclasses.dataclass(frozen=True)
class ReportRawData:
  report_title: str
  collection: list[OutputResult]
  drop_num: int = 0

  def __iter__(self):
    for output_result in self.collection:
      if output_result.title == self.report_title:
        yield output_result
