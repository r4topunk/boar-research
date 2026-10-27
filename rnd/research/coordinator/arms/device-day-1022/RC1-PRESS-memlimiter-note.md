# Android 17 memory limiter on the Pixel 8a (web tick 30, checked 2026-10-21 18:2x, 0 LLM)

- `adb shell am memory-limiter status` → **disabled** on this phone (Android 17, GrapheneOS). So the OS-level per-app anon+swap limit is not active today; lmkd remains the kill path. Re-check at device-day setup (row 0b) and record it in device.json.
- Live reading during the A1 run (RC1 1.5B generating): VmRSS 2.51 GB, RssAnon 1.29 GB, VmSwap 0.
- Device-day additions (W58–W60): (a) record `am memory-limiter status` in every device.json; (b) after any kill, pull `ApplicationExitInfo` (dumpsys activity exit-info team.sopa.aoair) and classify MemoryLimiter:AnonSwap vs lmkd; (c) sample RssAnon + VmSwap from /proc/<pid>/status every 5 s alongside PSS in the pressure cycles, and read the PRESS criterion against RssAnon+VmSwap too.
