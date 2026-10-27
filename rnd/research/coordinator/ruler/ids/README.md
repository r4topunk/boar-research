# ruler/ids: divergence-first ids files (2026-10-21; from tools/divergence_map.py, see DIVERGENCE-MAP-2026-10-21.md)

Every file has one id per line and a matching `.sha256` file. Dev ids only.
| file | n | use |
|---|---|---|
| divergent-main.ids | 30 | top D of MAIN 97 (live) |
| divergent-st180.ids | 40 | top D of the 180 self-tests (live) |
| divergent-pool.ids | 70 | union of the two above (run_pool.sh) |
| divergent-v01.ids | 20 | top D of the 72 v0.1 phone ids (phone-live) |
| sentinels-main / -st180 / -v01 / -pool .ids | 7 / 10 / 6 / 17 | stable, shown, judge-correct live items (K0 family; tiers in divergence-map.json) |
| stage1-pool.ids | 87 | divergent-pool + sentinels-pool = proposed desktop stage 1 |
| stage1-v01-phone.ids | 27 | warm-up + divergent-v01 + sentinels-v01 (phone order) |
| deterministic-v01.ids | 31 | warm-up + 30 ids answered without a model on all three phone models (skip list) |
| deterministic-pool.ids | 40 | desktop pool ids with 0 tokens on the K0+K1 controls and one text everywhere |

## Desktop (arms/null-cal/tools/run_pool.sh; ids must be in the 277 pool, which all pool files are)
    cd <workspace>/rnd/research/coordinator/arms
    OUT_BASE=<dir> bash null-cal/tools/run_pool.sh <arm> K0 ../ruler/ids/stage1-pool.ids <patch|.env|none>
    # control for the new ids (first time only; every id judged on the mini control):
    bash null-cal/tools/run_pool.sh _control K0 ../ruler/ids/stage1-pool.ids none
The arm judges only answers that differ from null-cal/control/pool-K0.json. Do NOT pass SCREEN_JSON=null-cal/pool/screen2-*.json: the GATE v2 bars belong to screen2. Calibrate a null on stage1-pool.ids first, using the same two patches: null-cal/null-s43.patch and null-ws.patch.

## Phone (BOAR Bench request)
    python3 -I ../ruler/tools/phone_request_from_ids.py gemma4-e2b/phone/q17b73-a/request.json <requestId> --skip ../ruler/ids/deterministic-v01.ids > req.json   # 43 q
    python3 -I ../ruler/tools/phone_request_from_ids.py gemma4-e2b/phone/q17b73-a/request.json <requestId> --keep ../ruler/ids/stage1-v01-phone.ids --model gemma-4-e2b-it-q4km > req.json   # 27 q
The warm-up is always kept first. Note that a skip list is only valid for an unchanged engine. If deterministic layers (facts, calculator, places, health-strict, cards) change, run the full 73 once.

## Device day 2026-10-22 (tools/device_day_requests.py; DEVICE-DAY-2026-10-22.md)
| file | n | use |
|---|---|---|
| dd1022-speed9.ids | 9 | DEV-SPEED17 / DEV-4B-PRESSURE: generating on bench 4B and 1.7B, 1.7B not declined |
| dd1022-layer10.ids | 10 | DEV-LAYERPAR: 4 deterministic layer ids + epi-1021 + 4 top-D divergent + geo-dev-1022 (2 dev probes, not v0.1) |
| dd1022-t1a / t1b.ids | 10 / 10 | DEV-GEMMA-T1 = divergent-v01 |
| dd1022-aunion10.ids | 10 | DEV-AUNION-NATIVE: >= 1 id per A-union pack (PK-4 desktop kept) |
| dd1022-press-c1..c3.ids | 3 each | DEV-4B-PRESSURE cycles (SPEED9 split) |
| dd1022-warn10.ids | 10 | DD2-RC1-LAYERWARN (10-21): v0.1 dev ids where NOTE-2 P2 fires on bench q4ba73-a, minus speed9/layer10 ids and lan-hlt-*, sorted, first 10 |
