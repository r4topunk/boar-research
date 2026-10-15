# Method summary

TL;DR: every decision in this record follows the same short protocol. Details per arm are in `arms/`; the judge triage rules are in `L1-PROTOCOL.md`; the criterion layout is in `CRITERION-TEMPLATE.md`.

- **Pre-registration.** The pass/fail rule of an arm is written to `<ARM>-criterion.md` and hashed (sha256) before any run that can decide something. A criterion is never edited after verdicts exist; a change is a new dated addendum.
- **Smoke first.** An arm runs on a small slice (20 items) or on replayed retrieval (no LLM) before a full run. Only arms that clear the slice rule go on.
- **Two judge levels.** L1 (cheap, low-effort judge on the slice) triages direction; L2 (the strongest judge, both A/B orders, two seeds, 95 % bootstrap CIs) confirms. L1 and L2 verdicts are never mixed in one number.
- **Held-out discipline.** Held-out and burnt sets are used only through scripts that print aggregates. Every exposure is logged, and a set that has been seen is treated as development data from then on.
- **Closed means measured.** A negative result is recorded in `reports/CLOSED.md` with its minimum detectable effect and what would reopen it.
