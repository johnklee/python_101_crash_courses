"""Module to hold utilities used in testing."""
import constants
import dataclasses
import functools
import numpy as np
import os
import pdb
from typing import Any, Callable, Optional


_ENV_PDB = 'LE_AUDIO_PDB'


@dataclasses.dataclass
class PerfP95:
  p95: float
  upper_bound: float


def get_round_digit() -> int:
  return int(
      os.environ.get(
          constants.ENV_ROUND_DIGIT,
          constants.ROUND_DIGIT))


def calc_p95_info(perf_data: list[float]) -> PerfP95:
  """Calculates the P95 related statistical data."""
  p95 = round(
      np.percentile(perf_data, 95), get_round_digit())
  q1, q3 = np.percentile(sorted(perf_data), [25, 75])
  iqr = q3 - q1
  upper_bound = round(q3 + (1.5 * iqr), get_round_digit())
  return PerfP95(p95=p95, upper_bound=upper_bound)


def pdb_able(func: Optional[Callable[..., Any]] = None,
             *,
             enter: bool = False,
             stop_services: bool = True) -> Callable[..., Any]:
  """Decorator of function which will enter PDB when any exception catched.

  This decorator will only be working when environment variable BCST_PDB is
  set to 1. Otherwise this decorator will be disabled in default.

  Args:
    func: The decorated function.
    enter: True to enter PDB right in the execution of the decorated function.
    stop_services: True to stop service(s) of device(s) in `gdevices` to avoid
      interference casued by threads launched in `ui_dump` service.

  Returns:
    The wrapper of decorated function.
  """

  def decorate_func(func: Optional[Callable[..., Any]]) -> Callable[..., Any]:

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
      if os.environ.get(_ENV_PDB, '0') == '1':
        try:
          if enter:
            return pdb.runcall(func, *args, **kwargs)
          else:
            return func(*args, **kwargs)
        except KeyboardInterrupt as ex:
          # answer = input(_INPUT_MSG_CONFIRM_SHORT_QUIT).lower()
          # if answer in {'y', 'yes'}:
          raise ex

          # logger.info('Back to work...')
        except Exception as ex:
          pdb.post_mortem(ex.__traceback__)
          raise
      else:
        return func(*args, **kwargs)

    return func_wrapper

  if func is None:
    # decorator was called with argument(s)
    return decorate_func
  else:
    # decorator was called without argument
    return decorate_func(func)


def print_p95(perf_data: list[float]):
  stat_info = calc_p95_info(perf_data)
  max_value = max(perf_data)
  print(
        constants.Color.BOLD + constants.Color.CYAN +
        f'=====> P95={stat_info.p95}; Outliner={stat_info.upper_bound};'
        f' Max={max_value}\n' +
        constants.Color.END)
