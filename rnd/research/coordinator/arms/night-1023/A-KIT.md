# A-KIT (KIT-V01; 0 LLM / judge / Opus / paid / phone; MacBook, 2026-10-23; criterion sha 36635ca23543a44e not edited) - ADOPTED KIT: K13 (no change)
Recipe = SEFIX-124 config: rs-SEFIX (H4-MERGE + SEFIX-F1/F2/F4; F3 off), env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1, MAIN 97, funnel-K3 traces (--tasks-from), K3 settings (a2 + append-budget), exactly sefix/ans-logs/replay_F1F2F4.out; only --packs differs (tools/run_kit.sh, score_kit.py). Control = sefix/replays/main.F1F2F4.jsonl (not rerun; chunk-level reproduces 42 / v0.1 28 / cm 14). Replays gitignored; replay caches deleted.
| kit | chunk92 | v0.1 52 | cm40 | art92 | lost vs 124 | gained | junk own (n) / x124 | kept tok x | lists changed |
|---|---|---|---|---|---|---|---|---|---|
| SEFIX-124 (K13) | 42 | 28 | 14 | 50 | - | - | 3.28 (50) / 1.00 | 586 / 1.00 | - |
| K13 + qa-ethereum-se + qa-bitcoin-se | 43 | 28 | 15 | 52 | 1 (vit-cry-001) | vit-cry-010, money-se-005 | 3.22 (49) / 0.98 | 572 / 0.98 | 20 |
| K13 + those + boar-nist-crypto | 43 | 28 | 15 | 52 | 1 (vit-cry-001) | same | 3.22 (49) / 0.98 | 571 / 0.97 | 20 |
| K13 + those + EIPs | not built (below) | | | | | | | | |
Junk sensitivity (both-no-fact set / control's no-fact set): 0.96 / 0.98 for both kits. Wall ~1.0 s/q (indicative, shared load).
## Rule (frozen): ADOPTED iff v0.1 chunk-level >= 31 AND losses <= 1 AND junk <= 1.15x
v0.1 28 vs 31 FAILS for both candidates (+0 net: +1 vit-cry-010, -1 vit-cry-001); losses 1 passes; junk 0.98x passes. **K13 stays.** Prediction (+2..+4 v0.1 crypto facts) missed: +1 gained, +1 lost.
## Why
- vit-cry-001 (quantum) was delivered from boar-crypto (ERC-7524 + ethereum.org PQ page); with qa-bitcoin-se the bitcoin quantum threads take all 7 slots and the fact chunk is displaced (crowding, same pattern as COVERAGE-MAP). vit-cry-010 (DAO) is gained from qa-ethereum-se / qa-bitcoin-se threads.
- The other crypto items stay undelivered with or without the SE crypto packs (cry-002 article-only, cry-005, cry-007, cry-009): their facts are not in these packs (COVERAGE-MAP: 0 S1 from them).
- nist-crypto (521 NIST articles, no vectors, no SE) is inert on the 97: kept lists and delivered set identical to the SE-only kit (only 1 token-level difference).
## EIPs pack: SKIPPED, with the reasons
1. The converter (rnd/kiln/packs/convert: stackexchange, medlineplus, factbook, pdf) has no markdown/front-matter format; building one + a builder run + sidecars is outside "existing converter, <= 60 min".
2. Not needed: boar-crypto (the K13 crypto pack) already carries 1208 CC0 EIP/ERC docs (sources.eips; titles "EIP-N: title"). Read-only shallow clone of ethereum/EIPs @ f1bcca1b (2026-10-22; LICENSE.md = CC0 1.0 verified): 603 non-Moved EIPs, 592 already in boar-crypto by number, the other 11 are fresh Drafts (EIP-8247..8450). A second copy would duplicate chunks and crowd, not add facts. (EIP-7251 and EIP-4844 are in boar-crypto already.)
## Caveats
Dev items (v0.1 52 + cooking/money self-tests 40); chunk-level facts are agent-keyed, lexical share >= 0.5 for v0.1; one replay per kit (retrieval only, seed-free); F1/F2 do not act on the v3 SE packs (they have chunk_vecs; those use the packDense2 path), so the new packs run on the dense path only; delivered counts are items (one flip = 1). Nothing committed or pushed; blind/, rnd/veil, bench v0.4 not read.
Data: a-kit.json, akit/tools/{run_kit.sh,queue1.sh,score_kit.py}, akit/replays/ (gitignored).
