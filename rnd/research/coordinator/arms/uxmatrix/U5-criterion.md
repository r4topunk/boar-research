# U5 FOLLOWUP-PACKS criterion (frozen 2026-10-23 before any replay; never edited after)
Question: with the knowledge pack on and the adopted search stack, does a source found on turn 1 survive the follow-up turn in OUR engine (desktop twin, 0 LLM)?
Row U5 of CLOSING-TESTS-2026-10-23.md. 0 LLM, 0 judge, 0 paid, 0 phone, MacBook only (mini not used). Never reads blind/.

## Engine and kit
- Tree kiln-local/rs-U5 = byte copy of kiln-local/rs-SEFIX (read-only, untouched) + arms/retrieve-sweep/patches/R5-STICKY.patch (sha 6b172fd2..., default off: RS_STICKY unset = rs-SEFIX code path). Identity check: LONGSESSION 50 turns, ON arm, rs-U5 vs rs-SEFIX, kept chunk ids + reason codes must match 50/50, else the carry columns are void.
- Kit = K13 (compose kits.py 10, the 13-pack kit SEFIX-124 was measured and adopted on; the "K1 kit" in the task text is read as this kit, because the six F8 gold packs must be in it). Settings packHeadPass a2, packDense2 append-budget (SEFIX run_main recipe), --gate search, model id qwen3-1.7b-q4km, ram 12, cpu embed, wide 0. Detector absent (lexical predicate), same in every arm.
- Replay tool: arms/coverage-map/searchpar/r5/tools/replay-sticky.ts (chained turns: an item with prevId gets the previous item's history from the chain file and, for RS_STICKY, the previous turn's own emitted sources). The engine never puts history into the retrieval query (R5), so turn 2 is searched with the user's fragment only.

## Sets (dev, agent-written; the ids UXT-24 used)
- F8: the 48 QFORM pairs (F0 -> F8) in arms/coverage-map/searchpar/r5/qform.chain.jsonl (96 turns).
- LS: the 20 LONGSESSION follow-up turns (followup = true, turns 2-5) of arms/coverage-map/searchpar/r5/longsession.chain.jsonl (50 turns replayed in order). Pair = (previous turn, follow-up turn). The UXT-24 subset of 16 pairs where his engine kept the referent on turn 1 is reported as a second line.

## Arms (all on rs-U5, K13)
- BASE: no switches (RS_MERGE, RS_SE_*, RS_KEEP_NOPROPER unset) = stock search on the same kit. (R5's base 2/48 used another recipe: rs-R5, v3proto cooking/money, packDense2 extra; it is quoted for scale only, not reused, because the recipe differs.)
- ON: SEFIX-124 = RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 (RS_HEALTH_NOSOURCE_FALLBACK unset).
- OFF: ON with the relevant pack removed from the kit. F8: the item's gold pack (items field pack; 6 runs, one per pack, both turns of that pack's 8 pairs). LS: per pair, the pack that supplied the referent-bearing kept chunk on the previous turn in ON (most frequent pack among those chunks, tie -> first in kept order); pairs whose previous ON turn kept no referent chunk use the pack of the follow-up turn's first ON kept chunk; pairs with no kept chunk in either keep the full kit (reported). Pack = the middle field of the chunk id (pack:local-<pack>:n).
- Each arm also runs with subject carry, RS_STICKY=2 (R5 variant: the previous turn's sources pinned last, matched against previous question + this turn; never displaces a base chunk). Carry runs are only used for the R and carry-junk columns.

## Metrics per set x arm
- Hit rule. F8: the item's normalised gold quote inside title+body of a kept chunk (score_r5 rule). LS: a referent string (lowercase) inside title+body of a kept chunk (proxy, no fact labels).
- K1 = hit on turn 1 (F0 / previous turn); K2 = hit on turn 2; S = K1 and K2 (survived); survival = S / K1; LOST = K1 and not K2; G = K2 and not K1 (found only on turn 2).
- R = LOST pairs where the same arm with RS_STICKY=2 hits on turn 2 (lost but subject carry recovers).
- Junk on turn 2 = off-subject kept chunks / all kept chunks, pooled over the set's turn-2 items. Off-subject: F8 a kept chunk whose docId is not the gold article (pack:local-<pack>:a<article_id>); LS a kept chunk with no referent string. Reported for the arm and for its carry run, plus the carry multiplier = off-subject kept count (carry) / off-subject kept count (no carry) over the same turn-2 items. LS also reports mean kept on the 30 self-contained turns 2-5 with and without carry (carry noise on topic switches).

## Gate
None: measurement. A follow-up fix (subject carry, or making the fragment point back) is worth proposing only if, in ON, on F8 R >= 10 of 48 at carry multiplier <= 1.20x, or on LS R >= 4 of 20 at carry multiplier <= 1.20x and self-contained mean kept <= 1.20x. Otherwise: no follow-up fix from this test.
Comparison line (not a gate): the app maintainer's FollowUp rule (UXT-24, his engine, KB + Vital + 6 packs) survives 17/18 F8 and 12/16 LS.
