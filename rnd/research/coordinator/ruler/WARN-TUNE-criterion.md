# WARN-TUNE criterion (frozen 2026-10-21 before any fit or count of the new features; 0 LLM, 0 judge, 0 generation, 0 paid)

## Hypothesis
A deterministic rule over features the engine already has (reason code, number of kept sources, max retrieval cosine, onSubject count,
citation count, answer length) raises the 1.7B warning line's precision for confident errors (CE) to >= 0.55 while recall stays >= 0.60:
warn the unwarned weak-source answers (WARNCAL U:kept-weak, P(CE) 0.46) and stop warning cited, well-supported ones.
Known before freezing (disclosed): WARNCAL bucket table (LP pooled per bucket P(CE)) and its by-set precision/recall; the new features were
not counted per label before this file.

## Data and labels (reused unchanged)
- Rows = WARNCAL LP rows: LITEPACKS MacBook traces K0/K1/K3 s42 x 277 items, judgments as tools/warncal_showanyway.py (sha 8e162cea...),
  whose definition block (everything before "R = []") is exec'd unchanged (row(), bucket(), labels via null-cal/tools/labels.py).
- Population for precision/recall = non-decline rows. CE = corr <= 1.5; correct = corr >= 4 (corr = mean correctness of the 2 orders).
- FIT set = the 180 self-tests (ST-cand 80 + ST-SE 100) x K0/K1/K3, Haiku 5.5-low labels only.
- EVAL set = MAIN 97 x K0/K1/K3 (held out within dev; never used for selection).
- Label families on EVAL: (H) Haiku census labels; (O) Opus-patched = Opus judge.v1 corr wherever an existing Opus judgment (both orders)
  of the identical (item id, answer text) exists, else Haiku. Opus sources (existing files only): ruler/warn-opus/out, ruler/cv5-per100/out,
  ruler/cv5-ladder/out, ruler/gemma-opus-main/out, arms/ce-opus-check/out, arms/refuse-unsupported/ce-opus-ru/out; texts resolved through the
  trace file of the judgment's runId (lp-* -> litepacks traces, lpctl-* -> lp-screens/control traces); other runIds are ignored and counted.
  Also reported: (O-only) the unweighted subset of EVAL rows with an Opus label (direction only; selected sample, not representative).
  Opus coverage of EVAL rows, of warned rows and of flagged rows is reported.

## Features (per row, from the trace; no replay)
- bucket = WARNCAL bucket (W:no-source, W:all-citations-removed, W:uncited-with-sources, U:grounded, U:kept-weak, U:no-kept(banner), U:deterministic).
- nkept = len(retrieval.kept) (= the sources event, pre-grounding).
- onsub = nkept minus N of grounding:off-topic-dropped-N minus N of grounding:health-off-topic-dropped-N, floored at 0.
- maxcos = max non-null similarity over retrieval.kept (dense/headpass picks carry a cosine; lexical hits do not); 0 if none.
- ncit = model-written citation count = len(done.cited) + sum of the numbers in citations:removed-* codes.
- alen = character length of the answer body (text minus the warning line).

## Rule family (enumerated exhaustively on FIT)
flag(r) = (warned(r) AND NOT E(r)) OR A(r), on non-decline rows.
- E (exempt, stop warning): bucket in SW AND up to 2 threshold predicates; SW = a non-empty subset of the 3 W buckets, or E empty.
- A (add warning): unwarned, outputTokens > 0, bucket in SU AND up to 1 threshold predicate; SU = a non-empty subset of
  {U:kept-weak, U:no-kept(banner), U:grounded}, or A empty. U:deterministic is never warned.
- Threshold predicate = feature <= t or feature >= t, grids: nkept 0..6; onsub 0..4; maxcos {0.55,0.60,0.65,0.70,0.75,0.80}; ncit 0..3;
  alen {150,250,400,600,900}. At most 3 threshold predicates in total; the two predicates of E use different features.
- Selection on FIT (Haiku): among rules with recall >= 0.60 and >= 30 flagged rows, max precision; ties: fewer predicates, then higher recall,
  then the first in enumeration order. Exactly one rule (SEL) goes to EVAL. The FIT top-10 are reported on EVAL as sensitivity only.

## Metrics
precision = CE among flagged / flagged; recall = flagged CE / all CE; P(correct|flagged), P(correct|unflagged), flagged n.
Before (current line) and after (SEL), on FIT and EVAL, by set (MAIN, ST-cand, ST-SE) and by arm; Wilson 95 % per cell; pooled EVAL
item-cluster bootstrap B 2000 seed 11 (cboot unchanged); paired before/after deltas on the same resample.
Per-100 under refuse-by-default (hon67.py per100 convention, unchanged formula): hidden = decline OR flag OR (outputTokens > 0 AND kept empty);
per 100 MAIN rows: correct-shown, CE-shown, partial-shown, hidden; before vs after with a paired cluster bootstrap; under H and O.

## Decision (EVAL = MAIN, points)
- PASS iff SEL reaches precision >= 0.55 AND recall >= 0.60 on MAIN under H AND under O.
- KILL iff no rule of the family (oracle search on MAIN itself, same enumeration, no flagged minimum) reaches precision >= 0.55 AND
  recall >= 0.60 under H AND O simultaneously (the same rule). The oracle best is reported (in-sample, optimistic).
- Otherwise INDETERMINATE (a rule exists in-sample on MAIN but the FIT-selected one does not transfer).
- PASS = a patch sketch for src/routing/answer.ts (no engine edit) + a screen proposal; never adopted on this file alone.

## Known limits (stated before the run)
Post-hoc on existing traces; Haiku-low judge over-calls CE (Opus precision about 0.40 vs Haiku 0.45 on MS); the judge sees the warning line
(hedge, about -0.27 corr), so moving the line changes labels in a real run and this replay cannot see that; one seed; K1/K3 share K0 text;
desktop proxy; dev sets only; no blind/, rnd/veil or bench/v0.4.
