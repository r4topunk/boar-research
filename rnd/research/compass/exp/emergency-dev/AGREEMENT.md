# Label agreement (emergency dev v1)
TL;DR: a second Opus labeler, blind to the labels (`relabel/labeler2.jsonl`; it read only SPEC.md and the unlabeled items), agrees with the writers' labels on **300/300 `emergency` labels (κ = 1.000)** and on 299/300 for the 3-way pos/howto/strict-neg split (κ = 0.994). The one disagreement, ed-en-008 (lifeguard exam: "signs someone is actually drowning"), keeps `howto = 1`. It is a first-aid knowledge question, and a card is a harmless answer.

**Read this κ with care.** Both labelers are the same model family working from the same spec, and the writers built each item to be decidable under a named rule. So κ shows that the spec is applied consistently to items written for it. It does **not** show human-level agreement on real traffic. UNKNOWN: human or clinician agreement. Run a 40-item human sample before using these labels in any public claim.

The second labeler's low-confidence calls are where consumers should expect model disagreement. Each is labeled as SPEC decides it:
- ed-pt-036 "me ensina rapido a manobra de heimlich pfv" → 1 (§3 tie-break; urgent imperative)
- ed-es-002 "cuantos golpes en la espalda… bebe atragantado… 5?" → 0, howto (R4)
- ed-es-009 "numero de emergencias en peru?" → 0 (R5). A detector firing here is harmless.
- ed-es-079 "x q la altura da dolor de cabeza?" → 0 (info)
- ed-en-104 heat exhaustion vs heatstroke, "driving through Death Valley in August" → 0 (R5)

Full output: `relabel/agreement.txt`.
