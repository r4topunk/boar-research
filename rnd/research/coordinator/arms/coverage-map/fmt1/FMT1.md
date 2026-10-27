# FMT1-SCAN: wider pool / full chunk-vector scan / 0.65 floor for format-1 packs (0 LLM, MacBook replays, 2026-10-23)
Criterion `../FMT1-criterion.md` sha256 `79fefb9cc799a6056cae4eec45de1e6f0649ca0e181ce71541f67fd191936daa`, frozen before any replay and not edited. 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone.
Patch `arms/retrieve-sweep/patches/FMT1-SCAN.patch` sha256 `3c67ce28c22fb32af1c031ade68b39afe1a51ff166369e2c8cbc106974c82914` (on rs-SEFIX, `patch -p1` dry-run clean). Tree kiln-local/rs-FMT1 = cp -Rc rs-SEFIX + patch. Switches are off by default: RS_FMT1_POOL (2000 | full) and RS_FMT1_FLOOR (0.65, format-1 pack chunks only, the bundled corpus stays at 0.70).

**TL;DR. Every arm is NO.** The full scan does what the probe predicted on b20 (Population ageing is kept at 0.755), but that is 1 of 4 MISSES topics, and on MAIN 92 it delivers 41 facts against 42 for the base. The 0.65 floor costs 3 to 5 facts on MAIN by crowding (vital5 kept chunks go from 45 to 62-65, and 28-32 kept lists change), and it drops Vaccination on the health topic b2. **Premise correction:** boar-simplewiki-en (v3proto) and boar-wiki-en-top100k are format 2 (meta formatVersion 2). In the 13-pack kit, wiki-vital5 is the only format-1 pack, so every effect here comes from wiki-vital5.

## Commands
```
cd <workspace>/rnd/research/coordinator/arms/coverage-map/fmt1
tools/queue.sh                                   # 6 arms on MAIN 97, then 5 on topics (sequential); tools/run_fmt1.sh <main|t27> <arm>
tools/run_fmt1.sh t27 P400                       # topic base, re-run right after the queue so its wall time is comparable (first run 10:4x ran at load 4, the arms at load 8-25)
python3 -I tools/ident.py replays/main.P400.jsonl ../sefix/replays/main.F1F2F4.jsonl     # 97/97 raw, wide, kept, codes
python3 -I tools/ident.py replays/t27.P400.jsonl ../../topics27/replay/misses.A1.jsonl  # 27/27
python3 -I tools/score_fmt1.py fmt1.json
```
MAIN 97 = the sefix run_main.sh recipe (13-pack N10 kit, funnel-K3 traces, packHeadPass a2 + packDense2 append-budget, wide 12), SEFIX-124 env. Topics = the misses/run.sh recipe (wiki-vital5 + essential corpus, persona detailed), SEFIX-124 env. Identity holds: 97/97 and 27/27, and the re-run topic base is 27/27 against its first run.

## The 6 arms (base = P400, which is SEFIX-124)
| arm | MAIN 92 chunk-level (cm / v0.1) | gained / lost | MAIN kept lists changed | vital5 kept chunks | topics recovered (of 4) | other topics changed | health losses | ms p50 / p95 MAIN | ms p50 / p95 topics | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| P400 base | 42 (14 / 28) | - | - | 45 | - (b13 already kept) | - | - | 931 / 1643 | 80 / 312 | - |
| P400 f65 | 39 (13 / 26) | +1 / -4 | 28 | 62 | 0 | 2 (b2, b5) | **1** (b2 Vaccination) | 989 / 1531 | 106 / 218 | NO |
| P2000 | 42 (14 / 28) | 0 / 0 | 1 | 45 | 1 (b20 Japan) | 0 | 0 | 1023 / 1555 | 141 / 295 | NO |
| P2000 f65 | 39 (13 / 26) | +1 / -4 | 29 | 62 | 1 (b20 Japan) | 2 | **1** (b2) | 1050 / 1512 | 139 / 350 | NO |
| FULL | 41 (13 / 28) | 0 / -1 | 5 | 46 | 1 (b20 Population ageing x2) | 0 | 0 | 1025 / 1511 | 239 / 461 | NO |
| FULL f65 | 37 (13 / 24) | +1 / -6 | 32 | 65 | 1 (b20 Population ageing x2) | 2 | **1** (b2) | 1008 / 1381 | 269 / 531 | NO |
Gate clauses: (a) +3 facts or 2 of 4 topics: fails for every arm (best is FULL / P2000: 0 or -1 facts and 1 of 4 topics). (b) Health: the f65 arms fail on b2; MAIN health items lose nothing in any arm. (c) p95 at most 2x base: passes for every arm, but MAIN is noisy (load 8-25 during the queue) and the topics p95 for FULL is 1.5-1.7x.

## Per-item
- FULL, MAIN (5 lists changed): lan-exp-001 loses 2 Languages of Singapore chunks; vit-sci-002 swaps Germany for Japan; cooking-001 and cooking-019 each lose one SE thread; **cooking-016 loses the fact** (two simmer and boil threads give way to the Boiling vital5 chunk). The full-scan chunks enter the fusion as semantic hits. When they rank higher, they push format-2 SE threads out of the per-article and top-K slots.
- P2000, MAIN: only lan-exp-001 changes (the same Singapore loss); there are no fact changes.
- f65 arms, MAIN: losses are cooking-016, money-006 (the ACH threads), vit-hum-004 (Lord of the Rings / Sauron), vit-cry-006 (the zero-knowledge proofs page), and in FULL f65 also vit-cry-001 and vit-cry-011. The one gain is cooking-006. The 0.65-0.70 vital5 band is mostly off-topic intros that take slots.
- Topics: b20 keeps Population decline + Japan (P2000) or Population decline + Population ageing x2 (FULL), with no Germany or Population density. b15 (compression) and b19 (instant table) cannot move by construction, as MISSES predicted. b13 stays as in base. With f65, b2 drops Vaccination (keeping Vaccine), and b5 drops Western Roman Empire.

## What the phone would need (bytes read per query, wiki-vital5)
- Base pool 400: about 400 rows x (384 B int8 vector + about 482 B title and body) = **0.35 MB**.
- Pool 2000: about **1.7 MB**, which is 5x the base.
- Full scan: 115,813 x 384 B = **44.5 MB of int8 vectors per query**. That means 44.5 MB resident if cached, or a 44.5 MB flash read per query if not. On the MacBook (one JS thread) it takes about 170-180 ms per query plus a 170-210 ms load once (logged as `[fmt1] ... loaded`). A W78-style 1-bit sidecar would be 5.6 MB per query plus an int8 rescore of the top 32. That was not built: the scan does not pay at the fact level.

## Reading
The first-stage pool is not what limits facts on MAIN. The 400-pool already catches the vital5 chunks that carry MAIN facts. A full scan adds on-topic chunks only on multi-entity topic strings (b20). Where it does change the fusion, it trades SE threads for vital5 intros. The 0.70 gate is doing useful work: lowering it to 0.65 adds 17-20 kept vital5 chunks and costs 3-5 facts plus a health source. A b20-type gain would need a full scan scoped to the rare case (no on-topic source kept), plus the keep-rule fix, and not a global change.

## Caveats and not run
Deterministic replays, so the margins are item counts. This is the bench engine, not the native Kotlin pipeline. Dev items, and the cm questions were written from the SE threads. Wall time was measured under load 8-25 from other jobs (the MAIN base also ran first, including seed indexing in its total, but `ms` is per retrieve call). enwiki top100k and simplewiki were not tested because they are format 2. Not run: a full scan gated to the no-kept-source case, and a 1-bit sidecar.
Files: FMT1.md, fmt1.json, tools/{run_fmt1.sh, queue.sh, ident.py, score_fmt1.py}, replays/ (gitignored).
