# RATIONALEPASS (T1 of DEEP-RESEARCH-2026-10-12): what the judge says is wrong or missing in arm H (frozen 2026-10-12)

## Tags
Tags: blocker
<!-- measurement arm, no generation, no Claude calls; thresholds below belong to later tasks. -->

## Question
Over the Opus judge.v1 rationales of arm H (cut 6 + Qwen3.6-35B + thinking 512, seed 42), which axes of wrong/missing content (stale, numeric, date, entity swap, over-generalised, fabricated) carry the loss, do the rationales name the correct fact, is the content recent (2024+), and which fact type do comparison/synthesis losses concern?

## Inputs
- V-para 51: blind/V-para/runs-dt512/dh-H-vpara-s42.judgments.jsonl + sha-matched traces; v0.2 110: blind/bench-v02/runs-dt512v02/dhv-H-v02-s42.judgments.jsonl + traces.
- primary bucket and loss per id: arms/lossmap/aggregates/lossmap-H-{vpara,v02}-s42.json (not re-run).
- Script-only checks, no gateway: (a) decline oracle; (b) CITEMAP-REF (reference_sources URL domains in blind/bench-v02/live/v0.2/questions.v02-new.jsonl and blind/V-para/items.jsonl; domains only).
- Classifier: typesafe-ai/jev via Vercel AI Gateway, tools/rationalepass.py (request shape, cache, retries as lossmap.py). State per item = rationale_1, rationale_2 (the two Opus rationales), answer (<= 2,500 chars), kept_source_titles, answer_declined. Boolean axes at p >= 0.6; fact_type = argmax of the choice.
- Cache of raw gateway responses under blind/<set>/runs-*/rationalepass-cache/; rnd gets ids, labels, probabilities, counts, domains only.

## Exact question texts (instructions and criteria, literal)
- `stale` (boolean): Do `rationale_1` or `rationale_2` say that a fact in the system answer (`answer`) was true once but is outdated or superseded?
  - true: the judge says a claim in the answer is out of date, no longer true, or replaced by a newer value, version, rule, price or office-holder
  - false: the judge does not describe any claim as outdated or superseded
- `numeric` (boolean): Do `rationale_1` or `rationale_2` say that the system answer (`answer`) has a wrong or missing number, quantity, rate, price or dose?
  - true: the judge faults a number, quantity, rate, price or dose in the answer, or says one that the reference gives is missing
  - false: the judge does not fault or ask for any number, quantity, rate, price or dose
- `date` (boolean): Do `rationale_1` or `rationale_2` say that the system answer (`answer`) has a wrong or missing date, year or period?
  - true: the judge faults a date, year or time period in the answer, or says one that the reference gives is missing
  - false: the judge does not fault or ask for any date, year or period
- `entity_swap` (boolean): Do `rationale_1` or `rationale_2` say that the system answer (`answer`) names the wrong entity (person, place, product or organisation)?
  - true: the judge says the answer names a different person, place, product or organisation than the correct one
  - false: the judge does not say any named entity in the answer is wrong
- `overgeneralised` (boolean): Do `rationale_1` or `rationale_2` say that the system answer (`answer`) gives a generic statement where a specific one was needed?
  - true: the judge says the answer is generic, general or non-specific where the reference gives a specific fact, figure, name or rule
  - false: the judge does not fault the answer for being generic where a specific statement was needed
- `fabricated` (boolean): Do `rationale_1` or `rationale_2` say that the system answer (`answer`) states a fact that is invented, non-existent or unsupported?
  - true: the judge calls a claim in the answer invented, fabricated, non-existent, hallucinated or unsupported
  - false: the judge does not call any claim in the answer invented or unsupported
- `rationale_names_correction` (boolean): Does at least one of `rationale_1` or `rationale_2` state what the correct fact IS, and not just that the answer is wrong or incomplete?
  - true: a rationale states the correct value, name, date or fact that should have been in the answer
  - false: the rationales only say the answer is wrong, incomplete, thin or generic without giving the correct fact
- `recent_event` (boolean): Does the question, or the fact that is missing or wrong in `answer` according to `rationale_1` or `rationale_2`, concern something from 2024 or later (recent events, new releases, current office-holders, current prices)?
  - true: the missing or wrong content concerns an event, release, office-holder or price from 2024 or later
  - false: the missing or wrong content is timeless or from before 2024, or no missing or wrong content is named
- `fact_type` (choice): What kind of fact is missing or wrong in `answer` according to `rationale_1` and `rationale_2`?
  - infobox_attribute: a fixed attribute of an entity: population, founding date, height, capital, length
  - country_number: a national statistic: GDP, inflation, area, rate
  - practical: a how-to step, rule, procedure or threshold
  - mechanism: why or how something works
  - other: none of the above fits

## Outputs and decision thresholds (DEEP-RESEARCH §3)
aggregates/rationalepass-H-{vpara,v02}.json, RATIONALEPASS.md. Loss-weighted shares as in lossmap.py (loss = ref points - boar points, mean of both orders), per axis, cross-tabbed by LOSSMAP primary; share of wrong-primary loss for the combos.
- O-4 CURRENTEVENTS: stale >= 40 % of wrong loss. O-5 NUMCHECK: numeric+date >= 40 % of wrong loss. O-8 abstention: oracle delta >= +0.03 (mean judge ratio, every wrong-primary item replaced by a decline; no declined items => rubric floor 1/1/1, ratio = 3/ref points). T3 CMPCARD/O-7: infobox_attribute+country_number >= 30 % of comparison+synthesis loss.
- Entity+fabricated >= 50 % of wrong loss: entity-probe line (training-gated), reported only.
Reading rules: single seed (V-para shares carry about +-0.05); rationale_names_correction rate qualifies stale as a lower bound. One EXPOSURES row (script-only read, 0 Claude calls).
