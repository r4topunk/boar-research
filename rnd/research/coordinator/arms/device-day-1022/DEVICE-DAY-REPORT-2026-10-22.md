# DEVICE-DAY REPORT 2026-10-22 (Pixel 8a, RC1) — STOPPED by coordinator at ~16:14 (research redirected to retrieval + answer quality with packs)

0 judge, 0 LLM, 0 paid. Phone minutes used: ~19 (0b 1 + W1 3 + H3 14 + R 1) of 117.

| row | ran? | gate temp (before -> after) | items | result vs frozen prediction | min |
|---|---|---|---|---|---|
| 0 Codex ladder | skipped (r4to's) | — | — | not decided | 0 |
| 0b setup | yes | 27.6 C | — | catalog read (see notes) | 1 |
| 1s A1 | skipped: already run 10-21 as rc-cv5-51-15b (51 traces in arms/rc1-pixel/a1/in) | — | — | — | 0 |
| W1 4B download | yes | 27.7 C | — | 4B listed + downloaded | 3 |
| H3 rc-speed9-4b | yes | 28.3 -> 36.2 C (gate 31.0 ok) | 1+9, 10/10 ok | readout ENGINE-OK; prediction MISS (decode 4.77 < 5.0, TTFT 4.03 > 3; answer 76 s in band) | 14 |
| H2a/H2b, W2, H5, H4, F | NOT RUN (stop order) | — | — | not decided | 0 |
| H6 | NOT RUN (stop order; also: RC1 cannot load v3 packs, bench-app picker unchecked) | — | — | — | 0 |
| H7 | NOT RUNNABLE (maintainer's 18.4 GB shards not on the phone) | — | — | — | 0 |
| R restore | yes | 36.2 C | — | done | 1 |

Notes
- 0b: installed RC1 base.apk sha a79011c6 (GitHub release rc1, reinstalled by another session today 13:29), NOT the runsheet's 2ef43258; same 2.0.0-rc1 / vc 4. Model Catalog lists Qwen3 4B (2.3 GB) AND Qwen3 1.7B (1.0 GB) — snapshot said no 1.7B, so rc-speed9-17b / rc-press-17b are runnable on this APK. Screenshot runs/0b/model-catalog.png. Knowledge catalog not read.
- W1: Wi-Fi was already ON (saved network); 4B downloaded 16:00:41-16:03:40 via adb tap; app made it ACTIVE. On-device sha not readable (release, app-private storage).
- H3: answer p50 76.0 s vs bench 22.97 (x3.31, Detailed/1024 length, DD1022 §1 "FAIL by length"), TTFT p50 4.03 s, decode p50 4.77 tok/s (bench 5.57, -14 %), PSS peak 4.48 GB, RSS 3.45 GB. The one lmk.txt line is a 14:04 kill of team.sopa.aoair.native (other package, before the run). Raw: runs/rc-speed9-4b/results/.
- R: RC1 force-stopped, Wi-Fi re-enabled and reconnected (state as found), nothing uninstalled. No download left in progress.

What needs r4to
- Decide whether the 4B should stay ACTIVE in RC1 (was 1.5B) — one tap in Model Catalog; 2.3 GB stays on disk.
- Note that another session replaced the RC1 APK today (a79011c6); yesterday's RC1 rows were on 2ef43258.

What needs the app maintainer
- Nothing sent. (If the RC rows resume: confirm 2ef43258 vs a79011c6 are the same build; the 1.7B in the installed catalog revives NOTE-1 rows.)
