# SYNTHDEEP (B7) replay gate, bench v0.1 public (0 LLM calls; 2026-10-12)
TL;DR: **FAIL.** With cmpSplit on, one more item has both sides in the kept sources (vit-sci-002, which also gains 2 gold). The gate needs ≥ 5. No gold is lost anywhere (60/60 checked). The split fires on all 7 two-sided items. On 5 of them the curated kit (crypto + Wikivoyage) has no article for either side (`pinned-0-0` or `0-1`), so there is nothing to pin. This is the same knowledge wall exp-28 found on the 4B kit. The 35B reader never sees the second side, so the hypothesis cannot be tested on this kit.

Setup: `tools/run-replays.sh` (replay-split.ts = deepcovfb replay-deep.ts + `--cmp-split`, lines marked SYNTHDEEP), `--deep --gate rules --tree wt/synthdeep --k 6 --pool 20`, packs crypto + wikivoyage, cache arms/deepcovfb/cache (new app dir 4661c7ce…: retrieve.ts changed). Analysis: `tools/gate.py`, which writes `aggregates/replay-v01.json`. Side attribution: the pinned side article, or a title that names or contains the side. Gold rule: quota.py.

| id | route task | sides | kept per side off → on | kept off → on | gold off → on | on codes |
|---|---|---|---|---|---|---|
| lan-cmp-001 | lookup | 2 | [1,2] → [1,2] | 5 → 4 | 2 → 2 /2 | pinned-2-2 |
| lan-cmp-002 | lookup | 2 | [0,0] → [0,0] | 4 → 6 | 0 → 0 /2 | pinned-0-0, off-topic-2 |
| lan-cmp-003 | lookup | 0 (no split) | – | 3 → 3 | 0 → 0 /1 | sides-0 |
| lan-cmp-004 | chat | 2 | [0,0] → [0,0] | 1 → 1 | 0 → 0 /2 | pinned-0-0, off-topic-2 |
| lan-cmp-005 | lookup | 2 | [0,0] → [0,0] | 1 → 2 | 0 → 0 /2 | pinned-0-0, off-topic-2 |
| vit-cry-005 | compare | 2 | [0,2] → [0,2] | 2 → 2 | – (no gold) | pinned-1-1, off-topic-1 |
| vit-sci-002 | lookup | 2 | [1,0] → **[1,1]** | 2 → 2 | 0 → **2** /2 | pinned-2-2 |
| vit-hum-002 | research | 2 | [0,0] → [0,0] | 0 → 0 | 0 → 0 /1 | pinned-0-0, off-topic-2 |

- Both sides represented: off 1/7, on 2/7 → **+1 (gate ≥ 5) → FAIL**. Both sides lost: 0. Gold lost: 0 items, whole set (60). Gold gained: vit-sci-002.
- Kept lists change on 4/60 items (lan-cmp-001/002/005, vit-sci-002). The split fires on no item outside this set.
- The ceiling on v0.1 is +6 (7 two-sided items, 1 already covered), so the ≥ 5 bar needs side articles that the kit lacks: species (bears, crocodiles, moose/bison), Mozi/Confucian, Privacy Pools. Only 1 of 7 items routes as task:compare, so a task-gated trigger would reach vit-cry-005 alone.
- Default off vs the dt512 replay (`arms/vitalpack/replay-base-dt512-v01.jsonl`): kept, raw and codes byte-identical **60/60**. Vs `arms/deepcovfb/replay-base.jsonl`: kept identical 54/60. The 6 that differ are tree differences, not the patch: that base is wt/cut7 (FACTS), where those 6 items do not retrieve (46 vs 54 retrieving).
- Not run: V-para / v0.2 (blind; no gold there). One option, not a decision: re-run the gate with wiki-vital5 in the kit (VITALADD), which carries encyclopedia side articles, before any judged run.
