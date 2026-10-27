# TK2-FIX v0.2 kit no-harm: PASS (2026-10-16 03:5x; 0 LLM / 0 judge / 0 paid; script-only on blind, scoped exception 10-16 04:0x)

Criterion TK2FIX-V02-criterion.md sha 81d0a51b… (frozen before either v0.2 replay). Closes the line TK2FIX-STEP0 skipped (G3 there was v0.1 only).
Replay: packs/tk2-replay/tools/replay-tk2.sh, --gate search --k 6, two passes, claim kit (crypto + wikivoyage, no geo providers = noplaces), v0.2 110 (questions.v02-new.jsonl), gold boar-eval/bench/v0.2/gold/sources.json (86 items with gold). cut 7 = kiln-local/be-0cfd4a77-cut7; tk2fix = kiln-local/be-0cfd4a77-cut7-tk2fix.

| cell (v0.2 110, kit) | rows ×2 | repeat identical | errors | gold kept (items) | gold entries kept | gold raw6 | kept slots | articles kept | empty-kept |
|---|---|---|---|---|---|---|---|---|---|
| cut 7 | 110/110 | 110 | 0 | 15 | 17 | 18 | 126 | 97 | 28 |
| tk2fix (v2) | 110/110 | 110 | 0 | 15 | 17 | 18 | 126 | 97 | 28 |

Diff tk2fix vs cut 7 over 110: kept set 0, kept order 0, kept titles 0, raw list 0, route (task/query/k) 0, reason codes 0, promptSha 0 (204/220 rows carry a prompt). Changed ids: none. Harm ids: none. Gold gains: none.

**Gate:** G0 infra PASS; G1 kept changes 0 ≤ 10 PASS; G2 gold kept 15 ≥ 15 PASS; G3 0 items lose a gold-bearing source PASS → **PASS**.

**Reading.** As expected: the kit carries no pack with source codes 9–12, so neither the bare-title change nor the title-lookup rule can fire; v2 is byte-neutral on v0.2 retrieval and prompts. With step 0's v0.1 identity (60/60) RULE 26 no-harm is now closed on both bench sets for the v2 patch; the PR still needs both patches (tk2fix.vs-cut7 + tk2-builder.vs-pr1, per TK2FIX-L1).

**Files:** TK2FIX-V02-criterion.md(+.sha256), tools/run_v02.sh, tools/compare_v02.py, runs/run-v02.log (summary lines only), aggregates/tk2fix-v02.json; traces blind/bench-v02/runs-packs/tk2fix-v02-kit.{cut7,tk2fix}.jsonl. One new replay cache key (tk2fix tree + kit, ~25 MB).
