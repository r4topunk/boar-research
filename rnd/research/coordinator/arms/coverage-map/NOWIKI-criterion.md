# NOWIKI criterion (frozen before any replay; 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone; MacBook replay only)
Date 2026-10-23. Asked by r4to: "what if we drop Wikipedia and keep only the small focused packs, which retain and search better?"
Question: does the adopted kit (SEFIX-124, K13) without the Wikipedia-family packs keep MAIN delivery and relieve crowding for the small packs?

## Kits (file paths = coverage-map/compose/tools/kits.py kit(10), the K13 / N10 kit of SEFIX-124)
- K13 (base): boar-crypto, wikivoyage, simplewiki (v3proto), qa-cooking-se, qa-money-se, factbook, medlineplus, firstaid, visa, qa-health-se, qa-travel-se, qa-outdoors-se, wiki-vital5.
- NOWIKI: K13 minus {boar-simplewiki-en, wiki-vital5} (11 packs).
- NOWIKI2: K13 minus {boar-simplewiki-en, wiki-vital5, boar-wikivoyage-en} (10 packs).

## Tree and recipe (all sets)
Tree kiln-local/rs-SEFIX, read-only. Env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 (F3 off) = SEFIX-124. The kit is the only variable between arms.
- MAIN 97: coverage-map/sefix/tools/run_main.sh flags exactly (dg-S-K1-main-s42 requests, funnel-K3 tasks-from, qwen3-1.7b-q4km, ram 12, --cpu-embed, wide 12,
  settings packHeadPass a2 + packDense2 append-budget), --packs = the kit. The three MAIN replays run sequentially with nothing else replaying (for ms).
  Identity: K13 kept chunk ids AND reason codes vs sefix/replays/main.F1F2F4.jsonl on 97/97; if not, the gap is reported and this K13 run is the reference.
- 180 self-tests (PACKPROOF set): the PACKPROOF ON requests (packproof/in/on-k13 140, on-k13+qa-ethereum-se 20, on-k13+qa-bitcoin-se 20), same flags as MAIN,
  tasks-from = the matching live ON traces (packproof/gen/<group>/traces.jsonl, for detector scores); --packs = kit (+ v3proto qa-ethereum-se / qa-bitcoin-se for those
  two groups). Parity of the K13 replay kept titles vs the live ON traces is reported (information).
- 27 Research Topics: topics27/misses/run.sh flags (t27-detailed-s42 requests, --corpus essential, --gate search, settings quickFirst/alwaysComplete false/a2/
  append-budget/personality detailed), tree rs-SEFIX + the SEFIX-124 env, --packs = the kit. Reference (not re-run): topics27/replay/misses.A1 (vital5 only, SEFIX-124).

## Metrics
1. MAIN chunk-level delivered facts of 92 (coverage-map/tools/chunklevel.py score(), unchanged), split cm 40 / v0.1 52; items gained and lost vs K13, by id.
2. MAIN kept-set changes per item vs K13 (keptFull chunk ids, as a set and in order), count and ids.
3. Health: health item = any item whose K13 or arm reasonCodes contain a code starting "grounding:health" or "instant:off-health" (W78 rule), on MAIN 97, the 180
   and the 27. Health loss = a health item where a health-family source kept under K13 (docId from boar-medlineplus-en, boar-firstaid-en, qa-health-se) is not
   kept under the arm. Health items changed (kept chunk ids differ) reported as information.
4. Self-tests: own article kept = some keptFull chunk whose article (v3proto article_meta url + title, the PACKPROOF match(): url + title, own.json arts incl.
   comparison partners) belongs to the item; per pack and pooled. The 20 boar-simplewiki-en items lose their own pack under NOWIKI/NOWIKI2 by construction:
   they are reported separately and EXCLUDED from the crowding count; crowding relief = own-article kept on the 160 other items (packs installed in every kit).
5. 27 topics: an expected/anchor title (topics27/aggregates/titles.json groups, lowercase match) among the kept titles (the TOPICS27 in_kept rule). Information only.
6. Bytes read per retrieving MAIN question, W78C accounting (exact int8): stage-1 packDense2 = sum over chunk_vecs packs in the kit of rows x 384 (per-pack rows from
   w78/replays-c/main.B.jsonl.denselog) + F1 = SE lead rows x 384 (cooking + money, from main.B.jsonl.f1log); wiki-vital5 format-1 pool re-rank upper bound 400 x 384
   noted separately. Pack bytes on disk per kit. Computed, not logged (rs-W78 is not touched).
7. Retrieval ms p50 (replay row "ms" = retrieve() wall) over retrieving items, per set and kit; MAIN is the timed set.

## Decision rule (frozen), per arm (NOWIKI, NOWIKI2) vs K13
PASS iff (a) MAIN chunk-level delivered >= 40 (42 - 2; if the K13 identity fails, >= K13 replay - 2) AND (b) v0.1 items whose chunk-level fact is lost vs K13 <= 3
(listed) AND (c) self-test own-article kept on the 160 rises by >= +5 vs K13 AND (d) 0 health losses (MAIN 97 + 180 + 27).
Verdict: DROP if NOWIKI passes (recommended default = NOWIKI2 if it also passes, else NOWIKI).
KEEP-AS-OPTIONAL if no arm passes but some arm meets (c) and (d) (Wikipedia costs the small packs but carries general facts: user-selectable, not default).
KEEP otherwise. The 27 topics are information (they need Vital by construction) and do not enter the verdict.
No blind/, rnd/veil/ or boar-eval/bench/v0.4 file is read. Output under coverage-map/nowiki/ (replays in nowiki/replay/, gitignored).
