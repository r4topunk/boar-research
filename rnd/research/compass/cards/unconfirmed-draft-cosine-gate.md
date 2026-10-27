# Decision 1: what to show when the compact tier's citation check fails (cosine gate for "not confirmed" drafts; the small-LLM entailment check rejected)
TL;DR: 44 % of the drafts the citation check declines are actually correct (precheck), and 7 % are confident-wrong. A 1.5B/4B "does the source state this?" check does not separate them, but bge-small cosine between the draft and its best source chunk (≥ 0.70) raises the share of correct drafts among those shown from 44 % to 59 % and cuts confident-wrong from 3 to 1. Proposed as a filter on top of Decision 1 option A, at ~0 ms cost.
Lane: Compass · Status: tested (pre-registered replay on d1a slice40 s42: FAIL) · Priority: C
Axes moved: quality ↑ (correct drafts shown instead of declined; option A's gain) with **truthfulness protected** (fewer confident-wrong than plain A) · latency ~0 (one embedding of the draft + dot products against chunk vectors that already exist) · resources 0.
Fits BOAR? Yes for EN, on both tiers: bge-small is resident, and chunk vectors exist (packs ship them; seed corpus embeds them). **PT drafts: probably not.** bge-small-en is English-only, and a PT draft vs an EN chunk will score low (UNKNOWN, not measured: tonight's pool has 0 PT drafts). For PT, option C (lexicon word check) or plain A with the label remains.
Evidence:
- **Local measurement (Compass, 2026-10-01, `exp/verify/`).** Sources:
  - drafts: every compact-tier draft declined by `grounding:all-citations-removed-declined-compact` (23) or `uncited-with-sources-declined-compact` (32) in the night's iPhone-profile traces (`boar-eval/runs/night-2026-10-01/ios-main-{s42,s43,v58x-s42,v5-t0}`, engine 0cfd4a77, Qwen2.5-1.5B), 55 unique drafts / 37 items;
  - labels: the bench's own precheck (`scorers/vendor/lantern/precheck.py`) on the draft text; 45 gradable, 28 unique items;
  - passages: rebuilt from the packs (zstd blocks) for the shown/raw source titles. The top-2 1000-char chunks by similarity to the draft are an approximation of what the model saw, because traces don't keep context text.

  | Policy on a declined draft | Shown | Correct among shown | Fail-missing | Confident-wrong | Correct kept |
  |---|---|---|---|---|---|
  | decline (main today) | 0/45 | — | — | 0 | 0/20 |
  | option A: show all, labelled | 45/45 | 44 % | 22 | **3** | 20/20 |
  | + Qwen2.5-1.5B yes/no "sources state the main claim?" | 26/45 | 38 % | 15 | 1 | 10/20 |
  | + Qwen3-4B yes/no (same prompt) | 10/45 | 50 % | 4 | 1 | 5/20 |
  | **+ cosine(draft, best chunk) ≥ 0.70** | 27/45 | **59 %** | 10 | **1** | **16/20** |
  | + cosine ≥ 0.75 | 20/45 | 60 % | 7 | 1 | 12/20 |

  - Median cosine by label: pass 0.79, fail-missing 0.66, confident-wrong 0.63.
  - Per item (first draft only, 28 items): all 39 % pass / 3 CW, versus cos ≥ 0.70 at 53 % / 1 CW.
  - The CW that survives every filter is `vit-cry-009` ("before EIP-7251 you needed 32 ETH to stake 10,000 ETH"): an arithmetic/logic error over correct facts, which no similarity or yes/no check catches.
  - **Strength: weak-moderate.** n is small and the drafts are correlated (4 runs, same items). Precheck is a lexical grader, and the passages are approximate. The threshold 0.70 was read off this data, so it is in-sample.
- **Why the LLM check fails here:** "precheck-correct" ≠ "stated in the passage". Many correct drafts come from model memory with a related source (the citation check declined them for exactly that reason), so an entailment check rejects correct and wrong alike. Cosine measures topical closeness, which tracks "the draft is about what the source is about" and correlates with correctness at this tier. This also argues against spending 0.75–2.4 s (desktop; more on phone) on an LLM check.
- **Dedicated small fact-checkers (literature; not runnable in llama.rn today):**
  - MiniCheck-Flan-T5-Large (770M): 74.7 % balanced accuracy on LLM-AggreFact, ≈ GPT-4 (Tang, Laban, Durrett, EMNLP 2024, https://arxiv.org/abs/2404.10774).
  - HHEM-2.1-Open (110M, flan-t5-base, English-only; the cross-lingual HHEM-2.1 is commercial) (https://huggingface.co/vectara/hallucination_evaluation_model).
  - LettuceDetect (ModernBERT token classifier on RAGTruth; multilingual EuroBERT versions for de/fr/it/es/pl/zh, **not PT**; tiny Ettin variants) (https://github.com/KRLabsOrg/LettuceDetect, https://huggingface.co/blog/adaamko/lettucedetect-multilingual).
  - All of these are classification heads (seq/token), which llama.rn doesn't run (it runs generation, embedding and rerank). Shipping one means a new runtime (onnxruntime-react-native): a multi-day engineering change and Anvil's call. Accessed 2026-10-01.
Test in boar-eval:
- **Replay, no new run (pre-registered now, before d1a results are read by me):** on tonight's `d1a-unconfirmed` traces (seed 42, PT slice + 72 set), take every **newly shown** answer (d1-metrics definition) with its judge label. Recompute cosine(draft without the label/snippet, best chunk of its shown sources) with bge-small, using pack chunk text by title, as in `exp/verify/collect.py` + `verify.mjs`.
- Policy "A + cos ≥ 0.70" vs plain A. **Success:**
  1. confident-wrong among shown ≤ ½ of plain A's (or both 0);
  2. ≥ 70 % of plain A's judge-pass answers are still shown;
  3. report PT and EN separately; if PT pass-recall < 50 %, the gate applies to EN questions only.
- If it passes the replay, the arm is d1a + 15 lines (cosine gate before `showUnconfirmed`), run on the gate + PT slice with ≥ 2 seeds.
Cost to try: replay ~1 h once d1a traces exist (CPU, bge only). Arm patch ~2 h. No downloads.

## Replay result (2026-10-01 ~23:20; `exp/verify-replay/`; threshold 0.70 frozen in this card before I read any d1a output)
- Set: the 20 items declined in `ios-main-slice40-s42` by the compact citation codes and shown by `ios-d1a-slice40-s42` (all 20 carry `grounding:unconfirmed-shown`). Labels are the d1a judge's (judge.v1, both orders; correctness ≥ 4 pass, ≤ 1 cw). 13 PT, 7 EN.

  | | shown | pass | fail | cw |
  |---|---|---|---|---|
  | plain A, all | 20 | 3 | 7 | **10** |
  | A + cos ≥ 0.70, all | 13 | 2 | 6 | 5 |
  | plain A, EN | 7 | 2 | 3 | 2 |
  | A + gate, EN | 7 | 2 | 3 | 2 (the gate removes nothing) |
  | plain A, PT | 13 | 1 | 4 | **8** |
  | A + gate, PT | 6 | 0 | 3 | 3 |

- Pre-registered checks:
  - (1) CW ≤ ½ of plain A: 5 vs 10, **PASS (at the limit)**;
  - (2) ≥ 70 % of plain A's passes still shown: 2/3 = 67 %, **FAIL**;
  - (3) PT pass-recall 0/1 < 50 %, so the gate would be EN-only, and on EN it removes nothing.
  - **Verdict: FAIL.** Demoted to C.
- **The bigger finding:** on this slice the drafts the citation check declines are mostly wrong. That holds even more in PT, where judge-cw is 8 of 13 ("Quito … capital do Japão", "O Saara é um vasto continente"). My offline estimate (44 % correct / 7 % CW) was far too optimistic, for two reasons:
  - the precheck only flags cw on explicit `forbid` terms, so it under-counts hallucinations the judge catches;
  - the night pool had no PT drafts.
- So **the citation check's PT declines look mostly correct, not over-strict.** This argues against showing unconfirmed PT drafts (option A on PT) and against loosening the check for PT (option C), unless C's kept answers are judged clean. n = 20, one seed. The cw/fail boundary is the judge's weakest call (cycle 5: 3/20 vs hand), but 10 cw vs 3 pass is far outside that error.
- What would still help PT: a better answer, not a better check. Two candidates: the instant snippet itself (d1a appends the source's sentence, so show **only** the snippet, translated by the template, instead of the draft), or the 4B tier.

## Body

### What this says about Decision 1 (A vs C)
- **Option A alone shows ~3 confident-wrong per ~45 declined drafts (7 %).** That is inside d1a's frozen A-truth bar (≤ 10 % of newly shown), but only just. With iPhone-scale run-to-run noise, a second seed could cross it.
- **Option C** only helps PT, and only by restoring word overlap. It doesn't make the answer more correct.
- **A + cosine gate** keeps 80 % of the correct drafts and removes 2 of 3 CW. It's the cheapest way to make A safer, for EN.

### Honest labelling (the second half of the coordinator's question)
- What the label can truthfully say depends on what was checked:
  - cited and the word check passed → normal answer with [n];
  - **cosine-gated draft** → "Not confirmed by the sources: they cover this topic but don't state this answer. Check before relying on it." (true: topical match, no statement match);
  - below the gate → the decline.
- The label must not say "verified", "according to the source", or keep a [n] that the check removed. d1a already strips unsupported [n] and appends the source's own sentence. Keep that: the user sees what the source actually says next to the unconfirmed claim.
- Safety queries stay strict (d1a already excludes `isSafetyQuery`). This gate must never relax that.
- UNKNOWN: whether users read such labels. No on-device UX data; the bench can't measure it.

### What would make it fail
- PT drafts (cross-lingual cosine with an English embedder).
- Drafts that are on-topic but wrong in a detail (numbers, comparisons: the `vit-cry-009` pattern). Comparisons are 5 of the 45, and their CW risk is the highest.
- Threshold over-fit: 0.70 vs 0.75 changes recall a lot (16 → 12 of 20). The replay uses 0.70 as frozen. Don't retune on the replay.

### Off-the-shelf candidates (see `../../SHELF.md`)
- `Linuss4880/MiniCheck-Flan-T5-Large-Q4_K_M-GGUF` (MIT, 487 MB): a ready GGUF of the strongest small fact-checker. Next local test, if T5 runs in node-llama-cpp.
- `gpustack/bge-reranker-v2-m3-GGUF` (Apache-2.0, 422 MB Q4_0): multilingual, via llama.rn `rerank()`. A candidate for the PT draft ↔ EN source check.
- `keisuke-miyako/multilingual-e5-small-gguf-q8_0` (132 MB): a cross-lingual cosine gate for PT drafts.
