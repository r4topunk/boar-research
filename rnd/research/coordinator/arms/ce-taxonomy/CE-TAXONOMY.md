# CE taxonomy: Qwen3-1.7B confident errors on the K0 pack set (27 items)

TL;DR
- 27 confident errors (CE) of the 1.7B on K0 (crypto + Wikivoyage packs), from the mini MAIN control (lpctl-K0-main-s42), judged by Haiku 5.5-low (judge.v1-low). Labels are from traces, judge rationales, reference answers and read-only pack text. No model or judge was run.
- 15 of 27 are knowledge gaps that new pack content would address (cooking, personal finance, EIP/crypto and travel facts absent from the K0 packs). 2 are fixable by the deterministic facts table (Greenland capital/population, Japan vs Germany density). 2 need model knowledge (tax premise reasoning, LOTR plot). 8 are unclear: 4 engine routing or health-guard faults and 4 reading failures, none of them pack gaps.
- 6 items had a relevant source retrieved and still went wrong (reading failures): lan-cmp-004, lan-exp-007, lan-rsn-003, vit-cry-002, vit-cry-003 (stale source), vit-cry-006. Reader fixes, not packs, are the lever for these.

## Method
- Items: rnd/research/coordinator/arms/lp-screens/screen-K0.ids (first 27 lines = problems).
- Traces: control/traces/lpctl-K0-main-s42.traces.jsonl (answer, warnings, retrieval titles, route codes). Retrieval traces hold titles only, so "had relevant source" was checked by reading the retrieved article text in boar-wikivoyage-en.sqlite and boar-crypto.sqlite (read-only).
- Judgments: control/judgments/lpctl-K0-main-s42-*.judgments.jsonl (both orders); reference answers from boar-eval/bench/v0.1/refs/refs.jsonl and boar-eval/bench/selftest/qa-*/refs/refs.jsonl.
- Deterministic coverage: arms/facts-r9/FACTS-R9.md and handoff/facts-r9-2026-10-20/facts.v1.json (country rows: capital, population, area, driving side, calling code, voltage, plug, Hz; no subnational territories).
- warned = the answer contains the "Not found in this phone's offline library" line. The trace's weak_sources flag alone does not count (it is set on most of the 27 items too).
- Per-item fields and reasons: ce-taxonomy.jsonl.

## Count tables

### question_type
| value | n |
|---|---|
| explanation | 12 |
| comparison | 5 |
| fact_lookup_number | 4 |
| other | 2 |
| reasoning_or_calculation | 2 |
| fact_lookup_name_or_date | 1 |
| recommendation_or_local | 1 |

### error_kind
| value | n |
|---|---|
| wrong_fact | 10 |
| hallucinated_specifics | 5 |
| misread_source | 4 |
| other | 4 |
| partial_missing_key_point | 3 |
| outdated | 1 |

### fixable_by
| value | n | items |
|---|---|---|
| new_pack_content | 15 | lan-cmp-005, lan-rsn-001, st-qa-cooking-se-003/-008/-012/-020, st-qa-money-se-007/-010/-011/-020, vit-cry-003, vit-cry-005, vit-cry-007, vit-hum-005, vit-trv-003 |
| unclear | 8 | lan-cmp-004, lan-rsn-003, st-qa-cooking-se-002/-013/-015, st-qa-money-se-004, vit-cry-002, vit-cry-006 |
| deterministic_fact_table | 2 | lan-exp-007 (needs a Greenland row), vit-sci-002 (needs a density template) |
| bigger_model_knowledge | 2 | st-qa-money-se-009, vit-hum-004 |
| better_retrieval_existing_packs | 0 | |
| not_fixable_offline | 0 | |

### warned vs unwarned
| warned | n | items |
|---|---|---|
| true | 16 | lan-rsn-001, st-qa-cooking-se-003/-008/-012, st-qa-money-se-007/-010/-020, vit-cry-002/-003/-005/-006/-007, vit-hum-004/-005, vit-sci-002, vit-trv-003 |
| false | 11 | lan-cmp-004/-005, lan-exp-007, lan-rsn-003, st-qa-cooking-se-002/-013/-015/-020, st-qa-money-se-004/-009/-011 |

Note: the 11 unwarned include 4 health-guard refusals or misroutes (st-qa-cooking-se-002/-013/-015, st-qa-money-se-004) and 3 confident wrong answers with no on-topic source (st-qa-money-se-009/-011, st-qa-cooking-se-020). The warning is a weak safety net: 11 of 27 CE were given with no warning line.

### had_relevant_source
| value | n |
|---|---|
| yes | 6 |
| no | 20 |
| unclear | 1 |

## Reading failures (relevant source retrieved, answer still wrong)
| id | source evidence (quote) | what went wrong |
|---|---|---|
| lan-cmp-004 | "weighing upward of 1500 lb (700 kg)" (moose, largest males) | source figure is for the largest males; answer used it as average and invented a bison weight |
| lan-exp-007 | "Greenland has far more ice cover (about 84% of its surface area)" | capital and ice right in source; autonomy omitted; population 580,000 not in source (mixed case) |
| lan-rsn-003 | "While the cheetah of Africa and Asia is faster, the pronghorn can sustain its maximum speed for much longer." | source says cheetah faster; answer named the regional pronghorn |
| vit-cry-002 | "Allow a committee of validators to force-include a set of transactions in every block" | answer misstated the mechanism and dropped the censorship purpose |
| vit-cry-003 | "Historical blocks and receipts currently occupy more than 400GB of disk space" | caveat: the retrieved EIP-4444 is the 2021 draft; the answer copied its wording, and the 2025 partial-expiry status is not in the pack (stale source) |
| vit-cry-006 | "Quadratic funding makes sure that the projects that receive the most funding are those with the most unique demand." | QF section present in the retrieved DeFi article; answer called QF a DeFi community-vote method |

## Reading the table
- Pack gaps dominate: 15 of 27 need new content, mostly cooking and personal finance, which the K0 packs do not cover (their retrieval returned off-topic articles).
- Engine faults are separate: 4 health-guard fires and 1 misroute (st-qa-cooking-se-002, -013, -015, st-qa-money-se-004) are labelled unclear. They are routing bugs, not knowledge gaps, and would be fixed in the engine rather than by packs.
- The deterministic facts table can cover 2 items. The Greenland case needs a subnational entry, which the country-only table lacks.
- Reading failures (6) are the lever that packs do not touch: the right fact was retrieved and still lost. The reader needs scope and comparison checks.

## Caveats
- had_relevant_source was judged on the full retrieved article text from the pack sqlite, not on the exact chunks the engine kept (the trace has titles only). A "no" means the retrieved article lacks the fact, so a chunk-level check cannot change it.
- Reference answers come from the bench refs; they are the judge's reference, not an independent ground truth.
- vit-* items are v0.1 dev (not held-out); st-qa-* items are public selftest sets.
