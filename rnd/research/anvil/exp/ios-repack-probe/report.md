# iPhone model bench bench-2026-10-03T13-58-31

Model models/qwen2.5-1.5b-instruct-q4km.gguf · pp 512 · tg 64 · 2 reps · cool to nominal · CPU (as the app)
Thermal states seen: nominal · ⚠ charging during the run

| config | n | pp t/s | Δ pp | tg t/s | Δ tg | warm starts | failed |
|---|---|---|---|---|---|---|---|
| base | 2 | 165.8 | +0% | 18.3 | +0% | 0 | 0 |

Median of the reps. Δ against `base` (the app's current settings). A warm start began above "nominal":
its numbers may be thermally limited. Decode (tg) drives the answer time; prefill (pp) drives the wait before the first word.
