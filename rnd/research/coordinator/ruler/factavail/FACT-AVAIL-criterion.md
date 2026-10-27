# FACT-AVAIL criterion (frozen 2026-10-21 before any call): is each v0.4 answer in the A-union packs? (r4to 2026-10-21: "calculate how the model performs with and without the information available")

Purpose: split the v0.4 items, BEFORE any app answer exists, into "information available in the installed packs" vs not, so the ruler reports the app's quality where it has the material separately from the content gap. Governs RULER-SPEC-v1 r4 §2.4 and the ORACLE arm.

## Inputs (pinned)
- Items v0.4 sha f9ad2f2f…; 75 items, 329 checklist points.
- Packs = the six A-union text packs in shared-data/packs/persona-a-union (shas in tools/factavail_prep.py; persona-map-v1 r1). Places tiles not included (no RC can use them today). The native app's built-in KB is not included (its text is not on disk; UNKNOWN until pulled from a device).
- Candidates: tools/factavail_prep.py (sha below): per point, FTS5 bm25 over each pack, two queries (point words; first-turn words), top 2 per query per pack, ≤ 24 passages. Output in/units.jsonl (sha below). Lexical candidates => every label is a LOWER BOUND on availability (a fact present in a passage the search missed counts as absent).
- Labeller: tools/factavail_judge.mjs (sha below), prompt verbatim in the file: "Does at least one passage state the information in the key point (the same fact, possibly in other words)? Answer yes only if a reader could write the key point from that passage alone; related or partial information is no."

## Procedure
1. Stage A: claude-haiku-5-5, effort low, all 329 units, cap 340 calls.
2. Stage B (validation): claude-opus-5-5 (default effort) on 40 units: the 20 Haiku-"yes" and 20 Haiku-"no" units first in sha256(key) order (if fewer than 20 of one label, all of them, filled from the other). Cap 45.
3. Bar: Haiku-Opus agreement >= 34/40 -> Haiku labels are primary. Else Opus labels all 329 (cap 340) and Opus labels are primary; Haiku kept as a row.
4. Item label from the primary labels: share = points stated / K. **AVAILABLE** share >= 0.5; **PARTIAL** 0 < share < 0.5; **NONE** share = 0. Also stored per item: the supporting passages (pack, chunk id, title) per stated point.
5. Freeze: out/factavail-items.json sha recorded in QUEUE + spec r4 §10 before any app arm answers v0.4. Never revised after app answers exist.

## Exposure
v0.4 question and checklist text go to Haiku/Opus with pack passages (labelling, no answering system). No agent reads point or passage text; outputs print keys and labels only. One EXPOSURES row.

## Pinned shas
4003d3adeaf1f6b852bfd9255bbdf47a1f9f57f900d1b8567a2f0e87620d16db  tools/factavail_prep.py
cc76b0af29216d683ff72d1e1c021f3822db7f5128e1796ee482ef22fd88b8d4  tools/factavail_judge.mjs
e14890183c84f0590bdd9a33a71434dace2d4f5c31f19827f3e9548ef0bcf4ba  in/units.jsonl
