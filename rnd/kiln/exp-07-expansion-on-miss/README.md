# exp-07: T2 "query expansion on a miss", measured in the real answer engine

Date: 2026-10-01 · Author: Kiln (R&D) · Request: r4to via ai research #2 · Spec: `review/competitor-app-adopt.md` T2 (reference `competitors/competitor-app/.../research/QueryExpansion.kt`, `ResearchOrchestrator.kt:72-113`) · Rule 0: local branch only, no PR.

## TL;DR

- **Verdict: DESCARTAR.** In all four configurations (2 device profiles × 2 corpus kits), T2 did not lower refusals or `weak_sources` at all: **0 changes**.
- **Regressions: 0.** Where T2 did not fire, the answer and sources are byte-identical with T2 off (same tree, same seed).
- **Extra latency on the questions where T2 fired:** median 0.9–1.1 s for the 1.5B and 2.6–2.9 s for the 4B on the desktop, under the < 5 s bar. But when T2 finds sources, the answer pays a full prefill: **+3.7 to +16.7 s** on the desktop, ~4× that on a phone.
- **Why it fails:**
  1. **On the compact tier (iPhone 13, 1.5B), new sources can't turn a decline into an answer.**
     - The 1.5B doesn't write the passages' `[n]` citations, so the citation gate declines anyway. The message just changes from "I didn't find this" to "The passages found don't support this answer".
     - The 1.5B also often ignores the expansion prompt and answers the question instead ("Yes, rhinos are larger than elephants"), so its terms are noise ("seconds" → *Second homes*).
  2. **On the Android tier (4B), sources that arrive are not cited, and none of them fully supports the answer.**
     - Every one of the 3 hits (World Cup → Wikivoyage *Russia/France/Croatia*; R0 → *Measles/Rabies/Ebola*; Mozi → *Impartiality*) ended in `grounding:uncited-warning`, so `weak_sources` stays.
     - It also **drops the visible line "This answer is not from an offline source on this phone"**, because sources now exist. That makes the answer *look* more grounded than it is.
  3. **Most misses aren't wording problems.** In P3, of the 5 trigger questions, 3 found no article under any term (Mozi ×2, far-UVC) and 1 is arithmetic (token-time, `vit-sci-003`). Expansion can't find an article the kit doesn't have.

## 1. What was built (local patch)

`t2-expansion-on-miss.patch` (against boar-app `14de1074`, `build/model-ab-rc6-eval`; `git apply` from the boar-app root):

| File | Change |
|---|---|
| `src/routing/expansion.ts` (new) | `EXPANSION_SYSTEM` (its own prompt: "ONE line, 4 to 6 search terms… synonyms, words the answering article would use, names of candidate entities"), `EXPANSION_MAX_TOKENS = 48`, `parseExpansionTerms` (first line, comma-split, drops terms whose words are all in the question, ≤ 6), `termOccurs` |
| `src/routing/answer.ts` (+36 lines) | Right after the on-topic gate (`grounding:no-good-source`). Fires only when **0 sources survive** and **all** of the following hold: `settings.expandOnMiss`, not health, not multipass, not reused sources, task ∈ lookup/research/compare/extract. Calculator / emergency / first-aid / places return before retrieval. Steps: 1 generate (temp 0, 48 tokens, no thinking) → terms → **drop terms with 0 hits in the index** (`retrieve(term, 3)` + word match: the app has no FTS df API) → 1 search with the kept terms → keep a chunk only if it passes the question's own gate **or its title names a kept term** |
| `src/models/settings.ts` | `expandOnMiss?: boolean` (off by default) |

Reason codes: `expansion:terms-N`, `expansion:kept-N`, `expansion:t=<terms>`, `expansion:hit-N` | `expansion:miss`, `expansion:ms-N`.

**Design change after the smoke test (declared):**
- **First version:** a passage was kept if its text contained a term.
- **Smoke test (3 items):** Mozi pulled in *Frequent flyer programs*.
- **Change:** tightened to "the title names the term", following a competitor team's entity-name intent.
- This is 1 item of the evaluated set, and no threshold changed.

## 2. Setup (same tree, same seed; only `expandOnMiss` differs)

- **Harness:** exp-06 (`../exp-06-desktop-answerer/`), the real `createAnswerer`.
- **Tree and machine:** tree `<runner>/kiln/app-14de107-t2` = `14de107` + the patch. Mac mini M4, CPU, 4 threads, seed 42, quick mode.
- **Questions:** vitalik58 (54 unique).
- **Runs:** `run-4.sh`, `run-4-vital5.sh`, and `run-on-rerun.sh` for the T2-on runs (see §5).

| Profile | Device simulation | Model |
|---|---|---|
| (a) iPhone 13 | `--ram-gb 4 --platform ios` | Qwen2.5-1.5B Q4_K_M (compact tier: declines on a miss) |
| (b) Android 12 GB | `--ram-gb 12 --platform android` | Qwen3-4B-Instruct-2507 Q4_K_M (answers from memory + `weak_sources`) |

| Kit | Packs |
|---|---|
| P2 (= Plumb's iPhone run 2) | essential corpus + `boar-crypto` + `boar-wikivoyage-en` |
| P3 (+ `wiki-vital5`, run 3) | P2 + `wiki-vital5.sqlite` (pinned `d3b87d56…`, read in place, not copied) |

## 3. Results: before × after

`declined` = the app declined. `weak` = `weak_sources` warning. `0 src` = no source shown. Over all 54 questions:

| Config | declined | weak | declined + weak | 0 src | T2 fired / hit | regressions | extra latency, fired, median (desktop) |
|---|---|---|---|---|---|---|---|
| (a) iPhone 13 · 1.5B · P2 | 29 → **29** | 29 → **29** | 29 → **29** | 11 → 8 | 9 / 3 | **0** | 1.1 s (hit: +3.7…4.5 s) |
| (b) Android · 4B · P2 | 0 → 0 | 29 → **29** | 0 → 0 | 11 → 10 | 9 / 1 | **0** | 2.9 s (hit: +16.7 s) |
| (a) iPhone 13 · 1.5B · P3 | 24 → **24** | 24 → **24** | 24 → **24** | 7 → 4 | 5 / 3 | **0** | 4.3 s (hit: +4.3…5.6 s) |
| (b) Android · 4B · P3 | 0 → 0 | 26 → **26** | 0 → 0 | 7 → 5 | 5 / 2 | **0** | 2.6 s (hit: +4.8, +7.9 s) |

Subset where T2 acts (0 shown sources with T2 off):

| Config | n | declined off → on | weak off → on | 0 src off → on |
|---|---|---|---|---|
| (a) 1.5B · P2 | 11 | 9 → 9 | 9 → 9 | 11 → 8 |
| (b) 4B · P2 | 11 | 0 → 0 | 9 → 9 | 11 → 10 |
| (a) 1.5B · P3 | 7 | 5 → 5 | 5 → 5 | 7 → 4 |
| (b) 4B · P3 | 7 | 0 → 0 | 5 → 5 | 7 → 5 |

- In every config, 2 of the zero-source questions don't trigger T2 by design: `vit-trv-001` and `vit-trv-002` are places questions (`task:places`, `places:no-pack`).
- **Bench scoring (cheap pieces only, on the fired questions; no claude -p judge):**
  - precheck v2.2: **identical off → on in all 28 fired rows**.
  - Jev v2: identical except `vit-hum-003` P3 4B (`wrong_or_incomplete_hedged` → `correct`), which the hand check below doesn't support.
  - Spend: 8 calls on ≤ 18 items, each capped at [usage detail removed], well within the [usage detail removed] ceiling.
- Per question: `results-<config>.md` (terms, sources, labels, start of the answer) and `results-<config>.json`.

### Hand check, profile (b): did `weak_sources` become a sourced answer, and does the source back it?

- **Answers that became "sourced": 0 of 3 hits.** All 3 kept `weak_sources` (`grounding:uncited-warning`), so there aren't 5 to check.
- All 3 hits checked by hand against the pack text:

| id | Question | New sources | Supports the answer? |
|---|---|---|---|
| vit-fa-026 (P2) | who won the 2018 World Cup final? | Wikivoyage: *Russia*, *France*, *Croatia* | **No.** Travel guides; nothing on the final. The answer is from memory |
| vit-fa-010 (P3) | which viruses have the highest R0? | *Rabies*, *Ebola*, *Measles* | **Partly.** *Measles* says "highly contagious … nine out of ten people…", but no R0 figure. Rabies/Ebola: no R0 |
| vit-hum-003 (P3) | Mozi vs the "out-competed" critique | *Impartiality* | **No.** No mention of Mozi or Mohism in either chunk |

## 4. Latency: desktop and device estimate

| | Expansion turn, median (desktop) | Device estimate | Basis |
|---|---|---|---|
| 1.5B (iPhone 13) | 0.86–0.88 s | **~3–5 s** | desktop 57 tok/s vs device 13–15 tok/s (exp-06 §4, Plumb run 2): ~4× on 48 tokens + a ~150-token prompt |
| 4B (Android) | 2.6–2.7 s | **~5–8 s** (UNKNOWN) | desktop 21 tok/s; no Android 4B device run on this build |
| Hit (sources then prefilled) | +3.7 … +16.7 s | ×4 on a phone | a full prefill of up to 6 extra passages |

The bar (median extra < 5 s on desktop) is met. On a phone, though, the 4B estimate is near or over 5 s for the expansion turn alone, before any prefill.

## 5. Harness bug found and fixed during the run (declared)

- **Symptom:** the first T2-on pass of profile (b) produced 0 terms on every question.
  - Direct calls to the same 4B with the same prompt gave good terms: `diag_expansion.mjs` → `diag-expansion.txt`.
- **Cause:** for `enableThinking:false`, the exp-06 adapter asked node-llama-cpp's Qwen wrapper to "discourage" thoughts. On Qwen3-4B-Instruct-2507, whose template has no `enable_thinking`, that returned `""`.
- **Fix:** apply it only when the GGUF template contains `enable_thinking`. Now in `../exp-06-desktop-answerer/runner/answerer.ts` (copy: `answerer.exp07.ts`).
- **The T2-off runs are unaffected:** the answer path never sends `enableThinking:false`. The **0 regressions** check confirms it, since off and on are byte-identical wherever T2 didn't fire.
- **All 4 T2-on runs were redone** after the fix. The invalid ones are kept in `runs/invalid-adapter-v1/`.

## Decisions / Options / Tasks

**Decisions (Kiln):**
- **DESCARTAR T2 as specified.** The adoption criterion (refusal or `weak_sources` falls, no regression, median extra < 5 s) fails on its first clause in every config.

**Options (not measured):**
- O-a: T2 only on the 4B **and** require the answer to cite. It wouldn't change today's counts (0 hits were cited), so it only makes sense together with O-b.
- O-b: put T2's terms **into the first retrieval** (the hybrid query) instead of a second pass. That costs no extra prefill on a miss, but adds a model turn to every knowledge question. Not worth it before the coverage gaps are fixed.
- O-c: the measured problem is mostly **coverage**, not wording. In P3, 3 of the 5 trigger questions found no article under any proposed term. That is a pack decision (Lantern / packs), not an engine change.
- Keep the visible "not from an offline source" line whenever the answer is uncited, even with sources present (Android hit case). That is a separate UX fix, not T2.

**Tasks:**
- [x] Patch, 4 configs × off/on, before × after, hand check, README.
- [ ] Coordinator / ai research #2: accept DESCARTAR.

## UNKNOWN

- Android device speed for the 4B on this build (no device run). The device latency estimate for (b) is an extrapolation.
- Whether the app's llama.rn renders the expansion prompt like node-llama-cpp. The 1.5B's format-following could differ on the device.
- FTS document frequency: the app exposes no df API. "Frequency 0" was approximated as "no word match in the top 3 retrieved chunks for the term", which could keep a term the FTS index would count as rare.
- Effect on questions that are not in vitalik58. The trigger set is small (9 and 5 questions).

**Metric:** refusal and `weak_sources` 0 → 0 change in 4/4 configurations; 0 regressions; T2 fired on 28 questions, found sources on 9, and **0 became sourced answers**.
**Next step:** exp-08 (O2 v2, coordinator queue), measured in this same harness as a deterministic paired counterfactual.
