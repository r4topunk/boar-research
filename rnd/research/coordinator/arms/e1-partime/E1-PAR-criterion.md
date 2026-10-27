# E1-PAR criterion (frozen 2026-10-21, before any E1-PAR device run; 0 LLM, 0 judge, 0 paid)

Source: DEVICE-DAY-2026-10-22.md step E1-PAR (predictions and rules committed in 1eae8371 / aa81a76d) + BLOCKCACHE64-criterion.md (ee39a755, unchanged, quoted for arm E). This file only freezes that text with a sha; no number is new.

## Setup
- Phone: Pixel 8a (serial ends ...2219), airplane mode on, AC power, BOAR Bench (team.sopa.boarbench), A-union kit (6 packs + gazetteer), Qwen3-1.7B (qwen3-1.7b-q4km), quickFirst. Driver: handoff/pixel8-2026-10-20/bench/boar_bench.py run e1par-{a,b,e,d}.
- Items: warmup + 10 ids (saf-008, saf-005, saf-007, saf-010, saf-011, lan-ref-002, vit-hlt-003, lan-exp-001, lan-rsn-003, vit-cry-009), same order in every arm. Requests sha: e1par-a a6f7f151, e1par-b 1d4abc84, e1par-e 337caf24, e1par-d 2d30aff9.
- Arms (APK sha256 prefix, engine tree):
  - A = current serial engine, the APK installed on the phone on 2026-10-21 (pulled and hashed: 284abdde = bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-nonet-gemma2-0ca54d870ba8.apk, tree 0ca54d87).
  - B = Promise.all pack search: boar-bench-...-parsearch-nonet-8ad2c4b0fae9.apk, fc1c855a, tree 8ad2c4b0.
  - E = B + BLOCK_CACHE 64: boar-bench-...-parsearch-blockcache64-nonet-31ba12c473d1.apk, 0a4e370e, tree 31ba12c4.
  - D (optional ceiling, measurement only) = B + BLOCK_CACHE 256: boar-bench-...-parsearch-blockcache256-nonet-3bf53253e984.apk, 74dbb664, tree 3bf53253.
- Order: A, cool-down, B, cool-down, E, then D only if time allows. Thermal start rule (this runner, stricter than the doc's 31.0 C): thermal status 0 and battery <= 30.0 C before each arm, polled every 20 s, wait at most 10 min; not reached -> arm NOT RUN. Battery temperature recorded before and after every run.
- Arm C and A2 are not part of this pass (deviation: no A2 drift control; the A-B-E order is one session on one cool phone).

## Metrics (tools/e1par_readout.py; definition checked on aunion73-a: same 10 ids give search p50 4.019 s, answer p50 10.052 s = the frozen basis)
- search p50/p90 = percentile (linear) of the summed 'search-wikipacks' span ms over the items that search packs; answer p50/p90 = percentile of totalLatencyMs over the 10 items.
- Hit identity = ordered retrievedTitles equal to arm A on every item.
- PSS peak = max app PSS in the 5 s telemetry sampler.

## Frozen predictions (DEVICE-DAY, replay of these 10 ids)
| arm | search p50 | answer p50 |
|---|---|---|
| A | 4.02 s | 10.05 s |
| B | 2.60-2.92 s | about 8.9 s |
| E | 1.26 / 1.42 / 1.72 s (at 16.0 / 12.5 / 8.0 ms per avoided decompression) | 6.67 / 6.77 / 7.21 s |
| D | 1.0 / 1.2 / 1.5 s | 6.6 / 6.6 / 7.0 s |

## Decision clauses
- Stop / void (any arm): retrievedTitles differ from A on any item -> that arm is VOID (bug; identity by construction). PSS peak > A + 0.3 GB or any LMK kill -> STOP that arm.
- B PAYS iff search p50 (A) - search p50 (B) >= 0.8 s AND answer p50 (A) - answer p50 (B) >= 0.8 s; otherwise DOES-NOT-PAY (the note then points to off-thread decompress or bounded materialization).
- E ADOPT iff (1) search p50 (E) <= 0.6 x search p50 (B), (2) retrievedTitles ordered-identical to A and B on every item, (3) PSS peak (E) - PSS peak (B) <= 0.032 GB; KILL otherwise. If search p50 (B) - search p50 (E) < 0.4 s the cache lever is closed on the phone.
- D (measurement only): PAYS-OVER-B iff search p50 (B) - search p50 (D) >= 0.8 s at identical titles; < 0.4 s -> the block cost is mostly materialize, cache lever closed.
- One session, one seed: no rerun unless an arm aborts; an abort is reported, not retried.
