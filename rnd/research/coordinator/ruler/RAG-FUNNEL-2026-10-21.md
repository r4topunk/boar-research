# RAG-FUNNEL (2026-10-21): where the key fact of a real dev item is lost, per pack set (K0, K1, K3)

TL;DR (0 LLM, 0 generation, 0 judge calls, 0 paid; stub-server replay on the MacBook + existing Haiku 5.5-low judgments)
- **MAIN keyed 92, 1.7B, K3 (lexical rule):** S1 not in any installed pack **45** · S2 in a pack, not retrieved **7** · S3 retrieved, dropped at keep **17** · S4 kept, answer wrong **15** · S5 kept and used correctly **8**.
- **S1 is the cooking/money self-tests (39 of 45):** their facts live in qa-cooking-se / qa-money-se, which no K-set installs. On v0.1 alone (52) S1 is 6.
- **S2 is not a loss on K3:** all 7 are router "no retrieval" items answered by a deterministic layer (Wikidata facts: winner, area, host, dates, depth, height; travel calculator), judge correctness 4.0-5.0.
- **The real losses on v0.1 sit after retrieval:** S3 16 (10 = the fact chunk was a dense candidate outside the top-2 picks, 3 grounding drops, 2 append-budget drops, 1 compression) and S4 15 (5 of them in the CE band, correctness <= 1.5). Only 8/52 reach S5.
- **K1 looks the same as K3** (S3 17, S4 17, S5 5); **K0** loses most items before retrieval (S1 60 / S2 11 on MAIN; S2 search 7).
- **Top 2 stages to optimise (K3, dU on MAIN 97):**
  1. **S3 keep step (17 items):** perfect-fix ceiling +0.115, self-test prior (+0.139 per item reached) **+0.025**; lever = dense-rank / keep (10 of 17 are 'dense candidate not picked').
  2. **S4 reading (15 items):** perfect-fix ceiling +0.103, self-test prior **+0.022**. ORACLE-REAL measures whether the reach prior holds on real items.
  - S1 (content) has the largest raw ceiling (+0.300 perfect, +0.063 prior) but it is the 39 cooking/money items that need the qa-* packs installed; that is SE-DUP's question, not a pipeline fix.
  - **Real-item prior:** FACTPRESENT's real cell (a) is -0.010 per item reached, so every stage ceiling is about 0 under it. The self-test prior is an upper bound.
- **Lexical caveat (measured):** the pack-presence rule is noisy. Read check of the K3 gold chunks: v1 4/10 real fact chunks, v2 6/10, v3 29/39 lexical golds Y/P; with 8 hand-found chunks, 37 items have a Y/P gold (22 Y, 15 P). `funnel_verified` in the JSON re-counts S1/S2 with the hand labels: K3 MAIN S1 44, S2 8 (v0.1: S1 5, S2 8); S3-S5 unchanged.

Files: `RAG-FUNNEL-2026-10-21.json` (sha256 in the commit row; per item x arm: stage, sub-stage, candidate share, fact candidates, kept share, pack hits, correctness, parity, gold), `tools/ragfunnel.py`, `tools/apply_funnel.py` (logging-only patch), `tools/ragfunnel_replay.sh` (replay driver), hand labels `arms/oracle-real/gold-labels.tsv`.
Rerun:
```
bash tools/ragfunnel_replay.sh <job dir: req/{K0,K1,K3}-{V01,CM}.requests.jsonl + stub_server.py> <FACTPRESENT replay tree be-0cfd4a77-cut7-litepacks-retfloor-fp>   # MacBook, ~4 min, detector :8094 must be up
python3 -I tools/ragfunnel.py <job>/out FACTPRESENT-2026-10-21.json RAG-FUNNEL-2026-10-21.json   # ~2 min, read-only pack FTS
```

## Method
- **Replay.** FACTPRESENT's replay (LITEPACKS adapter, LITEDECLINE_OFF=5, RETFLOOR base, stub llama-server, 0 generation) plus `apply_funnel.py`: logging only, three reason codes per item: `fun:raw` (retrieve() list, before any filter), `fun:dense` (the two-stage dense candidates attached beside it), `fun:compressed` (after compressContext, before grounding). `retfloor:cand` (pending X1/dense appends) and `retfloor:kept` come from the RETFLOOR patch.
  - Parity: kept titles equal the judged LITEPACKS runs on 97/97 MAIN items for each of K0, K1, K3.
- **Fact rule = FACTPRESENT's** (v0.1 grading must_any/must_k with the precheck semantics; self-tests in_pack_facts; share >= 0.5). Kept presence = FACTPRESENT's PRESENT on the dumped Context block. Candidate presence = the same rule on the union of candidate chunk texts (full text read from the kit pack file by chunk id).
- **Pack presence (pool search).** Per installed kit pack: FTS5 bm25 top 200 for OR(question tokens) and top 200 for OR(question tokens + grading terms). A pool chunk holds the fact when the rule on that chunk alone gives share >= 0.5 and its topic anchor (idf-weighted share of question tokens in title + text) >= 0.5.
  - v1 (anchor = 2 question tokens) failed a 10-chunk read (4/10); v2 (idf anchor) read 6/10; v3 adds a title tie-break for the gold pick. Each change was made after a read and before the next count. All 39 v3 gold chunks were then read and labelled (table in `arms/oracle-real/gold-labels.tsv`).
- **Stages** (first failing stage wins): S1 no installed pack chunk holds it; S2 a pack chunk holds it, no candidate does (S2 router = no `retrieve:yes`; S2 search otherwise); S3 a candidate holds it, the kept context does not (sub: grounding = in the compressed list, dropped after; compress = in raw, not compressed; append-budget = a pending X1/dense append cut by the 600-work budget; dense-rank = only in the dense candidate list, not among the D = 2 picks); S4 kept, judge correctness (Haiku 5.5-low judge.v1-low, mean of both orders) < 3.5 or declined (S4 ce = <= 1.5); S5 kept and correctness >= 3.5.
- **Ceilings.** dU on MAIN 97 (ratio of sums) if all items of a stage moved down one stage: perfect fix = items reach the reference score; self-test prior = each item gains +0.139 x its reference score (FACTPRESENT self-test cell (a)); real prior = -0.010 (FACTPRESENT real cell (a)).

## Funnel (lexical rule; counts of keyed items)
| pack set | subset | S1 not in pack | S2 not retrieved (router / search) | S3 dropped at keep (dense-rank / grounding / budget / compress / union) | S4 kept, wrong (CE) | S5 kept, right |
|---|---|---|---|---|---|---|
| K0 | MAIN 92 | 60 | 11 (4 / 7) | 8 (0 / 5 / 0 / 2 / 1) | 11 (5) | 2 |
| K0 | v0.1 52 | 20 | 11 (4 / 7) | 8 | 11 (5) | 2 |
| K1 | MAIN 92 | 45 | 8 (7 / 1) | 17 (10 / 3 / 2 / 1 / 1) | 17 (7) | 5 |
| K1 | v0.1 52 | 6 | 8 (7 / 1) | 16 | 17 (7) | 5 |
| K3 | MAIN 92 | 45 | 7 (7 / 0) | 17 (11 / 3 / 2 / 1 / 0) | 15 (5) | 8 |
| K3 | v0.1 52 | 6 | 7 (7 / 0) | 16 (10 / 3 / 2 / 1 / 0) | 15 (5) | 8 |
| any | cm 40 | 39-40 | 0 | 0-1 | 0 | 0 |

Ceilings, K3 (dU on MAIN 97): S1 n 45 perfect +0.300 / prior +0.063 · S2 n 7 +0.023 / +0.010 · S3 n 17 +0.115 / +0.025 · S4 n 15 +0.103 / +0.022. K1: S3 n 17 +0.112 / +0.024, S4 n 17 +0.117 / +0.025.

## Reading
- Adding packs moves items from S1/S2 into S3/S4 (K0 -> K1), not into S5. K1 -> K3 adds 3 to S5 (health/country items covered by medlineplus/firstaid/factbook).
- On v0.1, S3 + S4 = 31 of 52. The dense candidate list already holds the fact on 10 S3 items; X2b picks only the top 2 by cosine.
- S4 CE items (K3): vit-hum-004, vit-trv-003, vit-cry-002, lan-rsn-003, lan-rsn-004 (kept fact, correctness <= 1.5).

## Caveats
- Lexical presence on v0.1 is noisy both ways: generic grading terms and numeric regexes match unrelated chunks (the read check above), and the union-of-candidates rule for S3 is looser than the single-chunk pack rule. Treat S3 counts as upper bounds.
- One seed, Haiku 5.5-low (compresses gaps). Dev sets only (v0.1 public + self-tests); no blind/, no rnd/veil, no v0.4.
