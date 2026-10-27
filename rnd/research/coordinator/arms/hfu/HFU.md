# HFU: health-route recall on follow-up forms (cut 5, deterministic diagnostic)

Criterion: `HFU-criterion.md` (sha256 `64a6bf1de68d914ee1d36648c536ed7371793e665316c51c12cf0c5880310cdd`, verified before the run, unedited). Engine: `wt/cut5lite` @ 7173c9af. Tool: `tools/hfu.mts` (`tsx tools/hfu.mts <engine-tree> out`). Raw: `out/{summary.json,rows-a.json,rows-b.json,losses.tsv}`. No generation, no judge, no blind/veil/health-fresh/chat-v3 data.

## TL;DR
- **69 of 100 follow-up forms (69%) lose a health route their standalone form gets** (synthetic set B). Chat slices (A): 2 of 3 (n too small). Criterion set combined: **71/103 = 69%**. The >= 10% rule is **met** (also on EN only: 33/58 = 57%).
- Prevention follow-up ("How do I prevent it?"): **50/50 lost (100%)**. Action follow-up ("What should I do if I get it?"): 19/50 lost (38%): EN 4/29, ES 2/8 (1 recovered), PT 13/13 lost.
- Mechanism: the health flag in answer.ts is `isHealthQuestion(query) || isHealthFollowUp(query, userTurns) || cardEmergency`, and only `isHealthFollowUp` reads history. It requires (1) a previous health turn, (2) at most 12 words, **all** from a closed allowlist (`FOLLOW_UP_WORDS`), and (3) a match of `FOLLOW_INTENT` (what-do-I-do / is-it-serious / hospital / doctor / EN, PT, ES). Prevention, information and any phrasing with an out-of-list word ("tiver", "prevent") never match. Condition from history (`conversationCondition`) is still resolved in 41 of the 69 losses, but it is only consumed inside the health branch, so the card never fires. The query-only canonical-health-terms retrieval (answer.ts L932 without detector) also drops.

## Method
Health route of a form = answer.ts treats the turn as health (`isHealthQuestion || isHealthFollowUp || (!lexical && !fu && isCardEmergency)`) or an early card fires (snakebite card, CO hazard, emergency numbers). Replicated from the leaf modules (`context`, `conditionCards`, `firstAidCards`, `coHazard`, `emergencyNumbers`, `classify`, `routeGate`, `smallTalk`) with `userTurns` = earlier user turns. Reason codes shown: `health:lexical`, `grounding:health-card-condition`, `grounding:health-follow-up`, `condition:<card>[:from-history]`, `ui:safety-note` (isSafetyQuery), `retrieve:canonical-health-terms`, `answer:*` early cards, `task:<rule>`.

### Set A (chat slices v0-v2, 192 conversations)
Health keyword list (case-insensitive, word-start match on any turn, user or assistant): `KEYWORDS` in `tools/hfu.mts` (also in `out/summary.json`): dengue|malaria|zika|fever|febre|fiebre|sick|illness|disease|doenca|enfermedad|symptom|sintoma|doctor|medico|hospital|medicine|remedio|vaccin|vacina|pain|dor|dolor|injur|ferid|herida|bleed|sangr|burn|queimad|quemad|bite|picad|mordid|sting|poison|envenen|intoxic|allerg|alergi|asthma|diabet|insulin|pregnan|heart|coracao|stroke|avc|infarto|choking|engasg|drown|afog|hypotherm|insola|dehydrat|first aid|primeiros socorros|emergenc|ambulance|snake|cobra|scorpion|escorpi|jellyfish|tick|carrapato|health|saude|infection|virus|cancer|toxic|overdose|suicid|crisis|depress|anxiety|water safe/contaminated|agua potavel|boil.
Result: 18 of 192 conversations match; 11 later-user-turns in 11 multi-turn convs (7 are single-turn). "Standalone form" = the conversation's first user turn alone; "follow-up form" = each later user turn with earlier user turns as history. Baseline = first turn gets a health route (3 of 11). Lost = 2.

| id | first-turn (standalone) codes | follow-up codes | follow-up text |
|---|---|---|---|
| v1-037 | `condition:beesting` (health route) | `condition:beesting:from-history task:lookup` | "what if her face starts swelling?" |
| v2-037 | `condition:co` (health route) | `condition:co task:chat` | "my whole family has a headache and the heater is on, what now..." |

Counted losses: v1-037 and v2-037. Kept: cs-040 (`grounding:health-follow-up`, hypothermia card from history). Not counted because the first turn is itself an informational "what is X" question with no health route (so there is no standalone route to lose), but the follow-up is a health ask and also has no route: cs-030, v1-031 ("e se picar uma criança, o que eu faço?" after "o que é escorpião amarelo?", `condition:scorpion:from-history`, health=false), v1-038 (altitude), v2-039 (heatstroke, "mi amigo está confundido y no suda..."). Hand-flagged (non-deterministic, my reading): of the 8 follow-up turns that are health asks (cs-030, cs-040, v1-031, v1-037, v1-038, v2-031, v2-037, v2-039), 2 keep a health route (cs-040, v2-031, the latter only because the turn itself is lexically health) and 6 lose it (75%). The other 3 follow-ups (cs-036 vaccines/mRNA, v1-030, v1-035) are not health asks.

### Set B (synthetic pairs, 111 dev probes -> 222 follow-up forms)
Probes (single-turn, dev only): emergency-dev (Compass dev.jsonl; emergency=1 or howto=1, label = one of the 29 card keys, 1 turn) + bench v0.1 public health/danger items `vit-hlt-001/002/003, dng-001/002/005` + water-safety dev probes (expect pos, `water-safety.probes.jsonl`; heldout file not used). Condition names per card key are fixed in `LAB` in the tool. Templates (fixed before the run): turn 1 "Tell me about <condition>." then "How do I prevent it?" (prevent) or "What should I do if I get it?" (act). PT/ES: "Me fale sobre ..." / "Como posso prevenir isso?" / "O que devo fazer se eu tiver isso?"; "Háblame de ..." / "¿Cómo puedo prevenirlo?" / "¿Qué debo hacer si me pasa?" (my own translation, same two intents; PT/ES are an extension beyond the EN-only wording of the criterion). Standalone form = the probe text itself (lexical route only; see deviations). Baseline = standalone gets a health route: 100 of 222 forms (58 EN, 26 PT, 16 ES).

| form | lang | baseline | lost |
|---|---|---|---|
| prevent | EN / PT / ES | 29 / 13 / 8 | 29 / 13 / 8 (100%) |
| act | EN / PT / ES | 29 / 13 / 8 | 4 / 13 / 2 |

Totals: prevent 50/50 lost, act 19/50 lost (`out/summary.json`). The act forms that keep the route are exactly those where turn 1 is itself health and the follow-up words are all in `FOLLOW_UP_WORDS` (EN "What should I do if I get it?" passes; PT "tiver" does not).

Losses (69 forms; every item with its standalone and follow-up codes is in `out/losses.tsv`). Pattern is uniform: the standalone has `health:lexical ui:safety-note retrieve:canonical-health-terms` (plus `condition:<card>` / `answer:first-aid-card-snakebite` / `grounding:health-card-condition` where it names one), and the follow-up has only `task:research|lookup|chat`, with or without `condition:<card>:from-history`.

| group | lost forms | follow-up codes | example ids |
|---|---|---|---|
| EN, condition recovered from history, no health route | 17 | `condition:<card>:from-history task:research/lookup` | ed-en-007/008/016/018/037/065/071/077/094/100, vit-hlt-001/002, dng-001 (snakebite card lost), dng-002 |
| EN, nothing recovered | 16 | `task:research/lookup` | dng-005, ws-001/005/006/015/021, ed-en-088/097 |
| PT, condition from history | 16 | `condition:<card>:from-history task:research/lookup` | ed-pt-008/020/036/065/066/079/083 |
| PT, nothing recovered | 10 | `task:research/lookup` | ed-pt-042/074/093/094/100 (+ MULTI) |
| ES, condition from history | 8 | `condition:<card>:from-history task:chat` | ed-es-002/012/018/030/045/057/084 |
| ES, nothing recovered | 2 | `task:chat` | ed-es-004 |

## Deviations
1. **Learned emergency detector stubbed** (`learned = null`, the answer.ts path "without the detector"). It was not run on the Mac mini (mmBERT head needs the RN/llama.rn build). The detector takes `(query, userTurns)` and `learned.fire` alone sets the health flag, so it may rescue some follow-ups; and it would turn many standalone probes (75% of the emergency-dev positives name no condition, so the lexical standalone misses them: only 50 of 111 probes have a lexical standalone route) into baseline health routes. UNKNOWN: the detector's own recall on the 2-turn forms. The reported loss is the lexical fallback (device without the detector files / canary fail).
2. The route is replicated from exported leaf functions, not by running `createAnswerer` (it needs the RN engine); retrieval, gate pass and generation are out. `task:` codes are the rule classifier's.
3. Set A "standalone" is the first user turn (the dev slices have no standalone rewrite of a follow-up), so the deterministic baseline there is n = 3.
4. PT/ES template translation and the per-condition labels (`LAB`) are fixed in the tool; EN-only result is 33/58 (57%).
5. Set B follow-up forms with a non-health turn 1 are included when the standalone probe routes health (turn 1 "Tell me about <condition>." is itself health-lexical for 150 of 222 forms).

## Decision for the coordinator
Rule (>= 10% lost) met by a wide margin. A fix arm is justified; it would act in `isHealthFollowUp` (history-aware health flag: drop the closed-vocabulary and FOLLOW_INTENT gates when the previous user turn is a health turn, plus the prevention intent), reuse `conversationCondition` for cards, and feed `retrieve:canonical-health-terms` from the history. Safety note: for non-emergency prevention questions the target is the health route (extractive/health-grounded answer, no unsupported advice such as sunscreen or rosemary oil), not the first-aid card.
