# PACKSHAPE: reshape boar-factbook into short self-contained sentences (2026-10-23): LEVER-CANDIDATE (at the bar)

**Leitura para o r4to (PT-BR):**
1. Sim, no factbook: reescrever as linhas de tabela como frases curtas ("Kyrgyzstan's capital is Bishkek.", um chunk por grupo de campos) faz o fato certo chegar ao modelo **15 de 20 vezes, contra 7**. O artigo certo chega 18/20, contra 8.
2. O 1.7B acerta **10 de 20, contra 5** (0.25 -> 0.50). Quando o fato é entregue, acerta 9/15 = 0.60, contra 4/7 antes. Os dois números caem exatamente na barra congelada: LEVER-CANDIDATE, mas no limite, com 1 seed e CI de -0.05 a +0.50.
3. Não quebrou nada: o MAIN fica em 42 fatos (0 perdidos, 0 perdas de saúde), os outros 120 self-tests não mudam (own article 74 = 74) e a fatia do factbook no MAIN sobe só de 0.5 para 2.3 % dos slots.
4. Custo: o pack passa de 11.8 para 23.5 MB (+98 %, quase tudo vetores de 32 mil chunks pequenos, contra 10.5 mil). O build leva 3 s mais 181 s de vetores no MacBook, e 0 LLM. O shaper é 1 arquivo Python de regras.
5. Para os outros packs de tópico: o factbook é o caso fácil, porque é tabela estruturada. firstaid e medlineplus são prosa, e precisam de regras próprias (só estrutura, sem mudar o texto médico). Estimativa: cerca de meio dia de agente por formato, mais um gate 0-LLM (~30 min de replay) e 20 chamadas Haiku por pack. Antes de virar default, falta confirmar com uma 2ª seed (ou Opus), porque o resultado está em cima da barra.

Criterion: PACKSHAPE-criterion.md sha256 `89f565ca53a9abdb29781988432096801a2751002ade83cc52fca9a78bc44aca` (frozen before any build or replay, not edited). Frozen tools: tools/shape.py c6bd2914, tools/fbread.py e02aff72 (tools/FROZEN.sha256, verified after the run). Ledger: Haiku 20 of 60 (A only), Opus 0, paid 0, phone 0, generation 20 (mini).

## The 10-chunk diagnosis (original pack, 20 self-tests, 58 target facts; tools/diagnose.py, target_chunks.py)
| # | chunk (item) | what the model got | why |
|---|---|---|---|
| 1 | Kyrgyzstan Key facts (001: capital, population) | never in raw/kept; answered "7.5 million" from a vital5 lead | the Key facts block = 19 rows, 146 words, 28 numbers in one chunk, and it starts "Key facts:" (the engine skips it as lead). Its vector is an average of 19 topics |
| 2 | Malta Key facts (002) | not delivered; answer wrong-confident | same: 16 rows in one chunk; travel-se and simplewiki "Malta (island)" win the slots |
| 3 | Bhutan Key facts (004) | not delivered | same (137 words, 16 rows) |
| 4 | Paraguay Key facts (007, currency) | two other Paraguay chunks kept, this one not; invented "boliviano" | currency is row 12 of 17 in an untitled block |
| 5 | Paraguay Energy (007, hydro 99.4 %) | kept, read right | 13 rows / 27 numbers around 1 fact (Electricity, Coal, Petroleum) |
| 6 | Paraguay Economy (007, exports) | kept, read right | 10 rows; imports series repeated 3x |
| 7 | Bahrain Energy (009, "output per person") | kept; answered "554.2 million Btu" | label confusion: "Energy consumption per capita (Total energy consumption per capita 2023)" is the only "per capita" row it saw; the GDP per capita row sits in Key facts (not kept) |
| 8 | Bahrain Government, national symbols (009) | kept, useless | 4 rows of flag/anthem take a slot |
| 9 | Guatemala Natural hazards (015) | kept; answer half right | one row joins 4 facts ("volcanoes...; Caribbean coast...; volcanism: ... Santa Maria ...") |
| 10 | Montserrat Geography (016, 1997 Plymouth) | not kept (Geography rows kept instead); 1995/1997 conflated | the fact sits in row 9 of a 144-word coordinates/area block |
Summary: 25 of 58 target facts (43 %) sit in the Key facts chunk, which reached raw 0/20 and kept 2/20. The median target chunk has 137 words, 11.5 rows and 17 numbers. The rows never repeat the country name ("Capital: Bishkek"), and 12 of 58 target chunk bodies do not name the country at all. **Units are not the problem**: every value already carries its unit ("199,951 sq km"). The problem is many facts per chunk plus label-only rows.

## Shaping rules (frozen; criterion R1-R6)
Same text (the v3proto pack read read-only; 261 entries, page_id, url, CC0 licence, attribution, aliases). R1 the lead = a one-line summary from the Key facts fields. R2 Key facts become 4 groups. R3 one chunk per Factbook field, with fields under 12 words merged (at most 3 fields, 60 words). R4 one line becomes "<Country>'s <label> is <value>.", and a yearly series becomes one sentence. R5 Background sentences without the name get "<Country>: ". R6 section heading "<Country>: <group>", at most 120 words and 950 chars per chunk. No new facts: tools/check_facts.py found 0 articles with a new number and 0 new words. The R6 part numbers "(2)" are excluded as labels. Pipeline check: the unshaped text through the same builder reproduces the v3proto chunks 10,543/10,543, plus articles, meta and redirects identical.

## Before/after (examples.json)
- Kyrgyzstan, 146 -> 38 words. Before: "Key facts:\nOfficial name: Kyrgyz Republic\nCapital: Bishkek\n...19 rows". After (section "Kyrgyzstan: capital, population and area"): "Kyrgyzstan's official name is Kyrgyz Republic. Kyrgyzstan's capital is Bishkek. Kyrgyzstan's time zone is UTC+6. ... Kyrgyzstan's population is 6,219,751 (2025 est.)."
- Paraguay, 116 -> 28 words. Before: an Energy block with 13 rows (Electricity x5, generation x2, Coal x3, Petroleum x2, per capita). After ("Paraguay: Electricity generation sources"): "Paraguay's electricity generation sources (hydroelectricity) are 99.4% of total installed capacity (2023 est.). ... (biomass and waste) are 0.5% ..."
- Bahrain, 52 -> 11 words. Before: 4 natural gas rows plus "Energy consumption per capita (Total energy consumption per capita 2023): 554.202 million Btu/person (2023 est.)". After ("Bahrain: Energy consumption per capita"): "Bahrain's energy consumption per capita was 554.202 million Btu/person (2023 est.)."

## Pack and build
| | original (v3proto 4ce447e8) | shaped (981f7b4b) |
|---|---|---|
| bytes | 11,829,248 | 23,461,888 (+98 %; text part 14.46 MB, chunk_vecs 12.44 MB) |
| chunks | 10,543 | 32,056 (median 32 words, max 120) |
| build | - | builder 3 s (MacBook, metal) + chunk_vecs sidecar 181 s (177 chunks/s) |
File: kiln-local/shape-packs/shaped/boar-factbook.sqlite (inputs in-shaped/, provenance.json, logs/). The builder is the mini's build-wiki-pack.mjs 885d7913 with the wt/packcond libs. Not in shared-data, not published.

## Stage 1 (0 LLM; MacBook replays on rs-SEFIX read-only, SEFIX-124 env; identity BASE vs NOWIKI K13: MAIN 97/97, self-tests 140/140 kept ids)
| metric | BASE (K13) | SHAPED |
|---|---|---|
| ST20 own article in raw | 5 | 8 |
| ST20 own article kept | 8 | **18** |
| ST20 own fact chunk kept (primary) | 7 | **15** (+8: gained 001 002 004 005 006 009 010 014 017, lost 007) |
| ST20 fact chunk, loose rule | 7 | 14 |
| ST20 quotes delivered | 11 / 58 | 27 / 58 |
| other 120 self-tests own article kept | 74 | 74 (per pack identical) |
| self-test health losses | - | 0 |
| MAIN chunk-level /92 | 42 (cm 14, v0.1 28) | **42** (0 lost, 0 gained) |
| MAIN kept-set changes /97 | - | 5 (lan-exp-002, -003, -005, lan-cmp-003, vit-sci-002) |
| MAIN factbook share of kept slots | 2/397 (0.5 %) | 9/400 (2.3 %) |
| MAIN health losses (11 items) | - | 0 |
**Gate: (a) +8 >= +5 PASS, (b) 42 >= 41 PASS, (c) 0 health losses PASS.**

## Stage 2 (20 factbook items, SHAPED kit, Qwen3-1.7B Succinct seed 42, mini job pshape-on-s42 under the kiln slot lock; Haiku 5.5-low A only, PACKPROOF prompt)
Live kept lists = SHAPED replay 20/20.
| | BASE (PACKPROOF ON) | SHAPED |
|---|---|---|
| correct-any | 5/20 (0.25; A-only also 5) | **10/20 (0.50)**; delta +0.25 (CI -0.05..+0.50) |
| read right when the fact chunk is delivered | 4/7 (0.57) | **9/15 (0.60)** |
| labels CWS / CFM / WW / WC | 4 / 1 / 5 / 10 | 10 / 0 / 4 / 6 |
| Not-found banner | 6 | 7 |
Item flips: wrong to right on 001, 005, 006, 009, 014, 016, 019. Right to wrong on 010 (it was correct from memory before) and 013 (CWS became WRONG_WARNED with the fact delivered). 002, 004 and 017 got the fact and still answered wrong.
**Decision (frozen rule): LEVER-CANDIDATE.** Correct-any +5 meets the >= +5 bar exactly, and read-right 0.60 meets the >= 0.6 bar exactly.

## Predictions
P1 fact 7 -> 11: MISS (15, better). P2 kept 8 -> 11: MISS (18). P3 MAIN 42 +-1 and share up: HIT. P4 0 health: HIT. P5 correct 0.40 / read 0.65: MISS (0.50 / 0.60). P6 size +60 to 120 % and < 10 min: HIT (+98 %, 3 min).

## Caveats
- One seed. Haiku A-only labels (the BASE labels had A/B rechecks, but the A-only base is also 5/20). Self-tests are agent-written from this pack's text (dev, favours retrieval).
- Both decision numbers sit exactly on the bar: the result is thin, so confirm with seed 43 or Opus before adopting.
- BASE ON ran on the MacBook and SHAPED on the mini. Kept lists are host-identical (PACKPROOF ident5), but answer bytes differ by host.
- Shaped answers took about 15 s on the mini while another job held slot gen1, against 6.9 s for BASE on the MacBook, even though the shaped context is smaller (2,377 vs 2,705 chars p50). This is not a latency measurement.
- Second target (boar-firstaid-en) was not run (time). It needs its own criterion addendum (structure only, keep "AI-reviewed, not clinically reviewed").

## Commands
```
python3 -I tools/diagnose.py; python3 -I tools/target_chunks.py
python3 -I tools/shape.py <workspace>/kiln-local/shape-packs/in-shaped; python3 -I tools/check_facts.py .../in-shaped
(builder in kiln-local/shape-packs/builder) node scripts/build-wiki-pack.mjs --out ../shaped/base.sqlite --manifest ../in-shaped/manifest.json --name "..." --shards ../in-shaped/factbook.jsonl
tsx arms/headpass-st/tools/mini/sidecar_embed.mini.mjs shaped/base.sqlite --out shaped/boar-factbook.sqlite --name boar-factbook-shaped
tools/run.sh main|st BASE|SHAPED; python3 -I tools/score.py          # -> packshape.json
python3 -I tools/mk_req.py; tools/run_mini.sh start|fetch; python3 -I tools/stage2.py prep; ONLY_A=1 node tools/label.mjs judge/units.json judge/labels.jsonl; python3 -I tools/stage2.py agg   # -> stage2.json
```

## Addendum 1 (coordinator request 16:3x): seed 43 confirmation. The criterion is unchanged; this addendum adds the pooled rule
Pooled rule (stated by the coordinator before the run): **pooled correct-any >= 0.45 and pooled read-right-when-delivered >= 0.55 keep the LEVER-CANDIDATE.** Recipe: the same 20 items and SHAPED kit, the stage-2 recipe with seed 43 (mini job pshape-on-s43, slot gen2, 16:29-16:34), Haiku 5.5-low call A, PACKPROOF prompt, 20 calls (cap 20). Files: gen/on-k13s43/, judge-s43/, stage2-s43.json; tools/run_mini_s43.sh, `PS_SEED=43 tools/stage2.py`. Live kept lists match the SHAPED replay on 20/20.
| | seed 42 | seed 43 | pooled (40) |
|---|---|---|---|
| correct-any | 10/20 (0.50) | 10/20 (0.50) | **20/40 = 0.50** (bar 0.45) |
| read right when delivered | 9/15 (0.60) | 10/15 (0.67) | **19/30 = 0.63** (bar 0.55) |
| labels CWS / WW / WC | 10 / 4 / 6 | 10 / 5 / 5 | |
The BASE stays the PACKPROOF seed-42 ON run: 5/20, and 4/7 when delivered. Only one base seed exists, so the pooled comparison is against a single-seed base.
**Verdict: LEVER-CANDIDATE kept** (0.50 >= 0.45, 0.63 >= 0.55). The two seeds agree item by item on most items. The CI on the seed-43 delta against the base is +0.25 (+0.00..+0.50).
Leitura (PT-BR): a 2ª seed repete o resultado: 10/20 certo de novo, e lê certo 10/15 quando o fato chega. O ganho do factbook reformatado não foi sorte de seed. Falta só a régua Opus, se o pack for virar default.
