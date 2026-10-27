# False-refusal audit: build 14de107, iPhone 13, Qwen2.5-1.5B

> Lantern · sprint 2 · 2026-09-30. Tool: `tools/precheck.py --refusals` (logic in `tools/refusal_audit.py`). Consumers: modelos ai #2 (gate fix), Plumb (report).

## TL;DR

- **False refusals are rare:** 2/21 refusals in the factual run and 1/27 in the device run, meaning the retrieved source had the answer and BOAR still declined.
  - `vit-cry-009`: EIP-7251 retrieved 3×, both runs.
  - `vit-fa-011`: Wikivoyage "World War I" retrieved, factual run only.
  - Both were declined **after the model wrote a draft** (citation gate).
- **Most refusals are correct, and the gate does its job.** 14/21 and 17/27 refusals had sources that don't contain the answer. The gate declined a draft that would have been unsupported, which is how the confident-wrong rate stays at 5–10%.
- **The real problem is coverage, not the gate.** For **13 of 21 / 13 of 27** refusals, the answer article (Mozi, Measles, Tiger/Lion, Taiwan, Japan, Box jellyfish, The Lord of the Rings, Invisible hand…) exists in `wiki-vital5` (Wikipedia Vital Articles L5, 156 MB locally). That pack is **not** in the installed kit (`--install-assets boar-crypto,boar-wikivoyage-en`; setup decision UI-1c puts it only in the "Curious" profile).
- **The rows can't tell a refusal apart when the gate drops every source.** 5/21 and 9/27 refusals have `retrievedTitles: []` (`grounding:off-topic-dropped-N` then `no-good-source`). What was dropped is not recorded. Fix in §4.

## 1. Definitions (as implemented)

| Kind | Rule | Evidence available in these rows |
|---|---|---|
| `false-refusal` | Refused, **and** a retrieved source has the answer: (a) a retrieved title is one of the item's answer articles, source-aware (a Wikivoyage "Japan" is not Wikipedia "Japan"); or (b) the retrieved article's text satisfies the item's `must_any`/`must_k`, as a strong check | **Titles only.** Text is read from the local copy of the same pack (`shared-data/`), so it is an *article-level* proxy for the passage |
| `possible-false-refusal` | Only a weak text hit (a single broad `must_any` group) | Must be settled by hand. All 7 cases in these runs were settled in `data/refusal-hand-14de107.json` |
| `correct-refusal` | Retrieved sources don't have the answer. `retrieval-miss`: the answer article exists in an installed pack but was not retrieved. `not-in-pack`: it does not | |
| `unknown-dropped` | `retrievedTitles` empty: the gate dropped all sources before the `sources` event | Only pack presence can be reported |

Mechanism, from `reasonCodes`:
- `gate-after-draft` = `all-citations-removed-declined` / `uncited-with-sources-declined`. The model drafted, and the citation gate declined.
- `no-source` = `no-good-source` / `declined-compact` only.

## 2. Numbers

| Run | answers | refused | false-refusal | correct (not-in-pack / retrieval-miss) | unknown-dropped | answer in wiki-vital5 only |
|---|---|---|---|---|---|---|
| factual `…14de107.jsonl` | 38 | 21 (55%) | **2** (5% of answers) | 14 (14 / 0) | 5 | 13 |
| device `…14de107-device.jsonl` | 52 | 27 (52%) | **1** (2% of answers) | 17 (16 / 1) | 9 | 13 |

Every `false-refusal` and every `correct-refusal` is `gate-after-draft`, and every `unknown-dropped` is `no-source`.

## 3. Ids by kind

**Factual run (21 refusals)**
- false-refusal (2): `vit-cry-009` (EIP-7251 gives 32 and 2048 ETH), `vit-fa-011` (Wikivoyage WWI: "The defeated Central Powers were forced to give up their colonies to the Allied powers").
- correct-refusal (14): `vit-cry-005`, `vit-cry-006`, `vit-cry-007`, `vit-cry-010`, `vit-fa-003`, `vit-fa-004`, `vit-fa-013`, `vit-fa-014`, `vit-fa-015`, `vit-fa-023`, `vit-fa-027`, `vit-hum-004`, `vit-hum-005`, `vit-trv-004`. All 14 are not-in-pack.
- unknown-dropped (5): `vit-fa-005`, `vit-fa-010`, `vit-fa-021`, `vit-hum-001`, `vit-hum-002`.

**Device run (27 refusals)**
- false-refusal (1): `vit-cry-009`.
- correct-refusal (17): `vit-cry-006`, `vit-cry-007`, `vit-cry-010`, `vit-fa-003`, `vit-fa-008`, `vit-fa-009`, `vit-fa-013`, `vit-fa-014`, `vit-fa-023`, `vit-fa-027`, `vit-hlt-001`, **`vit-hlt-002` (retrieval-miss: Wikivoyage "Altitude sickness" is installed and answers the question; only "Andes" was retrieved)**, `vit-hum-004`, `vit-hum-005`, `vit-hum-006`, `vit-sci-002`, `vit-trv-004`.
- unknown-dropped (9): `vit-fa-005`, `vit-fa-010`, `vit-fa-021`, `vit-fa-026`, `vit-hum-001`, `vit-hum-002`, `vit-hum-003`, `vit-sci-001`, `vit-sci-003`.

**Answer article only in wiki-vital5** (the coverage lever):
- `fa-003` (Japan, 12x million confirmed in the text), `fa-004`, `fa-005`, `fa-010` (Measles), `fa-011`, `fa-013` (Giraffe), `fa-015`, `fa-021` (Tiger, Lion), `fa-027` (Taiwan), `hum-001`/`002`/`003` (Mozi, Mohism), `hum-004`, `hum-005`, `hlt-001` (Box jellyfish), `sci-002`.

Machine-readable versions: `data/refusal-audit-*.json` (per row: `refusal_kind`, `auto_kind`, `evidence`, `mechanism`, `retrieved`, `answer_in_installed_pack`, `answer_in_reference_pack_only`).

## 4. What `eval-iphone.mjs` / the in-app harness must record

The `sources` event already carries the whole `RetrievedChunk` (`chunkId`, `docId`, `title`, `body`, `source`, `score`, `similarity`, `relevance`; see `src/rag/retrieve.types.ts`, `src/rag/db.ts:205`). But `src/eval/answerEval.pure.ts:103` keeps only `.title`, and chunks the gate drops never reach the event (`src/routing/answer.ts:839`). To judge refusals from passage text instead of article proxies, a row needs:

1. `retrievedSources[]`: `{title, source, chunkId, score, similarity, relevance, text}` for the last `sources` event. `text` can be capped at ~600 chars. Change `answerEval.pure.ts:103` to map the full chunk, not just `.title`.
2. `droppedSources[]`: the same fields for chunks removed by the relevance gate (`answer.ts:839`, `off-topic-dropped-N`) and the health gate (`:848`), with the drop reason. This is what makes the `unknown-dropped` rows (5 and 9 here) classifiable.
3. `declinedDraft`: the model's draft text when the gate declines after drafting (`answer.ts:1224` `all-citations-removed`, `:1242` `uncited-with-sources`), plus which citations were removed. That separates "the draft was right but uncited" from "the draft was unsupported".
4. `installedPacks`: pack ids + manifest sha on the device at run time. Today the inventory is not in the rows, so "not-in-pack" is relative to the requested assets, not measured.

## 5. For modelos ai #2 (gate fix)

- **Don't loosen the citation gate globally.** 17 of the 18 gate-after-draft refusals in the device run had sources that lack the answer, so a looser gate would turn most of them into confident-wrong answers.
- **The one systematic false refusal is computational.** `cry-009` needs arithmetic on numbers present in the source (32 / 2048 ETH). The draft can't cite a derived number, so the gate removes it. A targeted fix: let an answer cite the passage that holds the operands.
- **fa-011** is the only case where a travel guide answered a history question. The gate likely judged a Wikivoyage page off-topic for "Who won WWI".
- **Bigger lever (not the gate): install `wiki-vital5`**, or fold those leads into the default kit. It would give answer articles to 13 refusals in each run. Size: 156 MB locally, which the setup decision puts in the "Curious" profile.

## 6. Run 3: device 52 WITH wiki-vital5 (same build 14de107, same flags)

Run: `rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device-vital5.jsonl` (Plumb, A/B #6).

```sh
python3 rnd/lantern/tools/precheck.py <run3.jsonl> --refusals \
  --installed-packs boar-crypto,boar-wikivoyage-en,wiki-vital5 --hand rnd/lantern/data/refusal-hand-14de107-vital5.json
```

`--installed-packs` is new: wiki-vital5 is counted as installed, so un-prefixed titles ("Mozi", "Lion") are looked up in it. wiki-vital5 holds **introductions only** (~1.2–1.7k chars per article), so a title match does not prove the answer is in the text. Every title-based case was read (`data/refusal-hand-14de107-vital5.json`).

| Run | answers | refused | false-refusal | correct (not-in-pack / retrieval-miss) | unknown-dropped |
|---|---|---|---|---|---|
| run 2, device without vital5 | 52 | 27 (52%) | 1 | 17 (16 / 1) | 9 |
| **run 3, device + vital5** | 52 | **18 (35%)** | **3** (6% of answers) | 10 (7 / 3) | 5 |

- **false-refusal (3):** `vit-fa-018` (vital5 "Paris": "Paris is the capital and largest city of France"), `vit-fa-011` (Wikivoyage "World War I": the defeated Central Powers…; the vital5 lead stops before the outcome), `vit-hum-005` (vital5 "Invisible hand": "used once in his Wealth of Nations").
- **correct-refusal (10):**
  - `vit-cry-006`, `vit-cry-007`, `vit-cry-010`, `vit-hum-006` (not-in-pack);
  - `vit-hlt-001`, `vit-hum-004`, `vit-sci-002` (retrieval-miss: Box jellyfish, The Lord of the Rings, Japan/Germany are in vital5 but were not retrieved);
  - `vit-fa-021` (vital5 "Lion" lead retrieved, no weight or tiger comparison);
  - `vit-hum-002` (partial source: the Mozi lead says "universal love" against Confucianism, but nothing on graded love or Mencius);
  - `vit-trv-004`.
- **unknown-dropped (5):** `vit-fa-010`, `vit-hum-001`, `vit-hum-003`, `vit-sci-001`, `vit-sci-003`. The first three have their answer article in vital5 (Measles, Mozi, Mohism), but the gate dropped every source.
- All false and correct refusals are again `gate-after-draft`, and all unknown ones are `no-source`.

**Reading, which agrees with Plumb's:** vital5 cut refusals from 27 to 18, but the false-refusal count went **up** (1 → 3). The right article now comes back more often, and the citation gate still declines the draft: Paris is the plainest case. The next bottleneck is the **gate/model over good sources**, not coverage. Three more refusals (hlt-001, hum-004, sci-002) are retrieval misses inside vital5.

## Decisions / Options / Tasks

**Decisions (Lantern):** `false-refusal` counts only with title evidence, or strong text evidence confirmed by hand. Weak text hits are always hand-checked (`--hand`).
**Options:** O1. Re-run the device subset with `wiki-vital5` installed (~10 min) to measure the coverage lever directly. O2. Implement §4 in the harness (owner: eval/app session, via coordinator).
**Tasks:** [x] audit tool + both runs + id lists. [ ] Plumb: add the §2 table to the report. [ ] modelos ai #2: §5.

**Metric:** false-refusal = 2/38 (factual), 1/52 (device), **3/52 (device + vital5)** of answers.
**Next step:** for modelos ai #2, the 3 run-3 false refusals (fa-018 Paris, fa-011, hum-005) are the gate test cases, alongside cry-009. For the harness, §4 item 2 (`droppedSources`) would make the 5 unknown-dropped rows classifiable.

## UNKNOWN

- (Runs 1–2) Which Wikipedia tier was actually on the phone. A retrieved title like "Japan at the 1986 Asian Games" shows some Wikipedia chunks were present, but `wiki-vital5` membership is unverified. If vital5 *was* installed, the 13 "vital5 only" cases become retrieval misses.
- Passage-level truth: the evidence is article-level, from the local pack copy. The passage the app actually retrieved may not contain the answer sentence (e.g. EIP-7251's constants table).
- The 9 `unknown-dropped` rows (device run) cannot be classified until the harness records `droppedSources` (§4).
