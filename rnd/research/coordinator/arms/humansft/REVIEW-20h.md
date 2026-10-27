# HUMANSFT review-sample-20h: faithfulness review

- Reviewer: independent Opus agent (claude-opus-5-5), 2026-10-07
- Rubric: STRICT, frozen (borderline = UNSUPPORTED; unstated causal links/placements = UNSUPPORTED)
- Source: `review-sample-20h.md` only (no other files, no web, no world knowledge)
- Citation markers ("[1]") not counted as claims. Disclaimer = "not in the passages"-type phrases.

| # | id | claims | sup | unsup | contr | discl | answers q | outside fill | note (≤ 12 words) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | clapnq--2689611084228995230 | 7 | 7 | 0 | 0 | 0 | y | n | verbatim; omits cirrostratus step (not needed) |
| 2 | clapnq--4427389245878997047 | 2 | 2 | 0 | 0 | 0 | y | n | omits "basic knowledge of other technical subjects" |
| 3 | clapnq--4940918682117558509 | 7 | 6 | 1 | 0 | 0 | y | n | "as a result of the attack" causal link unstated |
| 4 | clapnq--5297433923004722161 | 4 | 4 | 0 | 0 | 0 | y | n | complete |
| 5 | clapnq--6616776114356947680 | 3 | 3 | 0 | 0 | 0 | y | n | omits Schleiden 1839 plant-cells point (main points) |
| 6 | clapnq--6644184527764665957 | 6 | 6 | 0 | 0 | 0 | y | n | complete |
| 7 | clapnq--7284678856481580216 | 4 | 4 | 0 | 0 | 0 | y | n | omits Italians, Greeks, Hungarians, Poles, Slavic speakers |
| 8 | clapnq--9045656849776302810 | 3 | 3 | 0 | 0 | 0 | y | n | complete |
| 9 | clapnq-2533093386002638230 | 3 | 2 | 0 | 1 | 0 | n | n | championships attributed to Wizards; passage: Bulls years |
| 10 | clapnq-2839799694676987689 | 7 | 7 | 0 | 0 | 0 | y | n | omits US default: civil contract debt, not crime |
| 11 | clapnq-2900835412658458909 | 3 | 3 | 0 | 0 | 0 | n | n | never states Mary was the ruler restoring Catholicism |
| 12 | clapnq-3833406753075656280 | 4 | 4 | 0 | 0 | 0 | n | n | does not say when; passages give no stop time |
| 13 | clapnq-5220114941043729048 | 3 | 3 | 0 | 0 | 0 | y | n | omits North/South Fork confluence |
| 14 | clapnq-5802850458221685728 | 4 | 4 | 0 | 0 | 0 | y | n | omits Indian Removal Act 1830 (half the question) |
| 15 | clapnq-6438698312001115417 | 6 | 6 | 0 | 0 | 0 | y | n | complete |
| 16 | clapnq-7661308449181309097 | 4 | 3 | 1 | 0 | 0 | y | n | finches framed as "different resources" example; passage doesn't link |
| 17 | clapnq-8048522585381607401 | 5 | 5 | 0 | 0 | 0 | y | n | omits "first effort since 1964 Act" |
| 18 | hagrid-1596-0 | 10 | 6 | 4 | 0 | 0 | y | n | subject shifts Atrocitus->Red Lanterns; drops "apparently" hedge |
| 19 | hagrid-253-0 | 7 | 6 | 1 | 0 | 0 | y | n | "West Punjab, now part of Pakistan" not stated |
| 20 | hagrid-355-1 | 3 | 2 | 1 | 0 | 0 | y | n | "as of 2017" dating; [1] says 2016; omits 29.2M |

**Totals:** claims 95 · supported 86 · unsupported 8 · contradicted 1 · examples with ≥ 1 unsupported-or-contradicted claim = **6/20** (ids 3, 9, 16, 18, 19, 20) · outside fill 0/20 · disclaimers total 0 · answers q = 17/20 y.

Sensitivity (information only, not the rubric): 3 of the 6 flagged examples (3, 16, 20) fail only on a borderline item. Without those 3 the count is 3/20, which still misses the ≤ 2 bar.

## Unsupported or contradicted claims (verbatim)

1. **#3 clapnq--4940918682117558509** U: "Old Dan died later that night as a result of the attack": passage says only "badly wounded" and then "He dies late that night"; it states no cause.
2. **#9 clapnq-2533093386002638230** C: "career highlights and awards with the Washington Wizards: 6 × NBA champion (1991 - 1993, 1996 - 1998)": the title years match his Bulls years. Wizards = 2001–2003.
3. **#16 clapnq-7661308449181309097** U: "For example, in the Galapagos Islands, finches with small beaks...": passage never presents finches as an example of the "different resources" point.
4. **#18 hagrid-1596-0** U: "The power of the Red Lantern is harnessed through the Red Power Battery": passage never says power is harnessed through the battery.
5. **#18 hagrid-1596-0** U: "formed by Atrocitus using the blood of other inversions": passage hedges with "shown in a flashback as having apparently formed"; answer drops the hedge.
6. **#18 hagrid-1596-0** U: "The Red Lanterns harness the power of rage": passage says Atrocitus harnesses the red light of rage.
7. **#18 hagrid-1596-0** U: "and send their rings out into the universe": passage says "he sends his rings", i.e. Atrocitus, not the Red Lanterns.
8. **#19 hagrid-253-0** U: "West Punjab, now part of Pakistan": no passage states this; it is only implied by "what is now Pakistani Punjab".
9. **#20 hagrid-355-1** U: "around 33,332,025 as of 2017": [1] dates this figure "As of 2016"; [2]/[4] give no year for the total.

## Bar

Bar "examples with ≥ 1 unsupported-or-contradicted claim ≤ 2/20": **NOT MET (6/20)**.
