FAIL: 0 DROPPED, 4 WEAKENED (rules 1-2, 3, 4, 9). L0 bar "no instruction dropped" is not met. One revision is allowed by the stop rule.

Reviewed: prompt-diff.md, PROMPTDIET-criterion.md, and the relevant hunks of promptdiet-on-cut3.vs-0cfd4a77.patch (personalities.ts, rag/pure.ts, routing/context.ts). The patch text matches the diff table. Wording-only changes were accepted. Token counts below are approximate.

| # | Rule | Verdict | What changed / lost |
|---|---|---|---|
| 1 | "concise" (persona tone) | WEAKENED | The word and "short, direct" are gone, as is "Keep it short" in the reminder. Only the numeric bound "2-3 sentences" remains, which gives length but not the concision/directness instruction. The reminder sits in the user turn only. |
| 2 | "or a brief paragraph" | WEAKENED | Old allowed 2-3 sentences OR a brief paragraph. New allows only 2-3 sentences. This is stricter, not equal: the paragraph option for answers that need slightly more is lost, and so is "direct". The change is deliberate (the diff note says so), but it is a meaning change. |
| 3 | Bullets only for genuine lists | WEAKENED | "No lists unless asked" is not the old rule. Lost: (a) the permission to use bullets when the content is genuinely a list of distinct items, even if not asked. New text forbids that. (b) The warning against the "takeaway sentence + 3 bullets" shape. The diff's own note calls this the weakest edit. |
| 3b | Reminder "Keep it short" | KEPT | Redundant with "2-3 sentences" (see rule 1 for the concision caveat). |
| 3c | "(Response style:" to "(Style:" | KEPT | Label only. |
| 4a | "Use the context below when relevant" | WEAKENED | Dropped. Nothing now tells the model to use the context or to use it only when relevant. "Cite sources by number" and "If they don't cover it" only imply it. A risk is citing or leaning on irrelevant passages. |
| 4b | Cite "a source you used" | WEAKENED | Now "Cite sources", which loses the "only those you actually used" qualifier. |
| 4c | Citation format "[1] or [2]" to "[1]" | WEAKENED | The format is the same, "[n]". The "[1] or [2]" example showed that multiple sources can each be cited. The single example is slightly weaker for multi-source answers. Minor. Tests were updated to match "like [1]". |
| 5 | Uncovered question: say so, use general knowledge | KEPT | "they" = the sources named in the previous sentence. |
| 6 | No device actions, text only | KEPT | The examples shrank from 4 to 2 and "any other device or system" was folded into "devices". The rule is intact. |
| 7 | No false action claims | KEPT | "never claim you did" is attached to the device rule's action verbs, so it covers the same failure. The verb list is gone. |
| 8 | Identity: BOAR is the app, never the animal | KEPT | The animal rule is kept. "AI research", "on this phone" and "never describe yourself as one" are dropped, but none carries a rule. |
| 9 | Small talk: conversational, brief, "not as a command or task" | WEAKENED | "not as a command or task" is gone. It was the guard against treating a greeting as a task. The device rule only partly covers it. Low severity. |
| 10 | NO_SOURCE_INSTRUCTION | KEPT | All four parts are present: no source covers it; the app already tells the reader (the cd1478a gate); don't mention sources or the library; answer completely, and if unsure of a detail say which (the s32 gate). "in the offline library" and "specific" and "one" were dropped, and "the library" is still named in the don't-mention clause. |
| L | Language (PT strings) | KEPT | Untouched. |
| S | Safety (HEALTH_GROUNDING, device rule) | KEPT | HEALTH_GROUNDING untouched. |
| U | Uncited preface | KEPT | Post-generation text, untouched. |

## Minimal restoring wording (cost relative to the current new prompt)

| Rule | Replacement | Approx. cost |
|---|---|---|
| 1 and 2 (concise, brief paragraph) | styleReminder: "Short and direct: 2-3 sentences or a brief paragraph." (replaces "2-3 sentences.") | +9 tokens |
| 3 (bullets) | styleReminder: "Bullets only for genuine lists of distinct items." (replaces "No lists unless asked.") | +6 tokens, net of what it replaces |
| 4a, 4b, 4c (use context, cite used sources, [1] or [2]) | CONTEXT_INSTRUCTION: "Use the sources when relevant; cite those you used, like [1] or [2]." (replaces "Cite sources by number, like [1].") | +10 tokens |
| 9 (small talk) | "Answer greetings and small talk conversationally, briefly, not as a task." | +4 tokens |

Total to restore everything: about +29 tokens, which is about 1 s of time-to-first-text at 25 tok/s. The diet is claimed to save about 150 or more tokens (old fixed text is about 225 tokens, new about 75-80), so the L0 saving target of at least 150 would still be reachable, but this should be re-measured with the 4B tokenizer after the revision. The tightest case is the 150-token threshold.

Caveat: rules 2 and 3 are partly intentional behavior changes (stricter length and lists), not just loss. If the coordinator wants to keep them as such, the L0 text must be amended to call them out, and L1 must be the test. Under the frozen L0 as written, they are WEAKENED.
