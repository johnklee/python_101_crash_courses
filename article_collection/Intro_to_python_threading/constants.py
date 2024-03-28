class Color:
  """Terminal Color information."""

  # Color
  PURPLE = '\033[95m'
  CYAN = '\033[96m'
  DARKCYAN = '\033[36m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  DARK_RED = '\033[31m'

  # Set
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  END = '\033[0m'
  BLINK_SLOW = '\033[5m'

  # Combination
  BLINK_BOLD_RED_SLOW = BOLD + RED + BLINK_SLOW


ColorOptions = (
    Color.BLUE, Color.YELLOW, Color.GREEN, Color.CYAN, Color.RED,
    Color.DARKCYAN, Color.PURPLE)
