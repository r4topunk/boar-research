# CHATFAIL: multi-turn intent failures in the reference engine (proposed 2026-10-18 by r4to, from a live chat on boar-ios)

TL;DR: a 6-turn chat ("what can a smart contract do?" → "what does it look like?" → "I want to see the code" → "can you write it?") ends with the model refusing to write code twice in a row and repeating the definition. The cause is four engine rules, not only the model. All four live in the Kotlin reference (`android-native/engine`) and in the TS engine (`src/`). boar-ios is a straight port of that engine, so this belongs to R&D and not to an app fix. Status: **proposed, not frozen**. The loop freezes a criterion before any run (Ruleset 30).

## Trace (iPhone 13, boar-ios, tone Succinct, "Fast · on this iPhone", 2026-10-18 00:29)

| # | User | UI | Answer (short) |
|---|---|---|---|
| 1 | What can a smart contract do? | Searched 1 source · 9 s | definition (Smart contract article), fine |
| 2 | what it look like? | Searched 1 source · 8 s | **same definition again** |
| 3 | but how it look like? the program | Answered · 7 s | abstract "looks like a digital program…" |
| 4 | i want to see the code | Answered · 7 s | "you would need access to the blockchain platform… such as Ethereum or Solidity" |
| 5 | can you write it? | Answered · 5 s | **"Sure, but I can't write the code here"** |
| 6 | not even an example? | Answered · 5 s | **"Sorry, but I can't write the code for you"** |

Screenshots: r4to's chat 2026-10-18 (not stored). The expected answer from turn 2 on: a ~10-line Solidity example plus one sentence. A 4B writes that easily without a source.

## Mechanism per turn (reference file:line, Kotlin; TS and Swift identical)

| Turn | Rule that fired | Where |
|---|---|---|
| 2 | `whStart` + ≤ 12 words → `lookup`; "it" → FollowUp `direct` = previous + current → same article → same answer | `routing/Classify.kt` (lookup), `answer/FollowUp.kt:102` |
| 3, 4, 6 | `previousQuestion` takes only the **last** user turn; from turn 3 on that turn has no subject ("what it look like?"), so the topic anchor is lost and 0 sources come back | `answer/FollowUp.kt:80-86` |
| 4, 5 | the code intent regex only matches "write (a\|some) code"; "write it", "see the code", "an example" fall to `chat`/`lookup` (with retrieval and the Succinct 2–3 sentence cap) | `routing/Classify.kt:39`, TS `src/routing/classify.ts:18` |
| 5, 6 | `GROUNDING_INSTRUCTION` ("no ability… You can only respond with text… Never claim to have done something…") is read by the small model as "I can't write code". Succinct's "2–3 sentences, no lists" adds to it | `rag/RagPure.kt:171`, TS `src/rag/pure.ts:438` |
| 6 | the refusals at 4 and 5 go back in as "Recent conversation", so the next refusal is self-consistent (refusal snowball) | `RagPure.assemblePrompt` history block |

## Candidate levers (each one small, each one an arm)

- **L1 prompt (cheapest, same lane as HONESTPROMPT):** append to GROUNDING: "You can write text, code and examples: writing is not a physical action." Add an exception to the Succinct styleReminder: "…unless the user asks for code or an example."
- **L2 intent:** broaden `code` to cover write/show/see + it/the code/an example/a program, and "what does it look like" after a technical turn. Code goes without retrieval, without the 2–3 sentence cap, with a code block.
- **L3 anchor:** the follow-up anchor = the latest user turn that names a subject or found sources, not the immediately previous one.
- **L4 history:** drop assistant turns flagged as refusals from the history block (the decline detector exists: boar-ios `DeepResearch.swift:204`, port of the Kotlin one).
- **L5 UX (app, report only):** when a follow-up finds the same source as the turn before and the answer repeats it, "Searched 1 source" is misleading. Note for the app maintainer, not an engine arm.

## Proposed steps (the loop sets the numbers when it freezes)

- **Step 0 (0 calls, mac-cpu):** write a public probe set CHAT-FU-v1, ~30 short multi-turn chats with follow-ups whose intent changes (code/example/"show me"/"what does it look like"/"write it"/"in a table"/"shorter") on topics the library covers. Replay `classify` + `FollowUp.plan` before and after L2+L3. Gate = how many turns get the right task type and the right anchor. Deterministic, seconds to run.
- **Step 1 (generation, 4B desktop with the app's prompt assembly, like HONESTPROMPT):** current vs L1 vs L1+L2+L3+L4 on CHAT-FU-v1. Primary metric: **refusal rate on capability requests** (decline detector + a hand check). Secondary: Haiku judge ratio on the same turns, plus non-regression on v0.1 57 and longsession-v1 (no gain expected there; it is the safety net).
- Model: also run the 1.5B/1.7B (iPhone 13 path), where the refusal is probably worse.

## Interaction with HONESTPROMPT (running)

The app maintainer's honest sentence ("If you don't know, say so in one sentence. A shorter correct answer beats a longer one.") pushes in the **same direction as the refusal** seen here. HONESTPROMPT does not measure capability-request refusals (its sets are Thorough longsession + v0.1). Before recommending the honest edit to the app maintainer, run CHAT-FU-v1 turns 4–6 on its arms D0/D1/S0/S1 (≈ 4 × 30 short generations, 0 judge: refusal counted by the detector).

## UNKNOWN
- Which model answered: the iPhone 13 path is the 1.5B per boar-ios AGENTS.md; the "Fast" label does not say.
- Whether the app maintainer's native Kotlin app (fullnative-dev) still has these exact strings after his 10-17 release fixes (fix/rc-oct17). Check `RagPure.kt`/`FollowUp.kt` on his branch before sending anything.
- Prior: no measured refusal rate on capability requests in any of our sets (v0.1/v0.2/V-para are single-turn questions), so the ceiling is unknown. That is also why step 0 is 0-call.
