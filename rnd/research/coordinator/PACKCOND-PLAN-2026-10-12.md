# PACKCOND — research line for Knowledge Packs: "does the model find and use the answer when the right pack is installed?" (2026-10-12, loop coordinator; direction from r4to)

TL;DR: the product is a small model + user-selected, community-curated Knowledge Packs. The research question changes from "beat the bar on any question" to **"conditional on the pack that covers the question being installed, does the pipeline (retrieval → grounding → reading) reach the bar?"** — and, where it does not, which stage loses it. Everything needed to measure this exists today at 0 judge calls: the jev fact-in-text gate (WIKISECTION/WIKIFULL tooling), the LOSSMAP buckets, the H/K traces and Opus rows on v0.2 and V-para, and the curated packs (crypto, wikivoyage, places, preparedness, vital5, enwiki shards).

## 1. Decisions (fixed direction; r4to can override, each has a default)
- D1 **Primary metric of the line:** `in-pack conditional ratio` = judge.v1 floor-adjusted ratio on the subset of items whose rubric facts are present in the installed packs (jev fact-in-text ≥ 0.7, verified), reported next to the unconditional ratio and the subset size. The bar (0.50) applies to the conditional metric for the pack claim; the unconditional number stays reported.
- D2 **Loss decomposition per item in the conditional set:** F0 fact in pack? → F1 retrieved into raw? → F2 kept after grounding? → F3 used correctly in the answer? Buckets: `not-retrieved`, `dropped-by-grounding`, `retrieved-not-used`, `used-wrong`, `used-right`. This is RETRIEVAL-SCORECARD (10-06) at the fact level with the deep tier.
- D3 **Packs are first-class experimental units:** each pack gets a card (domain, source, licence, size, build date, chunking, coverage probe on its category of the dev sets) under `rnd/research/packs/<id>.md`; the kit of a run is always listed in the QUEUE row.
- D4 **No peer-pack crowding by default:** a pack enters a kit as the user's selection; multi-pack kits use the DEEPWIKI finding (crowding at 62 % share) as the known failure mode → the engine needs a per-pack quota or a pack-aware router; measured, not assumed.
- D5 **Judge/exposure rules unchanged:** frozen criteria, Haiku L1 → Opus L2, blind discipline, one EXPOSURES row per pass.

## 2. Options (exploration; not decided)
- O1 Pack-aware routing: classify the question to a pack (or "none installed") before retrieval; the "none installed" branch answers closed-book with an explicit "install pack X" hint (product UX + honesty).
- O2 Per-pack quota at k = 6 (e.g. ≤ 3 slots per pack) vs score-based merge; test on the two-pack and three-pack kits.
- O3 Pack chunking for small readers: shorter chunks + title/section headers in the chunk text (the 4B reads 400 tokens; the 35B 400–1,200) — a build-time knob measured by the F1/F2 rates.
- O4 Community curation format: a pack = sqlite (current format) + card + a 20-question "self-test" set the curator ships, scored by the same pipeline (gives the product a per-pack quality number).
- O5 Claim angle (honest): "with the matching pack installed, BOAR answers at X % of the reference on the pack's domain; without it, Y %" — stated per pack, with subset sizes.

## 3. Tasks (execution; P1 starts now at 0 judge calls)
| # | Task | Inputs | Output / metric | Cost | Status |
|---|---|---|---|---|---|
| P1 | **In-pack conditional measurement on existing runs** (H and K, v0.2 110 + V-para 51, s42): jev fact-in-text over the installed packs of those runs (boar-crypto, boar-wikivoyage-en, kit-vexact places on V-para) using the rationales → F0 per item; join with traces (raw/kept titles) and Opus scores → conditional ratios + the D2 buckets per pack and per category | existing judgments, traces, packs; wikifull_gate.py / section_gate.py | `arms/packcond/PACKCOND-P1.md`: table [pack × set]: n items with the fact in the pack, conditional floor-adj ratio (H, K), bucket shares | [usage detail removed] jev, 0 Claude | **running** |
| P2 | Same for the candidate packs not in the kit (vital5, preparedness, enwiki shard 07): "what would be covered if installed" + the P1 pipeline on a replay (0 LLM) for F1/F2 | packs on disk, replay-deep tools | coverage per category per pack; retrieval F1/F2 on covered items | 0 calls | after P1 |
| P3 | Pack cards for the 6 packs on disk (format, size, build, licence, category coverage from P1/P2) | P1/P2 | `rnd/research/packs/*.md` | 0 calls | after P2 |
| P4 | First pack-conditional arm (frozen criterion): the stage with the largest loss in P1 (expected: `dropped-by-grounding` or `retrieved-not-used`) gets one engine/prompt lever; measured on the conditional subset with the usual L1/L2 ladder | P1 verdict | LEVER/SMALL/NO on the conditional metric | ≈ 80 Haiku + 80 Opus | next week |
| P5 | Pack self-test format (O4) pilot on one pack: 20 public questions written by a curator (not Claude), scored by the pipeline | r4to / community | per-pack quality number | 0 calls to build; judge later | needs r4to |

Minimum that closes the loop: P1 (1 delivery) → the conditional ratio and its weakest stage (1 metric) → P4 (1 iteration).

## 4. UNKNOWN
- Whether the rubric facts of v0.2/V-para items are in any installed pack often enough for a usable conditional subset (WIKISECTION found 2/13 and 4/30 in the top-100k article; the curated packs are domain-specific, so crypto/travel may be high and reasoning/explanation near zero) — P1 answers it.
- How the community pack format handles tables and numbers (19.5 % of chunks unindexed in the enwiki builder).
- Whether the judge's reference (written with web access) is the right ceiling for a pack-conditional claim, or a pack-grounded reference should be written (v0.3 design question).

## 5. After P1/P2 (2026-10-12 evening)
- P1: with the matching pack installed, H reaches 0.55 floor-adj on v0.2 (n 32) vs 0.39 without; K 0.41 vs 0.29. Loss on in-pack items splits between grounding (right article dropped) and reading (fact kept, not used); article-level retrieval keeps only 11/32.
- P2: no pack on disk covers the V-para questions (10/51 with every candidate added); on v0.2 the top-100k pack lifts the conditional subset 32 → 59 but retrieval keeps about half, with 98 % crowding of kept slots.
- Consequence for v0.3 (decision input, r4to's): a Knowledge-Pack claim needs a **pack-matched item set** — each item written with the pack in hand and tagged with the pack id that covers it, reference answers grounded in the pack plus the writer's web check — so the conditional metric has n ≥ 100 per pack domain. Default if silent: the loop designs the format (`bench/v0.3/plan/pack-matched.md`) and r4to or a curator writes the items with a non-Claude model.
- P4 target (next frozen criterion): on the v0.2 in-pack subset (n 32 for H), a grounding lever (keep the article that contains the fact: pack-aware onSubject, or a per-pack quota) and a reading lever (fact-use instruction scoped to kept sources) measured on the conditional metric; expected +0.05…+0.10 conditional (half of the retrieved-not-used + dropped buckets), 0 judge calls until the replay shows the article kept on ≥ 50 % of the in-pack items.
