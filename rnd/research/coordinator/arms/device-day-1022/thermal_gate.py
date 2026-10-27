#!/usr/bin/env python3
"""LITELAT thermal gate: waits until the phone reports thermal status 0 and battery temp <= MAX_DC (deci-C),
polling every 20 s (max 30 min), then appends one JSON line (run label, temps, status, waited s) to thermal.jsonl.
usage: thermal_gate.py <label> [max_dC=340]"""
import json, os, re, subprocess, sys, time
ADB = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")
HERE = os.path.dirname(os.path.abspath(__file__))
label = sys.argv[1]; max_dc = int(sys.argv[2]) if len(sys.argv) > 2 else 340

def read():
    th = subprocess.run([ADB, "shell", "dumpsys", "thermalservice"], capture_output=True, text=True).stdout
    bat = subprocess.run([ADB, "shell", "dumpsys", "battery"], capture_output=True, text=True).stdout
    st = int(re.search(r"Thermal Status: (\d+)", th).group(1))
    temp = int(re.search(r"temperature: (\d+)", bat).group(1))
    hal = dict(re.findall(r"Temperature\{mValue=([\d.]+), mType=\d+, mName=(BIG|MID|LITTLE|VIRTUAL-SKIN)\b", th.split("Current temperatures from HAL:")[-1]) and
               [(n, float(v)) for v, n in re.findall(r"Temperature\{mValue=([\d.]+), mType=-?\d+, mName=(BIG|MID|LITTLE)\b", th.split("Current temperatures from HAL:")[-1])])
    skin = re.search(r"mValue=([\d.]+), mType=3, mName=VIRTUAL-SKIN,", th)
    return st, temp, hal, float(skin.group(1)) if skin else None

t0 = time.time()
while True:
    st, temp, hal, skin = read()
    if st == 0 and temp <= max_dc:
        break
    if time.time() - t0 > 1800:
        print("thermal gate: timeout after 30 min", file=sys.stderr); break
    print(f"  cooling: status {st}, battery {temp/10:.1f} C, skin {skin}", flush=True)
    time.sleep(20)
rec = {"label": label, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "thermalStatus": st, "batteryDc": temp, "skinC": skin, "halC": hal, "waitedS": round(time.time() - t0)}
open(os.path.join(HERE, "thermal.jsonl"), "a").write(json.dumps(rec) + "\n")
print("thermal gate ok:", json.dumps(rec), flush=True)
