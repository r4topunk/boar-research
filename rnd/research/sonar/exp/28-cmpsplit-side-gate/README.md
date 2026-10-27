# exp-28: cmpsplit v2.1 + per-side gate relaxation, L0 on the 4B kit (Sonar, 2026-10-03 night)

TL;DR: **KILL at L0** (~35 min). The relaxation (a side hit whose *text* names the side counts as that side) changes **0/14 side picks** and adds **0 facts**. It only pins the current picks, and 2 of those are garbage: "Mozi" → Budapest § Cinemas, because *mozi* is Hungarian for cinema; "grizzly bear" → Bear Valley § Drink. No L1, per the coordinator's condition (L1 only if L0 moves keys).
- **Why it can't work:** for 5 of 7 comparison items the asked fact is **not in kit A at all**, in any of the side's top 12 hits (populations, densities, grizzly/moose/Nile-crocodile sizes). That is the knowledge gap the K1 decision closed, not a gate problem.
- **Where a side passage does exist** (vit-cry-005 Privacy Pools), it sits at side rank 8 and the side keeps k = 3.

## Setup
- **Sides:** `comparisonSides` from the v2.1 worktree (`<workspace>/wt/cmpsplit-v21`, patch 2430f5bf).
- **Side search:** `searchDetailed(side, {k: SIDE_K, titles: [side]})` on kit A (Wikivoyage + crypto packs, the and-qwen 4B kit, no vital5), using the exp-26 harness.
- **Side pick:** `bestForSide`.
- **Caveat (UNKNOWN):** the engine's fusion order across packs + bundled corpus is approximated by pack score order.
- **Items:** the 6 two-sided comparisons + vit-cry-005 (lan-cmp-003 has no sides: "Which countries are bigger than India").
- **Fact check:** the lan-cmp precheck keys are answer-shape regexes ("^yes", "polar bear is bigger"), not passage keys. So `l0b.mts` checks one hand-written passage fact per side.

## Results
| Variant (`l0.mts`, `l0b.mts`) | Side passages carrying the side's fact (14 sides) | Notes |
|---|---|---|
| v2.1, fact anywhere in the side's top 3 | 6 (5 genuine: Tornado Cash, polar bear, bison, saltwater croc, Confucian; Mozi is a false match) | v2.1 pins only 1 per side, and only when the title names the side |
| **v2.1 + per-side relaxation (coordinator's hypothesis)** | **picks changed 0/14**; key/fact in pick 0 → 0 | adds pins on 5 unpinned picks, 2 of them garbage |
| side re-pick by exact side phrase in the text (0 cost) | 2 | weak |
| side re-pick by bge-m3 vs the full question, top 12 per side | 4 (3 genuine) | **+1 genuine (vit-cry-005: ERC-8262 Related Work, "Association Set Providers")**, loses polar bear and bison. 24 pairs/question ≈ 12–24 s on a phone (est.): dead on cost |

Facts absent from the side's top 12 in kit A: Brazil and Russia populations, Japan and Germany densities, grizzly bear and moose weights, Nile crocodile size. lan-cmp-001's base context already had both sides through the named path.

## Reading
- **Comparisons on kit A lose on knowledge**, not on the gate or the split. v2.1 shows both sides' articles, but the asked numbers usually aren't in Wikivoyage's text. This is consistent with v2.1's judged Δ −0.0015 on the 1.5B.
- **vit-cry-005 is a single item** whose fix is ranking within a side, not gating. Not worth an arm alone. A cheaper version would be a side-specific `k` (e.g. SIDE_K 3 → 9 for the crypto pack only), but n=1 → not proposed.
- **v2.1 alone on the 4B** (never run) has a low prior given the above. It is cheap on the existing tree `be-0cfd4a77-cmpsplit-v21`: 7 items, 1 rep, about 5 min on the mini. The coordinator decides whether to close that question.

## Files
`l0.mts` (relaxation), `l0b.mts` (re-pick variants + per-side facts), `pp.mts` (vit-cry-005 side ranking: ERC-8262 at rank 8 of 12), `lib.mts` (copy of exp-26's), `src` → exp-09 engine src copy.
