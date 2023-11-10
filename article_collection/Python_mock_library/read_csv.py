import csv
import os
import sys


def read_name(csv_file: str) -> list[str]:
  """Reads the column name and return names."""
  if not os.path.isfile(csv_file):
    raise Exception(f'{csv_file} does not exist!')

  names = []
  with open(csv_file, 'r') as fo:
    for row in csv.DictReader(fo):
      print(f'Reading row={row}')
      if 'name' not in row:
        print(f'Invalid row={row}')
        return None

      names.append(row['name'])

  return names


if __name__ == '__main__':
  names = read_name(sys.argv[1])
  print(f'Obtained names: {names}')
