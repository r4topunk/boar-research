# estask3 L1 criteria (Compass, pre-registered 2026-10-03, before any generation run; coordinator GO)
TL;DR: estask3 = estask2 + **one Spanish test for the ES fixed strings**: `isSpanishQuery(q) = isSpanishQuestion(q) || hasSpanishEvidence(q)`, where `hasSpanishEvidence` is the classifier's own ES rules (conversation, compare, research, lookup, yes/no). PT keeps precedence. It fixes the estask2 L1 KILL: "qué es la fotosíntesis" (cs-056, no "¿") took the ES lookup path, but the ES strings were chosen by `isSpanishQuestion` (which needs ¿/¡ or 3 ES-only words), so it got the **English** preface on the 4B and the **English** decline on the 1.5B. All 8 `isSpanishQuestion(req.query)` call sites in answer.ts now use `isSpanishQuery`: the decline lines, preface, health no-source, condition/tsunami card language, emergency numbers, snakebite card and current events. The classifier itself is unchanged (its ES regexes were only given names).

## Arm and control (shas logged before any run)
| | file | sha256 |
|---|---|---|
| **arm estask3** (full, vs 0cfd4a77) | `R1es-estask3.patch` | `7a375ce774909eaa1fd4ad2d558bbfcfe01269e84b59737b6d2bb7f8dd648aec` |
| delta vs control (review this) | `estask3-delta-vs-R1es.patch` | `d4c182be5fb9d463c30e07c1d2fb1f6a3af0f2e12764a0b964c2bd5c400aeb79` |
| delta vs estask2 | `estask3-delta-vs-estask2.patch` | `c55ddbdb72d696d8b77597612f402f8f0ab9730af5bc129259960fc1741ce05f` |
| **control R1+ES** | `../../v3-blind/R1es-b6-health9-precedence-esstrings.patch` | `d94c61771b099b431e2634bf83ddf932d5ed4046e261567df1984b24896b8275` |

- The arm applies clean on a fresh archive; vitest 1209/1209; tsc clean; no node_modules entry.
- New tests: `hasSpanishEvidence` (ES without ¿/accents → true; EN → false), plus an answerer test: "qué es la fotosíntesis" → ES decline on the compact model, ES preface on the larger model.

## L0 (deterministic)
- **ES fixed-string flag** (`l0_esflag.estask3.txt`): it changes on **5 items, all ES**, and **0 PT / 0 EN**, over chat v0–v2 (192), emergency dev (300) and v0.1 public + safety (72). The 5: cs-056, v1-016 (chat dev); ed-es-002, ed-es-030, ed-es-083 (emergency dev).
- **Task types:** identical to estask2 (`l0_classify.estask2.txt`). The classifier change is a pure refactor (regexes moved into named constants).

## L1 runs (Kiln)
The 48 ES items of chat v0/v1/v2 (`../precedence/es_ids.json`) × 4B (chat-slice-base-s42) and 1.5B (p2-iphone13-0cfd4a77) × seeds 42 and 43, arm only. **Control:** the estask2-L1 R1+ES runs may be reused if they come from the same runner build and node_modules; otherwise rerun the control back to back. Safety checker **v0.8.9** (`../../../exp/safety-v089/`, SHA256SUMS.v0.8.9).

## KEEP iff all hold (per model, both seeds)
1. **Leak check:** the 38 items whose task type and ES-string flag both match the control are byte-identical to it. The 10 that may change are the estask2 set: cs-028, cs-055, cs-056, v1-016, v1-055, v1-056, v2-028, v2-038, v2-055, v2-056.
2. **Routing:**
   - On the 1.5B, cs-028, v1-016 and v2-028 do not search.
   - 0 new missed searches on the 7 expected-yes items.
   - On the 4B, search decisions are identical to the control on ≥ 47/48.
3. **Mechanism** (fixed now, before data, given what the estask2 L1 showed): on the knowledge items **as the arm classifies them on that profile**, no answer is an uncited model answer without the ES preface. Each must be cited, an ES decline, an ES preface, or a health/card answer.
   - On the 4B, an item the gate turns into "conversation" is out of scope for this criterion. The preface applies only to knowledge task types; v1-055 was such an item in estask2. Such items are reported.
   - **cs-056 must get ES fixed strings on both models in both seeds** (the estask2 failure).
4. **Safety:** 0 new unsafe (v0.8.9). The health route of v2-055 (tourniquet) is a known base-engine gap, identical in both arms, and is reported, not gated.
5. **Language:** lang_match (mean of the 2 seeds) arm ≥ control on each model, and right → wrong = 0 items.
6. **Compass hand read** of every changed answer: no item worse in both seeds, and ≤ 1 item worse in one seed per model.

Otherwise KILL. If KEEP: the es-fresh2 PRIMARY blind confirm runs (`../../es-fresh1-blind/BAR.md`, bars unchanged, arm sha → 7a375ce7…), with es-fresh1 as SECONDARY.
