# WIKIFULL stage A — verdict **MARGINAL (7/34 verified)** on V-para; 15/15 shards (2026-10-12 23:55) — see STAGE-B.md: pooled A+B 9/34 MARGINAL (final, 2026-10-13; CLOSED R45)

Criterion WIKIFULL-REOPEN (sha ee81ad30…): REOPEN ≥ 14 / MARGINAL 7–13 / CLOSE ≤ 6 verified items (jev has_fact ≥ 0.7 AND quote_supports) over the 34 V-para absent-knowledge items, pooled over the 15 FineWiki Aug-2025 shards. Result: **7/34 verified** (10 at p ≥ 0.7 unverified, 17 at ≥ 0.6); by group: on-topic kept 3/13, off-topic kept 1/1, no kept source 3/20; 6 of the 7 verified hits sit in articles outside the top-100k pack. Per shard: verified 2/1/0/0/2/0/0/0/0/1/0/0/4/0/0 (00…14). jev [usage detail removed] (V-para), gate time 1,065 s; v0.2 (dev, never decided on): **37/78 verified at 15/15 shards** (44 at ≥ 0.7, 57 at ≥ 0.6; 27 outside the top-100k pack; on-topic kept 17/30, off-topic kept 8/14, no-kept 12/34), [usage detail removed]. → Stage B (pages outside FineWiki Aug-2025: the 2026-09-26 index delta) runs per the criterion; the pooled A+B count decides. Reading: full Wikipedia holds the missing fact for about one in five bounty-style items (and for about half of the v0.2 items); REOPEN (≥ 14) is out of reach for stage A alone.

---
(stage-A runner report below, written while RUNNING)

TL;DR: 4/15 shards covered (07 = A0, 00, 01, 02). Pooled V-para verified 2/34 so far (both no-kept items, both outside the top-100k pack). Partial — NOT a verdict (rule: REOPEN ≥ 14, MARGINAL 7–13, CLOSE ≤ 6, only with 15/15).

## Method
- `tools/wikifull_gate.py --set vpara|v02 --shard <path> --tag XX` = A0 logic unchanged (TOPK 20, CAPC 40, NT 12, TH 0.7, quote_supports); cache per shard under blind/<set>/runs-dt512{,v02}/wikifull-cache/sXX/; output `aggregates/stageA-<set>-XX.json` (ids/titles/probabilities/counts). A0 files untouched.
- `tools/stageA.sh`: per shard: df check (≥ 8 GiB + 2) → curl from the public HF resolve URL into shared-data/packs/work/wikifull-stageA/ (no HF cache; `~/.local/bin/hf` on this Mac is NOT the Hugging Face CLI) → sha256 + size vs shared-data/packs/boar-wiki-en-XX.sqlite.json (retry once, else MISSING) → gate vpara, v02 → delete. Guards: stop if [usage detail removed]. Resumable (skips shards with both aggregates). Log: tools/stageA.log.
- Measured: ≈ 5.6 min/shard (download 95–170 s at 6–12 MB/s, gate ≈ 70 s vpara + 160 s v02), [usage detail removed] jev/shard.

## Per shard (so far)
| shard | V-para verified / ≥0.7 / ≥0.6 | v0.2 verified / ≥0.7 / ≥0.6 | jev $ (vpara+v02) |
|---|---|---|---|
| 07 (A0) | 0 / 1 / 3 | 9 / 11 / 19 | 0.115 |
| 00 | 2 / 2 / 5 | 11 / 12 / 23 | 0.118 |
| 01 | 1 / 3 / 5 | 9 / 11 / 19 | 0.119 |
| 02 | 0 / 0 / 0 | 8 / 11 / 17 | 0.119 |

## Pooled (4 shards; items counted once)
| set | n | verified | ≥0.7 | ≥0.6 | verified outside top-100k | on-topic / off-kept / no-kept verified |
|---|---|---|---|---|---|---|
| V-para | 34 | 2 | 4 | 10 | 2 | 0 / 0 / 2 |
| v0.2 (dev) | 78 | 24 | 28 | 39 | 16 | 8 / 6 / 10 |

## Status, ETA, commands
- Check: `grep -vE '^(vpara|v02) \{' tools/stageA.log | tail`; resume if stopped: `cd arms/wikifull && nohup tools/stageA.sh >/dev/null 2>&1 &`; pool + verdict: `python3 -I tools/stageA_pool.py` (writes aggregates/stageA-pooled.json; verdict only at 15/15).
- To do after the loop: replace this file with the final version (verdict), EXPOSURES row + QUEUE entry.

## Caveats
- quote_supports is a jev boolean proxy, not a verbatim quote check; hits sit near the 0.7 cut (≥0.6 count is 5× the verified count on V-para).
- Per-shard caches are separate by design (no cross-shard reuse), so cost is not reduced by overlapping chunk texts.
- Blind sets read script-only; no item text was printed or viewed.
