# safety rules v0.8.1 (Compass, 2026-10-02): PT patterns for the 11 rules v0.8 left without one
TL;DR: v0.8 + 14 PT patterns (choke-finger-sweep, choke-water, heat-fluids-unconscious, heart-drive-self, stroke-wait, battery-wait, electric-touch, hypo-food-unconscious, scorpion-cut-suck, quake-coast-stay, rabies-wait), plus a PT 'unplug' exception on electric-touch. Checker unchanged (`safety_check.v0.8.py`, same sha as v0.8). Tests **239/239** (214 v0.8 + 25 PT pairs). Regression on 6,085 answers: **v0.8 → v0.8.1 0 changes; v0.7 → v0.8.1 1 change = cs-040** (the expected flip).

```sh
python3 build_v081.py           # ../safety-v08/rules.v0.8.json → rules.v0.8.1.json (byte-stable)
python3 run_tests.py            # 239/239
python3 regress.py v0.8; python3 regress.py v0.7   # → regress.txt
```
- With v0.8.1, all three languages have at least one pattern on every forbid rule (snake-tourniquet's torniquete/garrote covers PT/ES). UNKNOWN: precision on real PT/ES danger answers; the PT patterns are tested on hand-written sentences only (v0.1 has no PT danger answers).
- Frozen: `SHA256SUMS.v0.8.1`.
