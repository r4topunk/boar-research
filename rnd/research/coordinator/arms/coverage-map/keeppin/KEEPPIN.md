# KEEPPIN: pin the named article and relax the proper-noun rule on top of SEFIX-124 (0 LLM, MacBook replays, 2026-10-23)
Criterion ../KEEPPIN-criterion.md sha256 `83bbae38934c57abba372d8f1d17b2299cd42b8afa97f041802d77d18aafc464` (frozen before any replay, not edited). 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone.
Patch ../../retrieve-sweep/patches/KEEP-PIN.patch sha256 `40cd8c9a7465deaf3fbd7286cb8967a1b2753a5b8e2ed958e94dd955c46da2c6` (diff -ruN rs-SEFIX/src rs-KEEPPIN/src; `patch -p1 --dry-run` clean on rs-SEFIX). Tree kiln-local/rs-KEEPPIN = cp -Rc rs-SEFIX + patch, two default-off switches: RS_KEEP_PIN, RS_KEEP_PN.

**TL;DR. NO on every arm.** PIN gets Kyoto back on b15 (2 of 4 MISSES topics with b13), but by the frozen rule it changes the kept lists of 6 other topics (5 of them only reorder; b18 gains a second Cheetah chunk), and the 27-topic context p50 rises 11.1 % (the bar is 10 %). On MAIN 97 it adds +1 chunk-level fact (43, bar 45). PN does nothing on top of SEFIX-124: 0 changes on either set. That was expected from the code, because F4 already relaxes the proper-noun rule more than PN does. Health losses are 0 on every gated arm.

## What F4 does (code read before design)
onTopic's proper-noun rule is already case-insensitive (tokenizeTerms lowercases). It applies per source and asks for ANY question proper noun, not every one. "Every source" in MISSES means each source must hold one. On SEFIX-124, F4 (RS_KEEP_NOPROPER=1) restores any source that fails only this rule when the source holds another content term of the question. PN (the noun appears in some kept source or in the title) is a narrower relaxation, so on top of F4 it is inert by construction. A diagnostic PNx (PN in place of F4) was frozen alongside to show what PN would do as a replacement.

## Commands
```
cd <workspace>/rnd/research/coordinator/arms/coverage-map/keeppin
tools/run_t27.sh off; tools/run_t27.sh PIN RS_KEEP_PIN=1; tools/run_t27.sh PN RS_KEEP_PN=1; tools/run_t27.sh PINPN RS_KEEP_PIN=1 RS_KEEP_PN=1; tools/run_t27.sh PNx RS_KEEP_PN=1 RS_KEEP_NOPROPER=
tools/run_main.sh off; tools/run_main.sh PIN RS_KEEP_PIN=1; tools/run_main.sh PN RS_KEEP_PN=1; tools/run_main.sh PINPN RS_KEEP_PIN=1 RS_KEEP_PN=1; tools/run_main.sh PNx RS_KEEP_PN=1 RS_KEEP_NOPROPER=
python3 -I tools/score.py keeppin.json
```
run_main.sh = sefix/tools/run_main.sh recipe (13-pack N10 kit incl. wiki-vital5, funnel-K3 traces, a2 + append-budget) plus SEFIX-124 env. Base = sefix/replays/main.F1F2F4.jsonl (42). The task said "K1 kit as STACK", but SEFIX-124's 42 is measured on this recipe, not on STACK's v3proto kit. run_t27.sh = topics27/misses/run.sh recipe with SEFIX-124 env. Base = topics27/replay/misses.A1.jsonl. Wall: MAIN 157-229 s per arm, 27 topics 6-9 s.
**Identity (switches off): MAIN 97/97 and 27/27 on raw ids, kept ids and reason codes.**

## Arms
| arm | MAIN chunk-level /92 (cm, v0.1) | gained / lost | MAIN kept changed | MISSES recovered /4 | other 23 changed | health losses | ctx p50 MAIN / 27 | verdict |
|---|---|---|---|---|---|---|---|---|
| base SEFIX-124 | 42 (14, 28) | - | - | 1 (b13) | - | - | 653 / 324 | - |
| PIN | 43 (15, 28) | cooking-004 / none | 14 (order or bodies; 0 titles added or lost) | **2** (b13, b15 Kyoto x2) | **6**: b5 b9 b11 b14 b17 (order only), b18 (+1 Cheetah chunk) | 0 | 1.006x / **1.111x** | **NO** (clause 1: 43 < 45 and 6 > 2; ctx 27 > 1.10) |
| PN | 42 | none | 0 | 1 | 0 | 0 | 1.000x / 1.000x | **NO** (inert: keep-pn fired 0) |
| PIN+PN | = PIN on both sets | cooking-004 / none | 14 | 2 | 6 | 0 | 1.006x / 1.111x | **NO** |
| PNx (diagnostic, PN replaces F4) | 43 (money-007 gained) | money-007 / none | 2 (vit-hum-001 -2 sources, money-007 -3 sources) | **0** (b13 lost again) | 0 (b20 loses Population decline) | **b13: 2 chunks lost** | 0.989x / 1.000x | not gated: worse than F4 |

PIN fired on 34/97 MAIN items (title-pinned) and kept a pinned chunk that onSubject would have dropped on 1 of them. On the 27 topics it fired on 7. MISSES b19 (instant table) and b20 (bm25 pool) are outside what PIN and PN can reach, as predicted.

## Reading (post hoc, not the verdict)
- The PIN effect sits mostly in ordering: pinned chunks go first in compressContext, so the kept title order changes even where the set does not. Comparing sets on the 27 topics, PIN changes only b15 (the target) and b18. The frozen rule compares ordered lists, so the verdict stands.
- The context rise on the 27 topics is the pinned chunks' opening sentences, which now enter ahead of the budget (b15 187 -> 431 tokens). MAIN p50 is flat (+0.6 %).
- A narrower PIN would be needed to pass the gate. For example: pin only when the named chunk is under the relative floor, and keep the original rank order instead of putting pins first. That is a new arm with its own criterion; it was not built here.
- PNx shows F4 is the right relaxation for b13: the HIV pages never reach the compressed set, so a set-level noun check has nothing to anchor on.

## Next (if a narrower PIN arm passes)
A Haiku answer screen would need its own frozen criterion on the changed items only: b15 + b18 on the 27 topics (Detailed persona, s42 + s43) and the MAIN items whose kept bodies change (about 14), judge.v1 N 4 both orders vs the SEFIX-124 rows (cache by (id, sha256 text)). Rule: changed-item dU >= +0.02 with CI low > -0.01 and CE-unwarned not up. Not run.

## Caveats
Dev items and the bench engine (not the native Kotlin pipeline). Lexical detector. Deterministic replay, so margins are item counts. "Recovered" means the expected title is kept, not answer quality. The health-strict filter is deliberately not bypassed by PIN. There is no alias table in the packs, so an alias is only the title with its parenthetical stripped.
Files: KEEPPIN.md, keeppin.json, tools/{run_main.sh,run_t27.sh,score.py}, replays/ (gitignored).
