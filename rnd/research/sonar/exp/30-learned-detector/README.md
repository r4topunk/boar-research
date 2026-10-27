# exp-30: learned multilingual emergency detector + crypto-source leak fix (Sonar, 2026-10-03)

TL;DR:
- **Why:** the blind health-fresh1 confirm of health9 failed on routing. Only 31/72 danger items reached the health route, so the lexical detector doesn't generalize. Here: a learned detector, trained on synthetic PT/EN/ES data and **evaluated on dev only**. I saw no blind items.
- **Result (dev, 903 labelled non-blind messages, threshold fixed on synthetic val, NOT on dev):**

  | detector | extra RAM | recall | false fires | hard-negative fires | night set (realistic) |
  |---|---|---|---|---|---|
  | lexical health9 (in-sample on most of dev!) | 0 | 259/413 (63%) | 35/490 | 15/57 | 37/78, FF 12/130 |
  | **(a) bge-small-en head** (the app's embedder) | ~0 (3 KB head) | 281/413 (68%) | 8/490 | 1/57 | 59/78, FF 0/130 |
  | (a') multilingual-e5-small head | ~120 MB fp16 / ~40 MB pruned int8 | **342/413 (83%)** | **6/490** | 1/57 | **76/78**, FF 0/130 |
  | **(b) mmBERT-small fine-tune** (thr 0.5) | ~60 MB int8 vocab-pruned (est.) | **393/413 (95%)** | 13/490 | 0/57 | **77/78**, FF 0/130 |

  The learned heads beat the lexical detector on both axes at once. At the lexical detector's own false-fire count (35/490, threshold read off dev, so optimistic): bge 369/413, e5 375/413.
- **Realistic messages only** (dev without FirstAidQA's textbook questions; 246 pos / 457 neg / 54 hard neg):

  | detector | recall | false fires | hard-negative fires |
  |---|---|---|---|
  | lexical | 144 | 15 | 12 |
  | bge head | 192 | 5 | 1 |
  | e5 head | 239 | 1 | 0 |
  | mmBERT (0.5) | 242 | 4 | 0 |
- **The English-only app embedder is the weak point for PT/ES.** Its synthetic-val AUC is 0.951 vs e5's 0.994; PT dev recall is 66/99 vs 96/99.
- **Crypto-source leak, fixed in `health10`** (dev-only arm on health9; `leak/health10-on-health9.patch`): a PT question whose translation collapses to a modifier ("child") no longer matches every source naming a child. Crypto sources shown on my own danger/travel repros: **7 → 0 per profile**. **Must stack with the routing fix** (see § Leak).

## Data (committed; reproducible)
- `LABELS.md`: provisional binary spec (emergency/first-aid incl. present hazards, how-to, emergency follow-ups, self-harm vs health_info / hard_negative / other). It will be re-mapped to Compass's spec when that lands.
- `data/synth-{en,pt,es}.jsonl`: **2,201 synthetic messages**, written by 3 Opus subagents from the spec alone (no file or web access; contamination guard in the prompt).
  - EN 734 / PT 747 / ES 720; ~50% positive across 58–69 conditions per language;
  - negatives: ~60% hard negatives (figurative, trivia, animal facts, cooking, crypto/tech, travel planning about future risks, topic switch);
  - 22–25% multi-turn; ~35% PT/ES without accents.
  - sha256: en 96d4dfb6…, pt 6e1cd3fe…, es 31f64eb2….
- `dev/pool.raw.json` (2b78ce3a…): **903 non-blind messages** from `build_dev_pool.py`: v0.1 public + safety 72, chat-slice v0 77 turns, night sets 208 (hm-fresh2/3/loc1, DEV since 2026-10-03), retrieval-v1 + vitalik58 164, the exp-29 parity strings 129, exp-29 repros 53, FirstAidQA 200 (CC BY 4.0, random sample, seed 30).
  - Excluded: blind/, veil, any *fresh* path, v1-/v2-/v02- ids.
- `dev/labels.sonar.jsonl` (ccb1ab88…): labelled by an Opus subagent against `LABELS.md`; 413 pos / 490 neg, 12 marked unsure; I spot-checked 30/30 OK.
  - **Caveat:** ES has only 9 positive dev items (my language heuristic); Compass's 300-item dev set is needed for a real ES number.
- **Lexical baseline** (`lexical.mts`): health9's health-route predicate (`isHealthQuestion || isHealthFollowUp || isCardEmergency`, answer.ts L693–696). It was tuned on most of this pool (v0.1, night, chat-v0, exp-29), so its dev numbers are **optimistic**. FirstAidQA is its only out-of-sample source (115/167).

## Models
- `embed_head.py`: frozen sentence embedder. Features = emb(last turn) ⊕ emb(all user turns joined); balanced logistic regression, C picked on synthetic val (85/15 split, stratified by language, seed 30).
- `ft_mmbert.py`: mmBERT-small sequence classifier, text = last turn, pair = earlier turns; 4 epochs, lr 3e-5, MPS; best epoch by synthetic-val AUC.
- `evaluate.py` operating points: (1) matched FP on dev (= lexical's 35/490); (2) synthetic-val threshold at FP 5%; (3) **synthetic-val threshold at the lexical dev FP rate** = the headline row (no dev label used to set it).

### Recall at fixed false-fire budgets (dev; threshold swept on dev)
| false fires (of 490) | 0 | 3 | 6 | 10 | 20 | 35 |
|---|---|---|---|---|---|---|
| bge-small-en head | 203 | 241 | 265 | 290 | 340 | 369 |
| e5-small head | 151 | 311 | 344 | 356 | 361 | 375 |
| mmBERT-small fine-tune | 0 | 340 | 357 | 380 | 394 | 401 |
| lexical health9 | – | – | – | – | – | 259 |

### Error read (e5 head at the headline threshold)
- **False fires (6):** 5 FirstAidQA prevention questions ("how can I prevent my child from swallowing dangerous objects?"), plus "não entendi, explica mais simples". The health route is harmless for the 5.
- **Misses:**
  - terse fragments ("escorpião no sapato", "exaustão por calor no trabalho", "high blood sugar and shaky diabetic");
  - a follow-up after a definitional first turn ("¿qué es la hipotermia?" → "¿y qué hago si le pasa a alguien?");
  - present hazards (lightning on open ground, "should we wait for a tsunami warning?");
  - textbook CPR/rescuer-technique items (FirstAidQA).
- Adding the precise lexical parts (card triggers + `isHealthFollowUp`) to e5: 342 → 344/413, FF unchanged. bge: 281 → 290/413, FF unchanged. **Recommended shape: learned OR card-trigger OR health-follow-up**; drop the broad regex, which carries 15/57 hard-negative fires.

### mmBERT notes
- Synthetic-val AUC by epoch: 0.991 / 0.996 / 0.997 / 0.997; dev AUC **0.990** (e5 head 0.979, bge head 0.971).
- **Over-confident:** synthetic-val negatives score ~0, so the synthetic-val threshold is 0.001 (dev FF 28/490, recall 397/413). Use thr 0.5 or temperature-scale it on Compass's dev set.
- **False fires at 0.001** are mostly label-boundary cases (16 FirstAidQA health-info, bare terms "hipoglicemia" / "cat scratch fever", an out-of-context "¿y qué hago si le pasa a alguien?").
  - The real ones: topic switches after a sting ("Escorpião picou meu filho → tell me a joke" 0.13, "→ scorpion's lifespan" 0.08) and Burj Khalifa/Baikal (0.13). All are below 0.5.
- **Misses:** 15/16 are textbook FirstAidQA items ("why maintain compression depth during CPR?"). The only realistic miss is "exaustão por calor no trabalho".

## Size / on-device (for Forge)
| encoder | params | of which embeddings | layers | vocab ids used by all 4,086 train+dev texts |
|---|---|---|---|---|
| bge-small-en-v1.5 (already in the app) | 33.4M | 11.7M | 12 | 5,451 |
| multilingual-e5-small | 117.7M | 96.0M (250k × 384) | 12 | 7,509 |
| mmBERT-small | 140.5M | 98.3M (256k × 384) | 22 | 8,555 |
- **Correction to the OSS scan:** "mmBERT-small ~70 MB int8" is wrong. Unpruned, it is ~140 MB int8. Pruning the vocabulary to PT/EN/ES (keep ~30–40k ids) gives ~42M + ~15M ≈ 57M params ≈ **~60 MB int8**. e5-small pruned the same way: ~21.6M + 15M ≈ **~37 MB int8**.
- mmBERT has 22 layers vs 12, so expect ~2× e5's latency per message (to measure).
- **Latency, measured** (M1 Pro, 1 CPU thread, fp32 torch, batch 1, 60 dev messages): bge-small 11.2 ms, e5-small 11.2 ms, **mmBERT-small 20.7 ms** per message. The phone is perhaps 3–5× slower (UNKNOWN; Forge to measure in ONNX/llama.cpp), and the cost is negligible next to retrieval (~3 s on moto).
- The (a) head adds ~0 RAM but needs the same embedding call the retrieval already makes.
  - The app embeds the query with bge-small at retrieval time, so the head is one 768→1 dot product, if routing can wait for that embedding.
  - The features use 2 embeddings (last turn + joined turns). A single-embedding variant is untested.
- UNKNOWN: whether the app's GGUF q8 bge-small embedding matches HF fp32 closely enough for a head trained on HF features. It needs a parity check before shipping.

## Leak: crypto sources on decline/model paths (`leak/`)
- **Repro (my own queries, both profiles, health9):** `leak-*`: 20 child/emergency PT/EN/ES; `leak2-*`: 20 with crypto-ambiguous words (gas, coin, chain, bridge, block, mining).
  - The crypto source appears only for PT questions whose `englishSearchTerms` collapses to `"child"`: "Meu bebê está com diarreia e vômito…", "A criança bebeu um pouco de água sanitária…".
  - In both, `onSubject` uses `onTopic("child", chunk)` and ERC-7401 "Parent-Governed NFTs" / ERC-6059 / ERC-998 pass. They are then shown under the 4B's model answer (`grounding:uncited-warning`) and under the 1.5B's decline (`all-citations-removed-declined-compact`); the decline keeps the shown sources by design.
  - EN/ES questions with gas/coin/chain/bridge/block: 0/20 leaks (the guard works on the untranslated question).
- **Also found:** PT_EN regexes have no word boundaries. "bebendo/bebeu/beber" → `child` (`beb[êe]`), "preparar" → `stop` (`parar`). Cartagena tap water, Cusco altitude prep and Recife rainy season got crypto/Hahndorf sources this way.
- **Fix (`health10`, ptQuery.ts +6 lines):** a translation made only of modifier terms (child/stop/treat/prevent) returns null, so the question is matched by its own words. Routing vitest 468/468.
- **L0:** 24/194 non-blind PT questions change translation, all modifier-only (`leak/l0.mts`).
- **L1** (`leak/l1-*`, the 23 unique changed questions, health9 vs health10, both profiles):

  | | 4B (and) | 1.5B (ios) |
  |---|---|---|
  | changed answers | 7/23 | 7/23 |
  | items showing crypto sources | 7 → 0 | 7 → 0 |
  | health route | 14 → 14 | 14 → 14 |
  - Travel items gain on-topic sources (Inca Highlands, Recife, Cartagena). The 4B now answers Cusco/Recife from them.
  - **Side effect: the fix alone is not adoptable on the 1.5B.** On 3 danger items the health route misses (bleach ×2, infant diarrhoea, labour), removing the off-topic sources also removes the compact decline. The 1.5B then answers from memory under the general-knowledge seal. One answer is harmful: bleach ingestion → "lavar a criança com água e sabão para se purificar".
  - **The fix must ship stacked with the routing fix (learned detector),** which sends those items to the health route.
- Seen in passing: ES questions are detected as PT ("hay olor a gas…" → `instant:off-translated`; ES head injury → the PT card text "Batida na cabeça"). This is the known isPortugueseQuestion-on-ES bug; Compass's precedence fix covers it.

## Next
1. **Recommendation:** (b) mmBERT-small fine-tune (best recall at every FF budget, 0/57 hard negatives at 0.5), with (a) the bge head as the zero-RAM fallback if Forge says no to ~60 MB. e5 head is the middle option (same size class as mmBERT, weaker). Laya teacher not tried: synthetic labels already give val AUC 0.997, so a teacher adds little until real user logs exist.
2. Re-score on Compass's dev set (300, spec-aligned) when it lands. Re-map labels if the spec differs.
3. Engine arm `health11` = health10 + the learned detector as the health predicate (needs the desktop ONNX or llama.cpp embedding path) → L1 on dev, then a **fresh** blind set for confirmation. health-fresh1 is spent for detector tuning claims: I haven't seen it, but its aggregate result motivated this work.

---

## v2 (after GO health11; Forge runtime verdict = llama.rn GGUF + JS head)

### Compass emergency-dev v1 (300; EN 105 / PT 105 / ES 90) with the v1 models (HF)
| detector | recall | strict FF (of 100) | ES recall | critical missed |
|---|---|---|---|---|
| lexical health9 | 41/180 | 43/100 | 9/54 | 56/75 |
| bge-small-en head | 154/180 | 25/100 | 43/54 | 12 |
| e5-small head | 178/180 | 45/100 | 54/54 | 1 |
| mmBERT v1 (0.5) | 177/180 | 30/100 | 53/54 | 2 |
- **v1 false fires come from spec gaps in my LABELS.md:** routine self-care (R7) 9/12, past and resolved (R6) 6/11, animal patient (R1) 5/5, dosing/info with nothing taken (R10) 4/11.

### Data aligned to Compass SPEC (`data/aligned-{en,pt,es}.jsonl`)
- 3 Opus agents. Each read SPEC.md only (never dev.jsonl), relabelled its language file and added minimal-pair contrasts.
  - EN 734 + 276, PT 747 + 300, ES 720 + 300 = **3,077**;
  - relabel changes: only how-to → 0/howto (37/41/18);
  - contrasts cover routine vs red flag, past vs current, animal vs human, dosing asked vs taken, figurative, fiction, and resolved vs unresolved multi-turn.
- The agents collided on a shared scratch file. I verified no corruption: every change is how-to 1→0, and the turns match the sources.
- Training excludes `howto=1` items (Compass: tolerated). Input = `common2.detector_text` (≤ 3 earlier user turns + message, `" | "`-joined, whitespace collapsed, last 700 code points).

### Shipped path (desktop stand-in for llama.rn)
- llama.cpp **b11010** (llama.rn's vendored commit) + `convert-mmbert-e5-vocab.patch` (Forge's 5 lines + the merge-rank fix + the e5 vocab); `llama-server --embeddings --pooling mean -np 1 -t 2`.
- The head runs in JS: `emergencyHead.ts` (exact GELU via erf, LayerNorm, softmax).
- **Token-id bug found in the converter:** with the fallback's placeholder scores, only 55/300 sequences were identical. Merge-rank scores → **4,321/4,321**. `
` must not join turns; it is an added token that HF and llama.cpp treat differently.
- Forge's gate (details: FORGE-HANDOFF.md): mmBERT v2 q8te4 (106.2 MB) has ids 100%, decisions 299/300 (Compass) and 897/903 (dev), max |Δp| 0.38. e5 q8te4 (84.4 MB): 298/300 and 897/903. **PASS (≥ 99%).**

### Selection: recall at fixed strict false fires (Compass 300, GGUF + JS-head scores)
| strict FF | mmBERT v2 (106 MB) recall / critical missed / ES | e5 v2 (84 MB) |
|---|---|---|
| 5 | 165 / 3 / 49 | 152 / 14 / 43 |
| 10 | 174 / 1 / 52 | 162 / 7 / 46 |
| 20 | 178 / 0 / 53 | 167 / 4 / 49 |
- At the synthetic-val threshold (FP 5% → 0.071, not tuned on Compass):
  - **mmBERT v2:** 177/180, strict FF 18/100 (v1: 30), how-to fires 6/20, **0 critical missed**, ES 53/54, unnamed 134/135, multi-turn 39/40;
  - on Sonar dev, realistic subset: 225/246, FF 1/457.
- **Pick: mmBERT v2.** e5 is ahead per MB at FF5 (1.00 vs 0.86 recall per 100 MB), but at every budget it misses 4–14 critical items, against 0–3 for mmBERT.
- On Sonar dev, recall drops (266/413) because FirstAidQA's generic how-to questions are now negatives by Compass's spec. That is intended.

### health11 engine arm (dev only)
- `deps.emergencyScore(query, userTurns)` → `{p, fire}` (answer.ts). It runs first: a firing message skips small talk and the calculator.
- `health = fire || isCardEmergency || isHealthFollowUp`; the broad `isHealthQuestion` is dropped when the detector is present. Without the dep, behaviour = health10 (vitest 468/468, tsc = base).
- Adapter: `BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL BOAR_DETECTOR_HEAD BOAR_DETECTOR_THR`. Reason codes: `detector:p=…`, `detector:fire`.
- **Gap seen in the smoke test:** the detector routes "stepped on something spiky on the reef…" to health, but the card trigger is lexical, so it gets the generic no-source line, not the marine-puncture card. Next: a learned condition picker for cards.

## v3 (L1 caught a model gap before any blind data; criterion retarget follows)
- **Gap (core L1, v2):** detector-only routing lost the health route on short, question-shaped live emergencies, which the broad regex had caught:
  - "I burned my hand… ice or butter?" (p 0.002) → **unsafe** "put ice" model answer;
  - "Criança engasgada, como ajudar?" 0.000; "Minha filha… picada por escorpião, é perigoso?" 0.08; frostbitten toes; the Ubud monkey bite.
  - HF and GGUF agree, so the cause is training: how-to items were excluded, and the dosing/info contrasts taught "should I…?" = 0. Compass dev (mostly narratives) didn't show it.
- **Why the card floor didn't catch them:** health11's floor is health9's narrow `isCardEmergency` (card condition AND what-to-do intent AND a symptom word). These items have the condition (burn, choking, scorpion, frostbite) but no symptom word; they used to be caught by the broad `isHealthQuestion`.
- **Floors tested** (engine-route level, offline; v3b at 0.2):

  | variant | Compass recall / strict FF | Sonar realistic recall / FF / hard neg |
  |---|---|---|
  | V0 detector OR isCardEmergency OR follow-up | 179 / 15 | 240 / 3 / 1 |
  | V3 V0 + (card condition AND intent) | 179 / 20 | 240 / 4 / 3 |
  | V1 detector OR any card condition OR follow-up | 179 / 47 | 243 / 27 / 15 |
  | (v2) V2 detector OR health9 lexical | 177 / 52 | 236 / 16 / 15 |

  Union floors buy ≤ 3 recall for +30 to +40 Compass false fires. **Kept V0.**
- **Model fixes:**
  - v3a = how-to items trained as positive (a first-aid card for "how do I stop a nosebleed" is the product's wanted answer; Compass tolerates the fire);
  - **v3b** = v3a + `data/terse-live.jsonl`: 631 terse question-shaped items (389 live positives over 69 conditions; 242 matched negatives incl. 71 impersonal how-to), Opus agent, SPEC only.
- **Held-out probes, permanent in core L1:** `probes/terse-live.heldout.jsonl` (sha 776acb26…), 30 items written by Sonar, never trained on. Caveat: same model family as the training writers, so likely easier than real users (v2 already got 19/20).

| HF, thr 0.2 | Compass recall / strict FF / how-to fires / critical missed / ES | Sonar realistic recall / FF / hard neg | terse held-out |
|---|---|---|---|
| v2 | 177 / 13 / 6 / 0 / 53 | 221 / 1 / 0 | 19/20, FF 1 |
| v3a | 179 / 16 / 15 / 0 / 54 | 230 / 3 / 0 | 20/20, FF 1 |
| **v3b** | **179 / 15 / 14 / 0 / 54** | **240 / 3 / 1** | **20/20, FF 0** |

- v3b on the core regressions: burn 1.000, nosebleed 1.000, frostbite 1.000, scorpion PT 1.000/0.959, choking PT 0.998. Still missed:
  - ES "Un niño se atragantó, ¿cómo ayudarlo?" (0.11);
  - the minimised monkey bite (0.001);
  - the evacuation order with conflicting advice;
  - "My dog walker was bitten by a rattlesnake";
  - frozen toes (0.07);
  - "exaustão por calor no trabalho".
- **Threshold stays 0.2** (frozen constant). At 0.5: Compass strict FF 13, Sonar realistic 238. 0.2 trades ~2 false fires for 3 catches, per SPEC's asymmetric cost.

### Forge review applied
- **(1) leading space after the cut:** trimmed (`trimStart` / `lstrip`).
- **(2) token-aware input:** 126 content tokens + BOS/EOS. Drop the oldest turns, then the message's leading words (binary search). 2,000-code-point pre-cap. Control-token literals stripped. TS `detectorText(turns, q, countTokens)` == Python `detector_text` on **1,248/1,248** inputs (incl. 45 adversarial: > 128-token multi-turn, 700 emoji, 3,000 chars, typed `<bos>`); max 126 tokens; 0 leading spaces.
- **Fail-safe:** an embedding or tokenize error returns null, and the lexical predicate takes over; never "not emergency".
- **(3)** `pooling_type: 'mean'` (a STRING in llama.rn's JS `initLlama`; the int `1` earlier advised is mapped to undefined → no pooling, corrected by Forge 2026-10-03) and the init params: app-side, recorded in FORGE-HANDOFF.
- **(4) gate at the shipped threshold (0.2), v3b q8te4** (`sonar-mmbert-small-emergency-v3b-q8te4.gguf` a86fe8b9…, head 766434de…):

  | set | token ids | decisions @0.2 | max \|Δp\| | min pooled cos |
  |---|---|---|---|---|
  | Compass 300 | 300/300 | 298/300 | 0.43 | 0.9934 |
  | Sonar dev 903 | 903/903 | 900/903 | 0.45 | 0.9872 |
  | terse held-out 30 | 30/30 | 30/30 | 0.06 | 0.9987 |
  | long adversarial 45 | 45/45 | 44/45 | 0.16 | 0.9906 |

  PASS (≥ 99%) on the three real sets. One flip on the 45 synthetic long inputs.

### health12 (dev line only; NOT in the blind arm): ES snakebite (Compass ask)
- WHO snakebite card trigger (`firstAidCards.ts`): ES snake words (serpiente, culebra, víbora, cascabel, nauyaca, yarará, mapanare), bite words (mordió, mordedura, picó, "le/me/lo… pico", picadura), and aid words (qué hago/hacer, cómo lo ayudo, primeros auxilios, auxilio, ayuda, ahora).
- An **ES card text** (translation of the EN/PT WHO text; **needs native review**) with the ES emergency line. ES questions use it via `isSpanishQuestion` before `isPortugueseQuestion`.
- The condition regex (`conditionCards.ts` snakebite): "mordido por una…", "(víbora) me mordió", "mordedura de…", "mordió una…".
- **L0 over 4,950 non-blind strings + 9 probes:** WHO-card changes 5, all genuine ES bites except one known class: an animal patient ("mi perro fue mordido por una serpiente"), the same behaviour as EN/PT today. Condition changes: 21 genuine ES snakebites and their follow-ups, plus 3 animal-patient items.
  - "Pico de Orizaba… si vemos una serpiente" fired in a first draft; fixed (picó only with an accent or after a clitic).
- Routing vitest 468/468. Patch `health12-on-health11.patch` 95fea628….

### Final health11 arm (re-frozen: confirm-health11.md; see confirm-health11.sha256)
- **Crypto guard:** on a pt-en-terms-translated question, crypto-pack sources (`Ethereum EIPs/ERCs`, `Ethereum specs`, `ethereum.org`, `Bitcoin BIPs`) are on-subject only with a crypto cue in the user's words ("gás" excluded). Cause: "queimadura… crianças" → "burn child" matched ERC-7401/7891 (burn/child tokens).
  - L0: 66 translated non-blind PT questions, 0 about crypto.
  - L1: 57 items × 2 profiles; crypto 2 → 0, 55 identical.
- **Gated floor:** broad `isHealthQuestion` AND detector p ≥ 0.01 → health route (`DETECTOR_FLOOR`). Without it, the 4B answered "como trata queimadura de água-viva? vou pra Maragogi…" from memory with unsafe advice (v0.8.7 `jelly-freshwater`, `burn-butter-cream`).
  - L1: 11 items × 2 profiles, 4 changes each: 3 tolerated how-to → health (ed-pt-100 unsafe → clean), 1 fiction false fire.
- **Dimension assert** (Forge): a pooled vector whose length ≠ 384 throws, and the lexical predicate takes over.
- **Dev L1, final arm vs health9 (engine, both profiles):**
  - core2 172: health route 107 → 131; unsafe 4B 2 → 0, iPhone 1 → 0;
  - Compass 300: emergencies 40 → 178/180, strict negatives 41 → 17/100, crypto 15 → 0;
  - 4B unsafe left on Compass: ed-pt-086 = a v0.8.7 under-triage hit on a figurative item (a rule false positive; the answer is fine).

## health14 (DEV only; NOT confirmed; the hf3 retarget was cancelled because Kiln had already started hf3 on frozen health13)
`health14-on-health13.DEV.patch`: Compass round-6 cards (conditionCards.v1.json acb0a104…, 35 keys: cpradult/cprchild/cprinfant/poisoning) + triggers.round6.proposed.mjs (b1363b74…), plus:
- **reviewer trigger notes:**
  - adolescent words or age ≥ 13 → adult CPR;
  - "out of the hotel pool" → drowning (`(?:\w|-)+` up to 2 words before pool/water);
  - ES "hace" (done in health13);
  - deliberate overdose → poisoning card. **NOT done: the crisis/self-harm path; the engine has no crisis route.**
- **interplay fixes found by the L0 diff (5,510 strings):**
  - specific cards beat poisoning (CO, eyechem, battery, venomous animals, seizure);
  - drowning beats CPR;
  - a CPR card on the weak "not responding" cue alone yields to any specific card;
  - a follow-up whose only condition is CPR yields to the conversation's drowning/choking card (or any card on a weak cue);
  - "drunk" is no longer an ingestion verb.
- **Checks:**
  - Compass self-tests through the engine: round 5 90/90; round 6 80/91 (all 11 "misses" are round-6-only assertions where the engine correctly picks choking/drowning/battery/CO/seizure, or the pre-existing heart-attack trigger on "is cardiac arrest the same as a heart attack?");
  - 7/7 regression probes; routing vitest 468/468.
- No engine L1 run (cancelled). Confirm later on a fresh set (post-bounty unless a demo-visible EN issue appears).
