# CRYPTOFACTS step 1: coverage of the 11 v0.1 crypto items (2026-10-07 16:20). Verdict: **NO** (bars i and ii fail).
Criterion sha256 b093b65a…ffc60 (verified against .sha256, not edited). 0 model / 0 judge calls; v0.1 public question + rubric + grading only; no blind/, veil/, v0.2. 4B correctness = spctl-v01-s44 judge.v1-med, mapped.boar.correctness (both orders, equal in all 11).
Rule (letter of the criterion, mirrors FACTS step 1): A/B only if *everything the question asks* comes from value fields (number, date, name, parameter, enum), with ≤ 2 deterministic arithmetic steps. Purpose, mechanism, definition or "difference" parts are prose the rubric grades on lines 2–4, so they make the item C even when a name field would pass the precheck ("near-B" in the notes).

| id | short ask | class | 4B corr | sig20 | fields a table would need | likely stable source, licence |
|---|---|---|---|---|---|---|
| vit-cry-001 | quantum ECDSA emergency | C | 2 | yes | none (hypothetical response plan) | ethresear.ch post, licence UNKNOWN |
| vit-cry-002 | FOCIL (EIP-7805) + problem | C (near-B) | 1 | yes | EIP title, status, 1-line description | EIP repo, CC0 |
| vit-cry-003 | EIP-4444 change + disk saved | C (near-B) | 2 | yes | scope (pre-Merge), rollout date (2025-07), disk saved (~300–500 GB, a dated figure) | EIP repo CC0 + blog.ethereum.org, licence UNKNOWN |
| vit-cry-004 | PeerDAS + how sampling works | C | 4 | no | EIP-7594, fork (Fusaka); the mechanism is prose | EIP repo, CC0 |
| vit-cry-005 | Privacy Pools vs Tornado | C | 1 | yes | none (comparison) | vitalik.eth.limo UNKNOWN; Wikipedia CC BY-SA |
| vit-cry-006 | quadratic funding + weakness | C (near-B) | 3 | yes | formula (Σ√c)², weakness label (Sybil/collusion), origin (2018) | arXiv 1809.06421 UNKNOWN; Wikipedia CC BY-SA |
| vit-cry-007 | d/acc definition | C (near-B) | 1 | yes | expansion (defensive/decentralized/differential), origin post (2023-11) | vitalik.eth.limo, licence UNKNOWN |
| vit-cry-008 | Glamsterdam + headliners | B | 4 | no | order (after Fusaka), meta EIP-7773, headliners EIP-7732, EIP-7928 (4 fields) | EIP repo, CC0 (Draft meta: scope may change before activation) |
| vit-cry-009 | 10,000 ETH validators pre/post 7251 | B | 1 | yes | MAX_EFFECTIVE_BALANCE 32 → 2,048, activation min 32, fork (Pectra 2025-05) + 2 divisions | EIP-7251 + consensus-specs, CC0 |
| vit-cry-010 | DAO hack lessons | C | 4 | no | date (2016-06), ~3.6 M ETH, ETC split; lessons are prose | Wikidata CC0 / Wikipedia CC BY-SA |
| vit-cry-011 | Terra collapse cause | C | 4 | no | date (2022-05); cause is prose | Wikipedia, CC BY-SA |
Class counts: **A 0, B 2, C 9, D 0** (no price/TVL item; 003's disk figure is a dated measurement, not live). Items where the 4B fails (corr ≤ 2): 6/11; A+B among them: 1 (009).
## Bars (pre-registered)
| bar | strict (letter) | sensitivity: near-B counted as B | pass? |
|---|---|---|---|
| (i) ≥ 6/11 A+B | **2/11** (008, 009) | 6/11 (+002, 003, 006, 007) | strict FAIL |
| (ii) ≥ 4/7 signal20 A+B | **1/7** (009) | 5/7 | strict FAIL |
| (iii) ≤ 3 stable sources, clear licence | 2 (EIP repo, consensus-specs; both CC0) | ≥ 4 (EIPs, blog.ethereum.org, vitalik.eth.limo, arXiv/Wikipedia), 3 licences UNKNOWN or BY-SA | strict PASS, lenient FAIL |
**Verdict by the letter: NO.** The lenient reading also fails, on (iii). So the verdict does not depend on how near-B items are read.
## Projected effect if GO (FACTS method; a projection, not a measurement)
FACTS-JUDGE divides by the 57-item reference total (279.3 points; the control's boar total is 156.0, ratio 0.558). Criterion "/57" = rubric per item; both are shown.
- Strict (fires 008, 009): (a) FACTS pooled gain +0.94/fire → +1.9 pts → **+0.007 ratio** (+0.033/item); (b) each item rises to the FACTS post-arm mean of 4.33 (009 1.00 → 4.33, 008 2.67 → 4.33) → +5.0 pts → **+0.018** (+0.088/item). Both are below the ≈ 0.025 MDE. Lenient (6 fires): +0.020 (method a) to +0.033 (prose items capped at CRYPTOTRUTH's measured card level, 002 → 2.67). +0.057 only if every fire reached 4.33. 002/007 overlap CRYPTOTRUTH's gains (not additive). Assumptions: answers are deterministic (judge noise only); 009 needs the AR calculator plus a constants row (AR excluded 009 because "EIP-7251 table not in pack").
## Trigger risk and recall ceiling
- Phrasing of the 11: pure value lookup **1** (009; plus the second half of 003); "what is X" definitions **5** (002, 004, 006, 007, 008); explain/how/why/lessons **3** (001, 010, 011); compare **1** (005). Two-part "X and Y" questions: **6/11**. The FACTS trigger needs exactly one template, so it would not fire on those 6 as built.
- Engine route_task (control): lookup 5, chat 3, research 2, compare 1. CRYPTOTRUTH's EIP card fired 0/192 on dev chat, so real users rarely ask EIP-numbered lookups in the dev data.
- Recall ceiling from FACTS r5/r6 blind sets: 60–70 % on fresh phrasing. Held-out effect ≈ 0.6–0.7 × the dev projection: strict **+0.004…+0.013**.
## CRYPTOTRUTH vs this lever
CRYPTOTRUTH (wt/cryptotruth, patch b64b3e08…) = cut 6 + NOREC (a fixed "couldn't find X offline" line replaces 4B denials) + EIPABS (a verbatim EIP card with title, status and abstract; the 4B is bypassed when the question names one EIP-N and has no quantity/calculation cue). Result: Δ +0.0092 [−0.0034, +0.0244], cw 10 → 6, 5 item-seed fires (002 ×2, 005, 007 ×2), 0/192 chat. NOT ADOPTED: its G2 failed 1/3 fictional probes (ERC-77777, a denial outside the phrase list). It also stays out of the claim build because cut 6 is frozen to answer-identical changes (CLAIM-RUNS-cut6).
- Same lever? Partly. EIPABS is already the "EIP metadata" half of CRYPTOFACTS, taken from kit text at runtime instead of a table. Its quantity cue explicitly excludes 003 and 009, the only items a constants table adds. NOREC is a different lever (honesty).
- CRYPTOSEL (EIP-7251's 2,048 constant put into context) moved 009 only 1.00 → 1.08 (L1 FAIL). The 4B does not use the constant even when it is shown, so for 009 a deterministic answer is the only path. That is one item, ≈ +0.012 ratio at 1.00 → 4.33.
## UNKNOWN
- Licences of vitalik.eth.limo, blog.ethereum.org, ethresear.ch, arXiv 1809.06421 and ethereum.org text.
- Whether Glamsterdam's headliner set is final as of today (008 is B only while the Draft meta is stable).
- Crypto class mix of v0.2 (13/110) and V-para: not opened (blind/held-out). FACTS found v0.2 "explanation/reasoning-heavy".
- Whether the judge would credit a value-only answer on 008/009 for completeness (FACTS: completeness stayed at 2–3 on multi-part items).
