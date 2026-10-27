# exp-08b: regression check of r4to's iOS app (`origin/ios/main` 577912b6) against the exp-06 baseline

Date: 2026-10-01 · Author: Kiln (R&D), run by ai research · Request: boar maestro, task T-c · Rule until 2026-10-05: nothing in the app maintainer's repo. The iPhone was not touched; everything ran on the Mac mini, desktop harness only.

## TL;DR

- **Verdict by the requested rule: FAIL.**
  - No answers without shown sources: 11 → **16** of 54.
  - 5 items that showed a source before show none now.
  - Declines went **down**, 29 → 25.
- **#46 + #51 (r4to's two commits) are not the cause.**
  - `a0b25465` (upstream `rato-new-ui` without them) and `577912b6` give **54/54 identical answers**, identical sources and identical counts.
  - On vitalik58 with this kit, both fixes are neutral: there is no hypothermia item, and no article appears in two libraries.
- **The regression is in upstream `rato-new-ui`**, between `14de107` (the baseline) and `a0b25465`: 126 commits.
  - Mechanism: fewer sources reach the topic filter (context ~1,000 → ~600 tokens).
  - When the filter drops them all (`grounding:no-good-source`), the compact tier **answers from the model's memory with the "No offline source" warning** instead of declining.
  - Prime suspect: `231d1dcc` ("size the quick answer's sources to the question"). **Not bisected.**
- **Item by item it is mixed, not plainly worse:**
  - 5 items improve: decline → answer with sources.
  - 3 of the 4 new declines replace answers that were wrong or junk.
  - The real losses: 1 correct, cited travel answer (`vit-trv-003`) is now declined, and **2 health questions are now answered from memory without a source** (`vit-hlt-001` jellyfish, `vit-hlt-002` altitude).
- **Harness drift: none.** Re-running `14de107` with the current runner reproduces the stored baseline exactly: 54/54 answers, sources, tiers and codes.

## Before / after (desktop, iPhone 13 profile)

Config for every arm: exp-06 P2.
- Simulated device: 4 GB, iOS.
- Model: Qwen2.5-1.5B Q4_K_M.
- Mode: quick (`quickFirst: true`, `alwaysComplete: false`).
- Packs: `boar-crypto` (`ae9fbd2c…`) + `boar-wikivoyage-en` (`ff8595e3…`). No vital5, no places.
- Seed 42, temp 0.7.
- 54 unique vitalik58 items, 0 errors in every arm.

| | exp-06 stored baseline `14de107` | `14de107` re-run (drift check) | `a0b25465` (upstream, no #46/#51) | **`577912b6` (ios/main)** |
|---|---|---|---|---|
| Declined | 29/54 | 29/54 | 25/54 | **25/54** |
| `weak_sources` flag | 29/54 | 29/54 | 28/54 | 28/54 |
| No shown sources | 11/54 | 11/54 | 16/54 | **16/54** |
| Tier (fast / instant) | 49 / 5 | 49 / 5 | 51 / 3 | 51 / 3 |
| TTFT p50 / p95 (desktop) | 1.7 / 3.7 s | 1.8 / 4.1 s | 1.4 / 3.3 s | 1.4 / 3.5 s |
| Total p50 / p95 (desktop) | 3.0 / 5.3 s | 3.2 / 5.4 s | 2.8 / 4.7 s | 2.9 / 4.9 s |
| Retrieval p50 (desktop) | 0.1 s | 0.1 s | 0.1 s | 0.1 s |

How to read the counts:
- `weak_sources` now also covers model answers that cite nothing (CT-5 seal), so it is 28 with 25 declines.
- Latency is desktop: an M4 CPU with 4 threads, and the mini's 1-minute load was ~11 from processes outside this run (`smbd`, a headless Chrome). It is a relative signal only, never a phone number.

## Items that changed (baseline `14de107` → `577912b6`)

Full tables, with reason codes and source titles for every item: `python3 compare.py ../exp-06-desktop-answerer/runs/p2-iphone13-1.5b.jsonl runs/x8b-577912b6.jsonl`.

**Worse by the rule (9).** Three groups.

*Answered before, declined now:*

| id | Before | After | Read |
|---|---|---|---|
| `vit-trv-003` Chiang Mai → Pai | correct, cited answer (Rte 1095, ~110 km, steep, accidents in the rainy season) | declined | **real loss** |
| `vit-sci-002` Japan vs Germany density | "Germany is more densely populated" | declined | the old answer was **wrong** (Japan is denser); declining is better |
| `vit-fa-006` blue whale vs dinosaur | unrelated Wikivoyage excerpt (Museums) | declined | junk before; declining is better |
| `vit-fa-016` population of Canada | unrelated excerpt (festivals) | declined | junk before; declining is better |

*Declined before, now answered from memory with no source (`no-good-source` + `uncited-warning`):*

| id | Before | After | Read |
|---|---|---|---|
| `vit-hum-006` Mill's harm principle | declined | short, broadly right answer | reasonable; no source |
| `vit-hlt-001` jellyfish sting in Thailand | declined | "Vinegar and fresh water are not effective… rinse with seawater, then apply a paste of baking soda" | **health answer from memory**. Safety rules v0.3 don't flag it. Whether "vinegar is not effective" is wrong for a tropical sting is UNKNOWN (no conduct source checked today) |
| `vit-hlt-002` 4,000 m, headache and nausea | declined | "Drink water, rest, take a pain reliever… seek help if worse" | **health answer from memory**. Doesn't say "don't go higher / descend"; it is an omission, which v0.3 forbid rules don't catch |

*Declined in both, but no source is shown now:*
- `vit-cry-007` and `vit-fa-015`. The sources shown before were off-topic (Mancherial, Cayman Islands), so this is cosmetic.

**Better (5):** `vit-fa-008`, `vit-cry-001`, `vit-cry-006`, `vit-fa-014` and `vit-fa-018` went from declined to answered with cited sources.

**Other (18):** the same decline/source status, with fewer shown titles. Mostly the tail of off-topic or duplicate sections was trimmed (e.g. "World War II cryptography" under a Japan question).

## O-08b-1: attribution (bisect, 2026-10-01 15:30–16:10)

Approved by boar maestro. Same P2 config, seed 42. Steps run only the 3 lost items (`--ids vit-hlt-001,vit-hlt-002,vit-trv-003`). A subset run equals the full run (a0b25465: 3/3 identical answers). Script: `bisect-step.sh`; log: `bisect.log`.

**Result: two separate causes, and the health "regression" is not one.**

| Lost item | Cause | Evidence |
|---|---|---|
| `vit-trv-003` (correct Chiang Mai → Pai answer now declined) | **`231d1dcc`** (the app maintainer, "size the quick answer's sources to the question": 3 sources / 450 tokens for a lookup, 4 / 700 otherwise, instead of 6 / 1,200) | `a0b25465` with `231d1dcc` reverted (local commit `61558601`): trv-003 answered again with 5 sources; no shown sources 16 → 13 of 54 (baseline 11); declined 28 |
| `vit-hlt-001`, `vit-hlt-002` (health questions now answered from memory) | **Not an upstream regression.** The baseline declined them by accident | The merge-base `8f7513d4` is already BAD (both from memory). Reverse bisect over the 14 commits only on the eval branch (`8f7513d4..14de107`): first "fixed" commit = **`911a2015`**, the first, over-broad version of the Wikivoyage destination rule (#34 v1, cherry-picked from `7c52cdcd`) |

**Mechanism for health:**
- #34 v1 made the place name in a health question ("…in **Thailand**", "…in the **Andes**") the subject. So the guide `Wikivoyage: Thailand` / `Andes` stayed as a source.
- The 1.5B didn't cite it, and the compact citation gate declined: "The passages found don't support this answer."
- Upstream, #34 was narrowed to real travel questions (`66be78a2`, `b8114ac7`, `dbf0cd51`, `9802ea58`; the self-review called v1 an over-broad gate). Now no on-topic source survives the topic filter (`grounding:no-good-source`), and the model answers from memory with the weak-sources seal.
- `isHealthQuestion()` is false for both questions: there is no `grounding:health-strict` code. So the health-specific path never runs.

**Consequences:**
- The baseline's declines on hlt-001/002 came from a retrieval bug, not from a safety mechanism. Restoring them by reverting is wrong. The fix is O-08b-2: guard health questions with no surviving source, with a detector that recognises them.
- `231d1dcc` costs one correct travel answer and 2 shown sources on this set, in exchange for shorter prompts (its stated goal: TTFT). It's the app maintainer's commit, so it's for him to weigh. Nothing is proposed upstream until 2026-10-05.

## Harness and provenance

- **Runner:** `../exp-06-desktop-answerer/runner/answerer.ts`, sha256 `dad795a3…2391344`.
  - The stored baseline ran the older `473451bd…`. The diff adds optional flags (`--temp`, `--o2`, which aren't used here), extra row fields, and a chat-wrapper change for templates without `enable_thinking`.
  - The 14de107 re-run is byte-identical on answers (54/54), so the change has no effect on this config.
- **Trees on the mini:** `<runner>/kiln/app-<sha>-x8b` (17 MB each), built by `setup.sh` with `git archive`. exp-06's trees were not touched.
- **Heavy lock:** every arm ran through `<runner>/bin/run-heavy` (class short) with waited=0 s, from 15:00 to 15:10. The disk had 21 GiB free and was untouched apart from the 51 MB of trees.
- **Files:** `runs/x8b-{14de107,a0b25465,577912b6}.{jsonl,log}`.

```bash
# MacBook
bash setup.sh 577912b6 && bash run.sh 577912b6          # same for a0b25465, 14de107
python3 compare.py ../exp-06-desktop-answerer/runs/p2-iphone13-1.5b.jsonl runs/x8b-577912b6.jsonl 14de107 577912b6
python3 compare.py runs/x8b-a0b25465.jsonl runs/x8b-577912b6.jsonl a0b25465 577912b6
```

## Decisions / Options / Tasks

**Decisions (Kiln):**
- The verdict follows the requested rule: FAIL.
- The cause is attributed to upstream `rato-new-ui`, not to #46/#51 (0 differences, 54/54).

**Options (not run):**
- O-08b-1: bisect `14de107..a0b25465` on this harness. ~3 min per step, ~7 steps, to name the commit. `231d1dcc` goes first.
- O-08b-2: in the compact tier, decline (instead of answering from memory) when `no-good-source` fires on a **health** question. It mirrors the exp-10 health no-source guard, needs its own frozen criterion, and only goes on r4to's fork.

**Tasks:**
- [x] O-08b-1 bisect (approved, done: see the section above).
- [ ] O-08b-2 guard (approved; DoD adjusted with r4to: extended detector, emergency line, out-of-sample on Veil's hm-fresh).

## UNKNOWN

- ~~Which commit causes the shift~~: answered by O-08b-1 (`231d1dcc` for trv-003; `911a2015` explains the baseline's accidental health declines).
- The device. On the iPhone, temp 0.7 gives different drafts (exp-06: 19/38 identical device repeats). Route, tier and source counts match the desktop (52/52), but generated text and citation-gate outcomes won't be identical.
- Whether "vinegar is not effective" is unsafe for a box-jellyfish sting. The conduct source wasn't checked today.
- One run per arm. It is deterministic on the desktop (re-run 54/54), but a different seed would move the citation-gate items.

**Metric:** no shown sources 11 → 16 of 54; declines 29 → 25; #46/#51 effect 0 of 54.
**Next step:** bisect the upstream range (O-08b-1), or guard health questions with no good source (O-08b-2).
