# H1 for product: "an instant answer's source must be ABOUT the question's subject"

Kiln (R&D) · 2026-10-01 · **Proposal for a local branch, not a PR** (rule 0). Evidence: `README.md` §2–§5 in this folder.

## TL;DR

- **Problem:**
  - Answers served straight from a source passage without the model (instant snippet or health excerpt) come from **another entity** in 9 of 18 cases:
    - *Kantō region* for "Japan's population";
    - *South Holland* for the Netherlands;
    - *Perth* for "capital of Australia".
  - Health excerpts can come from a travel page: *Cold weather* "keep walking" for a hypothermia patient.
- **Fix:** before serving one, check that the source's **title** names the question's subject. Otherwise:
  - an instant snippet is not served, and the model answers;
  - a health excerpt from that source is skipped, and if none is left, the existing safe fixed text is shown.
- **Result:**
  - Frozen criterion passed out of sample in both profiles: cw / unsafe / misleading 2 → 0, 0 correct answers lost, 0 regressions.
  - In sample: cw + unsafe 3 → 0 (Android 4B) / 1 (iPhone 1.5B).

## Minimal diff (`h1-subject-check.patch`, against boar-app `611a4b92`, sha `b1d6d50d…`)

| File | Where | Change |
|---|---|---|
| `src/routing/answer.ts` | `createAnswerer` → `answer()`, right after `names` / `match:pt-en-names` (≈ l.767) | +9 lines: `h1Terms` and `h1About(title)`, defined below |
| `src/routing/answer.ts` | instant-snippet block, the `covers` condition (≈ l.882, after `sentenceNamesSubject(...)`) | +1 condition: `&& h1About(pool[snip.sourceIndex].title)`, reason code `instant:h1-not-about-subject` |
| `src/routing/answer.ts` | health-extractive loop `for (const k of healthSourceOrder(...))` (≈ l.931) | +4 lines: skip a source that is not about the topic, reason code `grounding:h1-not-about-subject-<k>` |
| `src/routing/answer.ts` | imports | `namedEntities`, `titleCovers` |
| `src/routing/o2WeakSupport.ts` | `namedEntities`, `titleCovers` | `export` only, no logic change |

`h1Terms` and `h1About`:
- `h1Terms`: the question's subject terms.
  - Health questions: `healthTopicTerms(query, english)`.
  - PT questions: the lexicon's English names (`englishNamesIn`).
  - Otherwise: the named entities (`namedEntities`, O2's extractor).
- `h1About(title)`: no subject → keep (fail open); else `titleCovers(term, title)` for some term.
- `titleCovers` gives no part-of coverage: "Kantō region" does not cover "Japan".

**Porting note:**
- `o2WeakSupport.ts` exists only on `feat/o2-compact-offsubject` (`611a4b92`), not on `origin/main` (`7aa67d5`) or `upstream/main`, and the O2 line was closed (FAILED).
- For a product branch, move just the 2 pure functions (`namedEntities`, `titleCovers` + `norm` / `stem` / `PREFIX`, ~70 lines) to a small module (e.g. `src/routing/subjectMatch.ts`).
- Then re-anchor the 3 `answer.ts` hunks by function, not by line number.
- In the measured patch the switch is `EXPO_PUBLIC_H1_SUBJECT=1`; a product branch would use a constant or a setting. **Rollback:** the switch.

## Acceptance criterion (frozen before the items existed) and results

**Criterion** (per profile, both must pass):
- C1: 0 correct answers lost.
- C2: 0 regressions (determinism + unchanged where H1 doesn't fire).
- C3: cw + unsafe of the instant tier falls.
- C4: ≤ 1 improper block per 10 fires.

| | In sample (137 q, both profiles) | Out of sample (Veil's 24 fresh, frozen) |
|---|---|---|
| Fires | 18: 6 final answers + 12 previews | 4: 3 finals + 1 preview, per profile |
| cw + unsafe (+ misleading previews) | finals 3 → 1 (iPhone) / 0 (Android); misleading previews 6 → 2 | 2 → 0 |
| Correct answers lost / improper blocks | 0 / 0 | 0 / 0 of 4 |
| Regressions | 0 (51/51 identical where it didn't fire) | 0 (24/24 off = off-rep; 0 changes where it didn't fire) |
| Examples | Netherlands: "South Holland … over 3." → "over 17 million"; hypothermia: "keep walking" → safe fixed text | Australia: "Perth is the capital…" → "Canberra" |

**Setup:** real `createAnswerer` on the Mac mini (desktop harness, exp-06), kit A, greedy, seed 42. Profiles: iPhone 13 (4 GB, Qwen2.5-1.5B) and Android (12 GB, Qwen3-4B). Labels by hand; Jev v2 is the second rater (agreement 36/45 in sample, 4/4 out of sample).

## Latency cost (only on blocked non-health answers; health blocks are faster, being fixed text)

| Profile | TTFT before (instant) | TTFT after (model answers) | Device estimate |
|---|---|---|---|
| iPhone 1.5B (desktop) | 0.16–0.65 s | 2.2–4.2 s | ~4× on an iPhone 13 → ~9–17 s (extrapolated, UNKNOWN) |
| Android 4B (desktop) | 0.2–0.4 s | 6–11 s | UNKNOWN (no Android device run) |

**Frequency:** 4 blocked non-health finals in 137 in sample, 1 in 24 out of sample.

## Caveats (before taking it to the product)

1. **Small out-of-sample proof:** 4 fires per profile. C4 passes at 0/4, so its "≤ 1 per 10" was never stressed.
2. **Recall is narrow.** It misses:
   - look-alikes the **PT lexicon itself** maps to ("São José dos Pinhais" → *Saint Joseph*, "Paraná" → *Paraná (state)*);
   - two-way title containment (*Tennessee River* ⊂ "Little Tennessee River");
   - class questions with no named subject ("most populated countries").
3. **It blocked the right health article** (*Choking*) because the health topic terms didn't match its title. Nothing was lost there (the app had already picked a Wikivoyage line), but a better excerpt picker would need the right article. Health title matching needs a check before shipping.
4. **It doesn't fix non-answers from the right entity** (*Brazil* "Brazilians are not Hispanic" for the largest state): 7 of 12 non-answer finals. That is O-H2, next.
5. **Device latency is extrapolated.** Measure TTFT on the iPhone with the switch on before shipping.
6. **Separate safety finding (not H1):** PT carbon-monoxide and heat-stroke questions got model answers from memory, without the health guard ("procure oxigênio… abra a janela", no "leave the house"). This is likely `isHealthQuestion` coverage. Unverified.

**Recommendation:** take H1 to a local product branch with the switch **on**:
- measure TTFT on the device, with 1 short device smoke run;
- fix caveat 3, the health title match, before calling it done.
