"""Constants used in LE performance parser task."""
import dataclasses
import enum
import os


# LE Audio environment variable prefix
_ENV_PREFIX = 'LE_AUDIO_PERF'

# Environment variable to represent DUT/SEC serial
ENV_ROUND_DIGIT = f'{_ENV_PREFIX}_ROUND_DIGIT'

# Environment variable to setup the searching timeout in second.
ENV_SEARCH_TIMEOUT = f'{_ENV_PREFIX}_PATTERNS_SEARCH_TIMEOUT_SEC'

# Perf round digit. e.g.: number = 0.1234
#   Perf round digit=1 > number = 0.1
#   Perf round digit=2 > number = 0.12
ROUND_DIGIT = 3

# When a start pattern is matched, the end pattern must appear within the
# timeout setting. If the timeout occurs, the process resets and searching
# begins again.
PATTERNS_SEARCH_TIMEOUT_SEC = int(os.environ.get(
    ENV_SEARCH_TIMEOUT, '30'))


class StrEnum(str, enum.Enum):
  """Accepts only string values."""
  pass


class HeadsetType(StrEnum):
  SamSung = 'SamSung'
  Sony = 'Sony'
  Largo = 'Largo'

  @classmethod
  def from_str(cls, headset_str) -> 'HeadsetType':
    for headset_type in cls:
      if headset_type == headset_str:
        return headset_type

    raise Exception(f'Unknown headset string="{headset_str}"!')


@dataclasses.dataclass
class LEAConfig:
  # b/326007878
  headset_type: HeadsetType
  connection_config: int
  streaming_confg: int

  @classmethod
  def get_samsung_config(cls):
    return cls.from_headset_type(HeadsetType.SamSung)

  @classmethod
  def from_headset_type(
      cls, headset_type: HeadsetType) -> 'LEAConfig':
    match headset_type:
      case HeadsetType.SamSung:
        return LEAConfig(
            headset_type=HeadsetType.SamSung,
            connection_config=2,
            streaming_confg=2)
      case HeadsetType.Sony:
        return LEAConfig(
            headset_type=HeadsetType.Sony,
            connection_config=2,
            streaming_confg=2)
      case HeadsetType.Largo:
        return LEAConfig(
            headset_type=HeadsetType.Largo,
            connection_config=1,
            streaming_confg=1)
      case _:
        raise Exception(f'Unknown Headset type=%s', headset_type)


class Color:
   ORANGE = '\033[33m'
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
   BLINK_SLOW = '\033[5m'
   BLINK_BOLD_RED_SLOW = BOLD + RED + BLINK_SLOW


def print_warning(message: str):
  print(f'{Color.BLINK_BOLD_RED_SLOW}===> {message} <==={Color.END}')


def to_alert_message(message: str) -> str:
  return f'{Color.BLINK_BOLD_RED_SLOW}===> {message} <==={Color.END}'
