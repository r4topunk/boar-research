# CRYPTOSEL L1 (v0.1 EN s44 + s45, judge changed items only): **FAIL** (target mean +0.472 < +0.5)

## Run identity
- Criterion `CRYPTOSEL-criterion.md` (sha256 6ba3e103…, frozen before any code). Stop rule: no revision after L1.
- Code frozen at patch `cryptosel-on-cut3.vs-0cfd4a77.patch`, sha256 948493ee1fe99e19b30672460812951581768ef39c278bcd080f392c2727bb79 (verified in the tree's PATCH_SHA256). Tree: mini `be-0cfd4a77-cryptosel` (src differs from `be-0cfd4a77-cut3` only in the 7 patch files). Runner be-ship 949eee03 (adapter copied from the cut3 tree, checked before the run).
- Config as cut3-confirm: requests re-keyed (arm cryptosel), detector v3b ON, `--places` kit-vexact, Android 12 GB 4B, kit A, seeds 44/45, heavy lock (waited for CVO to finish), 60/60 valid, 0 errors. Mini disk 47 GiB before and after. Scripts `rnd/kiln/l1/cryptosel-l1{,-wait,-judge}.sh`, `cryptosel-l1-analyze.py`; outputs in `boar-eval/runs/kiln/cryptosel-l1/` (analysis.txt).
- Judge: `judge.mjs --effort medium` (judge.v1-med), both orders, from the MacBook, 4 changed items x 2 seeds = 16 verdict pairs; cut 3 verdicts rebuilt exactly as in cvh-l1-analyze.py. Rubric = BOAR mean of 3 dimensions, both orders, then both seeds.

## Identity vs cut 3 (cut3-confirm traces)
Answer text differs on 4 items, in both seeds: the 3 targets and **lan-exp-007** (Greenland). lan-exp-007 is not crypto-routed: its sources, reason codes and context tokens (641->498) are identical to cut 3 (and to the CVH run), so the text change is generation noise, not the arm. It was judged too and counts in the changed-item set and the 57-item Δ. The other 56 items are byte-identical.

## Per-item rubric (mean of s44/s45)
| item | cut 3 | CRYPTOSEL | Δ | per seed (cut 3 -> new) |
|---|---|---|---|---|
| vit-cry-002 FOCIL (target) | 1.000 | 2.500 | **+1.500** | s44 1.00->2.67, s45 1.00->2.33 |
| vit-cry-003 EIP-4444 (target) | 2.167 | 2.000 | -0.167 | s44 2.00->2.00, s45 2.33->2.00 |
| vit-cry-009 EIP-7251 (target) | 1.000 | 1.083 | +0.083 | s44 1.00->1.17, s45 1.00->1.00 |
| lan-exp-007 (noise, same context) | 3.833 | 3.333 | -0.500 | s44 3.33->2.33, s45 4.33->4.33 |

**Target mean change: +0.472** (bar >= +0.5).

What happened in the answers: 002 now describes the committee/inclusion-list mechanism and censorship resistance (was a wrong "block inclusion/finality" story; confident-wrong gone in both seeds). 009 now reads the 2048 ETH cap and computes 5 validators, but still gets the "before" case wrong (it uses 2048 ETH as the pre-EIP cap and says 5 both before and after; the reference is 312 before / 5 after), so the judge barely moves it (correctness stays <= 1.0). 003 gains the 33,024-epoch cutoff but its "roughly 3 years / 10 months" are wrong and the disk figure is unchanged (~400 GB), so no gain.

## Safety and confident-wrong
- Unsafe (safety v0.9.1): cut 3 0/0, CRYPTOSEL 0/0 (s44/s45).
- Confident-wrong (mean correctness <= 1.0): cut 3 s44 4, s45 5; CRYPTOSEL s44 3, s45 4 (vit-cry-002 leaves the list in both seeds; vit-cry-009 stays on it).

## Paired 57-item Δ
Pooled BOAR/ref ratio (both seeds, 57 judged items; two-level bootstrap, items then seeds, 2000 draws, seed 11): cut 3 0.5656, CRYPTOSEL 0.5689, **Δ +0.0033, CI90 [-0.0049, +0.0139]**.

## Gates
| gate | result | verdict |
|---|---|---|
| target items mean rubric Δ >= +0.5 | +0.472 | **FAIL** (by 0.028) |
| no changed item down >= 1.0 | worst -0.500 (lan-exp-007, noise) | PASS |
| unsafe 0 | 0 | PASS |
| confident-wrong not up | 4/5 -> 3/4 | PASS |
| paired Δ >= 0 | +0.0033 | PASS |

**Overall: FAIL on the target gate; per the stop rule there is no revision after L1.**

## Reading
- The context fix works as designed: all three targets get the gold fact (L0) and the 4B uses it (002 and 009's cap, 003's cutoff). The judged gain concentrates in vit-cry-002 (+1.5); 009's arithmetic still needs a model that reads "before 32 ETH / after 2048 ETH" correctly, and 003's disk saving is not in the pack.
- lan-exp-007's -0.5 is noise with an identical context; without it the target gate is unaffected (it only counts targets), but it shows the one-sample noise on a single item is of the same size as the gap to the bar.
- The paired Δ is positive and its CI90 straddles 0, as expected for 3 changed items; no safety or confident-wrong regression, so the arm is harmless but not adopted under the frozen criterion.
