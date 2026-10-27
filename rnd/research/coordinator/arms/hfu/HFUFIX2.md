# HFUFIX2 scoring (G3' and G5b')

Criterion `HFUFIX2-criterion.md` sha256 `0b813a92...e7017` (verified). Same frozen patch 673ecf17e5414ec5dea9e0065f9a3ed458ffdd2664e639d22e730d2a5bdf5bac (`coord/hfufix` 923df0ce), no code change. Tool `tools/hfufix_g3b.mts` (routing only, generation and detector stubbed; control = same code with the rule off). Raw `out/hfufix2-g3-g5b.json`.

## TL;DR: NOT ADOPT. G3' fails the 90% bar (arm 64/76 = 84.2%); the control gap and G5b' pass. Per the criterion this closes the rescue.
| gate | result | verdict |
|---|---|---|
| G3' same route, arm | 64/76 = 84.2% (bar >= 90%) | FAIL |
| G3' arm - control | 84.2 - 40.8 = +43.4 points (bar >= 30) | pass |
| G5b' health routes added by arm over control (20 pairs, T2) | 0 (control 0, arm 0) | pass |

## Scope
"Card condition" = `conversationCondition(<probe's standalone question text>, []).condition` from the control engine (`src/routing/conditionCards.ts`, which wraps `regexCondition`), non-null and not "MULTI". 19 of the 58 EN dev probes qualify. Standalone form of each T2 = T2 with the condition label spelled out ("How long does <c> last?", "Is <c> dangerous?", "What causes <c>?", "How can I avoid <c>?", "What do I do now about <c>?"; the last has no pronoun, so my wording for its standalone form is a fixed choice). Follow-up form = "Tell me about <c>." then T2. Same route = health route kept.

## G3' per template
| template | standalone routes health (n) | control same route | arm same route |
|---|---|---|---|
| How long does it last? | 15 | 0 | 11 (73.3%) |
| Is it dangerous? | 15 | 15 | 15 (100%; "dangerous" is lexical health on its own) |
| What causes it? | 15 | 0 | 11 (73.3%) |
| How can I avoid it? | 15 | 0 | 11 (73.3%) |
| What do I do now? | 16 | 16 | 16 (100%; `isHealthFollowUp` already handles it) |
| **all** | **76** | **31 (40.8%)** | **64 (84.2%)** |

Failing ids (arm, 12 forms): `ed-en-049` (animalbite), `ed-en-060` (burn), `ws-015`, `ws-021`, each on "lasts", "causes" and "avoid". Same mechanism as HFU-FIX for ed-en-049/060: the turn-1 label ("animal bites", "burns") does not recover a card condition through `conversationCondition`, so the rule does not fire. For `ws-015` and `ws-021` the standalone probe text carries a card condition (as defined by the criterion) but the turn-1 label "contaminated drinking water" carries none.

## G5b'
The same 20 non-health pairs with T2 cycled in order: 0 health routes in control and 0 in arm; 0 added.

## Notes
Detector stubbed (lexical path). G2 and G5a are unchanged from `HFUFIX-build.md`. Arm clears the control-gap bar but misses the absolute bar by 5.8 points; failing forms are limited to 4 probes. No further rescue per the criterion.
