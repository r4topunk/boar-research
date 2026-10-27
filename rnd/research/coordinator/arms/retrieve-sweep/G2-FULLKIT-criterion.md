# G2-FULLKIT criterion (FROZEN 2026-10-22 01:3x, before any sidecar build result is read)

Question: with chunk-level dense vectors on every pack of the kit, under the no-displacement setting (head pass a2 + packDense2 "extra"), does the right chunk reach the context on the real items as well as on the pack questions, without harm?

Fixed: sidecars built with the DENSECHUNK-ST tool (sidecar_embed, bge-small-en-v1.5 q8_0 sha ec38e8da, int8 chunk_vecs) for boar-crypto, boar-wikivoyage-en, boar-visa-en into the v3proto set (factbook, firstaid, medlineplus, simplewiki already built 10-13); engine tree K1 litepacks (answer.ts 0d1ac07d), gate search, cpu embed, seed-free (0 LLM).
Reads (0 LLM):
1. Real items: MAIN 97 K1 questions, K1 kit all-v3 (crypto, wikivoyage, simplewiki), settings {packHeadPass a2, packDense2 extra} vs the funnel baseline. PASS iff recovery ≥ 5/25 (S2/S3) and losses ≤ 2/22 (S4/S5). (With simplewiki v3 alone: 4/0.)
2. Pack questions: QFORM 432, A-union all-v3 6 packs under the same settings vs the v2 control (same 6 packs, settings off and K1 settings on): report hit@kept per form pooled with paired CI; expected ≥ +8 pooled (G-extra gave +14.8 on the 3-pack subset); junk-kept and context tokens reported (no gate here: the answer screen prices them).
3. Costs: pack bytes v2 → v3 per pack; replay wall per query v2 vs v3 (desktop proxy; phone unmeasured).
Then (only if read 1 passes): answer screen, Haiku judge.v1 N 4 both orders on the changed-context items of MAIN 97 (1.7B on the mini, same engine state as the K1 mini baseline, cap 300): LEVER-CANDIDATE iff ΔU ≥ +0.02 with CI low > −0.01 and CE-unwarned not up; Opus CV5 51 confirm only after that (≤ 110).
Prediction: read 1 recovery 6–9/25, losses 0–1; read 2 pooled +10…+16; wikivoyage bytes +20…+25 %; answer screen ΔU +0.02…+0.05 on MAIN (smaller than the pack questions because 45/97 have no fact in any pack).
Caps: 0 LLM for reads 1–3; Haiku ≤ 300; Opus ≤ 110 only after the screen; paid 0; phone 0. Dev items only.
