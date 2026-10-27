# P3-NLI-0 ceiling check (hand-read by Compass after the frozen run; v0.1 dev items only)
Question: can ANY checker that compares answer sentences against the passages in the prompt flag the 7 positives?

| run | item | target sentence (short) | passage in the prompt says | contradicted by a passage? | contradicted by another sentence of the answer? |
|---|---|---|---|---|---|
| s42 | vit-trv-003 | Chiang Mai–Pai route "well-maintained… steep near Pai" | groceries; "Go next: Pai — tourist town"; city intro | no (silent) | no |
| s42 | vit-cry-002 | FOCIL "ensures validators include specific blocks… prevents malicious fork choices" | "this section outlines the roles…"; EIP-8369 is informational | no (silent) | no |
| s43 | vit-cry-002 | same two sentences | same | no (silent) | no |
| s42 | lan-cmp-003 | "No country is bigger than India by area" | "many Indian states are bigger than most countries" | no | **yes**: the next sentence says India is 7th after Russia, Canada… |
| s43 | lan-cmp-003 | same | same | no | **yes** |
| s43 | vit-hum-005 | "invisible hand… appears only once in Wealth of Nations, Book I ch. II" | Kirkcaldy: Smith's birthplace, "invisible hand" of markets | no (silent) | no |
| s43 | lan-exp-002 | "part of the Federal Republic of Yugoslavia"; "currency is the Euro, not yet fully adopted" | independence 2006; Kingdom of Yugoslavia 1929 | no (silent) | no |

- Passage-contradiction ceiling: **0/7**. Self-contradiction ceiling: **2/7**. Bar: ≥ 4/7.
- All 7 wrong sentences are **memory claims the passages don't address**. "Unsupported by the passages" would catch them, but correct answers carry correct memory facts the passages also don't state (Singapore "9 August 1965", P-2 post-mortem). So "unsupported" can't separate the 7 from the 20.
- Conclusion: on this set, "used-but-wrong" isn't a grounding error, it's a **memory error next to irrelevant passages**. Anvil's 4B got 4/7 from its own knowledge or self-consistency, not from the passages.
