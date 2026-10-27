# VITAL-MISSES criterion (FROZEN 2026-10-23 before any replay; never edited after; addenda go to MISSES.md)

Question: why do four TOPICS27 Research Topics (b13, b15, b19, b20) never get their article into the kept context on wiki-vital5, although the pack holds it, and do the adopted search fixes recover them without harming the other 23 topics?
0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone, no generation. MacBook replays only. Never read blind/, rnd/veil/, bench/v0.4. Do not edit wt/engfix or kiln-local generation trees (arms run on existing clones with env switches).

## System (same as TOPICS27 stage 1b)
Questions in/t27-detailed-s42.requests.jsonl (27 EN topic strings). Tool arms/retrieve-sweep/tools/replay-sweep.ts. Kit = shared-data/packs/wiki-vital5.sqlite only (format 1, sha d3b87d56...) + essential corpus. --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 --gate search --forward-opts --settings-json K1 {quickFirst true, alwaysComplete false, packHeadPass a2, packDense2 append-budget, personalityId detailed}; no --tasks-from (lexical detector).
Kept = the replay's `sources` list (engine pre-answer sources event, after compression, grounding and head pass). Raw = `raw` (k slots), wide = `wideFull` (wide 12).

## Expected titles (exact titles present in wiki-vital5, checked by sqlite before this file)
- b13 "How mosquitoes spread disease, and why HIV isn't one of them": {Mosquito-borne disease, Mosquito} (HIV, HIV/AIDS present, reported, not required).
- b15 "Kyoto's role in Japanese history and culture": {Kyoto, Heian-kyō} (History of Kyoto absent; Kyoto Prefecture reported).
- b19 "Travelling in Brazil: plugs, voltage and emergency numbers": {AC power plugs and sockets, Mains electricity} (Mains electricity by country, Emergency telephone number absent; Brazil present but alone does not count).
- b20 "Japan and Germany compared: population density and an aging society": {Japan, Germany, Population density, Population ageing} (Demographics of Japan / of Germany, Aging of Japan absent).
Item RECOVERED iff >= 1 of its expected titles is in kept.

## Stage where each is lost (from the existing TOPICS27 replay, before any new run)
- b13: S3 keep/onSubject (raw holds Mosquito-borne disease x2; code grounding:off-topic-dropped-4). Hypothesis: onTopic's proper-noun rule ("HIV" is a capitalised word after the first, so every source must contain "hiv").
- b15: S4 compress (raw holds Kyoto x2 at sim 0.796; context 541->187 keeps Heian period + History of Japan). Hypothesis: compression is query-relative and the possessive "Kyoto's" / first-word position; the probe also records whether the Kyoto chunks would pass onSubject ("Japanese" is the only proper-noun term).
- b19: before S1 (instant-table shortcut: answer:emergency-numbers, retrieve() never called).
- b20: S1 raw (raw = Hiroshima Prefecture, Population decline, Lost Decades, Kantō region; wide holds only 4) and S3 (all 4 dropped). Hypothesis: format-1 search = FTS5 OR query top 400 by bm25, cosine re-rank of that pool only, 0.70 gate: the expected chunks are not in the pool or score < 0.70; and the proper-noun rule requires "germany" ("Japan" is the first word, not counted).
Stage probe (0 LLM, embedding only, tools in misses/): for every expected-title chunk, its bm25 rank in the 400-candidate pool, term coverage vs required, cosine to the search query (pack int8 vec), gate 0.70, onTopic(matchQuery) strict and relaxed (F4), and whether compressContext keeps it given the raw list. Stage = first stage a chunk fails.

## Arms (each a full 27-topic replay)
- A0 base: kiln-local/be-0cfd4a77-cut7-litepacks, no env. Identity check: raw + kept titles vs replay/t27.replay.jsonl (report x/27).
- A1 SEFIX-124: kiln-local/rs-SEFIX (= rs-H4 + SEFIX-ALL), env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 (F3 unset). Switch-off identity: rs-SEFIX with no env vs A0 (raw/kept/reason codes x/27). Prediction: gidf, F1, F2 are inert on this kit (they act on format-2 packs / Stack Exchange packs only), so A1 = F4 alone; F4 recovers b13 only if the Mosquito chunks pass the rest of onTopic; b15/b19/b20 not recovered -> A1 fails the gate (1/4).
- A1d decomposition (diagnostic): rs-SEFIX with RS_KEEP_NOPROPER=1 only. Expected identical to A1.
- D1 question-form rewrite (diagnostic only, never a fix: no engine change): the four topics rewritten as questions, replayed on A0 and A1 trees:
  b13 "How do mosquitoes spread disease, and why can't they spread HIV?"
  b15 "What role has Kyoto played in Japanese history and culture?"
  b19 "What plugs, voltage and emergency numbers should I know when travelling in Brazil?"
  b20 "How do Japan and Germany compare in population density and aging society?"
  plus D1b b19-split "What plugs and voltage does Brazil use?" (what retrieval would return if the table did not intercept).

## Gate (an arm is a FIX only if all hold; A1 and A1d judged, D1 reported only)
1. RECOVERED on >= 2 of the 4 items (b13 b15 b19 b20).
2. Kept list (ordered titles) changed vs A0 on <= 2 of the other 23: q1 q2 q4 q7 q8 q9 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b14 b16 b17 b18 b21.
3. None of the 7 health topics (q2 q4 b2 b8 b13 b14 b21) loses a health-family source: every title kept by A0 on those topics is still kept by the arm.

## Deliverable
MISSES.md: criterion sha, commands, per-item stage table (raw/wide/kept titles + similarities), cause class per item (query form / lexical terms / lead-vector / keep rule / compress / instant-table shortcut), arm results vs the gate, a maintainer paragraph. Replays under replay/ (gitignored).

## Prediction (frozen)
b13 cause = keep rule (proper noun); b15 = compress (+ keep rule on "Japanese"); b19 = instant-table shortcut; b20 = lexical/pool + gate (format-1 search has no dense scan outside the bm25 pool) + keep rule. A1: 1/4 recovered (b13), kept changed on 0-3 of 23, gate FAIL. D1: rewrite recovers b15 (Kyoto becomes a proper noun after "What") and maybe b20; b13 unchanged by the rewrite alone (HIV still proper); b19 still the table.
