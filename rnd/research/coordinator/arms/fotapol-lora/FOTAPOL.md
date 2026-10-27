# FOTAPOL (Qwen3-1.7B + fotapol financial-RAG LoRA v4, 2026-10-21): stage 1 NO-GO on K0 and K1, stage 2 not run

TL;DR: with the LoRA applied and nothing else changed, GATE v2 reads **NO-GO on both screens**. K0: net 6, bar 10, at the null (null net 6 / 8). K1: net 9, exactly at the bar, but U_cov -0.084 is below the -0.071 minimum, and false refusals 4/20 sit at the maximum.
The LoRA makes answers shorter (about 8 tokens fewer) and drops the engine's `[n]` citation more often. An uncited answer goes behind the warning line, which counts as a refusal in the default product (warned 0 -> 5 on K0, 0 -> 7 on K1). Several of those were correct answers, so they count as false refusals. The card's trained behaviour (cite as `[Source N]`, refuse exactly with "I cannot answer...") does not carry over to BOAR's prompt and `[n]` numbering: 0 `[Source n]` tags and 0 trained refusals in 91 answers.
Onboarding: ONBOARDING.md. Criterion: FOTAPOL-criterion.md, sha256 `5a29ff23c19ea9159439b58f0ea2b70e7f63ff29b23aa6974e89c7f3fb8152ac`, cites GATE v2 sha 34ada53f. It was committed before screen generation (rnd 08c25e08).

## Gate lines (verbatim)
```
screen2 K0: problems 30 | fixed_u 7 (by refusal 4) | new CEu 1 | net 6 (bar 10) | false refusals 1/20 (max 2) | sentinels worse 5 (report only) | U_cov -0.0480 [-0.0918, -0.0124] (min -0.059) | changed 49 | dead changed 0 -> NO-GO
screen2 K1: problems 21 | fixed_u 10 (by refusal 3) | new CEu 1 | net 9 (bar 9) | false refusals 4/20 (max 4) | sentinels worse 5 (report only) | U_cov -0.0838 [-0.1547, -0.0177] (min -0.071) | changed 41 | dead changed 0 -> NO-GO
```

## Metrics (screen items; control = mini control, plain Q4_K_M)
| | K0 control | K0 LoRA | K1 control | K1 LoRA |
|---|---|---|---|---|
| CE-unwarned (problems + sentinels) | 30 | 24 | 21 | 12 |
| of the fixes, by refusal (warned) | | 4 of 7 | | 3 of 10 |
| declines / warned | 0 / 0 | 0 / 5 | 0 / 0 | 0 / 7 |
| false refusals (sentinels) | | 1/20 (st-qa-health-se-014) | | 4/20 (lan-cmp-003, lan-exp-003, st-qa-bitcoin-se-013, st-boar-medlineplus-en-019) |
| U on covered | 0.386 | 0.338 (-0.048) | 0.431 | 0.347 (-0.084) |
| `[n]` cited / shown live | 17/50 (0.34) | 12/45 (0.27) | 28/41 (0.68) | 21/34 (0.62) |
| `[Source n]` tags | 0 | 0 | 0 | 0 |
| output tokens mean (live) | 41.2 | 33.5 | 44.0 | 36.5 |
| wall sum / p50 | 106.5 s / 1.89 s | 113.5 s / 1.90 s | 148.6 s / 4.06 s | 170.0 s / 4.53 s |
| prefill p50 / decode tok/s p50 | 933 ms / 57.0 | 1,102 ms / 52.8 | 3,048 ms / 52.6 | 3,616 ms / 48.6 |
| mini loadAvg p50 | 4.3-4.7 | 4.5 | 4.5-4.8 | 6.3 |
Wall: the LoRA costs about +18 % prefill and -7 % decode at similar load (K0), as expected for an f16 LoRA off the CPU_REPACK path (gate17). The shorter answers offset most of it (K0 wall +7 %). On K1 the mini was more loaded (+12 %). On a phone a merged adapter (peft merge, then re-quantize) would remove the LoRA overhead. That is moot after a NO-GO.

## Examples (control -> LoRA)
- False refusal, lan-cmp-003 (K1, corr 5.0 -> 1.0): the control answered "Russia, Canada, Brazil, Australia [5]". The LoRA wrote "none of the countries listed are bigger than India by area": wrong, uncited, so it went behind the warning line.
- False refusal, st-qa-health-se-014 (K0, 4.0 -> 2.5): the same content as the control, but without the `[1]`, so it went behind the warning line.
- Fix, lan-cmp-005 (K1, 1.0 -> 4.5): the control's "Nile crocodile grows up to 16 meters" became a terse "The saltwater crocodile grows bigger than the Nile crocodile. [2]". The LoRA's shortening drops the invented detail here.
- Fix, st-qa-ethereum-se-002 (K0, 1.0 -> 3.0): ENS renewal "automatic" (wrong) -> "requires payment before the expiration date".

## Reading
Shorter answers remove some invented details (a real effect on the fixes not done by refusal: 3 on K0, 7 on K1), but that is within the null on K0 (nulls fix 9-10). The citation drops push correct answers behind the warning, the same failure as MINISTRAL3-3B. The card's own levers (false refusal 41 -> 4 %, citation completion 33 -> 83 %) were measured with its trained `[Source N]` prompt on financial tables. Under BOAR's prompt, citation completion goes down, not up. Variant (b) of the shortlist (the card's format) was not run. It would need an engine prompt and numbering change, and the criterion gated variant (a) only. No re-run to rescue a NO.

## Cost and disk
Haiku 5.5-low: 98 (K0) + 82 (K1) = **180 calls** (cap 600). 0 Opus, 0 paid. Mini generation 4 min (K0) + 9 min incl. queue (K1), plus the 2 x 5-item smoke.
Disk: the adapter dir on the mini (67 MB: LoRA GGUF + source safetensors) was deleted after the verdict. The recipe line is in rnd/kiln/MODELS.md and the deletion is in rnd/kiln/DISK-LOG.md. The conversion's 1.4 GB uv cache was deleted right after conversion. Mini free about 26 GiB.
Files: fotapol.env (+ .sha256), tools/{gen_only.sh, smoke.sh, extra_metrics.py}, smoke/, arms/fotapol/{traces, judgments, aggregates (incl. *.gate2.{txt,json}, *-extra.json), runs}, run-K{0,1}.log.
