
Every number on the page matches the public release. That covers the ladder SVG geometry, the tables, the phone, long-session, HEADPASS, pack and FACTS figures, and the CLOSED counts 76 = 61 + 13 + 2. Both must-fix items are wording, not data. A tile contradicts the page's own phone table, and the health card overclaims on a safety topic.

Scope: read-only, except for this file. Ground truth was `release-staging/research/` and `release-staging/bench/` only. I did not read `blind/` or `rnd/veil/`. I made no judge calls and used no paid API.

## 1. Verdicts

| Target | Verdict | must-fix | should-fix | nit |
|---|---|---|---|---|
| (A) research page | **PUBLISHABLE AFTER FIXES** | 2 | 10 | 7 |

## 2. Checks that passed (evidence)

- **Numbers.** Every row of the ladder table (index.html:241–247) and every ladder SVG bar and CI cap (l.236) back-computes exactly to BAR-TABLE §1a/§1b (BAR-TABLE.md:35–57). The scale is 0 → x=228, 666.67 px per unit. Example: H on V-para has width 290.67 → 0.436, with caps 0.401 and 0.472. The W/T/L column matches per seed. The other sources also match:
  - CI_cm 0.387–0.486: BAR-TABLE:126.
  - Seeds 0.412/0.460/0.425, mean 0.432, SD 0.025: BAR-TABLE:40.
  - Judge retest +0.004, r 0.96: BAR-TABLE:123.
  - Per-axis 0.660/0.301/0.341 and about 280 words: BAR-TABLE:89, 95.
  - Phone figures (DEVICE-X6.md:13–30): 72/72; 30.7/48.4 s; TTFT 18.5 s; 5.5 tok/s; PSS 5.88 → 4.23 GB; thermal; 0.529/0.403 vs 0.529/0.402; paired −0.000 (−0.026…+0.028); 3/44 byte-identical.
  - Long session: every per-turn ratio and every latency in the SVG tooltips equals `longsession/aggregates/longsession.json` (`per_turn`, `ext15.token_curve`, `ext15.blocks`).
  - HEADPASS 35/72/102, +0.033/+0.066/+0.095: HEADPASS-ST.md:29, 89; REPORT-PACKS:19.
  - Packs table, +0.042, −0.019 and 36 %: REPORT-PACKS:8–12, 31–45.
  - FACTS 4,233 entities, 761 KB, 70.0 %/96.6 %, 0/100, 8 fires: FACTS-r6-SET4.md:2, 8, 27–28; CLOSED R9.
  - DETMAX 0/240, 7 lost, 1 added in 192, threshold 0.2: DETMAX.md:13–18. S1/S2 120/120: DETFU.md:17–18.
  - Judge cost: about [usage detail removed] and about 5 min at N = 4 (TRACE-FORMAT.md:58). The `--strict --floor-errored` flags exist (harness/judge.mjs:19, 74). The decline score of about 0.31 is in TRACE-FORMAT.md:67.
  - CONTRIBUTING quality bars: CONTRIBUTING.md:29–30.
- **CLOSED figure** (l.272): 76 rows. 13 tooltips say "not detected": R1, 10, 11, 15, 17, 18, 22, 25, 37, 45, 46, 49 and 68. Two say "measurement": R75 and R76. That leaves 61 closed, which matches CLOSED.md:6–8 and the row labels.
- **Derived floor-figure numbers: arithmetic verified** from the K V-para per-axis means (BAR-TABLE.md:88):
  - R = (4.88 + 4.68 + 5.00)/3 = 4.853. S = (2.66 + 1.63 + 1.73)/3 = 2.007.
  - Check: S/R = 0.4135 (0.413) and (S−1)/(R−1) = 0.2613 (0.261).
  - Raw 0.50 at 0.5·R = 2.427 (2.43). Floor-adjusted 0.50 at 1 + 0.5·(R−1) = 2.927 (2.93). The minimum answer is 1/R = 0.206 (0.21).
  - The SVG geometry matches: reference bar end 661.9 → 4.853; thresholds 428.9/476.9 → 2.427/2.927.
  - The numbers are right, but the page does not label them as derived (S2).
- **Honesty.** Raw is always paired with floor-adjusted. Dev and held-out status is tagged per row. The deep tier is stated as "desktop only… not in the app… has not run on a phone" (l.233). The phone result is worded as "same judged quality, within noise" with "answers are not the same text" (l.351, 359). Win rate is stated. (The tile's scope is wrong: M1.)
- **Exclusions.**
  - No competitor names or other teams' numbers. No native-app comparison.
  - The only handles are inside the four URLs (`r4to`, and `the app maintainer` in the PR #85 URL).
  - No internal process talk. "Session" and "budget" appear only in their technical sense.
  - The health caveat appears at l.315, l.393 and l.461.
- **Page contract (static checks).**
  - `grep -E '#[0-9a-fA-F]{3,8}'` outside the `:root`/dark blocks (l.7–28) finds 0 hits. There are no rgb/hsl/named colours in rules or attributes. SVG fills and strokes use token classes only.
  - The dark palette is under both `@media (prefers-color-scheme: dark){:root:not([data-theme="light"])}` (l.15–21) and `:root[data-theme="dark"]` (l.23–28), each with `color-scheme:dark`. `body` background comes from `var(--bg)`.
  - `grep -c '—'` = 0. There are no `<script src`, `<iframe`, `<img`, `<!DOCTYPE>`, `<html>`, `<head>` or `<body>` tags. The one `<script>` is inline (copy buttons). The only external resource is a Google Fonts link.
  - `<title>BOAR Research Notes</title>`.
  - `.page{padding-inline:16px}`. Every SVG has a viewBox and sits in `.frame{overflow-x:auto}`. Every table sits in `.tbl{overflow-x:auto}`. Grids use `minmax(min(100%,…),1fr)`.
  - A bounds script (estimated glyph widths) found no SVG label outside its viewBox.

## 3. Findings (survivors after self-refutation)

| # | Location | Quote (≤ 15 words) | Severity | Fix (exact) |
|---|---|---|---|---|
| **M1** | index.html:146, glance tile "Wins vs reference" | "0 on every set, every seed, every configuration" | **must-fix** | The page's own v0.1 phone table (l.355–356) shows W/T/L 2/1/54 and 1/2/54 (DEVICE-X6.md:27–28). Replace the `<dd>` with: `<span class="big">0</span>on V-para and v0.2, every seed, every configuration (1–2 of 57 on public v0.1)` |
| **M2** | index.html:305, health card, first paragraph | "Health questions never reach the model’s memory." / "Health never goes through multi-pass research." | **must-fix** | This is not supported, and it is contradicted. Ordinary health questions are answered by the model under a "health grounding instruction" (pr1/WIRING.md:44). A standalone health question got a generated answer (LONGSESSION.md:52, answer B). The public release does not support the multi-pass sentence. Replace the paragraph with: `<p>Emergencies take a strict path. When a small emergency classifier fires (threshold 0.2), the engine answers with a first-aid card, an extractive passage from an offline source, or a “no safe source” reply. Other health questions get a health grounding instruction in the prompt.</p>` |
| S1 | index.html:145, tile "Best, hardest set" | "0.436 floor-adjusted on V-para, bar 0.50 (dev data, desktop only)" | should-fix | The tile does not name the configuration, so a skimmer reads 0.436 as the app's score. Replace the `<dd>` with: `<span class="big">0.436</span>floor-adjusted on V-para, bar 0.50. Deep tier + thinking, desktop only, dev data. The app’s 4B build: 0.261.` |
| S2 | index.html:187 caption + SVG2 (l.186) labels "V-para mean ≈ 4.85", "≈ 2.01", "= 2.43", "= 2.93" | "On V-para the references average about 4.85." | should-fix | The arithmetic is correct (§2), but derived numbers must be labelled. Change the caption's second sentence to: `On V-para the references average about 4.85 and our 4B build about 2.01 (derived from the per-axis means in BAR-TABLE §2).` |
| S3 | SVG2 (l.186), sublabel under "Minimum-score answer" | "refusal, empty, wrong" | should-fix | This conflicts with l.180 ("declines every question scores about 0.31"; TRACE-FORMAT.md:67, where D = 0.306 is measured on 79 declines). Change the sublabel to `1 of 5 on every axis`. Append to the l.187 caption: `A measured decline scores a little above this floor, about 0.31 raw.` |
| S4 | index.html:193 | "so every decision uses two seeds" | should-fix | This is false as stated. v0.2 deep rows, the slices and HEADPASS are one seed (the ladder table itself has a 1-seed row). Replace with: `so deep-tier decisions on V-para use two seeds.` |
| S5 | index.html:254, "How to read it" bullet 1 | "The formal raw rule … is met by the deep tier" | should-fix | This reads as "bar met" and lacks "desktop only" in the sentence. Replace the `<li>` with: `<li>Raw CI lows sit above 0.50 for the deep tier with thinking (V-para 0.524; v0.2 0.575, one seed). That is the formal raw rule, on development data and desktop only. The same runs are 0.436 and 0.508 floor-adjusted.</li>` (BAR-TABLE.md:39, 57, 73) |
| S6 | SVG6 retrieval diagram (l.324): `<text …>BM25</text>`, its subtitle, the lead-vector subtitle and `aria-label` | "BM25" | should-fix | The pack docs and the page’s own pack lede (l.376) say full-text search (FTS5; REPORT-PACKS.md:27). BM25 appears only as an FTS ranking in X3/qa-travel notes. Text changes: `BM25` → `Full-text search`. Keep `1,000-char chunks`. `one per article, 384-d` → `article leads, 384-d` (the lead is the first 2,500 chars, REPORT-PACKS.md:27; all 11 published cards have lead_vecs = articles). In the aria-label, "searched with BM25 over chunks and with article lead vectors" → "searched by full-text search over chunks and by article lead vectors". "Full-text search" is about 110 px, which fits the 150 px box. |
| S7 | index.html:329, HEADPASS reach figcaption | "quality rises +0.066 … a lever by its frozen rule" | should-fix | The "+ neighbours +0.033" bar in SVG7 was "measured beyond its frozen plan; label capped" (REPORT-PACKS.md:211, 242; HEADPASS-ST.md:45). Pre-registration is a selling point, so say so. Insert after the first sentence: `The neighbours-only step (+0.033) was measured beyond its frozen plan; its frozen label stays “not decidable”.` |
| S8 | SVG8 `aria-label` (l.368) | "every turn is at or above parity 1.0" | should-fix | Turn 3 is 0.970 (0.726–1.278) (LONGSESSION.md:18). Replace with: `…per turn; no turn’s confidence interval lies wholly below parity 1.0 (turn 3, the topic switch, is 0.97)…` |
| S9 | index.html:147, tile "Negative results"; l.270 lede | "registry rows, each with its test’s power" | should-fix | Many rows have MDE "n/a (gate)" (CLOSED R3–R6, R30, R32, R38–R44 and others). Tile: `registry rows: what was tried, how it was tested, what would reopen it`. Lede l.270: "the minimum detectable effect (MDE) of that test" → "the minimum detectable effect (MDE) where the test had one". |
| S10 | Whole page (readability, §4) | about 3,350 visible words + 9 figures | should-fix | That is about 13–15 minutes, not 10. Cut the three paragraphs in §4. |
| N1 | SVG9 (l.395), bar "Top-1 router, 4B" | "33" | nit | The source states "Net reach: router 31" (REPORT-PACKS.md:133; CLOSED R48 "R4 31"). Its route table sums to 33 (own-pack routes). Either use `31` (headline) or relabel the bar `Top-1 router, 4B (own-pack routes)`. |
| N2 | index.html:278, R27 card | "the model’s own selectors agree with the oracle 49 % and 46 %" | nit | S2 is a 4B verifier, not the 35B (CLOSED R27). Use: `the 35B’s self-selection and a 4B verifier agree with the oracle 49 % and 46 % of the time: chance.` |
| N3 | index.html:281, R20–R22 source line | "R20–R22 · V-para, 1–2 seeds" | nit | Budget 3072 was a Haiku judgment (CLOSED R22). Use: `R20–R22 · V-para, 1–2 seeds (3072: Haiku judge)` |
| N4 | index.html:325, HEADPASS diagram caption | "On health questions every appended chunk must also pass" | nit | The recheck applies on health-strict items (HEADPASS-ST.md:12). Use: `On health-strict questions every appended chunk…` |
| N5 | index.html:413, step 2 | "about 5 minutes with 4 shards" | nit | The command shown runs one lane. Append: `(4 shards = disjoint --ids and --gap-ms 0; see TRACE-FORMAT.md)`. |
| N6 | index.html:460, footer | "Every number on this page comes from the research repo and the bench repo" | nit | Append: `; the floor figure’s means and thresholds are derived from them, as marked.` |
| N7 | index.html:277, R8 card | "confident-wrong answers doubled, 7 to 15" | nit | 7 → 15 is more than double. Use: `more than doubled, 7 to 15`. |
| T1 | POST:10 | "a registry of ~75 ideas we measured and dropped" | should-fix | CLOSED has 76 rows: 61 closed, 13 "not detected" (parked, not dropped) and 2 measurements. Use: `a registry of 74 ideas we tested that did not pay off, with the numbers`. |
| T2 | POST:9 | "10-minute read" | nit | The page is about 13–15 minutes unless S10 cuts land. Use `short illustrated read`. |

## 4. Readability (a judge from another team, 10 minutes)

A reader gets the thesis in about 30 s (masthead + tiles) and the method in about 2 min (§1 pipeline + three scales + floor figure). The honest result takes about 2 min (§2 ladder). After M1 and S1 the first screen is self-consistent. The three heaviest paragraphs to cut:
1. **l.205**, "Bench v0.3 is being written… Gemma 4 26B… κ 0.32 and 0.55…". It duplicates the "Limits of the judge" card (l.440 onward). Keep the first sentence and drop the Gemma statistics.
2. **l.329**, the HEADPASS reach figcaption (5 sentences: the result, the v0.1 Haiku no-harm, costs and caveats). Keep "Reach first, then quality" + the +0.066 sentence + the S7 clause + "not a result against the bounty bar". Move the costs (60 % larger packs, about 420 tokens) to the l.321 prose.
3. **l.396**, the packs crowding figcaption (a 44-word first sentence + routing accuracies + the 36 % detail). Keep "One relevant pack helps; many packs crowd each other" with the two Δs. Shorten routing to "Routing to a single pack fails (0.25–0.61 accuracy; about 0.68 is needed to tie with peers)". Keep "Win rate 0 of 180. Dev data".
Second-tier candidates: the §3 closing paragraph l.283 (it repeats the lede l.270), and l.359 (keep the paired Δ and the 3/44 sentence, drop the A15 echo).

## 5. Self-refutation (what was tried against each finding)

- **M1 survives.** A defender could argue that "every set" means the bar sets. But the page itself prints 2 and 1 wins on v0.1 eighty lines later. A reader from another team will catch the contradiction, and it undercuts the "honest numbers" pitch.
- **M2 survives.** I checked whether cut 7 routes all health questions to health-strict. The firstaid card says that pack's items take the health-strict path (boar-firstaid-en.md:30), but WIRING.md:44 shows a health grounding instruction for model-generated answers, and LONGSESSION B answered a heat-illness question generatively. This is a safety-topic overclaim, so it stays must-fix.
- **S5 was considered for must-fix and downgraded.** README.md:42 itself says the deep tier "clears the formal raw rule", and the bullet places floor-adjusted beside it. The fact is supported. Only the "met" wording and the missing "desktop only" are at issue.
- **S6 was kept at should-fix, not must-fix.** BM25 is not false: SQLite FTS5 ranks by bm25, and HEADPASS-X3-criterion.md:7 and qa-travel-se.md:33 use the word. The issue is the inconsistency with the pack docs and the page's own l.376. Lead vectors in the raw list are supported: "Format-2 packs embed only article leads, so the engine cannot reach a fact deep in an article by vector search" (REPORT-PACKS.md:140), and lead rank appears in CLOSED R44. Only the subtitle is refined.
- **N1 was downgraded from should-fix.** The source is internally inconsistent: the table gives 33 and the prose gives 31.
- **Dropped findings:**
  - SVG label overflow: none found by the bounds check.
  - Literal colours: none.
  - Em-dashes on the page: 0.
  - "≈ 6–10 s" 4B p50: it matches README.md:25.
  - Packs sizes 89.0/137.2 MB vs the pack README's 84.9/130.9: the page follows REPORT-PACKS.md:43–44, which is a cited source.
  - The floor-figure arithmetic: verified correct.
  - The PR #85 URL handle: it is one of the four allowed URLs.

UNKNOWN:
- The public release does not document the exact fusion rule that builds the 6-passage raw list (how FTS and lead vectors combine). The diagram therefore shows inputs, not a rule.
- I could not verify the PR #85 contents from the release; only arms/pr1 is local.


> Hi all, the BOAR team is publishing its R&D so other teams can reuse it:
>
> - Research notes, a short illustrated read: PAGE_LINK
> - Research record (methods, frozen test criteria, device and long-session runs, and a registry of 74 ideas we tested that did not pay off, with the numbers): https://github.com/r4topunk/boar-research
> - Benchmark (public questions, gold, reference answers, the pairwise judge and a trace format any app can produce; held-out question contributions welcome, see CONTRIBUTING.md): https://github.com/r4topunk/boar-bench
> - Knowledge packs, per-source licences: https://huggingface.co/datasets/r4topunk/boar-packs
>
> We are not at the bar yet, and the record shows by how much. Numbers come floor-adjusted with win rates, dev vs held-out labelled. Happy to help anyone run the judge on their own app.

Changes from v1:
- T1: "~75 ideas … dropped" → "74 ideas we tested that did not pay off".
- T2: "10-minute read" → "short illustrated read".
- T3: each URL is last in its bullet, with no em-dash after it.
- Added one status line with no number ("not at the bar yet"), so the release cannot be read as a claim. The record supports it (README.md:42; BAR-TABLE.md:80).
- All four links are correct and public. PAGE_LINK stays a placeholder.

## Applied (2026-10-15)


| # | Status | Note |
|---|---|---|
| M1 | applied | exact text |
| M2 | applied | exact text |
| S1 | applied | exact text |
| S2 | applied | caption sentence as given; the following "Our 4B build sits at about 2.01:" became "The 4B build scores" to avoid repeating 2.01 |
| S3 | applied | sublabel `1 of 5 on every axis`; decline sentence appended to the caption |
| S4 | applied | exact text |
| S5 | applied | exact text |
| S6 | applied | label, subtitle and aria-label as given; `1,000-char chunks` kept |
| S7 | applied | clause inserted into the shortened HEADPASS caption |
| S8 | applied | aria-label as given |
| S9 | applied | tile and lede as given |
| S10 | applied | the three named paragraphs cut (l.205 Gemma statistics → one clause; HEADPASS caption 5 → 3 sentences, costs moved to the l.321 prose; packs caption shortened as suggested); second tier: l.283 removed, A15 echo in l.359 removed. Visible words 3,309 → 3,253 incl. tables; prose without tables/code ≈ 2,620 |
| N1 | applied | headline 31 (REPORT-PACKS.md:133, CLOSED R48): bar width, label, tooltip and aria-label |
| N2 | applied | exact text |
| N3 | applied | exact text |
| N4 | applied | exact text |
| N5 | applied | appended, flags in `<code>` |
| N6 | applied | appended to the footer sentence |
| N7 | applied | exact text |
| T1 | applied | in Draft v2 |
| T2 | applied | in Draft v2 |
| T3 | applied | in Draft v2 (URLs last, no em-dash after them) |

Static checks after the edits: hex colours outside l.7–28 = 0 hits; `grep -c '—' index.html` = 0; no `<script src`, `<iframe`, `<img`. Changed SVG labels are no longer than the strings they replaced, except "Full-text search" (about 110 px in the 150 px box, as the review estimated).
