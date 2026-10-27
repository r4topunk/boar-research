# runner-v04: ruler v0.4 on the app maintainer's native APK (Pixel 8a)

TL;DR: `gate` (refs + spec + errata frozen?) → install the arm's packs through the RC's own UI → `state --arm X` → `build --arm X --gen N` → `rc_eval.py run rv04-X-gN` → UI-queue items (multi-turn, show-anyway) → `convert`. Phone only after asking r4to **"pixel livre?"**. Spec: ../../RULER-SPEC-v1-r3-2026-10-21.md §0, §4.

```fish
cd <workspace>/rnd/research/coordinator/ruler/runner-v04
python3 -I ruler_v04.py selftest                 # 0 adb: converter on RC1 rows (51 traces, kept 1)
python3 -I ruler_v04.py gate                     # must print GATE OK before any v0.4 app answer
# per arm, in this order: AU (or AUP), B, C, A (one build per family), D
python3 -I ruler_v04.py state --arm AU --packs <ids as shown in the Knowledge screen> --photo catalog.png knowledge.png --refusal-file refusal.txt --warning-file warning.txt
python3 -I ruler_v04.py build --arm AU --gen 1   # requests/rv04-AU-g1.request.json + ui-queue/rv04-AU-g1.jsonl
python3 -I rc_eval.py check                      # airplane on, thermal 0, battery <= 35 C (spec §7.2 gate)
python3 -I rc_eval.py run rv04-AU-g1 --timeout-min 120
python3 -I ruler_v04.py convert --arm AU --gen 1 --ui ui-rows/rv04-AU-g1.jsonl
```

## Input contract
| file | content |
|---|---|
| requests/rv04-<arm>[-<family>]-g<gen>.request.json | the hook request: {requestId, pipeline (from state), evalSetVersion "v0.4-ruler", questions [{id, category = item type, query = the single turn}], models? }. All single-turn items, anchors included (67). Location sent only if the RC's hook takes it. Written only when the gate is open (else requests-dry/, which rc_eval.py cannot run) |
| ui-queue/<rid>.jsonl | items the hook cannot run: multi-turn conversations (8) and, after the run, the refused ids for show-anyway. One line: {id, turns[], context, via} |
| state/<arm>.json | RC state before the arm: device (rc_eval check), APK sha256 (pulled), declared installed packs, catalog/knowledge photo shas, refusal-string and warning-line shas, hookCapabilities (default = our reading of snapshot 5f8cc8f4; change only from a probe or a code reading of this RC, and write which) |

## Output contract
| file | content |
|---|---|
| results/<rid>/ | rc_eval.py output: rows.jsonl (hook rows), telemetry.csv (PSS, battery, thermal every 5 s), logcat, lmk, summary, device.json |
| ui-rows/<rid>.jsonl | the UI driver's rows: {id, via "ui", turns: [{user_index, answer, warned, refused, ttftMs, totalLatencyMs}], answer = "[Turn k]" blocks, outcome} |
| traces/<rid>.traces.jsonl | judge.mjs input: {itemId, runId, answer.text (warning line stripped), error, engine {arm, commit = apk sha prefix, apkSha256, appVersion}, ruler {kept, retrievedTitles, refusedZ, warningLine, via, modelId, personalityId, maxTokens, ttftMs, totalLatencyMs, tokPerSec, tokensGenerated, peakRssBytes}} |

## Arms (arms.json)
| arm | where | gens | packs | judges |
|---|---|---|---|---|
| AU (verdict) | phone | 2 | B kit + 6 persona packs (persona-map-v1.json) | Opus, Codex, Haiku-low |
| AUP | phone | 2 | the installable subset of AU, only when AU cannot be fully installed (spec §4.2) | same |
| B | phone | 2 | the RC default, README only | Opus, Codex, Haiku-low |
| A | phone | 1 | B kit + the family's persona; `--family` builds | Haiku-low |
| C | phone | 1 | none | Haiku-low |
| D | phone | 1 | A + D sets | Haiku-low |
| DECLINE, ONEB | desktop | 1 | — | — |

## Rules
- Packs only through the RC's own user flows (catalog download over Wi-Fi if the RC offers it, or a documented import). No adb push into app storage, no root. If AU cannot be fully installed: run AUP with the subset and record the missing packs in state (band "not scored on A∪"); if none installs, run B only.
- Wi-Fi only while installing; airplane mode on for every run (rc_eval refuses otherwise). PCAPdroid capture over the AU run for the offline gate.
- Thermal gate before speed-bearing runs (AU g1, B g1): battery <= 35 C, thermal status 0.
- Two generations for AU and B: run g1 and g2 as separate requests (the hook has no seed; label "seed not controllable").
- One EXPOSURES row per RC at its first v0.4 run; one QUEUE row per arm result.
- UNKNOWN until the RC lands: hook still present (`BenchActivity` + request64), pipeline accepted, notFound semantics (RC1 rows carry a `notFound` field: set hookCapabilities.declinedField = "notFound" only after checking it marks refusals), multi-turn / show-anyway in the hook. The UI driver for ui-queue is written against the RC's chat screen on the device day (android-app-qa skill), not before.
