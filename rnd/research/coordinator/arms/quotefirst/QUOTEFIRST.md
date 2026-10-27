# QUOTEFIRST: quote the answering source sentence first (Qwen3-1.7B, pack set K1)

Criterion `QUOTEFIRST-criterion.md` sha256 `604dec4d…` + patch `quotefirst.patch` sha256 `c362eb36…`, both committed (35110ec8) before generation. Screen only: Mac mini gen1 slot, seed 42; judge Haiku 5.5-low judge.v1-low, N = 4, both orders, MacBook; 48 Haiku calls (cap 160), 0 Opus, 0 paid API. Dev sets only.

## TL;DR

| Screen K1 (27 problems + 10 sentinels) | Mini K1 control | QUOTEFIRST |
|---|---|---|
| U (n 37) | 0.380 | 0.369 (Δ −0.011, CI −0.058…+0.028) |
| CE count | 22 | 21 (Δ rate −0.027, CI −0.162…+0.108) |
| Problems fixed (need ≥ 6) | — | **4** |
| Sentinels worse (max 1) | — | 0 |
| Answers changed | — | 24/37 |
| Warned (warning line) | 18 | 13 |
| First sentence carries a [n] | 4 | 10 |
| Answer length p50 (chars) | 257 | 228 |

**Verdict: NO-GO. The arm stops at stage 1, and stage 2 did not run.** The model follows the format only partly. It writes a [n] in its first sentence more often (4 → 10) and warns less often (18 → 13), but it paraphrases the source instead of copying it, and 20 of the 27 problems are still CE. 8 of those 20 carry the warning line, and the other 12 are uncited answers or cited paraphrases. Two of the four fixes move only 1.5 → 2.0, which is close to the judge-noise floor described in SCREENS.md.

## Gate output (verbatim)
```
screen K1: problems 27 (CE in mini control 21) | fixed 4 (need >= 6) | still CE 20 | sentinels worse 0/10 (max 1) | changed answers 24/37 -> NO-GO
  fixed st-qa-cooking-se-008 1.5 -> 2.0
  fixed st-qa-cooking-se-020 1.5 -> 2.0
  fixed trv-004 1.5 -> 4.0
  fixed vit-cry-005 1.5 -> 2.5
```

## Format note (0 LLM, before generation)
A first draft asked the model to put the copied sentence in quotation marks. A scratch unit test showed that `"…." [1]` disables CT-1: `citations.ts` `sentenceBefore` stops at the closing quote, sees no key terms and keeps any [n] without checking it. The frozen prompt therefore says "without quotation marks". No answer started with a quote mark (0/37). A check on src/routing (608 tests) gives the same result as the unpatched tree: only the PL-1 geoWiring test fails, from a missing asset.

## Examples (verbatim)
**trv-004** (fixed, 1.5 → 4.0)
- Control: "Not found in this phone's offline library. From the model's memory, may be wrong:\nTake the Metro to the city center from Lisbon Airport. The airport is almost entirely within Lisbon, so you can walk or take a local bus."
- QUOTEFIRST: "The Lisbon Airport is within Lisbon city limits, and the metro connects the airport to the city center [5]. Take the metro or bus to reach the city center."

**vit-cry-005** (fixed, 1.5 → 2.5; this is a paraphrase, not a copied sentence)
- QUOTEFIRST: "Tornado Cash is a decentralized cryptocurrency tumbler that mixes funds to obscure their origin, while Privacy Pools are a different type of privacy service that uses a decentralized network to hide transaction details. [1]"

**vit-cry-002** (still CE, 1.0 → 1.0)
- QUOTEFIRST: "Not found in this phone's offline library. From the model's memory, may be wrong:\nFOCIL (Fork-choice Enforced Inclusion Lists) is a mechanism in Ethereum that ensures consistency in fork choices during the blockchain's consensus process. It solves the problem of inconsistent fork choices by enforcing a list of blocks that are considered valid, thereby preventing forks from occurring."

## Reading
This result agrees with LITE17 Q, where a two-pass quote run gave +0.002. Asking the 1.7B to quote, in one pass or in two, does not fix its reading. 8 of the 20 remaining CE carry the warning line, so the model answered from memory there. On the others it paraphrases loosely instead of copying the source. Neither group responds to the format instruction.
