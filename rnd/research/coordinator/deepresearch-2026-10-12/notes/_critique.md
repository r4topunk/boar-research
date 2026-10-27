# Completeness critique: deep research 2026-10-12

Critic pass on 2026-10-12. Inputs: CONTEXT.md, all 9 notes files (datastores, retrieval, models_moe, knowledge_injection, engine_speed, generation_quality, structured_knowledge, eval_judge, prior_art), CLOSED.md, the 10-06/10-09/10-12 sweeps, arms/wikisection/WIKISECTION.md, and our top-100k pack `meta`.
Web: 2 fetches (a competitor team BENCHMARKS.md; arXiv 2609.04575 abstract).
**No researcher failed.** All 9 notes files are present, and each has a TL;DR, tables, a "found nothing" list and an UNKNOWN section.

## 0. A premise in CONTEXT.md is narrower than it reads (affects every angle)

CONTEXT says "the missing facts are not anywhere in the enwiki pack on 12/13 V-para items checked, so the facts live outside Wikipedia". WIKISECTION.md and the pack `meta` show that the check was narrower than that:

- **(a) Only the top-100k pack was checked.** It holds 98,389 articles from FineWiki's August 2025 Enterprise dump (`meta.sources`), not the full 15-shard enwiki.
- **(b) Items without a kept source were not checked.** Only the 13 + 1 V-para items that kept a source were tested. The 29/51 no-kept-source items carry 50–55 % of the loss and were never tested.
- **(c) On v0.2 the fact was often found.** The H5b anywhere-gate found it on 13/30 on-topic items (43 %) and 7/14 off-topic items, unverified.

**Consequence:** "Wikipedia is closed as a source" is proven only for top-100k × kept-source items × an August 2025 snapshot. A full-shard plus fresh-dump anywhere-gate over all absent items, the no-kept ones included, is the cheapest missing measurement. It extends datastores' WIKIFRESH proposal.

## 1. Open problems without a relevance ≥ 2 finding, and angles nobody tried

| open problem | coverage in the notes | verdict | untried angles / sources |
|---|---|---|---|
| Absent knowledge, no kept source | Many relevance-2 candidates: FCDO, SE practical, the post author blog, CDC, WikEM, Factbook (datastores); QINDEX/SPARSEDOC (retrieval, bounded by the B2 slice); WDGATE (structured); Qwen3-Next-80B (models, IKP-law projection +0.02 < MDE). Only one relevance-3 item: a competitor team freshness. | covered, but every candidate is gated on a coverage probe no one can run without items | (1) **Domain histogram of the reference answers' citations.** The reference is frontier + web. Count the domains/URLs it cited, aggregated and coordinator-only, to pick corpora by evidence instead of guessing. (2) Permissive synthetic-knowledge corpora: HF Cosmopedia v2 (Apache-2.0), Nemotron-CC synthetic QA, FineWeb-Edu-derived QA sets (check the licence per item). (3) Wikinews (CC BY 2.5) and Wikipedia "Current events" portal pages, for post-2025 facts. (4) Open Food Facts (ODbL), World Bank / OECD / UN data (CC BY 4.0) for numeric country/city facts. |
| Wrong facts | Integrative Decoding and ThinkMerge (relevance 2, 0-call seed-specificity gate); CoCoA (only with a kept source); SEP probes; KG-Infused RAG | covered at relevance 2 | (1) Measure the wrong-claim *type* split from the LOSSMAP rationales (numeric / date / entity-swap / stale) before choosing a lever. No note proposes this. (2) Numeric-claim verification against FACTS/Wikidata at answer time. Prior work: "FActScore-style claim checking with a local KB", e.g. VeriScore/FactCheck-Bench, and SAFE without web. (3) Staleness: the Qwen3.6 training cutoff vs the reference's dates. Nobody separated "wrong" from "outdated". |
| Comparison / synthesis cells (ratio 0.47) | generation_quality Q5 found no inference-time method; MEBench relevance 1; DER-RAG closed (SYNTHDEEP); KG-Infused RAG gated on a low-prior WDGATE; Factbook mentioned | **no direct relevance ≥ 2 finding** | (1) CLEF Touché comparative-question / comparative-argument retrieval tasks (2020–2022) and the CAM comparative argumentative machine. (2) Query-focused multi-document summarization for small LMs, e.g. QMSum / AquaMuSe follow-ups 2024–26. (3) Open per-entity attribute tables for "X vs Y": Wikipedia infobox extractions (DBpedia infobox dumps, CC BY-SA), World Bank WDI, Numbeo alternatives with open licences. (4) Opinion and comparison text in SE travel/expatriates answers, measured *for comparison items specifically* (datastores lists SE but gates it on absent items only). |
| Deep-tier phone latency | engine_speed is thorough: k2 renorm, NPU prefill, iqk, cache sizing, DEER; prior_art adds PR #219 | covered | (1) **Remote real-device access to a 12 GB Snapdragon:** Samsung Remote Test Lab, AWS Device Farm, Qualcomm AI Hub devices, BrowserStack. The single largest blocker is "no device", and nobody checked whether a rented device could run bmoe. Account and ToS actions belong to r4to. (2) Time-to-first-useful-content UX: stream a sourced card before thinking finishes. Prior art is a competitor team's [competitor score removed] s card. (3) Thermal-sustained numbers for 8 Elite Gen 5 (only Tensor G3 is measured). |
| Honest number / held-out v0.3 | eval_judge: GDPval wins+ties, ResearchRubrics binary criteria, n ≈ 140 for ±0.03, preference-leakage papers, cross-app regrade | covered as methodology; **missing a concrete non-Claude judge/reference path** | (1) Real human-written query pools as v0.3 seeds without Claude leakage: WildChat (ODC-BY) filtered to travel/research intents, MS MARCO / Natural Questions real queries, Researchy Questions (already named, not scoped). (2) Cost and availability of GPT-5.x / Gemini 3 judge APIs for a family-balanced panel (eval_judge names the need, not the path). (3) A human spot-check budget sized by evalstats PPI (about 25 labels): who does it, and the protocol. |

## 2. Relevance-3 findings to demote

| finding | reason |
|---|---|
| **k2 renormalisation** (arXiv 2609.04575) | Fails the relevance-3 bar on its own note's numbers. Engine_speed estimates +15–35 % decode on a compute-bound G3, which is a 13–26 % cut in answer time, below the 30 % threshold. The paper has **no wall-clock** (confirmed in the abstract) and only MMLU/GSM8K. The fetched abstract mentions MMLU only, so the GSM8K figure needs the full text. Knowledge-sensitive buckets (absent/wrong) are untested, and bmoe's sibling lossy knob (prefer-cached) cost −4 tinyMMLU. Its novelty label (closed_family_new_mechanism) is reasonable: no CLOSED row covers reduced-k. But it cannot be measured on a phone (none in hand), so it is a **desktop speed proxy only**. Demote to relevance 2. |
| **BigMoeOnEdge PR #200** (NPU prefill + CPU decode) | Labelled known: it is moe-on-device row 12 and competitors.md (10-06), not new. It is Snapdragon Hexagon ≥ v73 only, and **does not support our UD-Q2_K_XL experts** (Q4_0/Q4_K_M only, which means a 22.3 GB file). It is not in any release (v0.28.0 has no Android NPU prefill per WEB-SWEEP-2026-10-12). Decode drops 5–13 % with the NPU resident, and PR #219 measured 3.13 tok/s decode with the NPU armed. On today's G3 profile prefill is about 15–25 % of answer time, so the net time cut is probably < 30 %. Demote to relevance 2, device-blocked. |
| **a competitor team fresh-Wikipedia snapshot** | Keep as the top datastore test but flag its evidence strength. The +[competitor score removed] gain ([competitor score removed] → [competitor score removed]) is **inside a competitor team's own stated one-run noise of ±[competitor score removed]**. It is a single run, and the out_of_corpus n is not stated (BENCHMARKS.md fetched 10-12). The same doc calls breadth packs' 0.434–0.479 movement "noise". Our staleness is about 13 months; theirs was about 3 years (2023 → 2026-09). Labelled known (competitors.md 10-06 already proposed "check our pack snapshot dates"; it was never acted on). Not a constraint violation: a fresh dump > 100 MB needs r4to's OK. Do not demote, but treat the gain as unconfirmed. Use it only as a reason to run the 0-call anywhere-gate (§0), not as a predicted Δ. |

Other demotions to keep out of the action list (relevance < 3 in notes, listed to prevent re-work):
- **Qwen3-Next-80B:** est. 2–3.5 tok/s, so 7–10 min per thinking answer; IKP-law projection +0.02 < MDE.
- **K-quant Q3_K experts:** a > 100 MB download needs OK.
- **HOBBIT:** a second expert copy on disk.
- **Genie/LiteRT 4B:** proprietary QAIRT runtime, Snapdragon-only, outside llama.rn.
- **Licence violations, never ship:** WikiExpert-8B (CC-BY-NC), PAQ code (CC-BY-NC), DDInter (NC), jina v5 (NC), CRAG data (NC, eval only), RocketEval (paper NC-SA).

## 3. Contradictions (pairs)

1. **CONTEXT.md vs WIKISECTION.md.** CONTEXT says "facts not anywhere in the enwiki pack", while WIKISECTION checked only top-100k, kept-source items, August 2025, and v0.2 found 43 % (see §0).
2. **knowledge_injection vs retrieval on HyPE novelty.** knowledge_injection labels it known (precomputed rows 23–25, O6); retrieval labels it new. precomputed-knowledge.md rows 23/25 cover Raina & Gales and Doc2Query-- at abstract level, not HyPE itself. Resolution: the idea is known, HyPE's numbers are new.
3. **a competitor team BENCHMARKS internal.** A +[competitor score removed] freshness gain is called "the big gain", while a ±[competitor score removed] movement from breadth packs is called noise, in the same doc. datastores and prior_art repeat both without reconciling them.
4. **engine_speed vs prior_art on Snapdragon decode.** engine_speed's 8 Elite Gen 5 budget table uses decode 5.0–6.5 tok/s with NPU prefill. prior_art (PR #219) measures 3.13 tok/s decode with the NPU armed (Q4_0), and moe-on-device row 12 gives 3.21–3.25. The "75–100 s" and "≈ 1.7–2.2 min" Snapdragon estimates are therefore optimistic by up to about 1.6×.
5. **Closed-venue error counts in a competitor team, three different numbers.** structured_knowledge says "44 in one grading". prior_art says "38 of 73 errors". eval_judge says "44 of 86 errors". These are probably different gradings, but none of the notes says which. Pin the exact note and version before quoting.
6. **a competitor team corpus.** competitors.md (10-06) gives 36.8 GB storage and "2M articles in full, 21 GB". prior_art (10-12) gives 46.2 GB and 6.06M articles full text, 30.1 GB. This is version drift, not a contradiction. Quote with version 1.8.0.
7. **Qualcomm Qwen3-4B on mobile.**
   - dense-speed-android (10-06): "not supported on any mobile chipset".
   - engine_speed (10-12): the HF card lists Qwen3-4B-Instruct-2507 Genie binaries at 26.7/28.0 tok/s.
   - arXiv 2607.05475: Genie at 8.9–12.2 tok/s for a 3B.
   engine_speed resolves the first pair; the 3× framework gap stays open.
8. **the post author's speed bar.** CONTEXT gives 50 tok/s tolerable / 90 ideal (blog, primary). prior_art gives "> 100 tok/s feels fast" (a 10-04 X post via secondary crypto.news; the original is unreadable). Do not cite the 100 figure as primary.
9. **Licence details for Kiwix tooling.**
   - datastores: python-libzim GPL-3.0.
   - prior_art: libzim GPL-2.0, libkiwix GPL-3.0.
   Both can be true for different packages. Only matters if anything links them; build-time use is fine either way.
10. **RAG-in-the-Wild vs datastores' SE proposal.** RAG-in-the-Wild: SE-only retrieval lowers a 4B on SimpleQA (0.021) and MMLU. Datastores still proposes an SE pack. This is reconciled only by the R2-only / quota entry rule, which must be in the arm criterion.

## 4. Load-bearing claims to verify adversarially (primary source)

| # | url | exact claim | why it decides something |
|---|---|---|---|
| 1 | arms/wikisection/WIKISECTION.md + shared-data/packs/boar-wiki-en-*.sqlite (local) | Missing V-para facts are absent from the **full 15-shard enwiki** and from a **2026-09/10 dump**, including the 29 no-kept-source items (only top-100k × kept-source items were checked) | Decides whether the next datastore spend is Wikipedia-refresh or non-Wikipedia corpora |
| 2 | [competitor link removed] | Fresh 2026-09-01 Wikipedia raised the judged ratio 0.464 → 0.508 and out-of-corpus 0.33 → 0.65 beyond the ±0.05 one-run noise (n per category, repeat runs) | The only external evidence for WIKIFRESH; a single run inside noise |
| 3 | https://arxiv.org/html/2609.04575v1 | Qwen3.6-35B-A3B with top-4 of top-16 renorm: MMLU −0.35 pp (p 0.66), GSM8K −0.6, and routed params halved; no wall-clock speed | Justifies a K2HALF desktop arm; quality on knowledge recall is untested |
| 4 | https://github.com/Helldez/BigMoeOnEdge/pull/200 and /pull/219 | NPU prefill 1,418 tok in 8.2 s; decode with the NPU armed (3.13 vs 3.41–3.69 vs 5.0 tok/s); Q3_K and lower experts unsupported | Sets the device plan (Q4 file, Snapdragon only) and the latency claim |
| 5 | https://arxiv.org/html/2507.20059v1 | Qwen3-4B SimpleQA: Wiki-only 0.281, SE-only 0.021, all sources 0.339; LLM source routing does not beat "all" | The prior that single niche packs hurt; sets the pack entry rule |
| 6 | https://www.gov.uk/api/content/foreign-travel-advice/thailand + https://www.gov.uk/help/terms-conditions | FCDO travel advice is OGL v3, 226 countries, ≈ 4.7k words per country, via a keyless API | The cheapest new travel-practical source; licence is load-bearing for a public repo |
| 7 | https://archive.org/details/stackexchange_20260630 | Community SE dump through 2026-06-30 with per-site sizes, CC BY-SA per post, and no binding "no-LLM" term on the re-upload | Decides whether the SE practical/crypto packs can ship |
| 8 | https://arxiv.org/abs/2410.01556 | Integrative Decoding: LongFact F1@128 +5.7 on Qwen2-7B, recall 57.1 → 64.2, precision +1.7; text-level ensembles lose 3–25 F1 | The only wrong+thin lever with closed-book long-form gains; reopens the DEEPBO2 family with a new mechanism |
| 9 | https://github.com/19PINE-AI/ikp/blob/main/data/results/evaluation_summary.json | Qwen3-Next-80B IKP 0.564 (T4 0.71) vs Qwen3.5-35B-think 0.548 (T4 0.55), with mode confounds (instruct vs think, BF16) | Decides whether an 80B screen is worth a 30 GB download |
| 10 | https://arxiv.org/html/2510.04374v1 | GDPval headline = wins + ties, best 47.6 %, human agreement 71 % / auto-grader 66 % (fetch-summary only) | Would change the claim's headline metric |

## UNKNOWN
- Researchers' per-finding relevance scores were not in the notes, so §1 coverage is judged from the note text and the relevance remarks inside it.
- Whether the full enwiki shards were ever gate-checked anywhere else in rnd: not found in WIKISECTION, CLOSED or the sweeps.
