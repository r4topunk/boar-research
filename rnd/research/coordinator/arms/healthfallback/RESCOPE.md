# HEALTHFALLBACK (H7) re-scope (2026-10-16; META, BACKLOG row 9). 0 judge, 0 paid, 0 generation

TL;DR: **CLOSE H7 as written** ("no health source → deep model answers from memory + a mandatory safety line"). WARNSPEC's `warn:no-source` tier already is that safety line, HEALTHGAP owns the classes where a memory answer is unsafe, and the remaining effect sits on v0.2 only. **Re-scope the residue as HEALTHDROP.** On the public 180, every plain no-source refusal (18/18) happens *after* the health topic filter dropped retrieved candidates, and by the agent's reading 13/18 raw lists hold a chunk whose title names the question's topic. That is a reach/filter bug with a source on hand, so it is measurable and needs no answer from memory.

## 1. What H7 was
Filed 10-12 by DEEPHEDGE (QUEUE l.952; HANDOFF-10-12 item 5; CLOSED R40/R65). Problem: on v0.2, 18/110 items route `grounding:health-strict`; 17 keep no source; **12 get the identical canned line** (wt/cut7 answer.ts l.1120 → `noHealthSourceAnswer`, context.ts l.1417: "I don't have a reliable offline source on this, so I won't give health advice from memory…"). Mean ratio 0.435; LOSSMAP: the health-strict path = 0.24 of the v0.2 loss; detector p = 1.0 on 6 reasoning + 1 crypto item (false fires); **V-para 0/58**. Proposed fix: let the deep thinking model answer under a mandatory safety sentence. Prior +0.01…+0.02 v0.2 only. HEALTHQ: query = question 17/18, raw empty 6/18 (so 12/18 had candidates and lost them).

## 2. What is now covered (counts from the arm reports)
| arm | what it does | counts |
|---|---|---|
| HEALTHGAP r2 (PASS; wt/pr1 8ac9eb7a) | routes model-only health turns of class dose / poison / co / survival to fixed text (dose line, poisoning and CO cards, no-source line) or a sourced path (`health-dose-excerpt`, `health-survival-sourced`) | probes 19/64 fire, public 1/240, v0.1 0/60; changes outside fires 0/355 |
| WARNSPEC v2 + warn.patch v2 (PASS; `deps.warn` default off until v0.3) | banner on every model-generated ∧ health-shaped turn; tiers no-source / beyond-source / sourced | probes 3/64 (4B+HG), v0.1 4/60, 180: 36 (1/18/17); FP 4 on the 180; OFF identical 304/304 |
| NUMGUARD r3 (PASS; PR #85) | no model answer on a detector-fired numeric turn (calculator or restore fire) | override 0/32, 0/6, 0/18, 0/2; v0.1 0/60 changed |
| BONSAI2-2B Q2 layer table (64 items) | where health turns land today | refusal 41 (7 with a condition card), extractive 4, cards 2, converter 2, model 15 (detector 0/15, health-strict 0/15) |
None of the three touches the `grounding:health-no-source` refusal itself: HEALTHGAP *adds* turns to it (h10 h28), and WARN excludes it by construction (not M).

## 3. What remains: the no-source refusal
| set (existing traces, warnspec/aggregates/feats.jsonl) | health-strict | no-source | plain refusal (no card, no dose line) |
|---|---|---|---|
| v0.2 (QUEUE l.952, aggregates only) | 18/110 | 17 | 12 (ratio 0.435) |
| V-para | 0/58 | 0 | 0 |
| probes 64, 4B cut 7 / with HG r2 | 46 | 41 | 34 / 28 + h10 h28 |
| v0.1 60 | 4 | 2 | 0 |
| **180, 4B+X2b with its pack** | 27 | 20 | **18** (firstaid 8, medlineplus 3, health-se 4, outdoors-se 3) |
- 180, Opus L2 (existing headpass-st/gen-x2b judgments, 0 new calls): the 18 score **0.347 vs 0.591** for the other 162 = 15 % of the loss. Ceiling if the 18 reach the rest's mean: **+0.024 pooled**.
- All 18 carry `grounding:health-off-topic-dropped-N` (N 1–5); 17/18 also show `headpass:*health-dropped`. Raw titles include Delirium, Tremor, "How to minimize sea sickness?", "How could I treat scrapes outdoors", "Slow sand filter", "Solar water disinfection", "Oxygen saturation value of smokers", and the neosporin and neck-crunch threads. The self-test items were written from these packs, so the fact is in the pack and `onHealthTopic` throws it away.
- Detector false fires are a separate issue (Sonar): sand filter, camp-stove canisters, bread mould, smokers' oximeter readings.
- Fallback options **without** a source: (a) a general-care card, which adds nothing measurable (the gold is specific content); (b) "see a professional + what to tell them", which is the current line plus a template, a UX choice with no measurable score; (c) the deep tier from memory, i.e. H7, which needs a 12 GB device, has 0 V-para effect, reverses the engine's "never from memory on health" rule, and whose WARN no-source copy is already written. With a source dropped: (d) **rescue the dropped health-pack chunk** into the existing extractive path (source text, no model on the fast tier). Only (d) is measurable on public sets (the 180), and it keeps the safety rule.

## 4. Proposal: HEALTHDROP (frozen-criterion-ready; freeze sha before step 0)
- Mechanism (engine, default off `deps.healthDrop`): in health-strict, when `onHealthTopic` leaves 0 sources and raw holds ≥ 1 chunk with packId ∈ {boar-medlineplus-en, qa-health-se, boar-firstaid-en} (the WARN pack set) whose title passes `onSubject(matchQuery)`, keep the best such chunk and add `grounding:health-drop-rescued`. The turn then takes the existing `healthExtractive` / condition-card path unchanged. HEALTHGAP classes run first and are never rescued.
- Step 0 (0-LLM replay, stub + live detector :8094; 180 with packs, 64 probes, v0.1 60, MedlinePlus 20): PASS iff (a) rescues ≥ 9/18 on the 180 refusals; (b) changes outside `health-no-source` turns = 0 on all sets; (c) 0 changes on the 19 HEALTHGAP fires and the 46 detector-fired probes stay non-model; (d) an agent reads every rescued chunk: wrong-topic rescues ≤ 1, otherwise FAIL (the filter exists for plants, caves and TV shows); (e) OFF identical to wt/pr1 + warn v2.
- Stage 1 (only if step 0 passes): 4B s42 generation of the rescued items only (extractive is deterministic; deep tier not in scope). Haiku L1 → Opus L2 on the rescued vs OFF pairs. ADOPT iff Δ raw on the rescued items ≥ +0.10 with CI low > 0, and 0 rescued answers that the Opus reader flags as unsafe or as a wrong-condition quote. Expected pooled ≤ +0.024 on the 180, 0 on V-para. This is a product item, not a bar lever.
- Out of scope: detector false fires (Sonar), PT/ES, the deep tier, the refusal copy.

## 5. BACKLOG row 9 (rewritten)
| 9 | HEALTHDROP (re-scoped H7, 10-16; product-quality; 180 public) | mac-cpu | none | proposed (H7 CLOSED as written: WARNSPEC + HEALTHGAP overlap; no measurable mechanism without a source) | ≤ +0.024 pooled on the 180 (18 refusals at 0.347 vs 0.591); 0 on V-para | step 0 = 0-LLM replay gates (a)–(e) in arms/healthfallback/RESCOPE.md §4; after PR-1 lands (wt/pr1 + warn v2 base) | freeze HEALTHDROP-criterion.md, then patch onHealthTopic rescue (default off) + replay_all over 180/64/v0.1/MLP |

UNKNOWN: 13/18 "on-topic title in raw" is one agent's reading of the titles, not a script. The packId of the dropped chunks was not checked in the traces (the host match gives 8/18 health hosts, and the Wikivoyage/Appropedia/Army chunks come from other kit packs). Whether `healthExtractive` scores well on these 18 is not measured. v0.2's 12 are not checked for rescuability (blind traces not read).
