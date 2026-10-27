# VG v4 ship gate (VG-S2): independent review
**Verdict: FAIL.** One of the 2 fires is **WRONG**: vgq2-002 flips a correct "No" into a false "Yes". The bar requires 0 WORSE/WRONG. The other bars hold: 0 control fires, and 120/120 valid answers. Under the criterion, VG v4 is not shipped, and the adoption step does not apply.

Reviewer: Opus 5.5 (independent; did not write VG v4 or the probe set; did not open `blind/` or `rnd/veil/`), 2026-10-04.
Inputs:
- `vg4-S2-criterion.md` (sha256 1f31215b…, re-checked and matching);
- `vg4-S2-fires.jsonl`, `vg4-S2-apply.jsonl` and `vg4-S2-apply.txt` (verdictGuard.ts sha256 25d73a8b…, branch coord/vg4);
- `vg-probe-q2/items.jsonl`, read only for item kinds.

To explain the cause, I read `checkSuperlative` on `coord/vg4` (read-only).

## 1. Fires
| item | kind | question | before → after | label | reason |
|---|---|---|---|---|---|
| vgq2-002 | superlative | Is Lake Superior the biggest freshwater lake in the world **by volume**? | "No, … not the biggest … by volume. It is the largest by surface area, but Lake Baikal holds the title for the largest by volume." → "**Yes**, Lake Superior is the biggest freshwater lake in the world by volume. …" | **WRONG** | By volume, Lake Baikal holds about 23,600 km³ against Superior's about 12,000 km³. Superior is the largest freshwater lake by **surface area**. The original "No" was correct and consistent with its own facts. The repair is false, and it now contradicts the "Baikal … largest by volume" clause it keeps. Fact confidence: high. |
| vgq2-119 | compare2 | Does the city of Moscow have more people than the whole country of Norway? | "No, Moscow does not … Moscow about 12 million, Norway about 5.5 million. Therefore, Moscow's population is significantly larger…" → "Yes. Moscow has about 12 million residents, while Norway has approximately 5.5 million people." | **BETTER** | Moscow has about 13 million people (the answer says about 12 million) and Norway about 5.6 million, so "Yes" is correct. The contradiction is gone, and the restating "Therefore" sentence was dropped. Fact confidence: high. |

### Why vgq2-002 fired (for the fix)
`checkSuperlative` has three faults here:
1. **The quantity qualifier is ignored.**
   - "It is the largest by surface area" counts as a *yes* clause.
   - `sameScope` only compares an "in/of/among <ProperNoun>" scope. It never compares the measure ("by volume" vs "by area/surface area/population/length…").
   - Fix: when the question carries "by <measure>", a clause counts only if it names the same measure or none. A clause with a different "by <measure>" is never evidence, either way.
2. **A shared generic word makes another entity count as X.**
   - `xWords` for "Lake Superior" is {lake, superior}, so "Lake Baikal holds the title…" passes `aboutX`. It is therefore never checked as `OTHER_AHEAD`.
   - Fix: key X on its distinctive words only ("superior"). Drop the class nouns (lake, river, mount, mountain, ocean, sea, city, country, state, island, university…), as `entityKeys` already does for the two compare entities.
3. **"holds the title for the largest" isn't in `HOLDS`/`OTHER_AHEAD`.** Even when attributed to Baikal, it would not have counted against the flip.
   - Fix: add "holds the title (for|of) (the)? SUP".

Add vgq2-002's shape as a no-flag unit test, plus variants: "by area" asked with "largest by volume" answered, and "most populous" asked with "largest by area" answered.

## 2. Bars
| bar | result |
|---|---|
| 0 fires WORSE/WRONG | **1 WRONG** (vgq2-002) ❌ |
| 0 fires on 30 controls | 0 ✅ |
| ≥ 118/120 valid answers, 0 engine errors | 120/120 rows have a non-empty answer, and none looks like an error. 103 were EN model answers checked; 17 were skipped as `not-model-route`. ✅ (I saw the answers, not the engine log.) |

Fire count by kind (descriptive): superlative 1/30, compare2 1/30, threshold 0/30, control 0/30.

## 3. Missed self-contradictions (descriptive)
These are answers whose verdict contradicts facts stated in the same answer and that VG v4 did not flag. **There are 16 of them, against 1 correct catch (vgq2-119).** Many of these items' verdicts are also wrong in fact; this count is about internal contradiction only.

| kind | items | count |
|---|---|---|
| threshold (numeric) | 013 Statue of Liberty ("No" / "103 m … so, yes"), 016 Brazil ("No" / 213 M), 026 Golden Gate ("No" / "1.64 miles … just under a mile"), 086 Earth circumference ("Yes" / 40,075 < 50,000), 109 Sun distance ("Yes" / "so the answer is no") | 5 |
| threshold (date) | 055 first Moon landing ("No, … in 1969, after 1970") | 1 |
| compare2 | 039 gold vs lead ("No" / 19.3 vs 11.3 g/cm³), 050 Earth vs 2× Mars ("Yes" / "1.88 … no"), 059 Reno vs LA ("No" / "Reno … slightly further west"), 075 Rainier vs Mont Blanc ("Yes" / "Mont Blanc is taller"), 092 UK vs Japan ("Yes, the UK is smaller"), 102 Thames vs Seine ("Thames longer" / "Seine actually longer"), 114 −40 °C vs −40 °F ("Yes" / "same temperature") | 7 |
| superlative | 007 Mount Whitney ("Yes" / "not the highest … due to Denali"), 046 Pacific ("No" / "It is actually the largest"), 063 Atlantic ("Yes" / "second largest … not the biggest") | 3 |

Notes:
- Several misses end with the model's own correction ("So, no…", "So gold is actually denser"). A fix there would mean dropping the wrong lead, not flipping it.
- 039 is the same g/cm³ density gap as vgq-007 in VG-S.
- Fact errors that are internally consistent are not counted, and VG rightly stays quiet on them: 004 (South Island is larger), 025 (Saturn's rings are wider than Jupiter), 031 (Mauna Kea, base to peak), 037 (Mercury is more massive than Ganymede), 057 (London–Moscow is about 2,500 km).

AI-reviewed, not clinically reviewed.
