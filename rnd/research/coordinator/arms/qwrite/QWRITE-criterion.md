# QWRITE step 0: does a 4B-written search query put the fact chunk into the raw retrieval pool more often than the engine's own query on the 180 public self-tests? (frozen 2026-10-16 before any generation or replay; 0 judge / 0 paid; public items only)

## Tags
Tags: probe
Ruleset: 30

## Question
BACKLOG row 11 QWRITE (low prior: query2doc/HyDE gains scale with model size, small models marginal + factual errors; DEEPITER 35B follow-up queries NO). Public gate only (the row's second clause): on the 180 self-tests the fact chunk in raw top-8 must rise from the OFF count (H8-ST OFF = 69 on the cut-7 tree) by >= 15. The v0.2 clause (22/32) is NOT used. Use: PASS -> the declared judged stage below may run at a later META (not in this step); FAIL -> row 11 closes (CLOSED row, "step 0 FAIL").

## Fixed inputs
- Writer = Qwen3-4B-Instruct-2507-Q4_K_M (shared-models/), llama-server b11010 (spikes/llama-b11010-cpu), MacBook, one server, /v1/chat/completions, seed 42, temperature 0, max_tokens 24, no system prompt, user message exactly:
  "Rewrite as a 3-8 word search query naming the entity and the fact asked. Output only the query.\nQuestion: {question}"
- Output cleaning (fixed): first non-empty line, strip surrounding quotes/backticks, a leading "Query:" label and trailing punctuation.
- Generation gate per item: non-empty, <= 12 words, no answer leakage. Leakage = any number token (contains a digit) in the query that occurs in the item's in_pack_facts quotes/facts or answer and NOT in the question. A failing item falls back to the original query (counted, reported). Kill if > 18/180 fail.
- Replay = arms/qwrite/tools/replay-qw.ts = h8st/tools/replay-h8.ts copy + --qmap <json id->query>; mode "qw" replaces the query of the FIRST engine retrieve() call (and of the --pool 8 extra retrieve) with the item's rewritten query; later retrieve calls, task routing, the keep step and the prompt keep the engine's own query/question. Modes off,qw,off (pass 3 = repeat identity). 0 LLM, generation stubbed.
- Tree = kiln-local/be-0cfd4a77-cut7-tk2off (pristine cut-7 copy, as H8-ST REF); published packs; kit = claim kit (boar-crypto, boar-wikivoyage-en) + the item's pack; --gate search --k 6 --pool 8; the :8094 detector untouched.
- Reach definitions = h8st/tools/compare_h8.py: fact chunks = in_pack_facts chunk_index over the article's chunks by start, item pack only; raw6 = raw[:6]; top8 = fact chunk in raw[:6] or pool[:8]; kept = fact chunk among kept; article kept; empty kept.

## Gate (0 calls)
- G0 identity: off vs off2 identical on 180/180, and OFF top8 within +-3 of 69 (else STOP, report tree drift).
- G1 PASS iff top8(qw) - top8(off) >= +15 AND items losing the top8 fact (off yes, qw no) <= 5.
- Reported, not gating: raw6, kept, article kept, empty kept, per pack, SE/topic, writer s/item, fallbacks.
- Verdict: G1 PASS -> "step 0 PASS" (judged stage eligible); else "step 0 FAIL", row closes.

## Judged stage (declared, NOT run in this step)
random20 (seeded 4242 over the 180) x 2 arms = Haiku 5.5-low 40 calls; full generation ON (qmap in the engine) vs OFF on the 4B; LEVER if ratio Δ >= +0.03 with CI low > 0.

## Power
expected_delta: +0.00...+0.02 (prior)
n: 180
seeds: 1 (deterministic replay; writer temp 0)
mde: n/a (0-call gate, counts)
slice: all
l1_futility: n/a
reopen: a larger writer (deep tier) only with a new criterion
split (declared): per pack; SE (100) / topic (80)

## Ceiling (RULE 29; 0 calls)
ceiling: ORACLE-ST +0.095 when the fact is in the prompt; reach-only lever
bar_ceiling: below the bar alone; product/retrieval lever
launch: BACKLOG row 11 (coordinator, 2026-10-16)
transfer: engine option (writer call before retrieve) if PASS

## Budget (RULE 29)
wall_cap: 1 h
calls_cap: Haiku 0 / Opus 0 in this step; paid 0
disk: floor 5 GiB free on the MacBook
kill_if: busy.sh busy, replay errors, missing rows, > 18 generation fallbacks, disk < 5 GiB
