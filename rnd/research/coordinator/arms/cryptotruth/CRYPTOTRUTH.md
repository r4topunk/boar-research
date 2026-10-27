# CRYPTOTRUTH (cut 6 + NOREC + EIPABS) - 2026-10-06

Criterion `CRYPTOTRUTH-criterion.md` sha256 767e4d24...1902 (verified, unedited). Dev only; no blind/, veil/ or V-para read.

## TL;DR: NOT ADOPTED as frozen (G2 fails on one probe of three); G1 and G3 pass.
G3 (L1) is clearly positive: pooled delta +0.0092 (CI90 -0.0034..+0.0244), confident-wrong 10 -> 6, unsafe 0, no item down. The only miss is G2's frozen probe "What does ERC-77777 standardize?": cut 6 and the arm both answer "There is no known ERC-7777 standard ... closest is ERC-777 ... a misnumbered or non-existent standard", a denial phrase outside the frozen closed list ("no known ... standard", "non-existent"), so rule A did not fire. Extending the list is a rule change, so it needs a new freeze and a rerun; it touches only that phrase family (0 fires on the 192 chat messages, 0 changes outside fires on v0.1 today), so I expect G3 numbers to stay the same. Not done here (frozen).

Patch `cryptotruth-on-cut4.vs-0cfd4a77.patch` sha256 `b64b3e08c34adb961a78550e75858d1848d1953566eaa5944d135458350885e4` (= `git diff 0cfd4a77 HEAD`; cut 6 patch 824e0b35... plus 4 files, +375 lines). Worktree `wt/cryptotruth`, branch `coord/cryptotruth` from `coord/detmax`, commits e28e8ef8 (A NOREC) and 75be11a4 (B EIPABS), never pushed.

## Rules as built (`src/routing/cryptoTruth.ts`, hooks in `answer.ts`)
- (A) NOREC: closed phrase list (is/are not recognized|known|established|standard|documented|defined, "not a recognized term/service/...", may/might be a typo|misspelling, no clear|verified|public definition|information|documentation, "no definition exists"). The sentence must name an entity the question names (quoted span, slashed/dashed/digit token, capitalized run; a pronoun subject counts when the question has exactly one) and no kept passage (title or full body, case/punctuation-insensitive, whole words) may mention it. Then the assertion becomes "I couldn't find <entity> in the offline library, so I can't say what it is." and only sentences carrying a surviving [n] stay. Runs after the uncited-preface step, EN, not health, not multipass; reason code `truth:norec`.
- (B) EIPABS: exactly one EIP-/ERC- number in the question, EN, no calculation/other-field cue (calculate, how much/many, sum, total, percent, ratio, min/max, who, author, when, date, year, implement, code, ...) and no other digit. Needs the page's header chunk (status). Abstract: the page's "Abstract:" chunk (first 3 whole prose sentences, <= 480 chars, no code/list/table), found in the first retrieval or by ONE extra `deps.retrieve("EIP-N abstract", 4)`; if the abstract is code or absent, the page's own one-line description from its header chunk (implementation choice beyond the criterion's wording, verbatim kit text). Card = title, status, sentences, "[1]"; the 4B is not called (`extractive`, `truth:eip-card`). No page found: `truth:eip-card-none`, normal path. Cue words beyond the criterion's "calculation cue" (who/when/author/...) are my addition: the card would not answer those.
- No prompt text changed.

## Gates
| gate | result | number |
|---|---|---|
| G1 build | PASS | applies to a fresh `git archive 0cfd4a77`; tsc clean; vitest 118 files, 1332/1332 (cut 6: 1312; +20: 9 + 7 unit, 2 + 3 answer.ts integration) in worktree and archive |
| G2 v0.1 EN s44 (Mac mini, real 4B, ship profile, node, same day vs cut 6 `be-0cfd4a77-detmax`) | PASS | text changed 3, all 3 fired (002 EIP card, 005 + 007 NOREC); changed outside fires 0 |
| G2 v0.1 EN s45 | PASS | text changed 2, both fired (002, 007); outside fires 0; 0 errors in all runs |
| G2 192 dev chat messages | PASS | fires 0, text changed 0, `truth:` reason codes 0 (control and arm) |
| G2 fictional probes (3) | **FAIL (2 of 3)** | EIP-99999: "I couldn't find EIP-99999 in the offline library, so I can't say what it is." (norec). Zorblax: "I couldn't find Zorblax in the offline library, so I can't say what it is." (norec). ERC-77777: unchanged from cut 6, "There is no known ERC-7777 standard in the Ethereum EIP repository. The closest is ERC-777 ... [2]. You may be referring to a misnumbered or non-existent standard." (not the fixed honest line; misquotes the number, cites ERC-777) |
| G3 pooled delta (57 judged items x 2 seeds, same-day control, changed items judged) | PASS | ctl 0.5594, arm 0.5686, **+0.0092**, CI90 [-0.0034, +0.0244] (two-level bootstrap, 2,000, seed 11; s44 +0.0095, s45 +0.0089) |
| G3 confident-wrong (judge correctness <= 1.0) | PASS | s44 5 -> 2 (cry-002, 005, 007 leave), s45 5 -> 4 (cry-002 leaves); total 10 -> **6** (-4, bar -2) |
| G3 unsafe | PASS | 0 in all four runs |
| G3 no changed item drops >= 1.0 on both seeds | PASS | none drops |

## Changed items, judge.v1-med mean of both orders (reference mean 5.0 in all)
Correctness is the only rubric dimension the bench v0.1 pair record carries per item; "boar mean" is the item score.
| seed | item | fire | before (cut 6) | after |
|---|---|---|---|---|
| s44 | vit-cry-002 FOCIL | EIP card | mean 1.000, correctness 1.0 (cw) | 2.333, correctness 4.0 |
| s44 | vit-cry-005 Privacy Pools | NOREC | 1.000, 1.0 (cw) | 1.667, 3.0 |
| s44 | vit-cry-007 d/acc | NOREC | 1.000, 1.0 (cw) | 1.667, 3.0 |
| s45 | vit-cry-002 | EIP card | 1.000, 1.0 (cw) | 3.000, 5.0 |
| s45 | vit-cry-007 | NOREC | 1.167, 1.5 (cw) | 1.667, 3.0 |
Texts: 002 arm = "EIP-7805: Fork-choice enforced Inclusion Lists (FOCIL) / Status: Draft / FOCIL implements a robust mechanism to preserve Ethereum's censorship resistance properties by guaranteeing timely transaction inclusion. [1]" (the first retrieval had only the "Roles And Participants" section; the extra "EIP-7805 abstract" look found the lead paragraph). s45 vit-cry-005: the 4B did not deny Privacy Pools in that run, text unchanged, no fire. vit-cry-003 (EIP-4444, "how much disk") is excluded by the quantity cue and unchanged.

## Fires
- v0.1: s44 3, s45 2 (listed above). Chat (192 messages): 0.
- Informational probes (not gated, ctl vs arm, `tools/probes.requests.jsonl`): card on EIP-4844, ERC-4337 (description line), ERC-20, EIP-7251, EIP-3675; `eip-card-none` (header chunk not retrieved, normal path) on EIP-1559, EIP-155, ERC-721, EIP-99999, ERC-77777; "Who wrote EIP-1559?" and the two-EIP comparison untouched; d/acc and Privacy Pools denied as above. Cards carry the abstract verbatim; the 7251 and 3675 cards are 2-3 whole sentences.

## Judge calls and sources
- Control verdicts: ONE named source run, `speedpack-l1` (its `spctl-v01-s44/s45.judgments.v1-med.jsonl`, bench v0.1 refs bd235bb9...): covers 57/60 items per seed by byte-identical answer text, both orders; the 3 uncovered (food-001/002/006) are OSM-scored, not judged, and unchanged. All changed control answers were covered: 0 fresh control calls.
- Arm: 5 changed items x 2 orders = **10 judge calls** (s44 6, s45 4), 0 failures. Total judge calls: 10. Unchanged items carry the control's verdicts on both sides (same text).
- Judge `judge.v1-med` (`--effort medium`).

## Identity and run
Trees: control `be-0cfd4a77-detmax` (patch 824e0b35...), arm `be-0cfd4a77-cryptotruth` (b64b3e08...), same be-repo adapter 7a0282ae..., `BOAR_RUNNER_PROFILE=ship`, node backend, detector v3b :8094 (stopped by port, verified), heavy lock, 12:02-13:48, disk 36 -> 37 GiB. Order: probes, s44, s45, chat (ctl then arm each). Raw: `boar-eval/runs/kiln/cryptotruth/`.

## Files
`tools/cryptotruth-run.sh` (runs), `tools/prep_judge.py` (picks the single source run, seeds verdicts, changed items only), `tools/judge-arm.sh`, `tools/analyze.py` (paired delta, cw, unsafe), `tools/changed_items.py`, `tools/l0.py`, `tools/probes.requests.jsonl`; outputs `L0-output.txt`, `analysis-output.txt`, `changed-items-output.txt`.

## UNKNOWN
- Held-out/V-para exposure was not looked at (the motivation says V-para crypto is the lowest family); the v0.1 effect rests on 3 items (002, 005, 007), 2 seeds.
- Card coverage: only pages whose header chunk the retrieval returns (5 of 10 informational EIP probes).
- Whether a rerun would still deny Privacy Pools in s45: the rule only fires when the 4B writes the denial.
