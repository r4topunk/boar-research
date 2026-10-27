# DEEPMODE: the app's Deep Research mode (multi-pass) on Qwen3-1.7B, PARA135 protocol

**Leitura para r4to (PT-BR):**
1. O Deep Research do 1.7B é um interruptor (alwaysComplete): decompõe em 3 subperguntas, busca k 6 para cada (600 tokens), escreve 3 parágrafos curtos e sintetiza (2048 tokens) sem ver as fontes.
2. Busca melhor um pouco: tópicos com artigo esperado lido 25/27 vs 23/27 no rápido (+b13, b15, b20; perde b7 Napoleão).
3. Mas a resposta fica 3-4x mais longa (≈1.400-1.600 tokens) e o suporte não melhora: 0,444 sem suporte (Detailed 0,468, Succinct 0,283); a parte depois do 5º parágrafo é a metade sem suporte.
4. O juiz pune: U 0,174 vs Detailed 0,224 (−0,050, IC −0,087…−0,015) e vs Succinct 0,263 (−0,089); erros confiantes 57/100 vs 53 e 27; 5,6x mais lento no set A (58 s vs 10 s), 2,6x no set B (44 s vs 17 s).
5. Recomendação: não oferecer Deep Research com o 1.7B como modo geral (ou esconder/rotular "lento, experimental"); nem como fallback quando o rápido não acha nada (−0,016 nesse subgrupo, n 10, quase todo FACTS).

Criterion: DEEPMODE-criterion.md sha256 `cad5441f97e4c81c978ac8a4500e75fc85e0cd05e9dfd02786e8d738150c6e95`, frozen 2026-10-23 before any generation or judge call (never edited).
Haiku 5.5-low 532 calls (set A audit 430 of cap 450, 0 retries, 0 missing; set B judge 102), Opus 0, paid 0, phone 0. Calls ledger: CALLS.md.

## What the mode is (from the code, written into the criterion before the runs)
- Trigger: a settings flag, not a second pass. The app's Deep Research switch = AnswerSettings.alwaysComplete (boar-app settings.ts:499; the native app's toggle runs DeepResearch.kt, a golden-tested port with the same prompts and a 2048-token write-up cap). The bench engine also has deepen() after a fast answer ("offer-deep:multipass"), which runs the same multipass and ignores the reused sources; its cost is fast + deep (below).
- planAnswer: no deep model installed -> tier deep, mode multipass, retrieveK 6, thinking on (off here: --reasoning off), instant preview first.
- runDeepResearch (orchestrator.ts): (1) decompose, "You plan research.", 2-3 sub-questions, 150 tokens, temp 0.4; (2) for each sub-question: plain retrieve(sub, 6) (no K1 head pass / dense append / grounding guard), compress to 600 tokens, on-topic filter, a "short paragraph" sub-answer with citations, 300 tokens, temp 0.6; (3) synthesis from the sub-answers only (the model sees no source chunk here), nPredict = Max Output Tokens (2048), temp 0.6. Persona system prompt in every stage, style reminder never. Health-emergency questions stay single pass (1 of 78 here: dng-005).
- Run: Detailed persona (be0e6710), max tokens 2048, mini, K1 litepacks tree unpatched (only the adapter cap sed), seed 42. Set A wiki-vital5 + essential, set B K1 kit + essential.

## Commands
`python3 -I tools/mk_req.py`; `tools/run_gen.sh a` and `tools/run_gen.sh b` (mini jobs dm-a-deep-s42 27/27 in 28 min, dm-b-deep-s42 51/51 in 34 min, 0 errors); `python3 -I tools/prep_a.py`; `node tools/audit_a.mjs judge/prep.json judge/audit.jsonl`; `tools/judge_b.sh`; `python3 -I tools/agg_a.py`, `python3 -I tools/agg_b.py`, `python3 -I tools/agg_add1.py` -> aggregates/setA.json, setB.json, addendum1.json.
Post-freeze tool edits (aggregation only): retrieval ms for multipass = sum of the trace's retrieve events (the engine sets no timing.retrievalMs on that path); bool casts for JSON.

## Set A: 27 Research Topics (wiki-vital5)
| | fast Succinct (TOPICS27-S) | fast Detailed (TOPICS27) | DEEP |
|---|---|---|---|
| HIT (expected/anchor title read) | 23/27 | 23/27 | **25/27** (+b13 b15 b20, -b7) |
| chunks read p50 / items with none | 3 / 3 | 3 / 3 | 5 / 1 (b19 = deterministic table) |
| sentences / words p50 | 60 / 44 | 385 / 336 | 852 / 758 |
| unsupported share | 0.283 | 0.468 (0.447 all per-sentence) | **0.444** (sample 430 of 852, stratified) |
| partial share | - | 0.39 | 0.412 |
| invented specifics | 7 | 98 | 82 in sample, 162.5 est. (0.19 per sentence vs 0.25) |
| numbers absent from context (0 LLM) | 10 | 39 | 43 |
| banner "Not found..." | 13 | 11 | 0 (multipass has no weak-source banner) |
| output tokens p50 / at cap | 48 | 421 (cap 512) | 1603 / 2 at 2048 |
| retrieval ms p50 / total ms p50 | 44 / 3348 | 45 / 10310 | 177 / **57890** (deepen path fast + deep 68658) |

By paragraph position (DEEP, Wilson 95 %): pos 1 0.21 (0.10-0.38, 57 sent.), 2 0.24, 3 0.35, 4 0.54, 5 0.53, 6+ 0.50 (0.44-0.56, 470 sent. = 55 % of all, 59 % of invented). Detailed: pos 1 0.30, 2 0.55, 3 0.53, 4 0.31. DEEP opens better supported than Detailed and then decays to the Detailed level; the text past paragraph 5 is the bulk. Answers narrate the pipeline ("Perspective 1 emphasizes...").
Hit changes: b13 (Mosquito-borne disease, Malaria, Dengue read; fast kept nothing), b15 (Kyoto read), b20 (Population ageing/decline: an anchor-group title, still not Japan/Germany); b7 lost (Napoleon question read only "Fall of the Western Roman Empire").

## Set B: 51 CV5 dev ids (K1 kit), Haiku judge.v1-low N 4 both orders vs the bench v0.1 references
| | S17 fast Succinct | D17 fast Detailed | DEEP |
|---|---|---|---|
| U floor-adj (CI) | 0.263 (0.201-0.333) | 0.224 (0.165-0.293) | **0.174 (0.120-0.236)** |
| U raw / win-rate | 0.419 / 0.020 | 0.387 / 0.020 | 0.349 / 0.000 |
| correct shown /100 / confident errors /100 | 27.5 / 27.5 | 17.6 / 52.9 | 13.7 / **56.9** |
| chunk-level delivered facts (44 keyed) | 17 | 17 | 17 (+4 -4) |
| output tokens p50 / at cap | 41 | 392 | 1372 / 0 |
| retrieval ms p50 / total ms p50 | 158 / 4340 | 178 / 16929 | 375 / **44076** (deepen fast + deep 61512) |
| route | 42 fast + 9 instant | same | 42 multipass + 8 FACTS instant + 1 health single |

Paired: DEEP - D17 dU **-0.050 (-0.087...-0.015)**, better/tie/worse 15/11/25; DEEP - S17 **-0.089 (-0.131...-0.048)**, 10/8/33; (D17 - S17 -0.038 for reference).
Chunk-level: DEEP gains vit-cry-002, vit-cry-010, vit-sci-001, vit-hlt-003 and loses lan-rsn-001, lan-ref-002, lan-rsn-003, lan-exp-005 (the sub-questions drift off the question's named article). Fast context = PARA135 p1 dumps; its kept titles equal D17's on 50/51 (dng-005 differs).
Subgroup, fast kept nothing (10 ids): DEEP - D17 -0.016 (2/2/6); but 8 of the 10 are FACTS instant answers with identical text in both arms (their per-item judge differences, -0.33 to +0.5, are pure judge noise); on the 2 real items: vit-hum-003 +0.50, vit-sci-001 -1.00. Rest (41): -0.056 (13/9/19).

## Predictions (frozen)
| | prediction | result | |
|---|---|---|---|
| P1 | set A hit >= fast + 2 | 25 vs 23 | HIT (net +2: 3 gained, 1 lost) |
| P2 | set A unsupported strictly between 0.283 and 0.468 | 0.444 | HIT (barely; = Detailed's 0.447 all-per-sentence figure) |
| P3 | U(DEEP) - U(D17) >= +0.02 | -0.050 (CI excludes 0) | MISS |
| P4 | time >= 2x fast Detailed on both sets | 5.6x (A, vs a 512-cap Detailed) / 2.6x (B) | HIT |

Reading against the stated rule: U(DEEP) < U(D17) - 0.02 -> "hide or relabel Deep Research for the 1.7B (slower and not better)". The fallback reading (wins only where fast kept nothing) is not supported: that subgroup is -0.016 and has 2 non-identical items.

## Addendum 1 (coordinator request after the freeze; 0 LLM, 0 extra Haiku; tools/agg_add1.py -> aggregates/addendum1.json)
(a) Sub-queries. On-topic = shares >= 1 content word (5-letter prefix, not a stopword) with the question, or names an expected title (set A).
| | sub-questions | on-topic | Jaccard mean | sub-questions reading 0 chunks | chunks first introduced by sub-q 1 / by sub-q 2-3 | items whose chunks all come from sub-q 2-3 |
|---|---|---|---|---|---|---|
| A | 78 (3 per item, 26 items) | 75 (0.96) | 0.23 | 13 (17 %) | 74 / 61 (45 % extra) | 2 |
| B | 121 (39x3, 1x2, 2x1) | 108 (0.89) | 0.31 | 38 (31 %) | 97 / 82 (46 % extra) | 3 |
The lexical rule is lenient: most "on-topic" sub-questions are generic angles ("What are the practical implications...", "What factors influence...") that keep one question word; the off-topic ones lose the subject entirely ("How did the community and developers respond to the incident?"). The extra passes do add chunks (45 % of everything read), but a third of set B sub-questions read nothing after the on-topic filter, and the net delivered facts are unchanged (17 -> 17). Consistent with the planning prior: the 1.7B decomposes into template angles, not into the sub-facts the question needs.
(b) Matched length. The closest PARA135 arm by output tokens p50 is p5 on both sets (552 / 512 tokens vs DEEP 1603 / 1372): no PARA135 arm reaches DEEP's length, so length is only partly controlled. Against p5: set A unsupported 0.444 vs 0.519, invented per sentence 0.19 vs 0.27 (DEEP better per sentence at 3x the length); set B U 0.174 vs 0.218, dU -0.044 (-0.076...-0.013), 10/15/26, CE/100 56.9 vs 49.0 (DEEP worse). Reading: per sentence the multipass text is no worse supported than a long Detailed answer, but the judge scores the whole answer lower, so DEEP's loss is not only a length effect.

## Caveats
One seed (42), stage temperatures 0.4-0.6 (SEEDVAR rule: one-seed deltas < 0.05 on V-para are noise; here -0.050 on dev with a CI excluding 0, still one seed). Haiku audit (UNSUPPORTED = not in the chunks read, not false; DEEP's audit context is every chunk the research stages read although the synthesis sees only the sub-answers, which favours DEEP) and Haiku judge (compresses gaps, over-calls CE on long answers: DEEP is the longest arm). The 8 FACTS items with identical text were re-judged (no row reuse), so they carry judge noise into both comparisons. Bench engine K1 tree, not the native app (same prompts per its golden test; retrieval and guards differ); multipass skips the K1 head pass / dense append, the grounding guard and the weak-source banner. Max tokens 2048 vs 512 (TOPICS27) / 1024 (D17) / 512 (S17). Dev sets (CV5 51 of v0.1; the 27 topics are public). Not run: the 4B or 1.5B, thinking on, a second seed, PT, the phone.
