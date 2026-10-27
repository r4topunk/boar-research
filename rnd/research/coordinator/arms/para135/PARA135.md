# PARA135 (2026-10-23): Qwen3-1.7B constrained to exactly 1, 3 or 5 paragraphs

**Leitura para o r4to (PT-BR):**
1. O suporte cai já no 2º parágrafo, não no 3º+: o 1º parágrafo fica em ~27-36 % de frases sem suporte em todos os braços; do 2º em diante sobe para ~50-76 %. Pedir mais parágrafos = mais texto da memória do modelo.
2. Unsupported total: 1 parágrafo 0.33, 3 parágrafos 0.50, 5 parágrafos 0.52 (Detailed 3-5 antigo 0.45-0.47, Succinct 0.28). Especificidades inventadas (estimadas): 39 → 87 → 141.
3. Juiz Haiku nos 51 CV5: U praticamente igual (0.228 / 0.233 / 0.218, diferenças dentro do ruído), mas erros confiantes sobem 37 → 43 → 49 por 100. Succinct (S17) segue melhor: U 0.263, CE 27.
4. O modelo obedece: 1 e 3 parágrafos ~100 % nas respostas geradas, 5 parágrafos só 67 % (fica em 2-4 ou passa para 6).
5. Recomendação não muda: Succinct continua o padrão do 1.7B; nenhum braço de parágrafos fixos empata com ele (p1 −0.035 U, mais CE).

Criterion: PARA135-criterion.md, sha256 79b0482dd7ac186a77ad7eaa1beb8fe4509bc3bfdd257be630648bbc6ab4fb76 (frozen and read-only before any generation or judge call). Calls: CALLS.md (Haiku 736 of 1062; Opus 0; paid 0; phone 0).

## Commands
- Personas: personas/para{1,3,5}.json (file sha256 ee415c8a / e19fe460 / 54a04602; adapter persona sha 66b3e6f1 / aea817de / aee8b9a1, checked in every trace). Detailed system prompt verbatim; reminder "Be thorough: Answer in exactly N paragraph(s) that cover(s) the key points in depth, with reasons, comparisons and examples. Don't repeat yourself."
- Generation (mini, 6 jobs, slot lock gen1/gen2): `bash tools/run_gen.sh a|b 1|3|5` = TOPICS27 recipe (APFS clone of be-0cfd4a77-cut7-litepacks, guards answer.ts 0d1ac07d / adapter d53c1487, mini_gen_dump.sh) + adapter Max Output Tokens 512 -> 1024 by sed in the clone (the app's maxTokens setting 1024, as STYLE15B's Detailed arm). 0 answers reached 1024 tokens. Set A kit wiki-vital5 + essential (compose/packs-k13), set B K1 kit (compose/packs-k1). qwen3-1.7b-q4km, seed 42, --reasoning off, LITEDECLINE_OFF=5, b11010 CPU -t 4. 234/234 rows.
- Set A: `python3 -I tools/prep_a.py` (paragraph split tools/para.py + frozen outcome-blind stratified sample) -> `node tools/audit_a.mjs judge/prep.json judge/audit.jsonl` (TOPICS27 prompts/schema, per-sentence only) -> `python3 -I tools/agg_a.py` -> aggregates/setA.json.
- Set B: `bash tools/judge_b.sh 1|3|5` (shard_judge.sh Haiku 5.5-low judge.v1-low N 4 both orders, all 51 ids, preflight OK) -> `python3 -I tools/agg_b.py` -> aggregates/setB.json.

## Set A: 27 Research Topics (wiki-vital5 + essential), Haiku sentence support audit
| arm | sentences (audited) | unsupported share (est.) | invented specifics (sample / est. all) | compliance (=N / +-1) | banner | out tok p50 (mean) | ms p50 | words p50 |
|---|---|---|---|---|---|---|---|---|
| p1 | 148 (148) | 0.331 | 39 / 39 | 27/27 / 27 | 21 | 192 (182) | 8,133 | 156 |
| p3 | 350 (141) | 0.497 | 35 / 87 | 23/27 / 26 | 13 | 374 (377) | 13,874 | 310 |
| p5 | 523 (141) | 0.519 | 38 / 141 | 25/27 / 26 | 11 | 552 (547) | 18,951 | 449 |
| ref Detailed 3-5 (TOPICS27, cap 512) | 385 (385) | 0.447 (0.468 as reported with its batched labels) | 103 | n/a | 11 | ~420 | | |
| ref Succinct (TOPICS27-SUCCINCT) | | 0.28 | 7 | n/a | 13 | | | |
Context source: own dumped prompt 24/27, no chunks 3/27 (same 3 topics in every arm). 0 at cap. 0 declined.

### By paragraph position (unsupported share, Wilson 95 % CI; invented per audited sentence; share of the arm's estimated invented specifics)
| position | p1 | p3 | p5 | ref Detailed 3-5 (all per-sentence) |
|---|---|---|---|---|
| 1 | 0.331 (0.26-0.41), inv 0.26, 100 % (n 148) | 0.362 (0.24-0.51), inv 0.28, 37 % (n 47) | **0.273** (0.15-0.44), inv 0.27, 24 % (n 33) | 0.298 (0.22-0.39), inv 0.30, 30 % (n 104) |
| 2 | - | 0.592 (0.45-0.72), inv 0.24, 34 % (n 49) | **0.759** (0.58-0.88), inv 0.41, 32 % (n 29) | 0.550 (0.46-0.64), inv 0.32, 35 % (n 111) |
| 3 | - | 0.524 (0.38-0.67), inv 0.24, 29 % (n 42) | 0.586 (0.41-0.75), inv 0.31, 24 % (n 29) | 0.530 (0.44-0.62), inv 0.27, 30 % (n 115) |
| 4 | - | 0.667 (n 3) | 0.500 (0.32-0.68), inv 0.15, 11 % (n 26) | 0.312 (0.20-0.45), inv 0.06, 3 % (n 48) |
| 5 | - | - | 0.522 (0.33-0.71), inv 0.17, 10 % (n 23) | 0.80 (n 5) |
Finding: support breaks between paragraph 1 and paragraph 2, in every arm, including the old Detailed run. Paragraph 1 holds at 0.27-0.36 whatever N is (p5's first paragraph is no worse than a single paragraph); paragraphs 2-5 sit at 0.50-0.76. Invented specifics peak in paragraph 2 (p5: 0.41 per sentence), not in paragraphs 3-5 (0.15-0.31). In p5, positions 1-2 hold 56 % of the invented specifics. More paragraphs add text with the late-paragraph support rate, so the totals climb (39 -> 87 -> 141), but no single late paragraph is the problem. Banners go up as answers get shorter (p1 21/27: one paragraph cites less, so the uncited-with-sources release line fires more often; see ENG-BANNER-KEPT).

## Set B: 51 CV5 dev ids, K1 kit, Haiku 5.5-low judge.v1-low (n 51, item bootstrap B 2000 rng 11)
| arm | U floor-adj (CI) | U raw | win-rate | correct-shown /100 | CE /100 | out tok p50 | ms p50 | words p50 | compliance (51 / 42 generated) | banner |
|---|---|---|---|---|---|---|---|---|---|---|
| p1 | 0.228 (0.171-0.294) | 0.389 | 0 | 15.7 | 37.3 | 179 | 10,650 | 150 | 42 / 42 | 29 |
| p3 | 0.233 (0.180-0.292) | 0.393 | 0 | 19.6 | 43.1 | 350 | 14,938 | 277 | 41 / 40 | 14 |
| p5 | 0.218 (0.164-0.278) | 0.383 | 0 | 13.7 | 49.0 | 512 | 17,705 | 397 | 28 / 28 | 12 |
| ref D17 Detailed 3-5 (cap 1024) | 0.224 (0.165-0.293) | 0.387 | 0.02 | 17.6 | 52.9 | 392 | 16,929 | 303 | n/a | 21 |
| ref S17 Succinct (cap 512) | **0.263** (0.201-0.333) | 0.419 | 0.02 | 27.5 | **27.5** | 41 | 4,340 | 40 | n/a | 24 |
Paired vs p1 (dU, CI, better/tie/worse): p3 +0.005 (-0.025..+0.033) 16/17/18; p5 -0.010 (-0.038..+0.020) 13/20/18; D17 -0.004 (-0.036..+0.029); S17 +0.035 (+0.001..+0.068) 25/12/14. p5 vs p3 -0.015 (-0.044..+0.015). 9 of 51 ids are instant-tier fixed answers (identical text in all arms, 0 tokens); they are counted in U and in the 51-item compliance. All 306 rows new (0 reused), 0 at cap, 0 declined.

## Predictions (frozen)
| | prediction | outcome | |
|---|---|---|---|
| P1 | set A unsupported rises monotonically p1 < p3 < p5 | 0.331 < 0.497 < 0.519 | HIT (the p3 -> p5 step is small; the jump is p1 -> p3) |
| P2 | invented specifics concentrate in paragraphs >= 3 (p5: pos 3-5 > 50 % and higher rate than pos 1-2) | pos 3-5 hold 44.5 %; rate 0.22 vs 0.34 at pos 1-2 | MISS (they peak in paragraph 2) |
| P3 | U peaks at 3 or flat 1-3, drops at 5, more CE at 5 | 0.228 / 0.233 / 0.218; CE 37 / 43 / 49 | HIT on points (all U gaps inside the CIs: in practice flat) |
| P4 | compliance >= 80 % at 1 and 3, lower at 5 (A + B pooled, 78 per arm) | 69/78 (88 %), 64/78 (82 %), 53/78 (68 %) | HIT |

## Persona recommendation
Unchanged: Succinct stays the 1.7B default. Recommendation-change test from the criterion: p1 vs S17 is -0.035 U (CI excludes 0 by a hair) with CE 37 vs 27, and p1's set A unsupported 0.33 > Succinct 0.28, so no fixed-paragraph persona qualifies. "Short is safer" is confirmed in its strong form: the first paragraph is the best-supported one, and U does not rise with N (flat 0.22-0.23 while CE grows 6 points per two extra paragraphs). If a longer style is ever wanted, the cheapest safe shape is one paragraph, not 3-5.

## Caveats
One seed (42); Haiku audit (UNSUPPORTED = not in the context, not false) and Haiku judge (compresses gaps; over-calls CE on long warned answers); set A p3/p5 numbers are stratified-sample estimates (141 of 350 / 523 sentences) and per-position n is 23-49, so the CIs overlap except paragraph 1 vs 2; bench engine K1 tree, not the native app; maxTokens 1024 here vs 512 in TOPICS27 Detailed (no answer reached either cap here); the Detailed reference's by-position table uses its full per-sentence labels (385 units, unsupported 0.447 instead of the reported 0.468 with batched labels); num_absent is not computed for the Detailed reference; dev / public sets only.
