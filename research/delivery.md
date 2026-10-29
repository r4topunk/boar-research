# 13 · Delivery, not coverage

> Closed record · research record 1.1.2 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/delivery/ · Markdown twin: https://r4topunk.github.io/boar-research/research/delivery.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-19 → 10-23

**In one sentence.** With the 1.7B as main engine, the question became whether the one passage that holds the answer reaches the model. On questions written from the packs it often does, and answers jump; on real development questions the pack gain disappears, and almost every undelivered fact already sits in an installed pack. Search fixes delivered more facts; no answer-level gain was established, and one fix was withdrawn as unsafe.

## For curious readers {#curious}

#### Big gains on the library's own questions

On test questions written from a library's own pages, installing that library makes a big difference. On real practice questions, the same library made no measurable difference.

*Badge:* practice data · Claude Haiku judge · old scale · 27 vs 10 questions.

#### How you ask decides what it finds

Ask a yes/no question and the right page is found 83 % of the time; ask a bare follow-up like "and how long does it take?" and it is found 8 % of the time.

*Badge:* 48 facts × 9 phrasings · practice questions written by agents · search replay, no judge.

#### The book is on the shelf

Of 50 facts the app failed to bring to the model, 44 were already in a library on the phone. The problem was not missing knowledge; it was fetching it.

#### Better fetching, one fix withdrawn

Search fixes doubled how often the right passage arrived (21 → 42 of 92 facts). One more fix did better still, but it let unsafe health answers through on test prompts, so we withdrew it. Answers did not measurably improve.

*AI-reviewed, not clinically reviewed.*

**In one sentence card:** "The phone usually has the book; the hard part is opening it at the right page."

*Facts: [F-2080] [F-2092] [F-2100] [F-2095] [F-2097] [F-2025]*

## For tech people {#tech}

### Count delivery at chunk level; most misses are search, not missing content

We count a fact as delivered only when its quote sits inside one kept chunk; article-level counting had overstated delivery by 8–13 facts. On MAIN 92 keyed dev items, delivered facts went from 21 (no fix) to 28 with a global-IDF merge (word rarity computed across all installed packs, so small packs compete fairly; +6.2 points hit@kept, 0 lost), to 42 with three Stack Exchange search fixes (SEFIX-124), and to 47 with a fourth fix (F3, a health no-source fallback) that fired on 21 of 65 safety probes and raised unsafe answers from 9 to 13, so it was withdrawn. Answer-level gains stayed within noise: SEFIX-124 +0.013 (−0.008…+0.035) on all 97 (Haiku, two seeds). Of the 50 facts still undelivered, 44 already sit in the default 13-pack kit. A compact per-pack index (W78) cut the data read per question from 125.09 to 21.26 MB and the cold first stage from 620 to 92 ms on a desktop replay.

**Gotcha box: "self-tests flatter retrieval."** The pack gain on fact-added self-test items (+0.139, n 27) is −0.010 on real items (n 10) [F-2080].

**Safety box:** every retrieval change runs the 65 safety probes before merge; two otherwise-good configs (a wider append budget, the best RETBENCH config) were kept out because dose/number probes changed [D-177]. AI-reviewed, not clinically reviewed.

## For AI professionals {#ai}

### The record for this chapter

**Key facts (all dev; "U" = judge.v1 floor-adjusted ratio; Haiku unless named):**
- Self-tests vs real items: on 60 topical pack self-tests the pack gain sits on items where the pack adds the key fact, +0.139 (+0.075…+0.201), n 27; the same cell on real development items is −0.010 (−0.077…+0.050), n 10 [F-2080]. The self-test gain is not a word-overlap artefact (reweighted to real overlap +0.064, +0.035…+0.095; [F-1965]).
- Question form decides retrieval (48 pack facts × 9 phrasings, agent-written, 0-LLM replay): the gold chunk is kept for 50 % of base questions, 83 % of yes/no, 25 % of situational, 10 % of entity-free, 8 % of bare follow-ups [F-2092]. When the reference chunk is kept, the 1.7B scores U 0.876 (n 43, 2 confident errors) vs 0.185 (n 147, 75 confident errors), a between-item comparison on pack-written items [F-2093].
- The author, 10-22: "packs are the strategy"; small focused packs, full Wikipedia as a negative control [D-161] [D-162].
- A stricter count: from 10-22 a fact is "delivered" only when it sits inside one kept chunk; article-level counting had overstated delivery by 8–13 facts [D-165] [F-2095].
- Search fixes on MAIN 92 keyed items, chunk level: none 21 → global-IDF merge 28 → SEFIX-124 42 → SEFIX-ALL 47 [F-2095]. SEFIX-ALL's fourth fix (F3, a health no-source fallback) fired on 21 of 65 safety probes and unsafe answers rose 9 → 13 (blinded agent reading, one seed; AI-reviewed, not clinically reviewed); it was withdrawn [D-164] [F-2097]. The safe set SEFIX-124 gives +0.013 (−0.008…+0.035) on all 97 (two seeds): not a lever, adopted for delivery only [F-2025].
- Between items, delivery does not separate answers: delivered 0.420 vs not 0.419 (+0.001, −0.071…+0.069); within the same items, +0.044 (+0.009…+0.082, n 42, two seeds), and an Opus check on 28 delivered general questions +0.013, inside noise [F-2098].
- Where the undelivered facts are: 44 of 50 already sit in the default 13-pack kit (K13); new packs reach at most about one fact each [F-2100], so no new packs were built [D-173].
- Reading cost: a compact index inside each pack (W78) cut the data read per question from 125.09 to 21.26 MB and the cold first stage from 620 to 92 ms, with 42/42 facts kept (desktop replay; phone unmeasured) [F-2103].

**Key decisions:** [D-127], [D-160], [D-161], [D-162], [D-164], [D-165], [D-172], [D-173], [D-193], [D-194]. **Corrections to show:** F1b's "45 delivered" is 32 at chunk level; SEFIX-ALL's "55" is 47 [F-2095]; the Opus +0.173 "where the fact arrives" (n 22, selected slice) came from the run that included the withdrawn F3 [F-1593] [F-2096].

**Turning point:** 2026-10-22, the author's "packs are the strategy", followed the same day by the chunk-level rule that made the target measurable.

### 6.9 Self-test gains do not transfer; delivery does not separate answers

On 60 topical pack self-tests the pack gain concentrates on items where the pack adds the key fact (+0.139, +0.075…+0.201, n 27); on real development items the same cell is −0.010 (−0.077…+0.050, n 10), and the self-test gain is not a lexical-overlap artefact (+0.064 after reweighting to the real overlap distribution) [F-2080] [F-1965]. Retrieval depends on question form (hit@kept 83 % yes/no, 50 % base, 25 % situational, 10 % entity-free, 8 % bare follow-ups; [F-2092]). From 2026-10-22 delivery is counted at chunk level (article-level counts overstated it by 8–13; [D-165]). On MAIN 92 keyed items, delivered facts rose 21 → 28 (global-IDF merge) → 42 (SEFIX-124) → 47 (with F3, withdrawn after unsafe answers rose 9 → 13 on 65 probes) [F-2095] [F-2097]; the safe set changes U by +0.013 (−0.008…+0.035; Haiku, two seeds) [F-2025]. Between items, delivered vs not scores 0.420 vs 0.419 (+0.001, −0.071…+0.069); within items +0.044 (+0.009…+0.082, n 42, Haiku), Opus on 28 delivered general items +0.013 [F-2098]. 44 of 50 undelivered facts already sit in the installed kit [F-2100].

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-1593] Where the fact arrives. U 0.157 → 0.330, dU +0.173 (+0.082..+0.266); correct 13.6 → 50.0 per 100; decline 22.7 → 0 · set cooking/money self-tests (dev) (dev, development data) · judge Claude Opus U · n 22 · seeds 1 · CI n 22 units, seed 42 · date 10-22 22:32 · caveat: selected slice (newly delivered)
- [F-1965] PK-3 OVERLAP: Is the self-test pack gain a lexical-overlap artefact? reweighted to real overlap +0.064 (+0.035..+0.095) · set cand80 vs 37 real golds (status UNKNOWN) · judge reweighting · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-21 · caveat: criterion frozen: yes (fe44d05e); arm verdict: KILL (not an artefact; question type/reading)
- [F-2025] SEFIX-124: F1/F2/F4 without F3. chunk-level 42/92, 0 lost; pooled +0.013 · set MAIN 97, 2 seeds (dev, development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI +0.013 (−0.008..+0.035) · date 2026-10-22 · caveat: criterion frozen: yes (07ea2b5e); arm verdict: not a lever-candidate; adopted for delivery
- [F-2080] Pack self-test gain does not reproduce on real items. self-test fact-added cell +0.139 (+0.075..+0.201) n 27 vs real −0.010 (−0.077..+0.050) n 10 · set self-tests (pack-written) vs MAIN keyed (dev) (dev (pack-written self-tests), development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI 1 seed · date 2026-10-21 · caveat: post hoc; small n on real
- [F-2092] Question form decides retrieval. hit@kept base 50 %, keywords 62 %, yes/no 83 %, entity-free 10 %, situational 25 %, follow-up 8 % · set dev, agent-written (dev, development data) · judge replay · n UNKNOWN · seeds UNKNOWN · CI 48 facts × 9 forms · date 2026-10-21 · caveat: follow-up hole is a bench-engine artefact
- [F-2093] When the reference chunk is kept, the 1.7B answers near reference level. U 0.876 (n 43, CE 2) vs 0.185 (n 147, CE 75) · set pack facts (dev, pack-written) (dev (pack-written self-tests), development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI 192 answers, 1 seed · date 2026-10-21 · caveat: between-item comparison; real items flat (F-u-results-34) | QFORM items: 48 facts from public self-tests (factbook, firstaid, medlineplus) plus facts authored from pack text (crypto, wikivoyage, visa) x forms; Haiku judge.v1 ratio U, not an outcome label . Never print next to PACKPROOF correct-any as the same metric. AI-reviewed, not clinically reviewed.
- [F-2095] Chunk-level delivered facts on MAIN 92. N0 21; gidf 28; SEFIX-124 42; SEFIX-ALL 47 · set dev (dev, development data) · judge counts · n UNKNOWN · seeds UNKNOWN · CI replays · date 2026-10-22 · caveat: article-level counts overstated by 8-13
- [F-2096] SEFIX-ALL end-to-end. Haiku pooled +0.023 (+0.001..+0.048) over 97; Opus CV5 −0.002 (−0.062..+0.061); Opus where fact delivered (cm) +0.173 (+0.082..+0.266) · set MAIN 97 (dev) (dev, development data) · judge Claude Haiku; Claude Opus · n 42 · seeds UNKNOWN · CI 2 seeds / n 42 / n 22 · date 2026-10-22 · caveat: withdrawn: includes unsafe F3; SEFIX-124 alone +0.013 (−0.008..+0.035) AI-reviewed, not clinically reviewed.
- [F-2097] F3 health fallback is unsafe. fires 21/65 probes; unsafe 9 → 13 · set dev (dev, development data) · judge blinded agent reading · n UNKNOWN · seeds UNKNOWN · CI 65 probes · date 2026-10-22 · caveat: AI-reviewed AI-reviewed, not clinically reviewed.
- [F-2098] On real items, delivering the fact does not separate answers. delivered 0.420 vs not 0.419 (+0.001, −0.071..+0.069); within-item +0.044 (+0.009..+0.082) · set dev (dev, development data) · judge Claude Haiku; Claude Opus slice +0.013 · n UNKNOWN · seeds UNKNOWN · CI MAIN 92, 2 seeds · date 2026-10-23 · caveat: page must state plainly
- [F-2100] Undelivered facts are a search problem. 44 of 50 already in the K13 kit · set dev (dev, development data) · judge 0 LLM · n UNKNOWN · seeds UNKNOWN · CI 50 items · date 2026-10-23
- [F-2103] W78 stack reading cost. 125.09 → 21.26 MB per question; cold 620 → 92 ms; kept 96/97; facts 42/42 · set dev (dev, development data) · judge replay · n UNKNOWN · seeds UNKNOWN · CI MAIN 97 · date 2026-10-23 · caveat: phone unmeasured

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-127] 2026-10-19 · Focus finishing work on "tests with sources" (user has the matching pack) · why: bounty finish. · status: kept
- [D-160] 2026-10-22 · Carry chunk vectors forward only in no-displacement "extra" mode; fusion harmful on real items · why: fusion lost 6-8/22 real items. · status: kept
- [D-161] 2026-10-22 · Packs are the strategy: engine finds the context when the pack has it, model answers from it; stop expecting the model to answer alone; device day stopped · why: QFORM 0.88 vs 0.19. · status: kept
- [D-162] 2026-10-22 · Small focused packs, not giant ones; full Wikipedia = negative control · why: top100k takes 47-55 % of kept slots for net +2; small Q&A packs do not crowd; competitor full-enwiki search 17-21 s under model load. · status: kept
- [D-164] 2026-10-22 · Withdraw F3 (health no-source fallback) from the search fixes · why: unsafe 9 → 13 on 65 probes. · status: kept
- [D-165] 2026-10-22 · Delivery is measured at chunk level from now on · why: article-level overstated F1b by 13 facts. · status: kept
- [D-172] 2026-10-23 · Keep Wikipedia packs in the default kit K13 · why: removing them loses 9 MAIN facts, 10 general items, 2 health sources. · status: kept
- [D-173] 2026-10-23 · No new packs for coverage (gaps are search, not missing content) · why: 44/50 gaps already in K13; candidate packs ≈ 1 fact each. · status: kept
- [D-177] 2026-10-23 · X2B-BUDGET and RETBENCH best config stay out of ENGINE-RC · why: dose/number safety probes changed. · status: kept
- [D-193] 2026-10-21 · Adopt --no-repack as cross-host pairing flag for text pairing only; claim numbers keep default · why: 97/97 identical across hosts, quality-neutral (−0.012) · status: kept
- [D-194] 2026-10-23 · Succinct stays the 1.7B default; no conditional Detailed for delivered facts · why: STYLE-SEFIX dU −0.028, CE 26→46 per 100. · status: kept

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
