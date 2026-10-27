# exp-05: BGE query instruction prefix (T1 from review/competitor-app-adopt.md)

Date: 2026-10-01 · Author: Kiln (R&D) · Requested by r4to via ai research #2, through the coordinator · **Measurement only.** Rule 0: any diff stays on a local branch (no PR, no push).

## TL;DR

- **Verdict: DESCARTAR.** The adoption rule was "the gap grows AND recall@6 does not fall". **The gap shrank**, from +0.037 to −0.004, and **recall@6 did not move** (identical in every configuration).

  | | Raw query (today) | With the BGE prefix |
  |---|---:|---:|
  | Question → right lead: p5 / median | 0.566 / 0.783 | 0.522 / 0.774 |
  | Question → random lead: median / p99 | 0.372 / 0.529 | 0.370 / 0.525 |
  | **Gap (right p5 − random p99)** | **+0.037** (95% CI −0.08…+0.17) | **−0.004** (95% CI −0.10…+0.17) |
  | Pure semantic retrieval over 67,636 leads, recall@6 / recall@1 (42 q) | 0.905 / 0.833 | 0.905 / 0.810 |
  | Gold rank, paired per question (42 q) | — | **1 better, 6 worse, 35 same** |
  | **Hybrid recall@6** (pack search, `origin/main` code), retrieval-v1 (120 q) | **0.992** | **0.992** |
  | Hybrid recall@6, vitalik on the Wikipedia sample pack (16 q) | 0.750 (0.875 with lead rerank) | 0.750 (0.875) |
  | Hybrid recall@6, vitalik on the crypto pack (6 q) | 0.833 | 0.833 |

- **Why:**
  - Our queries are full natural-language questions, not short keyword queries.
  - BGE's own card says the v1.5 models were trained to work without the instruction: "No instruction only has a slight degradation in retrieval performance compared with using instruction", and it recommends testing both on the task ([BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)). On ours, the prefix slightly *lowers* the right-article similarity (paired median −0.006).
  - The hybrid search is driven by keywords, so the semantic gate almost never decides.
- **Repositioned cutoffs, which would be needed with the prefix and are not proposed:**
  - `MIN_SEMANTIC_SIMILARITY` 0.55 → 0.49 (right p2). It would leak **3.5% of random leads, against 0.5% today**.
  - `ANSWER_MIN_SIMILARITY` and `SEMANTIC_KEEP` 0.7 → 0.68 (same share of right leads kept).
- **The baseline reproduces:** the published right p5 0.573 / median 0.776 and random median 0.380 / p99 0.530 come out at 0.566 / 0.783 / 0.372 / 0.529 with the rebuilt script (≤ 0.01 apart). The original script was never committed; see §2.

## 1. What was measured

| Item | Value |
|---|---|
| Embedding model | `bge-small-en-v1.5-q8_0.gguf`, sha256 `ec38e8da…2f514`, checked at run time. It equals the app catalog entry (`manifest.ts` `bge-small-en-v1.5-q8`) and the pack's `meta.embeddingModelSha256`. Already on the mini, so **no download** |
| Query embeddings | [`embed_queries.mjs`](embed_queries.mjs) on the **Mac mini** (node-llama-cpp from `<runner>/eval-runner`, CPU, ctx 512, 4 threads, heavy queue `short`). Every question is embedded raw and with `"Represent this sentence for searching relevant passages: "`. Adapted from boar-app `eval/retrieval/embed-queries.mjs` (`c87234a9`), the script behind the published baseline vectors |
| Passage embeddings | **Unchanged**: the 67,636 int8 lead vectors in `boar-wiki-sample.sqlite` (sha256 `f03ee5f3…4b49`, built 2026-09-26, raw text, top 33,333 articles by views + every Wikivoyage guide), and the crypto pack's `lead_vecs`. Read-only on the MacBook; the 1.5 GB pack was **not** copied to the mini (its disk is below the 18 GiB floor) |
| Cosine | Exactly as the app: `cosineSimilarityInt8` on the int8 values; the stored scale is irrelevant |
| Questions | (a) boar-app `eval/retrieval/questions.v1.jsonl` (160; gold = one enwiki title), the set behind the published baseline. (b) Lantern's `vitalik-evalset.jsonl` (58; gold from `reference_sources`, as in `refusal_audit.answer_titles`: Wikipedia titles and EIP numbers) |
| (1) Distributions | [`dist.py`](dist.py), numpy. Right = cos(q, gold lead) for the 42 retrieval-v1 questions whose gold article has a lead vector. Random = cos(q, **every other** lead) (2.84M pairs, the full distribution instead of a sample). Gap = right p5 − random p99. Bootstrap 95% CI over questions; paired rank of the gold lead |
| (2) Recall@6 | [`recall_hybrid.test.ts`](recall_hybrid.test.ts), vitest, run inside a **scratch copy of boar-app `origin/main` `7aa67d5`** (r4to fork). This is where `retrieve.ts:166` / `passages.ts:33` live: `upstream/main` was reverted on 2026-10-01 to an older engine without `passages.ts`. Pack hybrid search `WikiPack.search(q, {k: 10, queryVec})`: keywords, named titles, and the lead gate `SEMANTIC_KEEP`, with the lead rerank off (default) and at weight 0.5. Only harness change: `SEMANTIC_KEEP` read from an env var in the scratch copy |
| Cutoff criterion | As for the original 0.55 floor: keep ~98% of right leads with < 1% of random. The 0.7 gates are quantile-matched to keep the same share of right leads |

**Correction to the task brief:** `SEMANTIC_KEEP` is `src/rag/wikiPack.ts:189` (used at `:720`), not `:226`. The other references (`retrieve.ts:166`, `passages.ts:33`, `pure.ts:51`, `pure.ts:256`) match `origin/main`.

## 2. Reproduce

```bash
cd rnd/kiln/exp-05-bge-query-prefix
# 1) query vectors on the Mac mini (heavy queue, short; no download)
rsync -az embed_queries.mjs questions.*.jsonl the mini:boar/kiln/exp-05/
<on the mini> "bash -lc 'cd <runner>/kiln/exp-05 && ln -sfn <runner>/eval-runner/eval/node_modules node_modules && \
  for s in retrieval-v1 vitalik58; do HEAVY_CLASS=short <runner>/bin/run-heavy Kiln env BOAR_EMBEDDING_GGUF=\$HOME/boar/shared-models/bge-small-en-v1.5-q8_0.gguf node embed_queries.mjs questions.\$s.jsonl qvecs.\$s.json; done'"
rsync -az 'the mini:boar/kiln/exp-05/qvecs.*' .
# 2) distributions + cutoffs (MacBook, read-only pack)
python3 dist.py ../../../shared-data/packs/boar-wiki-sample.sqlite qvecs.retrieval-v1.json questions.retrieval-v1.jsonl results/dist.json qvecs.vitalik58.json questions.vitalik58.jsonl
# 3) hybrid recall@6: scratch copy of origin/main with node_modules symlinked (boar-app untouched)
T=$(mktemp -d); (cd ../../../boar-app && git archive origin/main src package.json tsconfig.json) | tar -x -C $T
ln -s "$PWD/../../../boar-app/node_modules" $T/node_modules; mkdir $T/kiln; cp recall_hybrid.test.ts $T/kiln/
sed -i '' 's/^export const SEMANTIC_KEEP = 0.7;$/export const SEMANTIC_KEEP = Number(process.env.KILN_SEMANTIC_KEEP ?? 0.7);/' $T/src/rag/wikiPack.ts
printf 'export default { test: { include: ["kiln/**/*.test.ts"], testTimeout: 600000 } };\n' > $T/vitest.config.mjs
for keep in 0.7 0.6785; do (cd $T && KILN_SEMANTIC_KEEP=$keep KILN_QSET=retrieval-v1 KILN_PACK=…/boar-wiki-sample.sqlite \
  KILN_DIR=$OLDPWD KILN_OUT=$OLDPWD/results/recall.jsonl ./node_modules/.bin/vitest run kiln/recall_hybrid.test.ts); done   # + KILN_QSET=vitalik on both packs
```

Outputs:
- `results/dist.json`: distributions, cutoffs, bootstrap CIs and paired ranks.
- `results/recall.jsonl`: 24 configurations, per-question ranks included.
- `qvecs.*.json`: query vectors, raw and prefixed.

## 3. Cutoffs

| Constant (`origin/main`) | Today | Share of right leads kept / random leaked today | Value with the prefix (same criterion) | Kept / leaked with the prefix |
|---|---:|---|---:|---|
| `MIN_SEMANTIC_SIMILARITY` (`pure.ts:51`) | 0.55 | 95.2% / 0.52% | 0.49 (right p2) | 97.6% / **3.49%** |
| `ANSWER_MIN_SIMILARITY` (`pure.ts:256`) | 0.7 | 85.7% / 0.00% | 0.68 | 85.7% / 0.00% |
| `SEMANTIC_KEEP` (`wikiPack.ts:189`) | 0.7 | 85.7% / 0.00% | 0.68 | 85.7% / 0.00% |

- **The prefix makes the low floor worse:** keeping ~98% of right leads would let 7× more random leads through.
- The 0.7 gates just move to 0.68, with no gain.
- n = 42, so the right-article percentiles are coarse (p5 ≈ the 2nd-lowest value).

## 4. Diff (not recommended)

[`NOT-RECOMMENDED-bge-query-prefix.patch`](NOT-RECOMMENDED-bge-query-prefix.patch): the minimal change as specified. It adds `embedQuery()` and `BGE_QUERY_PREFIX` in `embed.ts`, touches the 2 call sites (`retrieve.ts:166`, `passages.ts:33`), and sets the 3 cutoffs at the values above. Passages are untouched (`seedCorpus.ts:247`, the pack builder).
- **Checked:** it applies cleanly on `origin/main` `7aa67d5` `src/rag` and reproduces the edited tree byte for byte.
- **Use:** kept only so that a future re-test does not have to rewrite it. It would go on a local branch, with no PR and no push (rule 0).
- **Not applied** in any worktree, and boar-app was not touched.

## Decisions / Options / Tasks

**Decisions (proposed)**
- D1. **DESCARTAR T1.** Keep the raw query embedding and the current cutoffs (0.55 / 0.7 / 0.7). Update `review/competitor-app-adopt.md` T1 to "measured, no gain" (owner of that file: the coordinator).

**Options**
- O1. Re-test only if short keyword-style queries become common: the planner's titles or LLM query expansion (T2). That is where BGE says the instruction helps.
- O2. Measure the built-in corpus path (`retrieve.ts` `semanticSearch` over the ~5,300 seeded chunks with `MIN_SEMANTIC_SIMILARITY`) through the app pipeline, if T1 is ever reopened.

**Tasks**
- [x] Distributions raw vs prefixed on the same lead embeddings, baseline reproduced.
- [x] Hybrid recall@6 raw vs prefixed, old vs repositioned `SEMANTIC_KEEP`, on retrieval-v1 and the vitalik set (2 packs).
- [x] Reference diff (not recommended).

## UNKNOWN

- The built-in corpus semantic path (`retrieve.ts` `semanticSearch`, `MIN_SEMANTIC_SIMILARITY` over the device-seeded corpus chunks) was not run end to end. Only the floor's effect was derived from the lead distributions, which is what the floor was originally calibrated on (commit `c87234a9`).
- Portuguese questions. All 218 questions are English, and the app searches PT questions through English names.
- Small n where gold leads exist: 42 of 160 retrieval-v1 golds and 6 of the vitalik golds have a lead vector, because the pack embeds only the top 33,333 articles. The hybrid recall uses 120 and 22 questions.
- The exact script of the published baseline (not in git). The rebuilt measurement lands within 0.01 of it.

**Metric:** gap 0.037 → −0.004 with the prefix; hybrid recall@6 0.992 → 0.992.
**Next step:** the coordinator records T1 as DESCARTAR. If T2 (query expansion) lands, the prefix can be re-checked on those short queries with this same harness.
