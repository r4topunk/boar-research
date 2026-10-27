# NOTE2-TRANSFER criterion (frozen 2026-10-21, before any count of this pass)

Hypothesis: ruler/hypotheses-round4-2026-10-21.json id NOTE2-TRANSFER (statement, method, kill verbatim there). Lane replay-0-llm.
Question: does NOTE-2's refuse-by-default rule hide the same share of answers on the Pixel 8a bench rows as on the desktop LITEPACKS traces of the same ids?

## The rule (NOTE-2 as written, = RU / REVEAL-CENSUS hidden definition, warncal_showanyway.py row())
Per row, among rows routed to the tier's LLM (receipt modelId = the LLM; deterministic layers = facts, cards, places, extractive, grounding-guard are out of the denominator):
hidden = decline (labels.is_decline: engine decline flag, engine refusal strings, short model abstention, empty body)
         OR answer text starts with the CMP30OFF line W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
         OR (outputTokens > 0 AND no kept source).
NOTE-2 applies it to the 1.7B and Gemma; the 4B shows its answers (its hide rate is reported as a counterfactual only). Health: hidden rows stay hidden, no reveal (counted, never in correct-hidden as a reveal benefit; reported separately).

Two readings of the phone rows (known before counting: the phone runs q17b73-a / aunion73-a / gemma73-a / gemmaa73-a / q4ba73-a are tree 0ca54d87 with engineOverrides.compactDeclinesOff unset, so the line is off: the 1.7B emits compact declines, Gemma and the 4B run as non-compact models and emit the cut 7 preface/banner instead):
- **P1 literal**: the rule above on the phone text as is.
- **P2 decision-equivalent** (the configuration NOTE-2 was validated on: lite compact tier + released declines): P1 OR, for a non-compact row routed to the LLM with outputTokens > 0 and no health code (grounding:health-*): grounding:no-source-memory in the reason codes, OR at least one kept source and no "[n]" citation in the final text (= engine release rules no-source / uncited-with-sources / all-citations-removed, answer.ts l.1228/1510/1529). For a compact row P2 = P1 (declined-compact codes are the same decisions as compact-decline-released codes). Validated on the desktop traces (P2-predicate vs line, agreement reported) before reading phone deltas.

## Pairs (shared ids = the v0.1 57 dev ids present in both; phone-only ids food/saf reported on the phone side only)
| tier | phone run | desktop trace (LITEPACKS frame, s42) | deciding |
|---|---|---|---|
| 1.7B kit | q17b73-a | arms/lp-screens/control/traces/lpctl-K0-main-s42 (mini; primary); arms/litepacks/traces/lp-K0-v01-s42 (MacBook; replication) | yes |
| 1.7B A-union | aunion73-a | arms/coverage-matrix/q17/traces/q17-KA-main-97-s42 | yes |
| Gemma kit | gemma73-a | arms/gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42 | yes |
| Gemma A-union | gemmaa73-a | Gemma K0 desktop (no desktop Gemma KA on MAIN; not pack-matched) | no (reported) |
| 4B A-union | q4ba73-a | arms/gemma4-e2b-vs4b/traces/gemma4-e2b-vs4b-K0-main-s42 (4B lite-tier swap, K0; not pack-matched) | no (reported) |

## Kill (from the hypothesis, fixed now)
KILLED iff, on P2, |hide rate phone - hide rate desktop| > 10 pp (hide rate = hidden / LLM-routed rows on the shared ids) for any deciding pair (1.7B kit, 1.7B A-union, Gemma kit). Then NOTE-2 quotes phone numbers per tier instead of desktop ones.
P1 consequence clause (config, not hardware): if P1 phone hide rate for the 1.7B or Gemma differs from desktop by > 10 pp while P2 holds, NOTE-2 must state that the rule needs the warning line (compact tier with released declines) in the build, and must not imply the current bench/RC default carries it.
RC clause (device day, 10-22, not decided here): NOTE-2's premise fails if the RC shows the warning line on <= 3/10 ids where the bench engine warns (P2 on the bench rows of the same ids); if the RC rows carry personalityId=detailed, only the warning-presence clause decides.

## Measures per tier (phone and desktop)
hide rate (P1, P2); hidden per 100 questions; seconds generated then hidden per 100 questions = sum over hidden rows with outputTokens > 0 of (total latency - retrieval) and of total latency (phone row timings; desktop host seconds reported, not compared); correct-hidden and CE-hidden per 100 questions over revealable hidden rows (text, not a decline, outputTokens > 0, not health): label = Opus judge.v1 where an Opus unit exists (unit = id | sha256(answer text)), else Haiku 5.5-low judge.v1-low; correct = corr >= 4, CE = corr <= 1.5. Hidden phone rows with no text (declines) are counted as not revealable; their desktop same-id label is reported as a proxy, separately.
Haiku: only hidden revealable phone rows with no existing label, N=4 both orders, cap 60 calls, order Gemma A-union, 1.7B, 4B. 0 Opus, 0 paid, 0 generation, 0 phone. Never blind/, rnd/veil, bench v0.4.

## Prior
Hypothesis: 1.7B hide 35-50 % of LLM-answered rows, Gemma 20-35 %, within +-10 pp of desktop. P(not killed) about 0.65.
