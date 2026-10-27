# LITEPACKS: which default general packs for the 1.7B 8 GB line (report, 2026-10-20)

Criterion frozen before generation: `LITEPACKS-criterion.md` (sha256 4e348a8b...). Data: `aggregates/litepacks.json`, `aggregates/examples.jsonl`; script `tools/agg.py` (`python3 -I tools/agg.py`, 0 LLM). All judgments are Haiku 5.5-low judge.v1-low, N 4 shards, both orders, existing; no generation or judge call was made for this report. Generation host: MacBook (deviation recorded in the criterion). Seed 42, one seed, dev sets only.

## TL;DR

- **MAIN verdict: NO CHANGE (K0).** No arm gains U >= +0.03; every U delta on MAIN is slightly negative (-0.004 to -0.012, CIs straddle 0). The verdict computed at 18:23 is unchanged after the secondary finished (the MAIN inputs did not change).
- **SECONDARY (report only): packs help only where the pack matches.** On the 80 candidate-pack self-tests U rises +0.036 (K1), +0.045 (K2), +0.069 (K3), CI low > 0; on the 100 off-pack SE self-tests nothing moves (-0.003 to -0.011, CIs straddle 0).
- **Crowding flag (frozen rule: U on the 100 SE self-tests below K0 with CI high < 0): no arm is flagged.** K1/K2/K4 sit at -0.009 to -0.011 with CI high +0.005 to +0.015.
- The price is on-device context: prompt tokens per answer go from 384 (K0) to 729-792 (K1-K4) on MAIN, retrieval p50 196 to 559-732 ms (desktop), ttft p50 1.6 to 3.9-4.4 s (desktop), and 0.74-2.5 GB more disk.
- Post-hoc (not frozen): CE-unwarned (default-mode confident-error load) is flat on MAIN for K1-K3 and higher for K4 (+0.062, CI -0.021...+0.144); K1/K3/K4 cut it on SE self-tests (-0.05 to -0.07).

## Table per set

U = Q with declined answers at 0 (no arm declines here, so U = Q). CE = share of non-declined answers with judge correctness <= 1.5 (frozen definition). Warned = answer starts with the warning line. Delta = K - K0 paired item bootstrap (B 2000, seed 11), 95 % CI.

### MAIN (n 97 = v0.1 57 + cooking-se 20 + money-se 20; off-pack for every arm; decides)

| arm | size | U | dU (CI) | CE | dCE | warned | prompt tok mean | retr ms p50 |
|---|---|---|---|---|---|---|---|---|
| K0 | 387 MB | 0.406 | - | 0.278 | - | 0.433 | 384 | 196 |
| K1 | 1.12 GB | 0.396 | -0.010 (-0.028...+0.008) | 0.278 | 0.000 | 0.474 | 729 | 559 |
| K2 | 1.13 GB | 0.399 | -0.007 (-0.025...+0.010) | 0.289 | +0.010 | 0.474 | 732 | 575 |
| K3 | 1.17 GB | 0.394 | -0.012 (-0.034...+0.009) | 0.289 | +0.010 | 0.484 | 746 | 732 |
| K4 | 2.93 GB | 0.402 | -0.004 (-0.025...+0.017) | 0.340 | +0.062 | 0.423 | 792 | 699 |

v0.1 alone (57): dU K1 -0.011, K2 +0.000, K3 -0.005, K4 +0.009 (all CIs straddle 0); cooking+money (40): dU -0.009, -0.019, -0.023, -0.023 (CIs straddle 0). Frozen rule: qualifying needs dU >= +0.03 with CI low > 0 and dCE <= +0.02; none passes (K4 also fails the CE clause).

### SECONDARY A: 80 candidate-pack self-tests (simplewiki 20, factbook 20, medlineplus 20, firstaid 20; each arm's own installed set, so pack-matched where the arm holds the pack; K4 holds none)

| arm | U | dU (CI) | CE | dCE | warned | dwarned |
|---|---|---|---|---|---|---|
| K0 | 0.393 | - | 0.275 | - | 0.475 | - |
| K1 | 0.429 | +0.036 (+0.010...+0.062) | 0.188 | -0.088 | 0.338 | -0.138 |
| K2 | 0.438 | +0.045 (+0.015...+0.076) | 0.150 | -0.125 | 0.338 | -0.138 |
| K3 | 0.462 | +0.069 (+0.038...+0.099) | 0.138 | -0.138 | 0.338 | -0.138 |
| K4 | 0.405 | +0.011 (-0.009...+0.032) | 0.200 | -0.075 | 0.350 | -0.125 |

Pack-matched slices (dU, CI): simplewiki-self-tests K1 +0.104 (+0.063...+0.143), K2 +0.105, K3 +0.106; factbook-self-tests K2 +0.077 (-0.008...+0.173), K3 +0.104 (+0.024...+0.190), K1 (pack absent) +0.031 (-0.026...+0.092); medlineplus-self-tests K3 +0.057 (+0.010...+0.112), K1/K2 ~0; firstaid-self-tests K3 +0.007 (-0.052...+0.065), the others ~0 (the K0 baseline is already 0.42 with CE 0.05, little to fix). K4 (top-100k Wikipedia) never exceeds +0.032 on any slice.

### SECONDARY B: 100 SE self-tests (travel, ethereum, bitcoin, health, outdoors; off-pack for every arm; crowding check)

| arm | U | dU (CI) | CE | dCE | warned | dwarned | prompt tok mean |
|---|---|---|---|---|---|---|---|
| K0 | 0.364 | - | 0.370 | - | 0.430 | - | 352 |
| K1 | 0.355 | -0.009 (-0.025...+0.007) | 0.360 | -0.010 | 0.590 | +0.160 | 678 |
| K2 | 0.354 | -0.011 (-0.027...+0.005) | 0.400 | +0.030 | 0.590 | +0.160 | 686 |
| K3 | 0.361 | -0.003 (-0.023...+0.017) | 0.380 | +0.010 | 0.550 | +0.120 | 699 |
| K4 | 0.354 | -0.011 (-0.034...+0.015) | 0.310 | -0.060 | 0.620 | +0.190 | 708 |

**Crowding flag rule (frozen): flag a set whose U on the 100 SE self-tests is below K0 with CI high < 0. Result: none flagged** (all CI highs > 0). Not noise-free though: the warned share on SE self-tests rises for every arm (+0.12 to +0.19, CI low > 0 for all four), meaning retrieval keeps off-topic sources more often and the model then answers from memory under the warning. U stays flat because those memory answers are about as good as before.

## Post-hoc column (NOT frozen; added after the 2026-10-20 evening product decision)

Definition: CE-unwarned = assertive answers without the warning line and with judge correctness <= 1.5, shown as count and per-item rate (count / n). Engine refusal and notice strings and short model abstentions are declines, not CE (strings from `arms/reread-2026-10-20/REREAD.md` / `reread.py`: context.ts health-from-memory refusal, geo.ts places pack, "I didn't find this in this phone's library", first-aid notices, "not enough information" style abstentions). In the new default mode warned answers are refused, so this is the confident-error load a user would actually see. Warned answers are removed entirely, so a set that warns more shows fewer unwarned CE by construction; read it beside U.

| arm | MAIN n 97: count / rate (d vs K0, CI) | cand-pack 80 | SE 100 |
|---|---|---|---|
| K0 | 5 / 0.052 | 8 / 0.100 | 16 / 0.160 |
| K1 | 5 / 0.052 (0.000, -0.062...+0.062) | 9 / 0.113 (+0.013, -0.063...+0.088) | 11 / 0.110 (-0.050, -0.120...+0.020) |
| K2 | 6 / 0.062 (+0.010, -0.052...+0.083) | 8 / 0.100 (0.000, -0.063...+0.075) | 12 / 0.120 (-0.040, -0.110...+0.040) |
| K3 | 5 / 0.052 (0.000, -0.062...+0.062) | 6 / 0.075 (-0.025, -0.088...+0.038) | 9 / 0.090 (-0.070, -0.140...0.000) |
| K4 | 11 / 0.113 (+0.062, -0.021...+0.144) | 8 / 0.100 (0.000, -0.075...+0.075) | 9 / 0.090 (-0.070, -0.130...-0.010) |

Reading: the packs do not raise default-mode confident errors on MAIN except K4 (11 vs 5, not significant, still the one that trips the frozen CE clause). The candidate-pack arms trade CE-warned for correct grounded answers (cand-pack CE 0.275 to 0.138 for K3), but the unwarned CE count does not fall there (8 to 6 for K3), so the "confident errors cut" benefit is in the show-anyway mode, not in the default mode. All CIs on these small counts are wide (single seed, 1-16 items).

## Retrieval shares (kept slots by pack; MAIN and SE)

- K1-K3 on MAIN: simplewiki takes 67-79 % of kept slots (crypto 11-14 %, wikivoyage 10 %), factbook 1.4-1.5 %, firstaid 6 % and medlineplus 0.4 % on K3. On SE self-tests simplewiki takes 66-83 %, i.e. it displaces wikivoyage (49 %) and crypto (40 %) of K0.
- K4 on MAIN: top-100k takes 83 % of kept slots (crypto 13 %), 100 % on cooking+money.
- Kept entries per item: K0 0.82 (MAIN), K1-K3 2.7-2.9, K4 2.4. K0 mostly retrieves nothing useful on casual questions (hence 43 % warned), the larger sets always fill slots.

## Per-category notes (MAIN, K0 / K1 / K3 U and CE; small n, indicative)

- explanation (11): U 0.376 / 0.407 / 0.436 (K3 +0.06); reasoning (11): 0.508 / 0.481 / 0.477 (K1/K3 slightly worse); comparison (7): flat.
- crypto (7): 0.277 / 0.253 / 0.281; CE stays 0.71 on K0 and K1 (0.43 on K3), unchanged crypto pack, the 1.7B gets these wrong regardless.
- honesty-refusal (6), danger (2+3), health (4), synthesis (3): flat or tiny drops (e.g. danger-situation K3 0.558 -> 0.483, n 3); no category shows a reliable gain.
- cooking (20): 0.341 / 0.317 / 0.315 and money (20): 0.367 / 0.373 / 0.347: the SE-style casual sets lose slightly under all pack sets (cooking CE 0.35 -> 0.40).
- Full table: `aggregates/litepacks.json` `per_category`.

## Examples (`aggregates/examples.jsonl`, kinds: fixed, unwarned_error, crowding, regressed)

Counts per arm (fixed / unwarned_error / crowding / regressed): K1 0/9/4/2, K2 2/8/5/2, K3 5/7/3/2, K4 0/9/8/2. "Fixed" = K0 warned confident error (corr <= 1.5) that K answers unwarned with corr >= 4.

Warned-wrong -> grounded-right (K3; all five are pack-matched or have the pack):
- st-boar-factbook-006 (Tanzania capital): K0 "Dodoma ... biggest city is Dodoma as well" (corr 1.0, warned) -> K3 "capital is Dodoma, biggest city Dar es Salaam [1]" (corr 4.0).
- st-boar-factbook-012 (Eritrea independence): K0 warned memory answer, wrong (1.0) -> "independent on May 24, 1993 after a referendum [5] ... ISAIAS Afwerki" (4.5).
- st-boar-factbook-008 (Mauritius economy): warned, 1.0 -> grounded 4.0.
- st-qa-health-se-004 (120 over 80): K0 explained the numbers as "engine's maximum" (1.0, warned) -> systolic/diastolic from medlineplus [1] (4.0).
- st-qa-outdoors-se-017 (cooking meat on a fire): K0 "cast iron skillet" (1.0, warned) -> skewers / pie iron from a retrieved source [4] (4.0).

Crowding cases (K0 corr >= 4 unwarned -> K worse by >= 1.5):
- st-boar-medlineplus-en-013 (irregular heart rhythm): K0 "atrial fibrillation ... ECG" (4.5) -> K1/K2 "ventricular tachycardia" cited [2] from simplewiki (1.0). The clearest case of a wrong simplewiki chunk displacing a correct memory answer; fixed on K3 (medlineplus present).
- st-qa-cooking-se-019 (garlic): K0 4.0 -> K1/K2/K3 warned and 1.5 (K4 unwarned cited [1], 1.0).
- st-qa-health-se-008 (MRI), -011 (death criteria): K0 4.0 -> 2.0-2.5 on K1/K2/K3/K4, now behind the warning line because retrieval kept off-topic simplewiki/top-100k text.
- K4 (8 cases): lan-rsn-006 Hundred Years' War 4.5 -> 1.0 (warned, "1337 to 1478"), st-qa-bitcoin-se-015 ASIC 4.0 -> 1.0, st-boar-medlineplus-en-020 vaccines 5.0 -> 3.5, plus ethereum/bitcoin/health SE items.
These are isolated items (3-8 per arm of 277), not a pattern significant at the set level, so the crowding flag stays off.

## Verdict and recommendation

- Frozen rule: **NO CHANGE (K0)** as the installed-by-default set on the lite line. No set clears +0.03 U on the off-pack casual MAIN set.
- Where the new packs help (candidate-pack topics) the effect is real and in the expected places (simplewiki, factbook, medlineplus; +0.04 to +0.07 U on the 80 self-tests, warned share -0.14, CE -0.09 to -0.14) but those are the packs' own topics (self-tests are pack-written, so this is a ceiling for on-topic use, not for casual traffic).
- Cost is concrete: about 2x context tokens and 3-4x retrieval time per answer on the desktop proxy for K1-K3; disk +0.74 GB (K1) to +0.78 GB (K3). K4 adds 2.5 GB for no U gain and +0.062 MAIN CE.
- If a pack must be offered, K3 (+0.78 GB, the 6 packs) is the best secondary trade-off and does not crowd; it should be user-selected for health/first-aid/country-facts rather than default, because MAIN shows no gain from it.

## Limits

One seed, 1.7B only, desktop (MacBook) timing proxies, single Haiku-low judge (compresses gaps; L1-PROTOCOL addendum), K1-K4 reuse K0 judgments where the answer text is byte-identical (delta exactly 0 on those). Self-tests are written from the packs, so the pack-matched gain is an upper bound. The post-hoc column is not part of the frozen rule and changes no verdict.
