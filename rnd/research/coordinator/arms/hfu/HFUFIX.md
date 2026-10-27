# HFUFIX scoring (G1-G5)

Criterion `HFUFIX-criterion.md` sha256 `306b2274...3807621` (verified). Frozen arm: patch sha256 `673ecf17e5414ec5dea9e0065f9a3ed458ffdd2664e639d22e730d2a5bdf5bac`, worktree `coord/hfufix` 923df0ce, no code change after the build. Scored with `tools/hfufix_g3.mts` (routing only, generation stubbed, detector stubbed as in HFU), control = same code with the rule off. Raw: `out/hfufix-g3-g5b.json`. Build numbers (G1, G2, G4, G5a): `HFUFIX-build.md`.

## TL;DR: NOT ADOPT as written (G3 and G5b fail the bars), though the rule itself is safe
| gate | result | verdict |
|---|---|---|
| G1 build | applies to fresh archive, tsc clean, 1315/1315 tests, 7 new | pass |
| G2 identity | v0.1 EN s44 60/60 identical (text, tier, passages, codes); chat 192: 3 changes (cs-040, v1-031, v1-037), 0 on conversations without a health condition | pass |
| **G3 recall (held-out T)** | **arm 144/248 = 58.1%** (control 58/248 = 23.4%); bar >= 90% | **FAIL** |
| G4 HFU set (descriptive) | 69/100 lost -> 36/100 lost | n/a |
| G5a chat false fire | 0 new health routes in conversations with no health condition | pass |
| **G5b 20 non-health pairs** | **4/20 health routes in arm, and the same 4 in control** (0 introduced by the rule) | **FAIL as written** (0 required) |

## G3
Items = the 58 EN dev standalone health probes of the HFU set (emergency-dev EN, bench v0.1 health/danger, water-safety pos probes) with their fixed condition labels. Standalone form of T = T with the condition spelled out ("Is <c> contagious?", "How is <c> treated?", "What are the symptoms of <c>?", "Can you get <c> twice?", "When should I see a doctor about <c>?"); follow-up form = "Tell me about <c>." then T. Same route = health route kept (lexical health flag or early card).

| template | standalone routes health (n) | control same route | arm same route |
|---|---|---|---|
| Is it contagious? | 47 | 0 | 21 (44.7%) |
| How is it treated? | 47 | 0 | 21 (44.7%) |
| What are the symptoms? | 58 | 58 | 58 (100%; the word "symptoms" is itself lexical health, so control already keeps it) |
| Can you get it twice? | 47 | 0 | 21 (44.7%) |
| When should I see a doctor about it? | 49 | 0 | 23 (46.9%) |
| **all** | **248** | **58 (23.4%)** | **144 (58.1%)** |

Failing ids (arm), 26 probes x 4 templates = 104 forms (the "symptoms" template never fails):
- 23 probes have no card condition: `ws-001..ws-022` (contaminated drinking water) and `dng-005`. `conversationCondition` recovers nothing for them, so the rule (which requires a recovered condition) cannot fire. No card exists for them.
- 3 probes with a card condition whose turn-1 label did not match the card regex: `ed-en-049` (animalbite, "animal bites"), `ed-en-060` (burn, "burns"), `ed-en-088` (bleeding, "severe bleeding").
Descriptive only (not the gate): excluding the 23 no-card water probes, arm = 121/133 = 91.0% (contagious 21/24, treated 21/24, symptoms 35/35, twice 21/24, doctor 23/26). The rule does what it is built to do where a card condition exists; the criterion's item set includes water probes it cannot reach.

## G5b
20 non-health pairs: first 20 non-health EN public v0.1 items in file order (`vit-hum-001..006, lan-exp-001/002, lan-rsn-001, lan-cmp-001/002, lan-rsn-002, lan-ref-001, vit-trv-003/004, vit-cry-001..005`), "Tell me about <topic>." (topic phrases fixed in the tool), templates cycled in the G3 order. 4 pairs route health in both control and arm: all use "What are the symptoms?" (`vit-hum-003, lan-exp-002, lan-ref-001, vit-cry-003`), where the follow-up's own word "symptoms" fires `isHealthQuestion` (code `health:lexical`, not a rule code; no `grounding:health-follow-recovered-*` appears in any of the 20). The rule introduced 0 health routes; the bar "0 health routes" is missed by a pre-existing lexical false positive that any history-less turn would also trigger.

## Deviations / notes
- Detector stubbed (lexical path): the learned detector may change both numbers. Dev only.
- Item set for G3 = HFU's EN probes; topic phrases for G5b are my fixed choice (listed in the tool).
- Recommendation for the coordinator (not automatic): the rule is safe (G2, G5a, 0 introduced in G5b) but does not meet G3 because 23 of the 58 EN probes have no card condition to recover; adopting it as written is not supported. A follow-up fix would have to recover a non-card health topic from history, which this criterion excluded.
