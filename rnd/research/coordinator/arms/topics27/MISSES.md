# VITAL-MISSES: why four Research Topics never reach the model on wiki-vital5 (0 LLM, MacBook replay, 2026-10-23)
Criterion MISSES-criterion.md sha256 `80316ed84531759ab4621cdc6bae8d96edac3979d5c5c3bf083868c1c44cafe7` (frozen before any replay, not edited). 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone, no generation.

**TL;DR.** Four different causes, none of them "the article is missing": b13 = keep rule (the proper-noun rule demands "HIV" in every source), b15 = compression (Kyoto chunks score 0.41 of the best chunk, floor 0.5) plus the same keep rule ("Japanese"), b19 = instant-table shortcut (the emergency-number table answers before any search; the plugs half alone hits a second table, facts-electricity), b20 = first-stage search (format-1 "semantic" only re-ranks the bm25 top-400 pool; the right chunks sit at bm25 rank 796-2258 or under the 0.70 gate) plus the keep rule ("Germany"). **SEFIX-124 does not pass the gate**: it recovers 1/4 (b13) and changes kept lists on 3/23 (b9, b12, b16); no health topic loses a source. The question-form rewrite recovers nothing.

## Commands
```
cd <workspace>/rnd/research/coordinator/arms/topics27
misses/run.sh A0  be-0cfd4a77-cut7-litepacks $PWD/in/t27-detailed-s42.requests.jsonl        # base, = TOPICS27 1b
misses/run.sh A1off rs-SEFIX $PWD/in/t27-detailed-s42.requests.jsonl                         # switch-off identity
misses/run.sh A1  rs-SEFIX $PWD/in/t27-detailed-s42.requests.jsonl RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1   # SEFIX-124
misses/run.sh A1d rs-SEFIX $PWD/in/t27-detailed-s42.requests.jsonl RS_KEEP_NOPROPER=1         # F4 alone
misses/run.sh D1base be-0cfd4a77-cut7-litepacks $PWD/misses/d1.requests.jsonl ; misses/run.sh D1sefix rs-SEFIX $PWD/misses/d1.requests.jsonl RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1
tsx misses/probe.mts replay/misses.probe.json ; tsx misses/densescan.mts replay/misses.densescan.json ; python3 -I misses/score.py
```
run.sh = replay-sweep.ts, kit wiki-vital5 only + essential corpus, qwen3-1.7b-q4km, ram 12, --cpu-embed, wide 12, gate search, K1 settings + personality detailed. Identity: A0 vs replay/t27.replay.jsonl raw/kept/reason codes 27/27; A1off (rs-SEFIX, no env) vs A0 27/27. Probe cosines reproduce the replay (Kyoto #19425 0.7964 both).

## Per-item stage table (A0; sim = cosine to the query; S1 raw k 4, S2 wide 12, S3 keep/onSubject, S4 compress, S5 shown)
| item | raw (sim) | wide extra | kept | expected-chunk probe (bm25 rank in the 400 pool, cosine, onTopic strict) | lost at | cause class |
|---|---|---|---|---|---|---|
| b13 | Rift Valley fever .750, Mosquito-borne disease .798 / .787, Chikungunya .783 | Aedes aegypti, Malaria, **Mosquito .762**, Zika, West Nile | none (off-topic-dropped-4) | Mosquito-borne disease ranks 1/3/11, .75-.80, onTopic false (no "hiv"); Mosquito 4/10/138, .72-.76, false | S3 | keep rule: "HIV" is a capitalised word after the first, so every source must contain "hiv"; the only sources that do are the HIV pages (.63-.73) |
| b15 | History of Japan .740, Heian period .705, **Kyoto .796 / .796** | Culture of Japan, Kyoto University, Kyoto Prefecture, Heian-kyō .730 | Heian period, History of Japan (context 541->187) | Kyoto #19425/#19426: compression share .41 of the best chunk (floor .50), onTopic strict false (no "japanese"); Kyoto #19424 (lead, rank 3, .743) passes both but is not in raw; Heian-kyō .67-.73, share .20-.23 | S4 (and S3 behind it) | compress (relative-relevance floor: the period articles repeat "Japanese", "history", "culture"; the Kyoto chunks say "Japan") + keep rule ("Japanese" is the only proper noun; "Kyoto's" is the first word, so not counted) |
| b19 | none: retrieve() never called | - | none | if searched: AC power plugs and sockets bm25 rank 1-3 but cosine .63-.67, Mains electricity .66-.70, all under the .70 gate; onTopic false (no "brazil") | before S1 | instant-table shortcut (answer:emergency-numbers answers the third clause only); the plugs half alone ("What plugs and voltage does Brazil use?") hits a second fixed table, answer:facts-electricity |
| b20 | Hiroshima Prefecture .728, Population decline .724, Lost Decades .710, Kantō region .710 | nothing (wide holds 4) | none (off-topic-dropped-4) | Japan #8487 rank 142 .654, #8488 rank 796 (outside pool) .714; Germany #6330 rank 123 .679; Population density rank 9 .669; Population ageing rank 1317-2258 (outside) .69-.755. onTopic strict: only Germany passes ("germany" required) | S1 (+S3) | lexical/pool: a 7-term OR query, format-1 "semantic" is a cosine re-rank of the bm25 top 400 only, and the 0.70 gate removes the in-pool ones (.65-.68); a full dense scan would put Population ageing .755 and Japan .714 in the top 5 (misses.densescan.json, 180 ms on the MacBook for 115,813 int8 vectors) + keep rule ("Japan" is the first word, so only "germany" counts) |
"Lead-vector" (format-2's one vector per article) is not a cause here: wiki-vital5 is format 1 with a vector per chunk; the loss is that those vectors are only read for bm25 candidates.

## Arms vs the gate (>= 2/4 recovered AND kept changed on <= 2 of the 23 AND no health-source loss)
| arm | recovered (expected title kept) | other 23 changed | health losses | verdict |
|---|---|---|---|---|
| A0 base | 0/4 | - | - | - |
| A1 SEFIX-124 (gidf + F1 + F2 + F4) | **1/4**: b13 (Mosquito-borne disease x2) | **3**: b9 (+ a second ACT chunk), b12 (+ Economy of Brazil x2: the TOPICS27 Brazil gap, a gain), b16 (+ Mount Kenya) | 0 | **NOT A FIX** (clauses 1 and 2) |
| A1d F4 alone | identical to A1 (27/27) | same | 0 | not a fix |
| D1 rewrite on A0 (diagnostic) | 0/4 | n/a | n/a | b13 empty; b15 History of Japan only (Kyoto in raw .782/.751, compression 405->139 drops it); b19 still the table; b20 raw = Hiroshima Prefecture only |
| D1 rewrite on A1 (diagnostic) | 1/4 (b13: Zika, Rift Valley, Mosquito-borne disease, West Nile) | n/a | n/a | b15/b19/b20 as on A0 |
gidf, F1, F2 are inert on this kit by construction (they act on format-2 / Stack Exchange packs; wiki-vital5 is format 1), so SEFIX-124 = F4 here. F4 fired on b9 b12 b13 b16 b20 (on b20 it keeps Population decline, not an expected title). The rewrite does not help: the topic phrases already reach the search unchanged, and the question words only add bm25 noise.

## Prediction vs result
b13 keep rule: hit. b15 compress + keep rule: hit. b19 instant table: hit (plus a second table, facts-electricity, not predicted). b20 pool + gate + keep rule: hit. A1 1/4, 0-3 changed, FAIL: hit (3 changed). D1: rewrite recovers b15: **miss** (compression still drops Kyoto); b20 maybe: miss (worse); b13 unchanged: hit.

## For the app maintainer note (reading)
His app holds every article these four topics need; it loses them in four places, and no single fix covers more than one. (1) b13 needs the proper-noun keep rule relaxed for a negated or secondary name ("why HIV isn't one of them"): with F4 (a source dropped only for lacking the proper noun is kept if it holds another question term) Mosquito-borne disease comes back, at the cost of 3 extra-source changes on other topics (one of them the wanted Economy of Brazil for b12). (2) b15 needs compression not to drop the article the topic names: the Kyoto chunks are the best by cosine (.796) but score 0.41 of the period articles in the word-overlap compressor; pinning chunks whose title is the topic's subject (the engine already pins named identifiers) would keep them. (3) b19 is a product choice: the emergency-number and electricity tables answer instantly and skip retrieval, so a three-part travel topic gets one part; either split the topic or let a table answer be followed by retrieval for the rest. (4) b20 needs a real dense search over format-1 chunk vectors (today only the bm25 top 400 are re-ranked, and a 7-term topic phrase puts Japan/Population ageing at rank 800-2200), plus a gate below 0.70 for format-1 comparisons (the in-pool Japan/Germany/Population density chunks score .65-.68). A question-form rewrite of the topic strings does not help any of the four. Short of engine work: swap b19 and b20, keep b13 and b15 only if F4 and a subject pin ship.

## Caveats
Bench engine (K1 litepacks tree), not the native Kotlin pipeline (NATIVE-PARITY: KB-only retrieval differs); lexical detector (no mmBERT); deterministic replay, so counts are item counts; "recovered" = an expected title kept, not answer quality (no generation, no judge). The dense-scan cost is the MacBook's (single JS thread); phone unpriced. Not run: a subject-pin compression arm and a full dense-scan / lower-floor arm (diagnosed by the probe only, not replayed, no patch written).
