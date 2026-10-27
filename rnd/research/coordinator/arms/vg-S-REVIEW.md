# VG ship gate (VG-S): independent review
**Verdict: PASS.** All three bars hold: the 1 fire is BETTER (0 WORSE or WRONG); there are 0 fires on the 25 control items; and the run is valid, with 90/90 answers produced and no engine errors visible.

Reviewer: Opus 5.5 (independent; did not write VG or the probe set; did not open `blind/` or `rnd/veil/`), 2026-10-04.
Inputs:
- `vg-S-criterion.md` (sha256 da3a50c4…, re-checked and matching);
- `vg-S-fire-013.json`;
- `vg-S-fires.jsonl` (90 rows);
- `vg-S-apply.txt` (verdictGuard.ts sha256 6f589e63…);
- `vg-probe-q/items.jsonl`, read only for the item kinds (sha256 c74cc932… per its README).

## 1. The fire
| item | kind | question | before → after | label | reason |
|---|---|---|---|---|---|
| vgq-013 | threshold (date) | Did humans land on the Moon before 1970? | "No, humans did not land on the Moon before 1970. The first human lunar landing was on July 20, 1969…" → "Yes, humans did land on the Moon before 1970. …" | **BETTER** | Apollo 11 landed on 20 July 1969, and Apollo 12 in November 1969, so "Yes" is correct. The new verdict now agrees with the answer's own date. Only the verdict sentence changed; the preface and the fact sentence are byte-identical, and the result is grammatical. Fact confidence: high. |

## 2. Bars
| bar | result |
|---|---|
| 0 fires WORSE/WRONG | 0 (1 fire, BETTER) ✅ |
| 0 fires on the 25 control items | 0 ✅ (the 25 control rows in `vg-S-fires.jsonl` have flagged=false) |
| Run valid: ≥ 88/90 answers, 0 engine errors | 90/90 rows have a non-empty answer, and none looks like an error. 81 were checked (EN model answers). 9 were skipped as `not-model-route`: these are retrieval or extractive answers that VG never touches by design. ✅ Caveat: I saw only the answers, not the engine log. "0 engine errors" relies on the runner's report plus the absence of error text. |

Fire rate (descriptive): 1/65 non-control items (threshold 1/20, compare2 0/25, rank 0/20).

## 3. Missed contradictions in the apply log (descriptive; not part of the gate)
These are answers whose verdict contradicts facts stated in the same answer and that VG did not flag. There are 10 of them, against 1 caught. Only 2 fall within VG's three checks as designed.

| item | kind | what the answer says | why VG didn't fire |
|---|---|---|---|
| vgq-007 | compare2 | "Lead is denser than gold." (11.3 vs 19.3 g/cm³), then "Wait—correcting: gold is denser". The final line is right, but the lead verdict is wrong. | **In scope, lost to v2.** "denser" maps to the population-density class, which only accepts per-km²/mi² units. g/cm³ has no class, so VG abstains. Safe, but a recall cost of the v2 tightening; a mass-density class (g/cm³, kg/m³) would catch it. |
| vgq-046 | compare2 | "Mexico City has a larger population than the State of Mexico." Then city 9 M, state 12 M: "the state's total population exceeds that of the city". | **In scope (yes/no compare) but not parsed.** The question ends "…, or is it the other way around?", so the second entity takes in the tail, and the verdict doesn't start with Yes/No. (Truth: the state is larger, ≈17 M vs ≈9 M.) |
| vgq-021 | threshold | "Yes, the Amazon … longer than 10,000 km", then "~6,400 km … less than 10,000 km". | Out of scope: VG thresholds are years only. A numeric-threshold check would catch it. |
| vgq-036 | threshold | "No, Kangchenjunga is not over 8,000 meters", then "8,586 meters". | Out of scope (numeric threshold). |
| vgq-053 | threshold | "Yes, Everest is taller than 30,000 feet", then "about 29,032 feet". | Out of scope (numeric threshold). |
| vgq-018 | rank | "No, France is not the largest EU country by area. It is, in fact, the largest…" | Out of scope: superlative yes/no questions. |
| vgq-045 | rank | "No, the Amazon does not carry more water than any other river", then "It is the largest river by volume". | Out of scope (superlative yes/no). |
| vgq-049 | rank | "No, Germany is not the most populous country in the EU", then "Germany has the largest population among EU countries". | Out of scope (superlative yes/no; the rest of that answer is also false). |
| vgq-057 | rank | "Yes, China is still the most populous", then "slightly fewer people than India". | Out of scope (superlative yes/no). Truth: No, India has been larger since 2023. |
| vgq-017 | rank | "Saturn is the sixth largest planet", then "ranks second in size after Jupiter". | Out of scope (rank-position question, not "which are bigger than X"). |

The pattern is clear: the 4B's verdict-vs-own-fact contradictions on this fresh set are mostly numeric thresholds (3) and superlative yes/no questions (4), not the date/compare/rank shapes VG covers. If VG is extended later, these two shapes are the next lever. Each needs its own frozen criterion and a fresh probe set, since these 90 items are now seen.

Seen but not a VG matter (facts wrong, verdict consistent with them, so VG correctly stays quiet):
- vgq-068: the Seine is longer than the Thames, but the answer gives 186 vs 200 mi.
- vgq-078: South Dakota is larger, but the answer gives overlapping figures.
- vgq-087: Algeria is the largest in Africa, but the answer says Sudan.

AI-reviewed, not clinically reviewed.
