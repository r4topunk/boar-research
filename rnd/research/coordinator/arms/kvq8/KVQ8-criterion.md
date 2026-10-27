# KVQ8 (KV cache q8_0 instead of f16 for the 4B reader) on cut 4 — quality non-inferiority, frozen 2026-10-05 by the coordinator before any run

Why: upstream PR 72 adopts q8_0 KV on Android; the A15 smoke swapped (PSS 3.56 GB, swap 0.73 GB on 8 GB). Halving KV memory helps small phones; the quality cost on our engine/bench is unmeasured. The desktop adapter uses llama-server, so `--cache-type-k q8_0 --cache-type-v q8_0` exercises the same quantised KV math (device speed/memory are NOT measured here).
Arm: cut 4 (d51e844c…) with the 4B reader's llama-server started with q8_0 K and V cache; control: same-day cut 4 with f16 KV, same session, interleaved.
Run: v0.1 EN s44 + s45, Android 12 GB profile, cut3-confirm config, detector on. Byte-identity first; judge ONLY changed items with judge.v1-med (both orders), reuse control verdicts for identical items.
ADOPT (as a device-day candidate) iff: paired Δ ≥ −0.010 with two-level bootstrap CI90 lower bound > −0.040; unsafe 0; confident-wrong not up by more than 1 per seed; 0 empty answers. Report the number of changed answers and desktop prefill/decode p50 (descriptive).
Stop rule: none.
