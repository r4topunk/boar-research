# CRYPTOSEL on cut 3 (retrieval engineer, 2026-10-05, DEV; L0 only, no judge, nothing pushed)

TL;DR: **L0 PASS after the one allowed revision** (round 1: 1/3 FAIL; round 2: 3/3). Branch `coord/cryptosel` (worktree `wt/cryptosel`, from `coord/final` = cut 3 a67c70db), 2 local commits, never pushed. The coordinator triggers L1.

- **Patch:** `cryptosel-on-cut3.vs-0cfd4a77.patch` (cut 3 + CRYPTOSEL), sha256 `948493ee1fe99e19b30672460812951581768ef39c278bcd080f392c2727bb79`. Applies cleanly to a fresh `git archive 0cfd4a77`; tsc clean there; vitest **1306/1306** (cut 3 is 1285, **+21 units**).
- Criterion `CRYPTOSEL-criterion.md` untouched (6ba3e103…). Kit: kit A (crypto + Wikivoyage), the cut 3 kit in `be-0cfd4a77-cut3`.

## Mechanism (`src/rag/specSelect.ts`, pure; hooks in `wikiPack.ts` and `routing/context.ts`)
Applies only to articles of the crypto pack's spec sources (`eips`, `ethspecs`, `bips`) that the question reaches. A question that names neither a standard (by number, matching that page) nor a constant gets null and nothing changes (byte-identical).
1. **Prefer** passages that write the EIP number or a constant the question names (UPPER_SNAKE or as words; `MAX_EFFECTIVE_BALANCE` ~ `MAX_EFFECTIVE_BALANCE_ELECTRA` at a `_` boundary). For a page the question names by number, the page's own title constant counts as named.
2. **Keep whole** a constants table with a named constant: placed first, no sentence cut (`compressContext`), only if it fits the budget (else normal path).
3. **Same budget:** the compressor work budget and the page's two-passage pick are unchanged (preferred passages replace others); the hit score is the keyword hit's, so fusion ranks them with the page.
Round 2 added (the revision): (a) the **Abstract** of a page named by number is preferred (an EIP states itself there and rarely repeats its own number); (b) the same preference applies when the page arrives on the **keyword route** (vit-cry-002's EIP-7805 never took the title route); (c) preferred passages are no longer cut by the 0.15 score floor. (a) is the one step beyond the criterion's literal wording: 002/003 name no constant and their pages' chunks don't repeat "EIP-7805/4444".

## L0 (stub-LLM replay, real engine + kit A, no detector/places; v0.1 EN 60 + V-exact 11 = 71 items; `tools/`)
Gold facts for the 3 targets are in `gold-facts.json` (sha256 e1ca7a4c…): pack sentences stating the fact the rubric needs. **Why not the stock goldhit R450 metric:** its gold for 002/003 is news text that is not in the pack, and for 009 it is the Abstract, not the table, so it cannot move on these items (goldhit-sent is 4/56 both before and after). The gold file was written after the round-1 replay had run on 009 only; derived from rubric and pack text, not from any context.

| bar | round 1 | round 2 (final) |
|---|---|---|
| gold fact in context on 002/003/009, ≥ 2/3 gain, 0 lose | 002 no, 003 no, **009 yes**: 1/3 **FAIL** | **002 yes, 003 yes, 009 yes: 3/3, 0 lost. PASS** |
| other contexts byte-identical, only crypto-routed change | 1 changed (009), crypto-routed | 3 changed (002, 003, 009), all crypto-routed; the other 68 identical (incl. the 5 other crypto-routed: 001, 004, 006, 008, 010). **PASS** |
| crypto-routed item loses its gold sentence | none | none (goldhit-sent on the 8 crypto-routed: 2 → 2, nothing lost). **PASS** |
| retrieval p50 ≤ 1.2× | n/a | **1.005×** (p50 of per-item min over 3 interleaved runs: 99.1 → 99.6 ms; one-shot runs 1.04/1.06/0.88, a single non-interleaved pair read 1.217 = noise). **PASS** |

What changed in the contexts (placed, after compression): 009 gains the table (`MIN_ACTIVATION_BALANCE` 32 ETH, `MAX_EFFECTIVE_BALANCE_ELECTRA` 2048 ETH), 443->416 tokens; 002 gains the EIP-7805 Abstract (IL committee, attesters vote only if all ILs are included) and loses the roles intro sentence and the EIP-8369 snippet (a mention of 7805), 179->124; 003 gains the EIP-4444 Abstract ("Clients must stop serving historical headers, bodies, and receipts older than 33,024 epochs") and loses the EIP-7927 meta snippet, 456->287.

## UNKNOWN / for L1
- Stub LLM: whether the 4B uses the extra facts is only measurable at L1. 003's disk saving (300–500 GB) is not in the pack; the context has the 400 GB / 1 TB motivation.
- 002 and 003 lose small side snippets (8369 and 7927 are not gold); the L1 rule "no changed item down ≥ 1.0" covers it.
- The Abstract rule is broader than the criterion's text: it also fires on any other EIP-numbered crypto question (here only 002/003 are affected among v0.1 + V-exact; held-out V-para not looked at, so its exposure is unknown).
- Sizes: 3 retrieval/compress hooks; no new model call; only a spec-source article triggers extra chunk-row reads (one `SELECT` per spec hit).

## Files
`tools/mktree.sh` (local desktop-node tree from a ref or worktree), `tools/replay.sh`, `tools/stub-server.mjs`, `tools/l0.py` (gold facts, changed items, p50), `tools/cmp.py` (context diffs), `tools/lat.sh` + `tools/latp.py` (interleaved latency), `tools/dumpart.mts` (pack article/chunk dump), `tools/items71.jsonl`; `L0-round1.txt`, `L0-round2.txt`; `traces-cut3.jsonl`, `traces-cut3+cryptosel.jsonl` (replay traces). Stub server needs `node tools/stub-server.mjs 18500 <workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf`.
