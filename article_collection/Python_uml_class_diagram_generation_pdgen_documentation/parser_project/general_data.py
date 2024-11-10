"""Module to hold general data structure used in LE parser."""
from __future__ import annotations

import constants
import datetime
import dataclasses
import enum
import os
import re
import utils
from typing import List, Optional, Protocol, TypeAlias


NullableDatetime: TypeAlias = datetime.datetime | None
NullableTimedelta: TypeAlias = datetime.timedelta | None


class EndResult(str, enum.Enum):
  """Evaluation result shown in the report (txt,csv)."""
  PASS = '(Pass)'
  FAIL = '(Fail)'
  TBD = '(Pass criteria TBD.)'


class ResetCallable(Protocol):
  def __call__(self, clean_raw_log: bool = True) -> None: ...


@dataclasses.dataclass
class Log:
  """Dataclass to hold parsing information of timestamp and message."""
  timestamp: str | None = None
  message: str | None = None


class OutputFormat(str, enum.Enum):
  PAIR = 'Pair'
  AUDIO = 'Audio'
  GENERIC = 'Generic'
  AUDIO_PATH_SWITCH_A = 'Audio_Path_Switch_A'
  AUDIO_PATH_SWITCH_B = 'Audio_Path_Switch_B'
  AUDIO_PATH_SWITCH_C = 'Audio_Path_Switch_C'
  AUDIO_PATH_SWITCH_D = 'Audio_Path_Switch_D'
  AUDIO_PATH_SWITCH_A2DP_2_LE_MEDIA_STREAM = 'AUDIO_PATH_SWITCH_A2DP_2_LE_MEDIA_STREAM'
  AUDIO_PATH_SWITCH_LE_MEDIA_STREAM_SW_2_A2DP = 'AUDIO_PATH_SWITCH_LE_MEDIA_STREAM_SW_2_A2DP'
  AUDIO_PATH_SWITCH_LE_MEDIA_STREAM_SW_2_A2DP_SW = 'AUDIO_PATH_SWITCH_LE_MEDIA_STREAM_SW_2_A2DP_SW'
  AUDIO_PATH_SWITCH_HFP_2_LE_CONV_SW = 'AUDIO_PATH_SWITCH_HFP_2_LE_CONV_SW'
  AUDIO_PATH_SWITCH_LE_CONV_SW_2_HFP = 'AUDIO_PATH_SWITCH_LE_CONV_SW_2_HFP'
  AUDIO_PATH_SWITCH_SPEAKER_2_LE_CONV_SW = 'AUDIO_PATH_SWITCH_SPEAKER_2_LE_CONV_SW'
  AUDIO_PATH_SWITCH_SPEAKER_2_LE_MEDIA_STREAM_SW = 'AUDIO_PATH_SWITCH_SPEAKER_2_LE_MEDIA_STREAM_SW'
  AUDIO_PATH_TASK_12 = 'Audio_Path_Task12'


@dataclasses.dataclass
class OutputResult:
  """Defines data structure of log parser.

  Attributes:
    title: Title of output log message.
    trial: The round of the test result.
    raw_data: Logs matching the patterns.
    mac_address_list: The matching mac addresses of output log message.
    output_list: List of output log message in output format.
    filter_out_time: The time extracted by the filter_out_pattern.
    temp_time: The time extracted by the matching logs.
    log_pattern_list: List of log patterns for events.
    filter_out_pattern: Filter out the matching pattern.
    output_format: The type of output format.
    log_pattern_dict: Disctionary of log patterns for events.
    event_start_time: Event start time.
    event_end_time: Event end time.
    start_to_end_duration: The duration between event of start time and end
      time.
    event_end_result: End test result for event(Pass/Fail/TBD).
    event_pass_criteria_sec: The time in seconds as event passing criteria.
    dialog_start_time: The time to pop up the confirm dialog.
    dialog_end_time: The time when the user presses the confirm dialog.
    dialog_process_duration: The duration of dialog process for the paring test
    final_duration: The pairing process time(start_to_end_duration -
      dialog_process_duration)
    cig_setup_start_time: The start time to set up CIG.
    cig_setup_end_time: The end time to set up CIG.
    cig_setup_duration: Setup CIG time period.
    cis_setup_start_time: The start time to set up CIS.
    cis_setup_end_time: The end time to set up CIS.
    cis_setup_duration: Setup CIS time period.
    ascs_start_time: The start time to set up ASCS.
    ascs_end_time: The end time to set up ASCS.
    ascs_setup_duration: Setup ASCS time period.
    ascs_end_result: End test result for ASCS time period(Pass/Fail/TBD)
    ascs_pass_criteria_sec: The time in seconds as ascs passing criteria.
    performance_index_collection: Performance index collection with key as name;
        value as performance data.
    first_hit_start_pattern_time: Time for the first hit of the start pattern.
  """
  title: str = None
  trial: int = None
  none = None  # A placeholder for reporting section
  raw_data: List[Log] = dataclasses.field(default_factory=list)
  mac_address_list: List[str] = dataclasses.field(default_factory=list)
  output_list: List[str] = dataclasses.field(default_factory=list)
  filter_out_time: datetime.datetime = None
  temp_time: datetime.datetime = None
  log_pattern_list: List[str] = dataclasses.field(default_factory=list)
  filter_out_pattern: List[str] = None
  output_format: str = None
  log_pattern_dict: dict[str] = dataclasses.field(default_factory=dict)
  performance_index_collection: dict[str, float] = dataclasses.field(default_factory=dict)
  first_hit_start_pattern_time: datetime.datetime | None = None

  # Used to calculate test event time
  event_start_time: datetime.datetime = None
  event_end_time: datetime.datetime = None
  event_deduct_timedelta: datetime.timedelta = datetime.timedelta(seconds=0)
  start_to_end_duration: datetime.timedelta = None
  event_end_result: Optional[EndResult] = None
  event_pass_criteria_sec: float = None

  # Used to calculate the time to dialog process for the paring test
  dialog_start_time: datetime.datetime = None
  dialog_end_time: datetime.datetime = None
  dialog_process_duration: datetime.timedelta = None

  # Used to calculate the pairing time for the paring test
  final_duration: datetime.timedelta = None

  # Used to calculate A2DP cost time (task 29)
  a2dp_switch_start_time: datetime.datetime = None
  a2dp_switch_end_time: datetime.datetime = None
  a2dp_switch_duration: datetime.timedelta = None

  # Used to calculate LE Audio cost time (task 29)
  le_audio_time_cost_start_time: datetime.datetime = None
  le_audio_time_cost_end_time: datetime.datetime = None
  le_audio_time_cost_duration: datetime.timedelta = None

  # Used to calculate start audio data time cost (task 29)
  start_audio_data_start_time: datetime.datetime = None
  start_audio_data_end_time: datetime.datetime = None
  start_audio_data_duration: datetime.timedelta = None

  # Used to calculate start audio data time cost (task 28)
  start_audio_data_time_cost_start_time: datetime.datetime = None
  start_audio_data_time_cost_end_time: datetime.datetime = None
  start_audio_data_time_cost_duration: datetime.timedelta = None

  # Used to calculate stop HFP time cost (task 30)
  stop_hfp_time_cost_start_time: datetime.datetime = None
  stop_hfp_time_cost_end_time: datetime.datetime = None
  stop_hfp_time_cost_duration: datetime.timedelta = None

  # Used to calculate stop LE audio time cost (task 31)
  stop_le_audio_time_cost_start_time: datetime.datetime = None
  stop_le_audio_time_cost_end_time: datetime.datetime = None
  stop_le_audio_time_cost_duration: datetime.timedelta = None

  hfp_time_cost_start_time: datetime.datetime = None
  hfp_time_cost_end_time: datetime.datetime = None
  hfp_time_cost_duration: datetime.timedelta = None

  audio_routing_time_cost_start_time: datetime.datetime = None
  audio_routing_time_cost_end_time: datetime.datetime = None
  audio_routing_time_cost_duration: datetime.timedelta = None

  audio_data_time_cost_start_time: datetime.datetime = None
  audio_data_time_cost_end_time: datetime.datetime = None
  audio_data_time_cost_duration: datetime.timedelta = None

  # Used to calculate PI in task 32
  stop_speaker_time_cost_start_time: datetime.datetime = None
  stop_speaker_time_cost_end_time: datetime.datetime = None

  # Used to calculate CIG time
  cig_setup_start_time: datetime.datetime = None
  cig_setup_end_time: datetime.datetime = None
  cig_setup_duration: datetime.timedelta = None

  # Used to calculate CIS time
  cis_setup_start_time: datetime.datetime = None
  cis_setup_end_time: datetime.datetime = None
  cis_setup_duration: datetime.timedelta = None

  # Used to calculate ASCS time
  ascs_start_time: datetime.datetime = None
  ascs_end_time: datetime.datetime = None
  ascs_setup_duration: datetime.timedelta = None
  ascs_end_result: str = None
  ascs_pass_criteria_sec: float = None

  # -Section1- Used to calculate the time to stop stream process for the audio
  # path switch test
  stream_stop_start_time: datetime.datetime = None
  stream_stop_end_time: datetime.datetime = None
  stream_stop_duration: datetime.timedelta = None

  # -Section2- Used to calculate the time of audio routing process for the audio
  # path switch test
  audio_routing_start_time: datetime.datetime = None
  audio_routing_end_time: datetime.datetime = None
  audio_routing_duration: datetime.timedelta = None

  # -Section3- Used to calculate the tome to create audio stream processing for
  # the audio path switch test
  stream_create_start_time: datetime.datetime = None
  stream_create_end_time: datetime.datetime = None
  stream_create_duration: datetime.timedelta = None

  # -Section4- Used to calculate the time to start audio data processing for the
  # audio path switch test
  send_audio_start_time: datetime.datetime = None
  send_audio_end_time: datetime.datetime = None
  send_audio_duration: datetime.timedelta = None

  @property
  def start_to_end_duration_in_sec(self) -> float:
    time_in_seconds = (
        self.start_to_end_duration.total_seconds() -
        self.event_deduct_timedelta.total_seconds())
    return round(time_in_seconds, utils.get_round_digit())

  @property
  def stream_stop_duration_in_sec(self) -> float:
    return round(self.stream_stop_duration.total_seconds(), utils.get_round_digit())

  @property
  def audio_routing_duration_in_sec(self) -> float:
    return round(self.audio_routing_duration.total_seconds(), utils.get_round_digit())

  @property
  def stream_create_duration_in_sec(self) -> float:
    return round(self.stream_create_duration.total_seconds(), utils.get_round_digit())

  @property
  def send_audio_duration_in_sec(self) -> float:
    return round(self.send_audio_duration.total_seconds(), utils.get_round_digit())

  def is_timeout(self, time_sec: float) -> datetime.datetime.timedelta | None:
    """Determines if the current time exceeds the timeout (time_sec seconds after the event start)."""
    if not self.first_hit_start_pattern_time:
        return None

    time_diff = (
        datetime.datetime.now() - self.first_hit_start_pattern_time)
    return time_diff if time_diff.total_seconds() > time_sec else None


class Pattern(Protocol):
  """Performance pattern protocol."""

  def search(self, line: str) -> re.Match[str] | None:
    """Searches the line according to assigned pattern."""

  def s(self, line: str, state: PatternEnum,
        cached_output: OutputResult,
        reset_func: ResetCallable | None = None,
        reset_before_start: bool = True,
        skip_end_pattern: bool = False) -> re.Match[str] | None:
    """Searches the line according to assigned pattern."""

  @property
  def match_count(self) -> int:
    """Matched count in parsing."""

  @property
  def cached_count(self) -> int:
    """Cached count which is resetable."""

  @property
  def cached_line(self) -> str:
    """Cached last matched line."""

  @property
  def timestamp(self) -> datetime.datetime | None:
    """Timestamp of matched line."""

  @property
  def is_ever_matched(self) -> bool:
    """Checks if pattern is matched ever."""

  @property
  def is_matched(self) -> bool:
    """Checks if pattern is matched or not."""

  @property
  def is_optional(self) -> bool:
    """If this pattern matching is optional or not."""

  def reset(self) -> bool:
    """Resets searching history."""

  def reset_cache(self):
    self._cached_count = 0
    self._cached_line = None


class PatternBroadcastEnum(enum.Enum):
  """Defines constants of broadcast log pattern."""
  START = 'Start'
  CREATE = 'Create'
  CREATE_QUEUED = 'Create queued'
  CREATE_AUDIO_BROADCAST = 'BroadcastCreateAudioBroadcast'
  LEA_START_BROADCAST = 'BoradcastLeAudioServiceStartBroadcast'
  CREATE_BIG = 'BroadcastCreateBig'
  SET_ISO_PATH = 'BroadcastSetISODataPath'
  START_AUDIO_HAL = 'BroadcastStartAudioHal'
  AUDIO_SESSION_AIDL_STARTED_HARDWARE_OFFLOAD_ENCODING = (
      'BroadcastAudioSessionAidlStarted_HardwareOffloadEncoding')
  JNI_PAUSE_BROADCAST_NATIVE = 'BroadcastJniPauseBroadcastNative'
  STOP_AUDIO_HAL = 'STOP_AUDIO_HAL'
  PAUSE = 'PAUSE'
  STREAMING = 'STREAMING'
  END = 'End'
  TBD = 'TBD'

  SERVICE_STOP = 'Service Stop'
  STACK_STOP = 'Stack Stop'
  AUDIO_HAL_STOP = 'Audio HAL Stop'
  REMOVE_ISO_PATH = 'Remove ISO Path'
  TERMINATE_BIG = 'Terminate BIG'
  TERMINATE_BIG_CMPL = 'Terminate BIG Complete'
  BROADCAST_STOPPED = 'Broadcast Stopped'

  SERVICE_PLAY = "Service Play"
  SERVICE_PAUSE = "Service Pause"

  CONTROL_VOLUME_WITH_VALUE = "Control Volume"
  STACK_CONTROL_VOLUME = "Stack Control Volume"
  STACK_VCP_WRITE_CONTROL_POINT = "Stack VCP Wrote Control Point"
  STACK_VCP_NOTIFICATION = "Stack VCP Notification"

  GATT_START_SCAN = 'GATT_START_SCAN'
  ID_FOUND = 'ID_FOUND'
  SELECT_SOURCE = 'SELECT_SOURCE'
  GATT_SYNC_DEVICE = 'GATT_SYNC_DEVICE'
  SOURCE_SYNCED = 'SOURCE_SYNCED'

  SINK_SYNCED_2_BIS = 'SINK_SYNCED_2_BIS'
  BASS_CLIENT_SERVICE_ADD_SOURCE = 'BASS_CLIENT_SERVICE_ADD_SOURCE'
  BASS_CLIENT_STATE_MACHINE_CONNECTED = 'BASS_CLIENT_STATE_MACHINE_CONNECTED'
  BASS_CLIENT_SERVICE_REMOVE_SOURCE = 'BASS_CLIENT_SERVICE_REMOVE_SOURCE'
  BASS_CLIENT_STATE_MACHINE_UPDATE_SOURCE = 'BASS_CLIENT_STATE_MACHINE_UPDATE_SOURCE'
  BASS_CLIENT_STATE_MACHINE_EXIT_CONNECTED = 'BASS_CLIENT_STATE_MACHINE_EXIT_CONNECTED'


class PatternEnum(enum.Enum):
  """Defines constants of log pattern."""
  # Enum for general setting.
  LOG_ERROR = 'GeneralLogError'

  # Enum for default setting.
  TBD = 'TBD'
  TBD2 = 'TBD2'
  STATE_1 = 'State1'
  STATE_2 = 'State2'
  STATE_3 = 'State3'
  FOOL_PROOF = 'FoolProofPatterns'
  SENTRY = 'Sentry'
  SENTRY2 = 'Sentry2'
  RESET_CIS_REQ = 'RESET_CIS_REQ'

  # Enum for common behavior
  CUSTOM_START = 'Customized start'
  START = 'Start'
  OPTIONAL_START = 'Optional Start'
  END = 'End'
  RESET = 'Reset'
  RESET2 = 'Reset2'
  PREFIX_DROP = 'Prefix drop'

  # Enum for call
  NEW_CALL = 'CallsManager_ActiveCallForNewCall'
  END_CALL = 'CallsManager_CallState2DISCONNECTED'

  # Enum for prerequisite condition check
  PRE_RING_TONE_ENABLED = 'Ring tone should be enabled'

  # Enum for pair pattern
  BLUETOOTH_BOND_STATE_MACHINE = 'Bluetooth_Bond_State_Machine'
  INTENT = 'Intent'
  PAIRING_DIALOG = 'Pairing_Dialog'
  DIALOG_ACCEPTED = 'Dialog_Accepted'
  GATT_START = 'Gatt_Start'
  GATT_END = 'Gatt_End'
  CSIP_SET_COORDINATOR_STATE_MACHINE = 'Csip_Set_Coordinator_State_Machine'
  CSIS_ACTIVE_OBSERVER_SET = 'Csis_Active_Observer_Set'
  CSIP_SET_MEMBER = 'Csip_Set_Member'
  GATT_SERVICE_DISCOVER_USE_LE_TRANSPORT = 'CsisActiveObserverSet_Discover'
  GATT_SENDING_REQUEST_2_UPPER_LAYER = 'SendingGattRequest2UpperLayer'

  # Enum for stream from headset pattern
  MEDIA_SESSION_SERVICE = 'Media_Session_Service'
  MSESSTRIGGER_PLAY = 'MsessTrigger_Play'

  # Enum for audio test pattern
  ASCS_SETUP_START = 'OnAudioSinkResume'
  ASCS_SETUP_START_OP2 = 'LE_AUDIO_SOFTWARE_ENCODING_DATAPATH, cookie=0x400, state=STANDBY'
  ASCS_SET_STREAMING = 'ASCS_Set_Streaming'
  CIG_SETUP_START = 'CIG_Setup_Start'
  CIG_SETUP_END = 'CIG_Setup_End'
  CIS_SETUP_START = 'CIS_Setup_Start'
  CIS_SETUP_START_OP2 = 'CIS_Setup_Start_OP2'
  CIS_SETUP_END = 'CIS_Setup_End'
  LE_CREATE_CIS = 'LE_Create_CIS'
  LE_SETUP_ISO_DATA_PATH = 'LE_Setup_Iso_Data_Path'
  ASCS_SETUP_END = 'Start_Sending_Audio'
  AUDIO_HW_BLE_ENCODE_START = 'Audio_Hw_Ble_Encode_Start'
  AUDIO_HW_BLE_ENCODE_DONE = 'Audio_Hw_Ble_Encode_Done'
  BT_AUDIO_PROVIDER_STUB_ENCODING = 'BT_Audio_Provider_Stub_Encoding'
  BT_AUDIO_PROVIDER_STUB_ENCODING_SUCCESS = 'BT_Audio_Provider_Stub_Encoding_Success'
  BT_AUDIO_SESSION_AIDL_ENCODING = 'BT_Audio_Session_Aidl_Encoding'
  AUDIO_HW_BLE_UPDATE = 'Audio_Hw_Ble_Update'
  BT_AUDIO_SWE_SUCCESS = 'BTAudioProviderStub_SWE_Success'
  BT_AUDIO_SWE_ENCODING_SUCCESS = 'BTAudioProviderStub_SWE_Encoding_Success'
  BT_AUDIO_A2DP_ENCODING_SUCCESS = 'BTAudioProviderStub_A2DPEncodingSuccess'
  BT_AUDIO_SWE_UPDATE_METADATA = 'BTAudioSessionAidl_SWE_UpdateSourceMetadata'
  AUDIO_MEDIA_PLAYER_STATE_PLAYING = 'AudioMediaPlayerWrapper_StatePlaying'

  # Enum for CallAnswerFromHsPattern
  BLUETOOTH_INCALL_SERVICE = 'Bluetooth_Incall_Service'
  TELEPHONY = 'Telephony'
  ON_AUDIO_METADATA_UPDATE = 'On_Audio_Metadata_Update'
  UPDATE_CONFIG_CONVERSATIONAL = 'Update_Config_Conversational'
  AUDIO_HW_BT = 'Audio_Hw_Bt'
  BT_LE_AUDIO_SWD = 'BTAudioProviderStub_LEAudioSWD'
  TELE_EVENT_REQUEST_ACCEPT = 'TelecomEvent_RquestAccept'

  # Enum for outgoing call test
  LE_CREATE_CIS_SUCCESS = 'Le_Create_CIS_Success'
  AUDIO_HW_BLE_DECODE_START = 'Audio_Hw_Ble_Decode_Start'
  AUDIO_HW_BLE_DECODE_DONE = 'Audio_Hw_Ble_Decode_Done'
  BT_AUDIO_PROVIDER_STUB_DECODING = 'BT_Audio_Provider_Stub_Decoding'
  BT_AUDIO_SESSION_AIDL_DECODING = 'BT_Audio_Session_Aidl_Decoding'
  ON_AUDIO_SOURCE_RESUME = 'On_Audio_Source_Resume'

  # Enum for Media Streaming - Connection interruptted and reconnected test
  LE_AUDIO_PROFILE_CONNECT = 'Le_Audio_Profile_Connect'
  LE_AUDIO_PROFILE_STATE = 'Le_Audio_Profile_State'
  LE_AUDIO_PROFILE_STATE_2 = 'Le_Audio_Profile_State_2'
  BT_STACK_CODEC_CONFIGURED = 'Bt_Stack_Codec_Configured'
  BT_STACK_QOS_CONFIGURED = 'Bt_Stack_Qos_Configured'
  BT_STACK_ENABLING = 'Bt_Stack_Enabling'
  BT_STACK_CIS_CREATE_FOR_DEVICE = 'Bt_Stack_Cis_Create_For_Device'
  BT_STACK_STREAMING = 'Bt_Stack_Streaming'

  # Enum for Call conversational - Connection interruptted and reconnected testclear
  BT_STACK_STATE = 'Bt_Stack_State'
  ADD_CIS_TO_STREAM_SINK = 'Add_Cis_To_Stream_Sink'

  # Enum for Audio path switching (LE media streaming -> Phone Speaker)
  BT_STACK_STOP = 'Bt_Stack_Stop'
  BT_STACK_LE_AUDIO_CLOSE = 'Bt_Stack_Le_Audio_Close'
  LE_REMOVE_ISO_DATA_PATH = 'LERemoveISODataPath'
  LE_REMOVE_CIG = 'Le_Remove_Cig'
  COMPLETE_LE_REMOVE_CIG = 'Complete_Le_Remove_Cig'
  LE_AUDIO_STOPSESSION = 'Le_Audio_Stopsession'
  GETTNOTIFEVENT_CODEC_CONFIGURED = 'Gattnotifevent_Codec_Configured'
  AOC_OUTPUT_STOPPED = 'Aoc_Output_Stopped'
  AOC_SINKBT_ESCO = 'Start Audio'
  AIDL_END_SESSION = 'AIDLEndSession'
  ON_LOCAL_AUDIO_SOURCE_RESUME_STATE_INFO = (
      'OnLocalAudioSourceResume_ReceiverIDLE_SenderREADY_TO_RELEASE')
  LE_AUDIO_STATE_MACHINE_PROCESS_HCI_NOTIFY_ON_CIG_CREATE = (
      'LEAudioStateMachine_ProcessHciNotifOnCigCreate')
  START_SENDING_AUDIO = 'ASCSSetupEnd'
  RECV_CALL_CONTROL_REQUEST = 'TbsGenericOnCallControlPointRequest'

  # Enum for Audio switch switching (Phone Speaker -> LE media streaming)
  AOC_OFF_SC = 'Aoc_Off_Sc'
  SINK_BT_A2DP_BLE_OUTPUT_STOPPED = 'SinkBT_A2DP_BLE_OutputStopped'
  BLE_START_STREAM_BEGIN = 'BLEStartStreamBegin'
  BLE_START_STREAM_DONE = 'BLEStartStreamDone'
  RECV_CMD_LE_CREATE_CIS_SUCCESS = 'Receive_Cmd_LE_CREATE_CIS_Success'
  SEND_CMD_LE_SETUP_ISO_DATA_PATH = 'LESetupISODataPath'
  RECV_CMD_LE_SETUP_ISO_DATA_PATH_COMPLETE = 'CisSetupEnd'
  BT_AUDIO_PROVIDER_STUB_STREAM_SUSPEND_TYPE_1 = (
      'BTAudioProviderStub_StreamSuspend_Type1')
  BT_AUDIO_PROVIDER_STUB_STREAM_SUSPEND_TYPE_2 = (
      'BTAudioProviderStub_StreamSuspend_Type2')
  ASE_TO_STREAMING_STATE = 'LEAudioStateMachine_ASE_ENABLING_STREAMING'
  FACTORYAIDL_ENCODING_GETPROVIDER = 'Factoryaidl_Encoding_Getprovider'
  BT_STACK_ENCODING = 'Bt_Stack_Encoding'
  FACTORYAIDL_ENCODING_OPENPROVIDER = 'Factoryaidl_Encoding_Openprovider'
  FACTORYAIDL_DECODING_GETPROVIDER = 'Factoryaidl_Decoding_Getprovider'
  BT_STACK_DECODING = 'Bt_Stack_Decoding'
  FACTORYAIDL_DECODING_OPENPROVIDER = 'Factoryidl_Decoding_Openprovider'
  UPDATE_CONFIG_CONTEXT = 'Update_Config_Context'
  GATT_STREAMING = 'Gatt_Streaming'

  # task 12
  # Enum for Audio switch test(LE conversation stream -> DUT Speaker)
  BT_STACK_SUSPENDREQUEST = 'Bt_Stack_Suspendrequest'
  BT_AUDIO_PROVIDER_STUB_SUSPENDED_ENCODING = 'BT_Audio_Provider_Stub_Suspended_Encoding'
  AUDIO_HW_BLE_SUSPEND = 'Audio_Hw_Ble_Suspend'
  AUDIO_HW_BLE_ENCODE_SUSPEND_DONE = 'Audio_Hw_Ble_Encode_Suspend_Done'
  BT_AUDIO_PROVIDER_STUB_SUSPENDED_DECODING = 'BT_Audio_Provider_Stub_Suspended_Decoding'
  AUDIO_HW_BLE_DECODE_SUSPEND_DONE = 'Audio_Hw_Ble_Decode_Suspend_Done'
  BLE_OUTPUT_SUSPEND_STREAM_DONE = 'BLEOutWrapper_SuspendStreamDone'
  AOC_SPEAKER_STARTED = 'AOCSpeakerStarted'

  # Enum for Audio switch test(Phone Speaker -> Le Conversation Stream)
  AOC_OFF = 'Aoc_Off'
  VOICE_SPEAKER_MIC = 'Voice_Speaker_Mic'
  AUDIO_HW_PATCH_ROUTING = 'AudioHWPatchVoipOrAudioRoutingOrLowLatencyPlayback'

  # Enum for Audio switch test(Music Output -> Call Output)
  TBSGENERIC_ONCALLCONTROL = 'Tbsgeneric_Oncallcontrol'

  # Enum for Audio switch test(Music Output -> Call Output)
  ON_AUDIO_METADATA_UPDATE_MEDIA = 'On_Audio_Metadata_Update_Media'

  # Enum for Audio switch test(LE media streaming -> A2dp HW offload)
  BLUTOOTH_ACTIVE_DEVICE = 'Bluetooth_Active_Device'
  BT_STACK_HW_ENCODING = 'Bt_Stack_Hw_Encoding'
  LE_AUDIO_CLEANUP = 'Le_Audio_Cleanup'
  AUDIO_HW_A2DP_START = 'Audio_Hw_A2dp_Start'
  A2DP_PLAYING = 'A2dp_Playing'
  AUDIO_HW_A2DP_DONE = 'Audio_Hw_A2dp_Done'
  BT_AUDIO_PROVIDER_FACTORY_AIDL_A2DP_HW_ENCODING = 'BTAudioProviderFactoryAIDL_A2DP_HWDecoding'
  FETCH_AUDIO_PROVIDER_BT_AUDIO_HAL_AWDP_SW_ENCODING = 'FetchAudioProviderBluetoothAudioHalA2DPSWEncoding'
  BT_AUDIO_PROVIDER_FACTORY_GET_AUDIO_HAL_CAP = 'BTAudioProviderFactoryAIDL_GetAudioHALCap'
  LE_AUDIO_CLEANUP_SINK = 'LEAudio_CleanupSink'

  # Enum for Audio switch test(A2dp HW ffload -> LE media streaming)
  A2DP_STREAMING_STOP = 'A2dp_Streaming_Stop'
  A2DP_STREAMING_SUSPEND_FINISHED = 'A2dp_Streaming_Suspend_Finished'
  ON_LOCAL_AUDIO_SOURCE_RESUME_IDLE = 'ASCSSetupStart'
  AUDIO_HW_BLE_START = 'Audio_Hw_Ble_Start'
  SWITCHING_DEVICE_SIGNAL = 'ReceiveSwitchingDeviceSignal'
  AUDIO_SUPPORT_SW_ENCODING_CODEC = 'BTAudioProviderFactoryAIDL_SupportSWEncoding'
  AUDIO_SUPPORT_SW_DECODING_CODEC = 'BTAudioProviderFactoryAIDL_SupportSWDecoding'
  AUDIO_SUPPORT_HW_DECODING_CODEC = 'BTAudioProviderFactoryAIDL_SupportHWDecoding'
  AUDIO_SUPPORT_HW_DECODING_SUCCESS = 'BTAudioProviderFactoryAIDL_HWDecoding_Success'
  LE_AUDIO_TIME_COST_START = 'LEAudioStartStreaming'
  A2DP_STATE_MACHINE_NOT_PLAY_2_PLAY = 'A2dpStateMachine_NotPlay2Play'

  # Enum for Audio switch test(LE media streaming -> A2dp SW encode)
  BT_STACK_SW_ENCODING = 'Bt_Stack_Sw_Encoding'

  # Enum for Audio switch test(LE media stream -> HFP)
  HENDSETSERVICE_SETACTIVEDEVICE = 'Headsetservice_Setactivedevice'
  ASCS_SET_IDLE = 'Ascs_Set_Idle'
  GETTNOTIFEVENT_RELEASING = 'Gettnotifevent_Releasing'
  AUDIO_EVENT_CONNECTED = 'Audio_Event_Connected'
  SCO_EVENT = 'Sco_Event'
  BTA_AG_CONNECT_OPEN = 'BTA_AG_ConnectOpen'
  AUDIO_SOURCE_HAL_CLIENT_STOP = 'AudioSourceHALClient_Stop'
  AUDIO_SINK_HAL_CLIENT_STOP = 'AudioSinkHALClient_Stop'

  # Enum for Audio switch test(HFP -> LE conversation streaming)
  HENDSETSERVICE_DISCONNECT_AUDIO = 'Headsetservice_Disconnect_Audio'
  SCO_CLOSE = 'Sco_Close'
  AUDIO_DISCONNECTED = 'Audio_Disconnected'
  AIDL_STARTREQUEST = 'Aidl_Startrequest'
  GETTNOTIFEVENT_STREAMING = 'Gattnotifevent_Streaming'
  BT_AUDIO_HAL_START_STREAM = 'Bluetooth Audio HAL start stream'
  LE_AUDIO_IDLE_2_STREAMING = 'LEAudioStartStreaming'
  BTA_AG_CLOSE_SCO = 'BTA_AG_CloseSCO'
  HS_SM_AUDIO_DISCONNECTED = 'HeadsetStateMachine_AudioDisconnected'

  # Enum for Reconnect - Turn off/on DUT BT test
  CSIP_SET_INFO = 'Csip_Set_Info'
  ACCEPT_LE_CONNECTION = 'Accept_Le_Connection'
  CC_REMOVE_DEVICE_FROM_ACCEPT_LIST = 'OnCommandComplete_RemoveDeviceFromAcceptList'
  GATT_LE_CONNECTION_COMPLETED = 'GATT_LE_CONNECTION_COMPLETED'
  LE_AUDIO_ENTER_DISCONNECTED = 'Le_Audio_Enter_Disconnected'
  CREATE_ACL_CONNECTION = 'Create_Acl_Connection'
  CREATE_ACL_CONNECTION_COMPLETED = 'Create_Acl_Connection_Completed'

  # Enum for BR/EDR Pairing
  ADAPTER_CONNECTION_STATE_CHANGE = 'Adapter_Connection_State_Change'
  A2DP_CONNECTED = 'A2dp_connected'

  # Enum for BR/EDR Reconnection by Setting UI
  BT_A2DP_SERVICE_JIN_CONNECT = 'Bt_A2dp_Service_Jin_Connect'
  ADAPTER_PROFILE_CONNECTION_STATE_CHANGE_A2DP_DISCONNECT = 'Adapter_Profile_Connection_State_Change_A2dp_Disconnect'
  BT_A2DP_SERVICE_JIN_CALLBACK = 'Bt_A2dp_Service_Jin_Callback'
  SET_A2DP_ACTIVE_DEVICE = 'Set_A2dp_Active_Device'
  A2DP_SERVICE_SET_ACTIVE_DEVICE = 'A2dp_Service_Set_Active_Device'
  BT_A2DP_SERVICE_JIN_SET = 'Bt_A2dp_Service_Jin_Set'
  HFP_CONNECT = 'Hfp_Connect'
  BT_HEADSET_SERVICE_JIN_CONNECT = 'Bt_Headset_Service_Jin_Connect'
  ADAPTER_PROFILE_CONNECTION_STATE_CHANGE_DISCONNECT = 'Adapter_Profile_Connection_State_Change_Disconnect'
  ADAPTER_PROFILE_CONNECTION_STATE_CHANGE_CONNECT = 'Adapter_Profile_Connection_State_Change_Connect'
  BT_HEADSET_SERVICE_JIN_CALLBACK = 'Bt_Headset_Service_Jin_Callback'
  SET_HEADSET_ACTIVE_DEVICE = 'Set_Headset_Active_Device'
  AUDIO_DEVICE_ADDED = 'Audio_Device_Added'
  A2DP_AUDIO_DEVICE_ADDED = 'A2dp_Audio_Device_Added'
  HFP_AUDIO_DEVICE_ADDED = 'Hfp_Audio_Device_Added'

  # Enum for Reconnect - from settings ui test
  LE_AUDIO_ENTER_CONNECTING = 'Le_Audio_Enter_Connecting'

  # Enum for Media/Call controls
  VOLUME_STATE_UPDATE = 'Volume_State_Update'
  GROUP_VOLUME_STATE_CHANGE = 'On_Group_Volume_State_Changed'
  VOLUME_CHANGED_BY_BT = 'VolumeChangedByBT'
  MEDIA_CONTROL_PAUSE_REQUEST = 'Media_Control_Pause_Request'
  CALL_REMOVED = 'Call_Removed'

  # Enum for task 37
  GATT_CONNECT_MANAGER_FOUND_TA = 'GATTConnectManagerFoundTA'
  GATT_CONNECT_SUCCESS = 'OnGattConnectedSuccess'
  CSIP_CACHED_INFO = 'CsipSetCoordinatorService_EventDeviceAvailable'
  TASK_37_EVENT_END = 'TASK_37_EVENT_END'

  # Enum for task 38
  BT_STACK_ASE_STATUS_RELEASE = 'BTStackASEStatusReleasing'
  GATT_NOT_IF_EVENT_ENABLING_STREAMING = 'ProcessGattNotifEvent_EnablingStreaming'

  # Enum for task 42
  ON_LOCAL_AUDIO_SOURCE_METADATA_UPDATE_STARTED = 'AudioReceiverState_Idle2Started'
  RECONFIGURE_OR_UPDATE_METADATA_RINGTONE = 'ReconfigureOrUpdateMetadata_Ringtone'
  AUDIO_HAL_START_INPUT_STREAM = 'AudioHALStartInputStreamGroup'
  START_RECV_AUDIO = 'StartRecvAudio'

  # Enum for task 7: Outgoing Call Pattern (HW)
  LOCAL_AUDIO_SOURCE_RESUME_RIDLE_SIDLE = (
      'OnLocalAudioSourceResume_ReceiverIDLE_SenderIDLE')
  GROUP_STREAM_CONFIG_CONTEXT_TYPE = 'GroupStream_ConfigContextType'
