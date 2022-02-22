from pprint import pprint
import re

df_output='''
Filesystem      Size  Used Avail Use% Mounted on
udev            3.9G     0  3.9G   0% /dev
tmpfs           792M  1.9M  790M   1% /run
/dev/sda5        39G   31G  5.7G  85% /
tmpfs           3.9G     0  3.9G   0% /dev/shm
tmpfs           5.0M  4.0K  5.0M   1% /run/lock
tmpfs           3.9G     0  3.9G   0% /sys/fs/cgroup
/dev/loop0      128K  128K     0 100% /snap/bare/5
/dev/loop1      219M  219M     0 100% /snap/gnome-3-34-1804/72
/dev/loop2       62M   62M     0 100% /snap/core20/1328
/dev/loop3       56M   56M     0 100% /snap/core18/2284
/dev/loop4       62M   62M     0 100% /snap/core20/1270
/dev/loop5       66M   66M     0 100% /snap/gtk-common-themes/1515
/dev/loop6      219M  219M     0 100% /snap/gnome-3-34-1804/77
/dev/loop7      248M  248M     0 100% /snap/gnome-3-38-2004/87
/dev/loop8      249M  249M     0 100% /snap/gnome-3-38-2004/99
/dev/loop9       44M   44M     0 100% /snap/snapd/14978
/dev/loop10      66M   66M     0 100% /snap/gtk-common-themes/1519
/dev/loop11      55M   55M     0 100% /snap/snap-store/558
/dev/loop12      51M   51M     0 100% /snap/snap-store/547
/dev/loop13      56M   56M     0 100% /snap/core18/2253
/dev/sda1       511M  4.0K  511M   1% /boot/efi
tmpfs           792M   24K  792M   1% /run/user/125
'''

def parse_df_output(df_output: str):
  pattern = (
      r'(?P<filesystem>\S+)\s+(?P<size>\d+[GMK]?)\s+(?P<used>\d+[GMK]?)'
      r'\s+(?P<avail>\d+[GMK]?)\s+(?P<pert>\d+%)\s+(?P<mount>\S+)')

  df_info_list = []
  for mth in re.finditer(pattern, df_output):
    df_info_list.append((
        mth.group('filesystem'), mth.group('size'), mth.group('used'),
        mth.group('avail'), mth.group('pert'), mth.group('mount')))

  return df_info_list


pprint(parse_df_output(df_output))
