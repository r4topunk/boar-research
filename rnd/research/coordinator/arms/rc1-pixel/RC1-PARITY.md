# RC1-PARITY: RC1 (1.5B, Detailed) vs bench engine on the 9 speed ids (2026-10-21)

TL;DR: RC1 had **0 packs installed** (logcat: "knowledge base + 0 packs"), so it searched only the bundled knowledge base, whose hits pass a 0.7 similarity gate. The bench kit retrieved on 6/9, and 5 of those 6 came from packs only (Wikivoyage, Appropedia). Its single base-KB hit (Sahara) is exactly RC1's one retrieval. Content: RC1 has the key string from the bench answer on 6/9. 0 LLM, 0 judge. Internal; descriptive only.

## Sources
- RC1: handoff/pixel8-2026-10-20/bench/results/rc-speed9-15b/ (rows.jsonl, logcat.txt line 836, request.json). There is no kit.txt; device.json has no pack list.
- Bench (Pixel 8a, bench app, persona succinct, maxTokens 512): q4ba73-a (4B A-union), q17b73-a (1.7B kit), aunion73-a (1.7B A-union), cmp30-q15 (1.5B bench, 6 of 9 ids). Bench kit corpus: boar-crypto.sqlite and boar-wikivoyage-en.sqlite (kit.txt).
- Per-row data: aggregates/parity.json.

## Per id
Same for every RC1 row: reasonCodes = eval:fixed-model, retrieve:relevant-to-task, generate:fixed-qwen2.5-1.5b. Packs installed: 0. "key" is the gold-bearing string the 4B A-union bench answer states, matched with a case-insensitive regex on the RC1 answer.

| id | RC1 ret | prompt tok | ctx tok b/a | bench retrieved (source) | RC1 chars | bench chars 4B/1.7B | key | RC1 has key |
|---|---|---|---|---|---|---|---|---|
| lan-rsn-004 | no | 68 | 0/0 | none | 108 | 101/112 | 1804 | no (says 1959) |
| lan-cmp-005 | no | 57 | 0/0 | Wikivoyage: Bijagos Islands | 2326 | 223/62 | saltwater larger | no (says Nile)* |
| lan-rsn-006 | no | 60 | 0/0 | Wikivoyage: United Kingdom | 1764 | 158/128 | 1337-1453 | yes |
| lan-rsn-005 | no | 61 | 0/0 | none | 3505 | 277/224 | Amazon | yes (literal; names Nile vs Congo as the disputed pair) |
| lan-cmp-002 | no | 53 | 0/0 | Wikivoyage: Dalton Highway +2 | 2166 | 234/237 | polar bear larger | yes (then contradicts itself) |
| lan-cmp-004 | no | 61 | 0/0 | Wikivoyage: North American wildlife | 785 | 277/169 | bison weighs more | yes* |
| lan-hlt-003 | no | 53 | 0/0 | Appropedia: GEM mosquito FAQ, Wikivoyage: China | 1355 | 220/80 | cannot transmit HIV | no ("can potentially transmit", then "not involved") |
| lan-exp-003 | no | 61 | 0/0 | none | 1810 | 186/140 | 1963 | yes |
| lan-exp-005 | **yes (Sahara)** | 324 | 66/66 | Wikivoyage: Sahara + **Sahara (base KB)** | 2429 | 381/252 | 9.2 million km2 | yes |

\* The bench arms disagree with each other here: on cmp-005 and cmp-004, the 1.7B and the 1.5B bench rows follow the Wikivoyage chunk to the opposite verdict from the 4B's (Nile / moose). The match is scored only against the 4B's key.

Aggregates: RC1 retrieved on 1/9 and the bench (4B A-union) on 6/9. Bench base-KB hits: 1/9, the same id as RC1. Content match: 6/9. RC1 answers average 1.8k chars, against 0.1-0.4k for the bench at succinct (Detailed persona and 1024 tokens, so length is not comparable).

## Why RC1 retrieved on 1/9 (inference from snapshot wt/native-qa/android-native @ 5f8cc8f4, not RC1 itself)
1. **No packs:** DeviceEvalRunner.kt:244 lists packs as files/corpus/*.sqlite. RC1 logged "+ 0 packs" (logcat l.836), so nothing was in files/corpus: the release app had not downloaded any pack.
2. **Base KB gated:** Retriever.kt:72 passes knowledge-base hits through RagPure.gateByRelevance, with ANSWER_MIN_SIMILARITY = 0.7 (RagPure.kt:41). Large-pack (format-2) hits are not gated (same block, "+ wikiLexical"). With no packs, only base-KB chunks at similarity >= 0.7 survive, and only Sahara did.
3. **Not routing, persona or model:** all 9 rows carry retrieve:relevant-to-task (DeviceEval.kt:172), so retrieval ran and was not skipped. retrievalUsed is simply titles.isNotEmpty() (DeviceEvalRunner.kt:302). Persona and the 1.5B have no branch in this path.
Most likely cause: an empty pack directory on the RC1 install, which leaves the 0.7-gated base KB as the only source. The same ids on a bench kit with Wikivoyage installed retrieve 6/9.

## Deviations
- ruler/ids/dd1022-rc-speed9-17b.ids does not exist (no ruler/ids/ dir). Ids taken from requests/rc-speed9-15b.request.json.
- The snapshot is not RC1: RC1 rows lack the expectedKbHit field that the snapshot's DeviceEvalRunner.kt:312 writes. Cited lines are inference.
- The key strings are hand-picked from the 4B bench answer (no gold file read). A literal match is not correctness (see rsn-005, cmp-002). Bench promptTokens are null, so prompt sizes are compared for RC1 only.
- Pack hits are not gold-bearing evidence: several bench pack hits are off-topic (Wikivoyage: China for mosquitoes, Bijagos Islands for crocodiles).
