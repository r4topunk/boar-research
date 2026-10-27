# Knowledge packs as research modules (concept note, 2026-10-04)

TL;DR:
- Today a "pack" is mostly a text corpus (`kind: "corpus"` in `src/rag/packs.ts`). The domain behavior that actually moved scores lives as one-off code beside it: `cryptoPack.ts`, `poiPack.ts`, health cards, the travel-distance calculator.
- Proposal: a pack is a **module**: content + when to use it + how to use it + its own safety rules + its own eval slice. One manifest (Zod) per pack.
- The evidence favors this: raw-text packs moved the 4B ≈ 0. Structured, task-shaped knowledge moved items a lot (Paris–Rome 0.29 → 0.94, vegan venues 0/6 → 6/6, health route 12 → 59/60).
- MVP: refactor nothing first. Build **one** new pack in the module shape for a family where the 4B loses, then measure it with the usual L0 → L1 funnel.

## Why "more text" stopped working for the 4B (measured)

| Lever | Result | Source |
|---|---|---|
| vital5 leads (50k articles) | Δ 0.000 | QUEUE E1(a) |
| top100k Wikipedia full articles | Δ −0.005 | exp-33 |
| retrieval v2 (gold sentence in context 7 → 18/56) | Δ −0.021 | exp-35 + DIAGNOSIS.md |
| perfect Wikipedia passages (oracle, Wikipedia-only share) | ≤ +0.017 | Anvil oracle split |

Mechanisms from the rv2 diagnosis: the 4B misreads numbers in long context, partial fragments override correct memory, off-topic windows add noise. More raw text feeds all three.

## What a pack module contains

| Part | What it is | Existing example |
|---|---|---|
| Content | Text passages, **or** structured rows (tables, POIs, facts), **or** pre-written cards | Wikivoyage; OSM POIs; GeoNames cities; first-aid cards |
| Trigger | Cues that say "this pack applies" (keywords, entity types, GPS, an embedding gate) | crypto cue/ticker gate; danger detector |
| Answer mode | `passages` (RAG) · `lookup` (exact row → template) · `tool` (deterministic compute) · `card` (reviewed fixed text) | travel-calc = tool; venues = lookup; health = card |
| Context shape | What the 4B sees: short, answer-first, numbers explicit, one fact per line | city header in GPS answers |
| Safety | Pack-specific rules and refusals | CO hazard, health guards |
| Provenance | Source, licence, build date, sha256 | GeoNames CC BY 4.0, MedlinePlus rows |
| Eval slice | Dev probes + false-fire set for this pack | Sonar's 47 travel/food probes |

## Candidate packs (ranked by bounty fit; to be re-ranked by 4B-LOSS-ANATOMY.md)

1. **Destination pack** (the post author's framing: travelling offline): Wikivoyage city + OSM POIs + emergency numbers + local hazards + units/currency notes + distance tool. Mostly built already, scattered across the engine.
2. **Facts tables pack**: country/city/planet/element/population-type tables answered by `lookup` (no long context to misread). Targets the "4B misreads numbers" mechanism.
3. **Distilled explainer pack**: short, fact-dense entries for high-traffic topics, written offline by a frontier model from sources chosen by pageviews (never from bench questions). Targets the out-of-kit gap (72% of v0.2). Risks: token cost to build, leakage if topic selection touches the bench, factual errors need a spot-check.

## MVP that closes the loop

- Pick one pack after the loss anatomy shows which bucket is biggest.
- Build it in the module shape inside the engine arm only (no framework refactor).
- L0: deterministic trigger precision/recall on its probe + false-fire sets.
- L1: v0.1 EN, 2 seeds, judge.v1; adopt if Δ ≥ +0.02, confident-wrong and unsafe not up, latency on the 4B path ≤ +1 s.
- If it works, write the manifest schema from the two real uses (destination + the new one), not before.

## UNKNOWN
- How much of the 4B's loss is "knowledge missing" vs "context misread" (pending `4B-LOSS-ANATOMY.md`).
- Whether a distilled pack beats raw Wikipedia for the 4B (never tested; Q450's edge came from noise-free, question-shaped passages).
- Size budget: the kit is ~6.5 GB today; models ~3 GB; 50 GB cap leaves room, but phone install time grows with size.
