"""Constants used for le audio test."""

### Generic Constants Begin ###
DATETIME_FMT = '%m-%d %H:%M:%S.%f'
TIME_FMT = '%H:%M:%S.%f'

# LE Audio Performance Test Pass Criteria. For details, refer to:
# - go/le-audio-perf-parser-kpi-values

# Task 1: Generic: Pair and connection
PAIR_AND_CONNECT_TIME_SEC = 15.08

# Task 2: Generic: Reconnect - Turn off/on DUT BT
RECONNECT_BT_OFF_ON_TIME_SEC = 9.1

# Task 3: Media Streaming: One earbud dropping the connection and reconnection
MEDIA_STREAM_INTERRUPT_AND_RECONNECT_TIME_SEC = 3.42

# Task 4: Call conversation: One earbud dropping the connection and reconnection
CONVERSATION_STREAM_INTERRUPT_AND_RECONNECT_TIME_SEC = 4.9

# Task 5: Media Control: Play music from LE Audio device
# Task 26: Media Control: Play music from LE Audio device (SW)
STREAM_FROM_HEADSET_TIME_SEC = 2.4

# Task 6: Call Control: Incoming call from LE audio device
# Task 27: Call Control: Incoming call from LE audio device (SW)
CALL_ANSWER_FROM_HEADSET_TIME_SEC = 2.6

# Task 7: Call Control: Outgoing call from DUT
# Task 36: Call Control: Outgoing call from DUT (SW)
OUTGOING_CALL_FROM_DUT_TIME_SEC = 2.8

# Task 8: Stream interrupted by incoming call: LE media stream -> LE conversation stream
# Task 40: Stream interrupted by incoming call: LE media stream -> LE conversation stream (SW)
LE_MEDIA_STREAM_TO_LE_CONV_STREAM_TIME_SEC = 2.0

# Task 9: Stream resume back after call end with LE audio device: LE conversation stream -> LE media stream
# Task 39: Stream resume back after call end with LE audio device: LE conversation stream -> LE media stream (SW)
LE_CONV_STREAM_TO_LE_MEDIA_STREAM_TIME_SEC = 3.7

# Task 10: Media streaming: LE media stream -> DUT(speaker)
# Task 35: Media streaming: LE ISO Media Streaming -> Speaker (SW)
LE_MEDIA_STREAM_TO_DUT_SPEAKER_TIME_SEC = 0.32

# Task 11: Media streaming: DUT(speaker) -> LE media stream
# Task 34: Media streaming: Speaker -> LE ISO Media Streaming (SW)
DUT_SPEAKER_TO_LE_MEDIA_STREAM_TIME_SEC = 2.15

# Task 12: Call conversation: LE conversation stream -> DUT(speaker)
# Task 33: Call conversation: LE ISO Conv Streaming (SW) -> Speaker
LE_CONV_STREAM_TO_DUT_SPEAKER_TIME_SEC = 0.31

# Task 13: Call conversation: DUT(speaker) -> LE conversation stream
# Task 32: Call conversation: Speaker -> LE ISO conv Streaming (SW)
DUT_SPEAKER_TO_LE_CONV_STREAM_TIME_SEC = 2.35

# Task 14: Media streaming: LE media stream -> A2dp HW offload
LE_MEDIA_STREAM_TO_A2DP_HW_OFFLOAD_TIME_SEC = 1.21

# Task 15: Media streaming: A2dp HW offload -> LE media stream
# Task 29: Media streaming: A2DP (HW/SW) -> LE ISO Media Streaming (SW)
A2DP_HW_OFFLOAD_TO_LE_MEDIA_STREAM_TIME_SEC = 2.36

# Task 16: Media streaming: LE media stream -> A2dp SW encode
# Task 38: Media streaming: LE media stream (SW) -> A2dp SW encode
LE_MEDIA_STREAM_TO_A2DP_SW_ENCODE_TIME_SEC = 1.65

# Task 17: Media streaming: A2dp SW encode -> LE media stream
A2DP_SW_ENCODE_TO_LE_MEDIA_STREAM_TIME_SEC = 2.31

# Task 18: Call conversation: LE conversation stream -> HFP
# Task 31: Call conversation: LE ISO Conv Streaming (SW) -> HFP
LE_CONV_STREAM_TO_HFP_TIME_SEC = 1.35

# Task 19: Call conversation: HFP -> LE conversation stream
# Task 30: Call conversation: HFP -> LE ISO Conv Streaming (SW)
HFP_TO_LE_CONV_STREAM_TIME_SEC = 3.26

# Task 20: Generic: Reconnect - disconnect/connect from phone setting UI
# TBD

# Task 21: [Classic] Generic: Pair and connection
# TBD

# Task 22: [Classic] Generic: Reconnect - disconnect/connect from phone setting UI
# TBD

# Task 23: Media/Call Control: Volume change
LE_2_DUT_CONV_VOLUME_CONTROL_TIME_SEC = 1.3

# Task 24: Media Control: Pause Music From HS
PAUSE_MUSIC_FROM_HS_SEC = 0.4

# Task 25: Call Control: End Call From HS
END_CALL_FROM_HS_SEC = 2.9

# Task 28: Media streaming: LE ISO media stream (SW) -> A2dp (HW)
LE_MEDIA_STREAM_SW_TO_A2DP_TIME_SEC = 1.21

# Task 37: Generic: Reconnect by TA
# TBD

STREAM_FROM_HEADSET_ASCS_TIME_SEC = 1.76

CALL_ANSWER_FROM_HEADSET_ASCS_TIME_SEC = 2.08

OUTGOING_CALL_FROM_DUT_ASCS_TIME_SEC = 2.14


# LE Audio Broadcast Performance Test Pass Criteria. For details, refer to:
# - go/le_audio_broadcast_perf_criteria
# Task 1: Start broadcast latency
LE_BROADCAST_START_LATENCY_SEC = 2.5

# Task 2: Stop broadcast latency
LE_BROADCAST_STOP_LATENCY_SEC = 1

# Task 3: Broadcast -> Incoming call switch
LE_BROADCAST_INCOMING_CALL_SWITCH_SEC = 5

# Task 4: Call ended -> broadcast resume latency
LE_BROADCAST_BROADCAST_RESUMATION_FROM_CALL_END_SEC = 4.5

# Task 5: Media control latency(Play)
LE_BROADCAST_MEDIA_PLAY_LATENCY_SEC = 1

# Task 6: Media control latency(Pause)
LE_BROADCAST_MEDIA_PAUSE_LATENCY_SEC = 1

# Task 7: Volume control latency
LE_BROADCAST_VOLUME_CONTROL_LATENCY_SEC = 1

# Task 8: Find private broadcast
LE_BROADCAST_FIND_PRIVATE_BROADCAST_SEC = 10

# Task 9: Join private broadcast
LE_BROADCAST_JOIN_PRIVATE_BROADCAST_SEC = 10

# Task 10: Leave private broadcast
LE_BROADCAST_LEAVE_PRIVATE_BROADCAST_SEC = 2
