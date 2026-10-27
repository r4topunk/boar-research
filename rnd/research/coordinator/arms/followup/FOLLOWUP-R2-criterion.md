# FOLLOWUP r2: does an article-anchored neighbour fetch (the previous answer's top source article(s), its chunks scored against the BARE follow-up, best 1-2 added as pinned candidates before the keep step) put the follow-up's target chunk in the kept context, and does it move the judged turn-2 answer? (frozen 2026-10-16 by the FOLLOWUP r2 agent, before any r2 code, replay, generation or judge call; measurement arm, direction-only)

Frozen before any run. Inputs fixed by sha below. r1 = FOLLOWUP-criterion.md a97b22d3 (G3 FAIL: gold chunk kept 1 -> 3/20, gold article 2 -> 10/20).

## Tags
Tags: none
Ruleset: 30

## Question
r1 showed that query expansion with the turn-1 terms reaches the article but keeps turn 1's lead/fact chunks, not the neighbour that answers the follow-up. r2 mechanism, `deps.followupAnchor` (engine, off by default; r1's `deps.followupContext` stays unset in every r2 cell):
- Fires when the conversation has an earlier user turn, the current turn is a follow-up by r1's lexical test (<= 8 words, a referring pronoun or an ellipsis opener; followup.ts), the previous assistant turn carries `sources` (shown titles; r1's optional ConversationTurn field), the turn is English and not the today-in-history path, and the plan retrieves (not multi-pass).
- Anchor articles = the first <= 2 distinct titles of that `sources` list, resolved STRICTLY as shown: a title "Label: X" whose label is a pack source label (packs.ts SOURCE_LABEL) resolves to an article titled X whose rendered source is that label's; any other title resolves to an article titled exactly that (case-insensitive) whose rendered source is enwiki (the label-less render). Searched in every installed format-2 pack. No fuzzy, no redirects, no sibling articles in other sources.
- All chunks of the anchored article(s) are scored with the pack's own passage score (wikiPack passageScore: BM25-like term weight of the follow-up's FTS stems, heading counts double) against the BARE follow-up text. The best ANCHOR_N = 2 chunks with score > 0 that are not already in the retrieved list are appended to the retrieved list (before the substantive filter, compression and grounding), pinned in compressContext (as an identifier page is) and exempt from the off-topic and health-topic grounding drops (they belong to a page the previous answer already showed). matchQuery and searchQuery stay the bare follow-up (no turn-1 terms anywhere).
- Reason codes: `followup:anchor:<n>` (n = chunks fetched over the anchored articles, 0 when no title resolves), `followup:anchor-kept` (>= 1 anchor chunk is in the final kept sources).
OFF (switch absent) = unchanged by construction; verified below. Use: direction for a post-10-20 engine patch and for the app passing shown source titles in its history turns.

## Fixed inputs
- Pairs `pairs.jsonl` sha256 5f687e26e899e7242623693350dad33c718bff0b84f69ba90eea8bb267e92aec, gold `gold.json` e81d771e84c776ac00f14063d7ab07813d329727c598b6c6f3a59652d16a7e78 (r1's; unchanged).
- Replay questions: r1's `runs/q/t1-*.jsonl` (cat in pack-name glob order sha256 0b43f15326f361e5d2d092a48bb39cf233c1879175fe43d2cb74b4ba12bdb0b7) and `runs/q/t2-*.jsonl` (cat sha256 fd127663e7b0430659740e18a666e880881d4151fa62799863a0561567e1e61a): turn-2 history = [user: t1 question, assistant: "(previous answer)" + sources = the t1 OFF replay's kept titles]. Bench v0.1 questions.public (60), claim kit.
- Tree kiln-local/be-cut7-followup (r1 tree = wt/pr1 8ac9eb7a + tools/followup.patch ad3a59b9), patched in place with the r2 code; ARM file -> pr1+followup-r2. The r2 patch `tools/followup-r2.patch` (vs the r1 tree) and its sha are recorded in `tools/followup-r2.patch.sha256` and the report; requirements: tsc clean, src/routing vitest all pass + >= 3 new anchor tests. Eval switch: adapter FOLLOWUP_ANCHOR=1 -> deps.followupAnchor (tools/followup-r2-adapter.eval.patch).
- Arm **ON** = replay mode "anc" (deps.followupAnchor true, followupContext unset); control **OFF** = same tree, both switches unset. Replay driver: r1's tools/replay-fu.ts (sha 22c40d8a…) plus a mode "anc" line only; --gate search, --k 6, lexical detector, no LLM; kit per pair = claim kit + the item's own pack.
- Public sets only (180 self-tests, v0.1 public). No blind/, no rnd/veil/; no EXPOSURES row.

## Ceiling (RULE 29; 0 calls, computed from r1's existing runs/q before the freeze)
ceiling: the strict anchor can reach the gold chunk only where turn 1's OFF kept sources show the gold article under its rendered title in the pair's pack: 7/20 (fu-03, 06, 08, 12, 14, 15, 19). fu-16/17/18 (factbook) show "Wikivoyage: <country>" (kit pack article, not the factbook one) and the other 10 never kept the gold article. OFF keeps gold on 1 (fu-01, outside the 7) -> strict maximum ON = 8/20; the gate needs 6 of the 7 reachable pairs.
bar_ceiling: n/a (product-only: multi-turn is not in V-para / v0.2)
launch: coordinator 2026-10-16 (FOLLOWUP r2 step 0, MacBook lane)
transfer: product-only

## Power
expected_delta: unknown on answers; reach is the deciding quantity
n: 20 turn-2 answers (judged), 20 + 20 + 60 replay items (gate)
seeds: 1
mde: ≈ 0.04 raw at n = 20 (Haiku); direction-only, no LEVER/SMALL/NO label
slice: pairs.jsonl (20 public pairs)
l1_futility: n/a (direction-only; no Opus stage)
reopen: FOLLOWUP r1 G3 FAIL (a97b22d3); r2 = new mechanism (anchor fetch), same pairs, same gate shape
split: target-gained = pairs where ON keeps the gold chunk and OFF does not (step-0 replay) vs the rest

## Budget (RULE 29)
wall_cap: 1.5 h
calls_cap: Haiku 40 / Opus 0 (0 paid, 0 jev)
smoke: fu-01 t1 + t2 OFF + t2 ON generated first (infra only: rc 0, non-empty, 0 errors; followup:anchor present on t2 ON, absent on t2 OFF) -> smoke.verdict.json
kill_if: any generation error/empty answer; the 0-call gate FAIL (-> stop, 0 generation, 0 Haiku); MacBook gen lane busy (busy.sh) -> stop after step 0 and report; free disk below the 5 GiB floor -> stop generation
checkpoint: the 0-call gate, before any generation or judge call

## Precheck (0 calls)
token_projection: 750 (turn-2 prompt with history + up to 2 pinned anchor chunks) / token_budget: 1100
disk_peak_gib: 0.05
off_baseline: OFF cell of this tree + wt/pr1 replay for OFF byte-identity
call_pattern: Haiku 5.5-low N=4 shards, pairwise ON vs OFF turn-2 answers, both orders (20 x 2 = 40 calls); rubric per item = conversation context line with the turn-1 question + the pair's t2_key_fact; no reference rows exist for agent-written follow-ups, so the read is pairwise W/T/L only (an item is a win when ON wins both orders, a loss when OFF wins both, otherwise a tie)
lane: mac-gen
opus_clause: none
wall_cap_h: 1.5
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. **Step 0 (0 LLM; tools/gate0-r2.py over replay outputs):**
   - G0 infra: every replay cell 0 errors, repeat identity (off,off and anc,anc passes) on all items.
   - G1 OFF byte-identity: the OFF cell on the patched tree = the same replay on wt/pr1 (raw ids, kept ids, promptSha) on the 20 turn-2s and the 60 v0.1.
   - G2 turn-1 identity: ON vs OFF identical (raw ids, kept ids, promptSha, reason codes) on the 20 turn-1s and the 60 v0.1, and `followup:anchor` fires on 0 of these 80.
   - **G3 reach: gold chunk in kept context on the 20 turn-2s; PASS if ON >= 7 (OFF = 1 in r1; re-measured here).**
   - **G4 no loss: no turn-2 where OFF keeps the gold chunk and ON does not, and no turn-2 whose OFF kept chunk ids are not all still kept ON (an anchor may add, never displace).**
   - Descriptive per pair: gold article / gold chunk kept OFF vs ON, gold chunk in raw top 6, anchor fired, chunks fetched, anchor chunk ids, anchor-kept.
   - Gate = G0 AND G1 AND G2 AND G3 AND G4. FAIL -> stop, report, 0 generation, 0 Haiku.
2. Gate PASS, busy.sh shows the MacBook gen lane free and free disk >= 5 GiB -> generation (one llama-server, detector :8094 untouched, 4B Qwen3-4B-Instruct-2507 Q4_K_M, threads 4, seed 42, maxTokens 512, succinct persona, quickFirst true / alwaysComplete false, per-pack kit): t1 (20, switches unset), then t2 OFF and t2 ON with history = [user: t1 question, assistant: the t1 answer text + sources = the t1 trace's kept titles]. Smoke first (fu-01). Descriptive: codes, gold article kept, gold-chunk sentence (>= 40 chars) in the prompt, prompt tokens, latency. If the lane is busy the arm stops after step 0 (reported, not a failure of the mechanism).
3. Haiku pairwise as in call_pattern: 40 calls. W/T/L over 20; split target-gained vs rest.
4. **Verdict (frozen, direction-only):** DIRECTION-POSITIVE if W > L overall AND W > L on target-gained; DIRECTION-NEGATIVE if L > W overall; FLAT otherwise. A DIRECTION-POSITIVE read licenses at most a larger multi-turn slice post-10-20, never adoption.
- One generation per arm. No rerun except an infrastructure error before the first token.

## Stop rules and outputs
MacBook disk floor 5 GiB, one llama-server at a time, never stop :8094, none of our servers left running. Haiku <= 40, Opus 0, 0 paid. No git push; commit arm files in rnd. Outputs: `FOLLOWUP-R2.md` (cites this sha), `aggregates/gate0-r2.json`, `tools/` (patch + sha), `runs/replay-r2/`. One QUEUE row (tools/qrow.sh, tag main) + BACKLOG row 17 update.
<!-- END FROZEN -->
