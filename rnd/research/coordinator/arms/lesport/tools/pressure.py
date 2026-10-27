#!/usr/bin/env python3
"""S1 memory-pressure helper: allocate+touch N GiB, hold until killed; self-abort if swap used > 6 GB."""
import sys, time, subprocess, re
n = float(sys.argv[1]) if len(sys.argv) > 1 else 11
b = bytearray(int(n * 2**30))
for i in range(0, len(b), 4096): b[i] = 1
print("touched", n, "GiB", flush=True)
while True:
    o = subprocess.check_output(["sysctl", "-n", "vm.swapusage"]).decode()
    if float(re.search(r"used = ([\d.]+)M", o).group(1)) / 1024 > 6: print("ABORT swap"); sys.exit(1)
    for i in range(0, len(b), 65536): b[i] = 2   # keep pages hot
    time.sleep(2)
