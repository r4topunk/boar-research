# TOPICS27: the app maintainer's 27 RC1 Research Topics on wiki-vital5 + Qwen3-1.7B Detailed (bench engine)
Criterion: TOPICS27-criterion.md sha256 `c97bd9d7f30ecba384899f778a7b406dafa4f3dbf4d8e53284e24b3b0559a6da` (frozen before any run); splitter tools/split.py sha256 `b8a389a4...` (b8a389a41ce9bd7ccc21c3ed3b08ae8a00cfe1f0dcb857f2fcde4b42c1eadaa1), frozen with it.

## Stage 1 reading (written before stage 2)
1a (tools/titles.py -> aggregates/titles.json): every topic is PRESENT; every required group has a title in wiki-vital5 itself (the corpus is not needed for any topic). wiki-vital5 holds intro chunks only (<= 3 chunks per article).
1b replay (replay/t27.replay.jsonl, 59 s incl. first-run seed indexing): raw k = 4; on 24/27 an expected/anchor article is kept. Exceptions: b13 kept list empty (raw on-topic: Mosquito-borne disease x2), b19 never retrieves (engine answers deterministically, reason answer:emergency-numbers), b20 raw off-topic (Hiroshima Prefecture, Population decline, Lost Decades, Kanto region) and kept empty. Partial: b12 keeps Russia + Economy of Russia only (Economy of Brazil in raw, dropped); b11 keeps Polar bear + Kodiak bear + Bear (no Grizzly/Brown bear); b15 keeps Heian period + History of Japan (Kyoto in raw, dropped); context compression hits q1 (433 -> 184 tokens), q4, b10, b15, b18 (127 tokens).
Title reading of the b* top-6 (wide pool): on-topic b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b14 b16 b17 b18 b21; partly b11 (polar bear only), b12 (Brazil only as economy), b13 (diseases, no Mosquito / HIV), b15 (Kyoto present but the kept two are period articles); off-topic b20; b19 not retrievable (deterministic path).

## Result (frozen rule): KEEP 7, FIX-PACK 0, SWAP 20
Commands: stage 1a `python3 -I tools/titles.py`; stage 1b replay-sweep.ts (exact command in the criterion; out replay/t27.replay.jsonl); generation `tools/run_gen.sh` (mini, job t27-detailed-s42, K1 litepacks tree unpatched, kit wiki-vital5 sha d3b87d56 checked by the adapter, persona detailed, seed 42, 27/27 rows, 0 errors, run 263 s, peak RSS 2.67 GB); `python3 -I tools/prep.py` (split + dumped contexts); `node tools/audit.mjs judge/prep.json judge/audit.jsonl` (Haiku 5.5-low); `python3 -I tools/agg.py` -> aggregates/{topics27,summary,titles}.json.
- Titles: q* expect titles present 12/15 (missing: Spring, Epistaxis, Emergency bleeding control; each q* topic has >= 1); PRESENT 27/27, all in wiki-vital5 itself. b* anchors present in every required group (b19 via AC power plugs and sockets).
- Live kept: an expected/anchor article reaches the context on 23/27 (miss b13 kept empty, b15 Kyoto dropped for Heian period + History of Japan, b19 deterministic emergency table, b20 off-topic raw and kept empty); in raw 25/27. Replay vs live kept titles identical 25/27 (b12, b21 differ in the last slot).
- Answers: mean 330 words, 385 sentences; Haiku: UNSUPPORTED 180 (0.468), PARTIAL 150, SUPPORTED 55; 98 unsupported/partial sentences carry an invented specific; 0-LLM numbers absent from the context 39. 11/27 answers open with the "Not found in this phone's offline library ... may be wrong" banner, 9 of them although on-topic chunks were kept (q8 b1 b3 b4 b5 b8 b11 b16 b18).
- Haiku 298 invocations (cap 300): 290 per sentence (q1..b14#2) + 8 batched calls (b14..b21 remainder, 95 sentences); 0 missing, 0 retries needed.

| key | area | titles present | in raw | in kept | sentences | unsupported (+partial) | invented | verdict | reason |
|---|---|---|---|---|---|---|---|---|---|
| q1 | Science | 5/6 | yes | yes | 17 | 3 (+7) | 3 | KEEP (watch) | Season + Axial tilt kept; one false specific (Mars tilt "about 2 degrees") |
| q2 | Health | 2/2 | yes | yes | 16 | 7 (+3) | 4 | SWAP | 0.44 unsupported; COVID dates/agents from memory |
| q4 | First aid | 1/3 | yes | yes | 14 | 6 (+5) | 0 | KEEP (watch) | Nosebleed kept; unsupported advice lines but no invented specific |
| q7 | Climate | 2/2 | yes | yes | 14 | 2 (+7) | 2 | KEEP (watch) | Greenhouse gas/effect kept; methane x25 not in context |
| q8 | Weather | 1/1 | yes | yes | 15 | 7 (+7) | 3 | SWAP | 4 Monsoon chunks kept but banner says not found; crops/months from memory |
| q9 | Earth science | 1/1 | yes | yes | 16 | 4 (+9) | 7 | KEEP (watch) | Plate tectonics kept; 7 partial/unsup specifics |
| b1 | History of science | 4/4 | yes | yes | 18 | 4 (+12) | 1 | KEEP (watch) | Darwin + Wallace kept |
| b2 | Health | 7/8 | yes | yes | 15 | 10 (+5) | 7 | SWAP | 0.67 unsupported; smallpox-vaccine history invented ("19th century, attenuated") |
| b3 | Biology | 2/3 | yes | yes | 18 | 10 (+7) | 12 | SWAP | step-by-step biochemistry not in the intro chunks |
| b4 | History | 2/2 | yes | yes | 15 | 6 (+9) | 4 | SWAP | 0.40; two-topic comparison over 2 short intros |
| b5 | History | 2/3 | yes | yes | 17 | 2 (+11) | 2 | KEEP (watch) | Fall of the WRE kept |
| b6 | Space | 3/3 | yes | yes | 17 | 5 (+7) | 0 | KEEP | Black hole + Event horizon kept, no invented specific |
| b7 | People | 2/3 | yes | yes | 13 | 6 (+5) | 7 | SWAP | invented title "L'homme d'Etat"; Napoleon III chunk crowds |
| b8 | Medicine | 1/2 | yes | yes | 15 | 8 (+5) | 1 | SWAP | 0.53 unsupported |
| b9 | Geography | 2/2 | yes | yes | 15 | 9 (+6) | 4 | SWAP | 0.60; Washington DC analogies from memory |
| b10 | Myths | 1/1 | yes | yes | 14 | 6 (+7) | 2 | SWAP | Moon myth and length not in the kept intro |
| b11 | Animals | 3/3 | yes | yes | 14 | 7 (+7) | 2 | SWAP | Grizzly/Brown bear never kept (Kodiak bear instead) |
| b12 | Geography | 4/4 | yes | yes (Russia only) | 14 | 10 (+3) | 9 | SWAP | Brazil articles dropped; Brazil figures invented |
| b13 | Health | 2/2 | yes | no | 10 | 10 (+0) | 6 | SWAP | kept list empty although Mosquito-borne disease is in raw |
| b14 | Health | 3/4 | yes | yes | 13 | 5 (+6) | 1 | SWAP | 0.38 (batched audit); dose guidance (minutes/week) not in the chunks |
| b15 | Travel | 1/2 | yes | no | 14 | 6 (+5) | 5 | SWAP | Kyoto dropped; Nara temple misattributed to Kyoto |
| b16 | Earth science | 1/2 | yes | yes | 13 | 9 (+4) | 5 | SWAP | 0.69 (batched); geology beyond the intro |
| b17 | History | 2/2 | yes | yes | 15 | 7 (+6) | 1 | SWAP | 0.47 (batched); Solidarity-as-cause of the Wall is wrong |
| b18 | Animals | 1/1 | yes | yes | 13 | 8 (+4) | 4 | SWAP | one 127-token Cheetah chunk for a 3-5 paragraph answer |
| b19 | Travel | 1/3 | no | no | 2 | 1 (+0) | 1 | SWAP | routed to the emergency-number table; plugs/voltage never answered |
| b20 | Geography | 4/7 | no | no | 15 | 15 (+0) | 4 | SWAP | off-topic raw, no context; Germany density ~80/km2 invented |
| b21 | Health | 1/3 | yes | yes | 13 | 7 (+3) | 1 | SWAP | 0.54 (batched); ADE mechanism not in the intro |

## Prediction vs result
PRESENT 22-25 -> 27 (missed high: Vital level 5 holds every topic); IN KEPT 17-22 -> 23 (just above); unsupported share 0.25-0.40 -> 0.468 (missed high); SWAP 3-7 -> 20, FIX-PACK 3-6 -> 0 (missed: the frozen rule sends retrieval misses to SWAP via the answer clause first, and the 1/3 + one-invented-specific bar is met by most Detailed answers).

## Swap list for the app maintainer (reading, not the rule)
The frozen rule flags 20 of 27, which mostly measures the Detailed persona (3-5 paragraphs over 1-3 short Vital intro chunks makes the 1.7B fill from memory), not bad topics. Ranked by cause:
1. Swap now (structural, the topic does not reach the model): b19 (the router answers it with the emergency table only; plugs/voltage never searched), b20 (Japan/Germany: raw is Hiroshima / Lost Decades, empty context, invented densities), b13 (mosquito/HIV: kept list empty even though Mosquito-borne disease ranks in raw), b12 (Brazil vs Russia: Brazil chunks dropped, Brazil figures invented), b15 (Kyoto: the Kyoto article is dropped for Heian period, and a Nara temple is placed in Kyoto).
2. Swap or narrow for 1.5-1.7B (process/step topics the intro chunks do not cover, heavy invention): b3 (photosynthesis step by step, 12 invented specifics), b2 (vaccines smallpox to mRNA), b7 (Napoleon), b9 (Canberra), b16 (Kilimanjaro), b18 (cheetah, a single 127-token chunk).
3. Keep (context delivered, few invented specifics): q1 q4 q7 q9 b1 b5 b6. The remaining ones (q2 q8 b4 b8 b10 b11 b14 b17 b21) sit near the bar: keep for the 4B, keep for the 1.7B only with the Succinct style.
Also for the app maintainer: 9 answers show the "Not found in this phone's offline library" banner even though on-topic chunks were kept (q8 Monsoon x4, b1, b3, b4, b5, b8, b11, b16, b18): in the bench engine the weak-sources grounding check fires on long Detailed answers; check whether the native app does the same.

## Caveats
Bench engine (K1 litepacks tree), not the app maintainer's native Kotlin pipeline (NATIVE-PARITY found KB-only retrieval differs); essential corpus (300 + 1000 + 4000 articles) may differ from RC1's built-in corpus (no topic needed it). Haiku support audit, not a correctness judge: UNSUPPORTED means "not in the context", the 1.7B is often right from memory; the 8 batched calls (b14..b21) label more strictly than the per-sentence calls (unsupported 0.61 vs 0.42), so b14 b16 b17 b18 b21 verdicts are softer than they look. One seed, EN only (PT not run), 1.7B only (4B and 1.5B not run), Detailed only.
Addendum 1 (prep, not in the criterion text): for b13, b19 and b20 the model received no context block, so their sentences were audited against "(no source chunks were given to the model)"; b19's answer is the app's deterministic emergency table (correct numbers, but off the plugs/voltage part of the topic).
