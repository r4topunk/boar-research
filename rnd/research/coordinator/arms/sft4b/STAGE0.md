# SFT4B stage 0: data + environment (2026-10-13, criterion sha 5853b8ea…, unedited)

## Verdict: STOP (environment), data side PASS
- **Blocked:** the bf16 weights were not downloaded. Qwen/Qwen3-4B-Instruct-2507 at rev cdbee75f… is 8,060,917,568 B (7.51 GiB). The mini has 29 GiB free, so 22 GiB would be left, under the 25 GiB floor. `tools/mini/download_base.sh` refused, and `<runner>/kiln/sft4b/download.status` says BLOCKED. So the 50-step smoke LoRA and the base→Q4_K_M export-parity test were **not run**.
- **Unblock (coordinator):** stage 0 parity and stage 1 both peak at about 15 GiB of transient space: base + f16 GGUF, or base + merged model. The f16 can be deleted after quantizing, and the base after merging. For the floor to hold, the mini needs about 40 GiB free. Class-B candidates from DISK-LOG: `kiln/wikifull-b` raw.jsonl 3.1 GB (T2 is closed), `kiln/packs/{dl,work}` ≈ 1.3 GB, `<runner>/ci/node_modules` 1.6 GB. That gives ≈ 35 GiB, still short. Another option is a declared temporary dip below the floor.

## 1. Disjointness (`tools/disjoint_check.py`, seed 42)
- 798 articles are excluded across the 11 packs: 225 self-test item sources (+ in_pack_facts articles), 435 item-draw candidates (a conservative extra) and 138 same-stem or word-prefix titles. They are listed in `data/excluded-articles.json`, with stem hashes.
- Pool: hold-out 100 articles reserved first (10 + 9 × 10), then 1,500 training candidates (140 per wave-1/2 pack, 120 per wave-3 pack), each with 1–2 adjacent chunks. For SE packs the first chunk comes from the answers. 5 hold-out articles failed 5 writer rounds and were replaced by seed-4242 draws (`holdout-pool-extra.jsonl`).
- `--check` on pool, hold-out, extra, train and hold-out sets: **0 excluded-id overlaps, 0 same-stem overlaps, 0 train∩hold-out** (`aggregates/disjoint.json`).

## 2. Renderer (`tools/render_prompt.py` + `render_core.mts`)
- The renderer calls the cut-7 tree's own `sectionAt`, `isSubstantive`, `compressContext` (budget 1200, ≤ 4 sentences per chunk) and `assembleChatMessages` with the succinct persona and style reminder. Pack titles are bare for sources ≥ 9, as cut 7 does.
- Replay of SEEDGEN B1 (15 qa-health-se prompts, raw chunk ids from densechunk-st OFF, kept set from the B1 traces): **passage block byte-identical 15/15; full system+user byte-identical 10/10 on items with passages**. Of the 5 no-source items, 3 match and 2 differ only by the engine's no-source style suffix, which training never uses (`aggregates/render-validate.json`).

## 3. Writer (`tools/write_examples.py`, `write_all.sh`, `write_round.sh`)
- Haiku 5.5 (`claude -p --model claude-haiku-5-5 --effort low`, isolated like boar-eval's claude-cli) wrote 5 candidates per call, 4 calls in parallel, with a JSON schema and per-batch caching. It answers extractively and cites by letter. Letters are mapped to the rendered `[n]` after compression.

## 4. jev filter (`tools/filter_jev.py`)
- One request per example on {passages = rendered context block, question, answer}, both thresholds frozen: quote_supports ≥ 0.9 and answers_question ≥ 0.8. Every verdict is cached.
- **2,174 requests, [usage detail removed] spent** (cap [usage detail removed]; [usage detail removed].505 → 0.447).
- **Round-1 pass rate 1,103/1,593 = 69.2 %**, above the 50 % stop rule. By pack: factbook 0.89, simplewiki 0.85, firstaid 0.83, health 0.74, outdoors 0.69, bitcoin 0.67, cooking 0.65, medlineplus 0.64, travel 0.59, money 0.57, ethereum 0.47.
- Retry rounds (one near-verbatim sentence) on articles that failed. Over all rounds: 1,364/2,087 = 65.4 %. Drops: 621 quote_supports, 125 answers_question, 8 before jev (cited chunk compressed away, or a missing or bad marker).

## 5. Datasets (mlx-lm chat format; metadata in `*.meta.jsonl`)
- `data/train.jsonl`: **1,200** examples, water-filled to ≤ 117 per pack (cooking 93, ethereum 89, money 92, travel 108; the rest 116–117). 969 from round 1, 231 from round 2. sha 8b15e48d…
- `data/holdout.jsonl`: **100** examples, one per reserved article, never trained on. sha e1fc1d0b…
- Lengths: at most ≈ 900 tokens per example (well under 2,048). Answers have a median of 16 words (max 40).
- Leakage: the highest word-Jaccard with any of the 220 self-test questions is 0.41 (guard at 0.5 dropped 0). In a 20-example spot-check I found 0 self-test paraphrases and the format was correct; 1/20 keeps a first-person SE voice ("My recommendation would be…").
- **Risk for stage 1:** the targets are one-fact, 1-sentence answers (median 16 words; cut-7 answers run ≈ 50). 99 % cite only [1] and there are no distractor passages, so the LoRA may learn shorter, single-fact answers against multi-fact self-test rubrics. Flag this for the coordinator before stage 1; it does not change the frozen criterion.

## 6. Environment (mini)
- `<runner>/kiln/sft4b/.venv`: Python 3.14.7, mlx 0.32.3, mlx-lm 0.32.0 (`mx.default_device()` = gpu, a test op runs), torch 2.11.0 cpu, gguf-py from llama-b11010; 0.97 GB.
- llama.cpp b11010 (4bc272f): `convert_hf_to_gguf.py` is present; `build-cpu/bin/llama-quantize` was built (target only).
- `data/train.jsonl` and `data/holdout.jsonl` are copied to the mini, with matching shas.
- Disk on the mini: 30 → 29 GiB. DISK-LOG has one row.
- Ready but **untested**: `tools/mini/smoke_lora.sh` (rank 16, all 7 linear projections × 36 layers, lr 1e-5, max seq 2048, seed 42, mask_prompt, batch 4, scale 20; 64 train / 16 hold-out examples as valid) and `tools/mini/export_base.sh` (base → f16 → Q4_K_M, then the f16 is deleted).
- Export-parity caveat: the claim model is unsloth's Q4_K_M (manifest rev a06e946b…), probably made with an imatrix. A plain requant from bf16 will not be byte-identical, so parity has to be judged by eye on 10 items, as the criterion allows. The MacBook side (a side-tree adapter copy with model id `qwen3-4b-instruct-2507-base-requant-q4km`) is not built; its disk has 12 GiB free, which leaves room for a 2.3 GiB Q4 above the 8 GiB floor.

## v2 targets (coordinator request, 2026-10-13 21:xx; MacBook only, no mini work)
- Why: the v1 targets are too short (median 16 words, against ≈ 50 for cut-7 answers on the self-tests, p10–p90 32–70). For v2 I kept the same disjoint candidates and the same v1 question per article (the passing one if any, else the latest). The writer (`tools/write_v2.py`) now sees the **engine-rendered context block** for that question and cites its [n] directly. Target: 35–60 words = the fact + one supporting detail + citation(s). Retry rounds go to articles whose example failed. The filter is `tools/filter_v2.py`: same frozen jev filters, cache and arm cap, plus pre-checks for 35–60 words, citations only to shown passages, and the self-test similarity guard.
- **jev:** v2 cost [usage detail removed] (r1 [usage detail removed], r2 [usage detail removed], r3 [usage detail removed], hold-out r4–r5 [usage detail removed], pilot prompt [usage detail removed]). Arm total [usage detail removed] of [usage detail removed]; [usage detail removed].447 → 0.369.
- **Pass rate (jev-checked):** r1 795/1,417 = **56.1 %** (49.7 % of all r1 answers, since 181 were dropped for length before jev); r2 197/708 = 27.8 %; r3 82/528 = 15.5 %. All rounds: 1,074/2,653 = 40.5 %. Drops: 1,542 quote_supports, 37 answers_question, 355 outside 35–60 words, 2 citing an unshown passage.
- **`data/train.v2.jsonl`: 1,000 kept** (sha a7b7b1b5…; 744 from r1, 174 from r2, 82 from r3). By pack: topic packs 116–125 each; SE packs ethereum 49, cooking 64, money 62, travel 77, bitcoin 82, outdoors 91, health 95.
- Length: median 44 words, p10 38, p90 53. Citations: [1] 959, [1]+[2] 38, [2] 3. 89 prompts show 2 passages. Highest self-test Jaccard 0.39.
- **`data/holdout.v2.jsonl`: 84 of the same 100 hold-out articles** (sha e49e52c9…; rounds 1–5). 16 articles never produced a passing v2 target, and the retry yield fell to 1/16 in r5, so I stopped. Length median 43.5 (p10 38, p90 53); all cite [1].
- Spot-check of 6: faithful and on-target, but the 35-word floor often pulls in a third, tangential passage sentence as padding (e.g. "Toddlers are learning to feed themselves" in an iron-dose answer).
- **Stage 1 set: v2** (`train.v2.jsonl` + `holdout.v2.jsonl`). It meets ≥ 1,000 kept at ≥ 50 % pass on the round-1 jev-checked basis, the same basis v1 used. It **fails** on the of-raw basis (49.7 %) and the all-rounds basis (40.5 %), and SE packs are under-represented (466 of 1,000). That is the coordinator's call. v1 files are unchanged.
- Raw v2 writer files (8 MB) are not in git; they can be rebuilt from the cached writer batches, and their shas are in `data/MANIFEST-uncommitted.txt`.

## v3 targets (distractor-rich; addendum 2, sha 653745c7…): **STOP: 2 of 5 0-call gates FAIL after round 1** (2026-10-13 22:3x, MacBook only)
- **Pipeline:** `tools/v3_prep.py`: 1,499 train articles (the v1/v2 question each) + the 84 v2 hold-out articles (v2 question). `tools/v3_replay.sh` → `replay-v3.ts` (a packroute replay-pr.ts copy that also emits chunk bodies): kit + pack, `--gate search --topk 6 --tree wt/packs`, 11 calls, about 100 s each, 0 LLM. `tools/v3_build.py`: distractors = the raw top-6 minus every chunk of the gold article (2,769 gold-article hits removed), with FTS5 BM25 neighbours from the same pack as fallback (1,288 of 4,583 shown distractors). Render = stage-0 `render_core.mts` (cut-7 compress, budget 1,200). The engine's relative-relevance floor drops many distractors, so dropped ones are replaced, up to 8 attempts. Gold position is randomised with the new optional `order` field (the engine would otherwise put gold at [1]); this changes only the passage order, not the block format. `--validate` still gives a byte-identical passage block 15/15 on B1, including both 3-passage prompts. `tools/zstd_shim.py` exists because Python 3.14 here lacks `zstandard`.
- **Contexts:** train 1,190 gold-present + 414 gold-absent; hold-out 53 + 17 = 70 of the 84 articles (14 lost: 245/309/6 train/hold-out builds failed on fewer than 2 distractors kept or on gold dropped by compression). Two-gold: 90 % designated, 439 downgraded when compression dropped the 2nd chunk, which leaves 584/1,243 two-gold prompts. Shown passages: 3: 662, 4: 699, 5: 250, 6: 63. Gold first position: 1: 317, 2: 345, 3: 357, 4: 168, 5: 47, 6: 9.
- **Writer:** `tools/v3_write.py` (Haiku 5.5 low, 5 per call, parallelism 4). 341 calls (6 pilot), 0 failed. The gold-absent opening is the engine's own `uncitedPreface` line ("This answer is not from an offline source on this phone; …", which opens 73 cut-7 self-test answers). Citation style is cut-7's "… [n]." per sentence.
- **Filter:** `tools/v3_filter.py`. jev runs on {cited_passages, uncited_passages}. Thresholds are as frozen. no_distractor_attribution = 1 − P(yes: "states as fact anything that appears only in uncited_passages"). The gold-absent answers_question uses general-answer wording, because the v1 criterion text counts "not available" as false.
- **Round 1:** 1,674 answers. Pre-jev drops: 39 length, 3 with no citation, 8 where the writer judged a distractor covers the question. jev checked 1,624, passed **622 = 38.3 %** (present 477/1,203 = 39.7 %, absent 145/421 = 34.4 %). jev drops: 714 quote_supports (439 of them at 0.80–0.89), 259 absent no_distractor_attribution, 28 answers_question, 1 present distractor.
- **Pass rate by group:** topic packs 0.68–0.76; SE packs 0.10–0.28 (ethereum 0.10); single-gold 0.48; two-gold 0.31.
- **Gates (on round 1; rounds 2–3 were not run, because the round-1 gate cannot be recovered):**

  | Gate | Value | Result |
  |---|---|---|
  | kept ≥ 1,000 | 562 (450 present + 112 absent) | **FAIL** |
  | median target ≥ 35 words | 49 (p10 44, p90 56) | PASS |
  | gold-present citing > 1 source ≥ 30 % | 33.3 % (150/450) | PASS |
  | jev round-1 pass ≥ 50 % | 38.3 % | **FAIL** |
  | gold-absent share 15–25 % | 19.9 % | PASS |

  Even with retries, kept would reach about 1,000 at best, since only 1,190 present contexts exist.
- **Spend:** jev v3 [usage detail removed] (1,693 requests at about [usage detail removed]e-5 each). Arm total [usage detail removed] of [usage detail removed]; [usage detail removed].369 → 0.296.
- **Not written:** train.v3, holdout.v3, review20, MANIFEST-v3. Round-1 selection stats are in `aggregates/filter-v3.json`. Raw writer outputs, contexts and replay raws (about 33 MB) are not in git; their shas are in `data/MANIFEST-uncommitted.txt`.
- **Caveats:**
  - Gold-absent shares its questions with gold-present examples of the same article (420 train copies).
  - Distractors sometimes repeat the gold fact; in factbook, neighbouring countries share identical lines.
  - The 40-word floor pushes the writer to pad with off-topic sentences from the passage.
  - The MacBook disk was 6.2–6.6 GiB free during the run (another session was creating replay app dirs). I deleted this arm's 11 app dirs (264 MB).
