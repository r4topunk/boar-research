# LITEPACKS criterion (frozen 2026-10-20 before any generation)

## Question
With Qwen3-1.7B as the main 8 GB model and the compact declines released behind a warning line (decision 2026-10-20; LITEDECLINE OFF5 + CMP30OFF warning), which set of general knowledge packs, installed by default, raises usefulness and cuts confident errors on casual questions without crowding the retrieval slots or blowing the phone budget?

## Arms (installed pack sets; all already built; pack files sha-pinned in the requests, as LITE5/LITEDECLINE used them)
- K0 claim kit: boar-crypto (ae9fbd2c, 36,093,952 B) + boar-wikivoyage-en (ff8595e3, 351,092,736 B) = 387,186,688 B
- K1 = K0 + boar-simplewiki-en (v3proto 99bcec30, 735,510,528 B) = 1,122,697,216 B
- K2 = K1 + boar-factbook (v3proto 4ce447e8, 11,829,248 B) = 1,134,526,464 B
- K3 = K2 + boar-medlineplus-en (v3proto e805ccea, 4,530,176 B) + boar-firstaid-en (v3proto 0a7dffa6, 26,329,088 B) = 1,165,385,728 B
- K4 = K0 + boar-wiki-en-top100k (9123b372, 2,542,215,168 B) = 2,929,401,856 B (measured here for the 1.7B; DEEPWIKI found it crowds k = 6 on the deep tier)

## System (identical across arms except the installed set)
Cut 7 + X2b desktop tree (kiln-local/be-0cfd4a77-cut7-headpass-x2, answer.ts 289607fd) + the CMP30OFF answer.ts delta (arms/cmp30off/tools/cmp30off.vs-cut7.answer.diff, answer hunks: compactDeclinesOff "all" releases the five compact-only declines and prefixes the released answer with exactly "Not found in this phone's offline library. From the model's memory, may be wrong:") + the LITEDECLINE adapter (1.7B untiered = compact as in the product; LITEDECLINE_OFF=5 -> "all"). Qwen3-1.7B Q4_K_M (b139949c), --reasoning off, seed 42, llama-server b11010 CPU -t 4, settings quickFirst, packHeadPass a2, packDense2 append-budget (the lite line's pack configuration) on every set and arm. Host: the Mac mini is unreachable at freeze time (ssh timeout 17:4x), so the MacBook (M1 Pro) runs generation (deviation from the brief, recorded); one llama-server at a time on an OS-assigned port (never 8094/8191); detector :8094 used, never started or stopped; disk guard >= 4 GiB free on the MacBook (outputs are small); servers stopped when done.

## Sets (dev only; no bench/v0.4, no blind/, no rnd/veil)
- MAIN (decides) = bench v0.1 public: 60 generated, 57 judged (the 3 venue items food-001/002/006 have no rubric reference) + selftest qa-cooking-se (20) + qa-money-se (20): public casual-question sets outside the 180 whose packs are in no candidate set (off-pack for every arm). MAIN n = 97. v0.1 alone (57) is reported beside it. Rivalset is not used (its refs are placeholders; judge.v1 needs a reference).
- SECONDARY (report only, no-harm check) = the 180 pack self-tests, each arm's installed set as above (not the item's own pack): split into candidate-pack self-tests (simplewiki, factbook, medlineplus, firstaid: 80, pack-matched when the arm contains the pack) and SE self-tests (travel, ethereum, bitcoin, health, outdoors: 100, off-pack for every arm).

## Judge
Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, via arms/deepthink/tools/shard_judge.sh with absolute paths; check_judgments.py after each run (fail closed). K0 judged in full; K1-K4 judged where the answer text differs from K0's; identical answers reuse K0's rows (delta exactly 0).

## Budget
calls_cap: Haiku 2900 / Opus 0
(5 arms x 277 judged items x 2 orders = 2,770 upper bound; 0 paid API.)

## Metrics (per arm and set)
- s per item = mean of the 3 judge dims averaged over both orders; Q = sum s / sum s_ref.
- U = U0 = Q with s := 0 for every declined answer (trace answer.declined); with OFF5 only non-compact declines can remain.
- Confident-error rate CE = share of non-declined answers with judge correctness (mean over orders) <= 1.5.
- Warned share = share of answers whose text starts with the warning line.
- Retrieval share of kept slots per pack = kept source entries attributed to each pack / all kept entries (attribution by source label and title, mapping recorded in the report).
- Context tokens per answer (timing.promptTokens, mean and p50) = phone prefill cost proxy; retrieval ms p50 reported beside it (desktop).
- On-disk size of the installed set (bytes above).
- Paired deltas K - K0: item bootstrap B 2000, seed 11, 2.5/97.5 percentiles.

## Decision rule (stated before running)
On MAIN (n 97): pick the smallest set by on-disk size among K1-K4 whose U gain over K0 is >= +0.03 with paired CI low > 0 AND whose CE rate is not higher than K0's by more than 2 points (CE(K) - CE(K0) <= +0.02). If none qualifies, report the best trade-off and recommend no change (K0). SECONDARY never changes the verdict; a set whose U on the 100 SE self-tests falls below K0 with CI high < 0 is flagged as crowding harm in the report.

## Outputs
arms/litepacks/LITEPACKS.md (TL;DR table per set, verdict, per-category notes, examples warned-wrong -> grounded-right, crowding cases), aggregates/litepacks.json, one QUEUE row, commit to rnd (own paths + QUEUE.md).
