# KEEPPIN criterion (frozen 2026-10-23 before any replay; never edited after)
Task KEEP-PIN: two late-stage losses from VITAL-MISSES (topics27/MISSES.md): compression's relative floor drops the article the question names (b15 Kyoto, share .41 < .50), and the proper-noun keep rule drops sources lacking the question's proper noun (b13 HIV, b20 Germany). 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone. MacBook replays only.

## Base and tree
- Base = SEFIX-124 as it is: kiln-local/rs-SEFIX tree, env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 (F3 unset).
  MAIN 97: sefix/tools/run_main.sh recipe (13-pack N10 kit incl. wiki-vital5, funnel-K3 traces, packHeadPass a2 + packDense2 append-budget), base replay = sefix/replays/main.F1F2F4.jsonl (chunk-level 42 of 92).
  27 topics: topics27/misses/run.sh recipe (wiki-vital5 + essential corpus, gate search, K1 settings + detailed), base replay = topics27/replay/misses.A1.jsonl.
- Arm tree = kiln-local/rs-KEEPPIN = cp -Rc rs-SEFIX + arms/retrieve-sweep/patches/KEEP-PIN.patch, two default-off switches. Identity: switches off reproduces both base replays (raw, kept chunk ids, reason codes) on 97/97 and 27/27, else no verdict.
- Observed before design (code read, no replay): onTopic's proper-noun rule is already case-insensitive (tokenizeTerms lowercases) and is per source "ANY question proper noun in this source"; SEFIX F4 (RS_KEEP_NOPROPER=1, on in SEFIX-124) already restores any source that fails only that rule when it holds another content term. So PN on top of SEFIX-124 is expected to be (near) inert by construction; measured anyway.

## Arms (env on top of the base env)
- base: no new switch.
- PIN (RS_KEEP_PIN=1): a raw candidate (the post-substantive list compression sees) whose title is named by the question is pinned. "Named" = some title segment (split on ": ", trailing parenthetical qualifier stripped) has >= 1 term and every term of it is a question term (tokenizeTerms of the question; the engine's existing titleSegmentNamed / NAMED_ARTICLE test; possessive "Kyoto's" -> kyoto). Pinned chunks: (a) join compressContext's existing pinned set (exempt from the 0.5 relative floor, placed first); (b) are exempt from onSubject in the non-health keep step (cryptoBlocked still applies). Health-strict filtering (onHealthTopic) is NOT bypassed. No alias table exists in the packs; alias = the parenthetical-stripped segment only.
- PN (RS_KEEP_PN=1): after onSubject and F4, a source dropped by the keep step comes back if it passes onTopic with the proper-noun check skipped AND some kept source (or its own title) holds a question proper noun (case-insensitive term match).
- PIN+PN: both.
- Diagnostic only (not gated): PNx = PN with RS_KEEP_NOPROPER unset (PN as a replacement for F4), MAIN 97 and 27.

## Metrics
- MAIN 97: chunk-level delivered facts (tools/chunklevel.py score() on the 92 keyed items: v0.1 share >= 0.5 in one kept chunk body; cm quote substring of one kept chunk body), per-item gains/losses vs base.
- 27 topics: expected-title-in-kept for the 4 MISSES topics (topics27/misses/score.py EXP: b13 Mosquito-borne disease|Mosquito, b15 Kyoto|Heian-kyō, b19 AC power plugs and sockets|Mains electricity, b20 Japan|Germany|Population density|Population ageing), counted absolutely (base has b13 = 1/4); other-23 kept-title lists changed vs base.
- Kept-set changes per item (kept chunk ids differ vs base), both sets.
- Health losses: on health items (MAIN: base reasonCodes contain grounding:health-strict; 27: q2 q4 b2 b8 b13 b14 b21) any base kept chunk id missing in the arm. Must be 0.
- Context tokens: per item sum over keptFull of ceil(len(title + "\n" + body) / 4); p50 over all items of the set; arm p50 <= 1.10 x base p50 on each set.

## Gate (per arm: base excluded)
LEVER-CANDIDATE iff
  ( chunk-level MAIN >= 42 + 3 = 45   OR   >= 2 of 4 MISSES topics recovered with <= 2 of the other 23 changed )
  AND 0 health losses (both sets) AND context p50 <= +10 % (both sets).
Else NO. Item counts, deterministic replay: no CI. A LEVER-CANDIDATE goes to a Haiku answer screen under its own criterion (not run here).
