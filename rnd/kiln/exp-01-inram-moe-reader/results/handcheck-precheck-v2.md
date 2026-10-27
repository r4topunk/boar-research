# Hand check: precheck v2 vs Kiln's reading (exp-01 answers)

TL;DR:
- **Pass/fail agreement is 10/10**, so the pass% is usable.
- **Exact-status agreement is 8/10.** Two answers I label confident-wrong came out as `fail-missing` in precheck: they state something false that no `forbid` term covers.
- **So precheck's confident-wrong% is a lower bound**, not an estimate.

Method:
- Sample: 10 real exp-01 answers, 5 from precheck's pass pool and 5 from its fail pool, across all 3 models, drawn with seed 20260930 (`handcheck-sample.json`).
- I wrote my labels from the question, the item notes and the answer **before** revealing the precheck verdict.
- Precheck: `rnd/lantern/tools/precheck.py` v2 (2026-09-30).

| # | Item | Model | Answer (short) | Kiln label | precheck v2 | Pass/fail agrees? | Status agrees? |
|---|---|---|---|---|---|---|---|
| 1 | vit-fa-002 | qwen2.5-1.5b | South America, Aconcagua, diverse landscapes, airlines (thin but ≥2 real facts) | pass | pass | ✓ | ✓ |
| 2 | vit-fa-010 | qwen3-4b | measles R0 ≈ 15–18, the most contagious | pass | pass | ✓ | ✓ |
| 3 | vit-fa-006 | qwen3-4b | (no-LLM snippet) museum passage about a Blue Whale model; does not answer | fail-missing | fail-missing | ✓ | ✓ |
| 4 | vit-hum-004 | qwen3-4b | "Gríma does **not** kill Saruman… Gríma is killed by Aragorn and Legolas" | **confident-wrong** | fail-missing | ✓ | ✗ |
| 5 | vit-hlt-003 | qwen2.5-1.5b | more dangerous; different strain raises risk of DHF | pass | pass | ✓ | ✓ |
| 6 | vit-cry-011 | ling-3.0-tiny | UST sell-off, peg broke, $40B lost; says "partially collateralized by LUNA", never "algorithmic" | fail-missing | fail-missing | ✓ | ✓ |
| 7 | vit-fa-020 | qwen3-4b | 8,848.86 m, world's tallest, Nepal–China border | pass | pass | ✓ | ✓ |
| 8 | vit-hum-001 | qwen2.5-1.5b | generic "extend love to all beings"; no benefit/consequentialist grounding | fail-missing | fail-missing | ✓ | ✓ |
| 9 | vit-cry-006 | ling-3.0-tiny | no square-root rule; weakness given as "concentration among well-capitalized groups" (the real weakness is collusion/Sybil) | **confident-wrong** | fail-missing | ✓ | ✗ |
| 10 | vit-fa-026 | qwen3-4b | France beat Croatia 4-2, Moscow | pass | pass | ✓ | ✓ |

**Consequence for the exp-01 README:**
- The pass% numbers are reported as they come.
- Confident-wrong% is reported as "≥ precheck count".
- The two misses above are counted by hand as a note, not merged into the table.

The finding goes to Lantern: `forbid` lists cannot catch novel false claims. Candidate fix: a judge-only "states a falsehood?" flag on `fail-missing` items.
