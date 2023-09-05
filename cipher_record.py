#!/usr/bin/env python3

import subprocess
import sys
import argparse

frequency = sys.argv[1]
duration = sys.argv[2]
output = sys.argv[3]

cmd = f"tshark -i lo -f udp -w - | " \
      f"tshark -r - " \
      f"" \
      f"-Y 'gsm_a.rr.algorithm_identifier' -T ek -e gsm_a.rr.algorithm_identifier -e frame.number -e frame.time -l > {output}"
p_tshark = subprocess.Popen(cmd, shell=True)

p_grgsm = subprocess.Popen(["grgsm_livemon", "-f", frequency])

p_tshark.wait()
p_grgsm.kill()
