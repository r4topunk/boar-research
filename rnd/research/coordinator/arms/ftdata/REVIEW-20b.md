# REVIEW-20b: faithfulness review of review-sample-20b.md

- Reviewer: independent Opus (claude-opus-5-5), strict frozen rubric (borderline = UNSUPPORTED).
- Source: `review-sample-20b.md` only. No other files, no web, no world knowledge.
- Date: 2026-10-07. Pure connectives not counted; a misplaced causal "therefore" counts as a causal-link claim.

## Per-example grades

| id | claims | sup | unsup | contra | discl | answers q | outside fill | note (≤12 words) |
|---|---|---|---|---|---|---|---|---|
| ft1k-0110 | 17 | 16 | 1 | 0 | 0 | y | n | Complete; "only the second" is an added exclusivity inference |
| ft1k-0134 | 10 | 8 | 2 | 0 | 0 | y | n | Broken fragment "in international finance from NYU..." mid-paragraph |
| ft1k-0153 | 12 | 11 | 1 | 0 | 0 | y | n | Bridge sentence missing; misplaced "therefore"; dangling "It can decrease" |
| ft1k-0247 | 17 | 17 | 0 | 0 | 0 | y | n | Clean, complete |
| ft1k-0301 | 14 | 14 | 0 | 0 | 0 | partial | n | Omits all-time head-to-head record (Sydney 34, West Coast 22) |
| ft1k-0358 | 20 | 20 | 0 | 0 | 0 | y | n | Clean, complete |
| ft1k-0362 | 15 | 14 | 1 | 0 | 0 | y | n | "later named" timing not given; meta "The passages describe" |
| ft1k-0387 | 14 | 14 | 0 | 0 | 0 | y | n | Clean, complete |
| ft1k-0424 | 12 | 12 | 0 | 0 | 0 | y | n | Clean, complete |
| ft1k-0501 | 14 | 13 | 1 | 0 | 0 | partial | n | 2011 LA-move sentence missing; "That same year" dangles to college |
| ft1k-0506 | 13 | 10 | 3 | 0 | 0 | y | y | Three framing additions; "rather than feeding by mouth" is outside gloss |
| ft1k-0520 | 13 | 11 | 2 | 0 | 0 | partial | n | Omits Fortress of Solitude imprisonment; never names Superman II |
| ft1k-0522 | 11 | 10 | 1 | 0 | 0 | partial | n | "Why" unanswered: Port Sudan preference omitted; Sudan Memory omitted |
| ft1k-0564 | 12 | 11 | 1 | 0 | 0 | partial | n | Omits pool elevation (~1,000 m); "run by" not stated |
| ft1k-0591 | 13 | 13 | 0 | 0 | 0 | partial | n | "How it came to be port" uncovered, no disclaimer |
| ft1k-0798 | 11 | 10 | 1 | 0 | 0 | y | n | Extends "beyond scope" to Pocket/Rocket Pool/VIPnode |
| ft1k-0834 | 13 | 13 | 0 | 0 | 0 | partial | n | Omits {locale} URI substitution rule (MUST replace) |
| ft1k-0894 | 7 | 7 | 0 | 0 | 0 | partial | n | Omits go-bag for foot/public transport (no-car case) |
| ft1k-0922 | 10 | 10 | 0 | 0 | 0 | y | n | Clean, complete |
| ft1k-0998 | 13 | 12 | 1 | 0 | 0 | partial | n | Omits "same person for each family member"; abrupt jump |

## Totals

- Claims 261; supported 246; unsupported 15; contradicted 0 (unsupported+contradicted rate 5.7 %).
- Examples with >= 1 unsupported-or-contradicted claim: **11/20** (0110, 0134, 0153, 0362, 0501, 0506, 0520, 0522, 0564, 0798, 0998).
- Of those, examples with >= 1 non-borderline unsupported claim: **2/20** (0153, 0501); other 9 are borderline-only.
- Outside-knowledge fill: 1/20 (0506).
- Disclaimer phrases: 0/20 (0362 has a meta "The passages describe", not a disclaimer).
- Answers that do not read as a direct answer: 1/20 (0522, the "why" is missing).
- Coherence breaks from deleted text (fragment / dangling referent): 3/20 (0134, 0153, 0501).
- Answers omitting a question part the passages cover: 8/20 (0301, 0501, 0520, 0522, 0564, 0834, 0894, 0998).
- Answers question: y 11, partial 9, n 0.

## Unsupported or contradicted claims (verbatim)

| id | claim (verbatim) | class | reason (≤15 words) |
|---|---|---|---|
| 0110 | "Schumann's setting applies only to the second" | U, borderline | Passage says Schumann set the second; never says he did not set the first |
| 0134 | "George served in that partnership as chief consultant and managing director" | U, borderline | Passage: "where" (at CSFB); "in that partnership" is an added placement |
| 0134 | "After the sale, George stayed involved with the business, serving as vice-chairman" | U, borderline | "Stayed involved" and post-sale timing are framing; "its" referent ambiguous in passage |
| 0153 | "Models used in such studies therefore need to compensate for population structure" | U, clear | "Therefore" now follows the robustness claim; passage ties it to homogeneity violation |
| 0362 | "The asteroid was later named after Camilla" | U, borderline | "Later" is a timing not given in passages |
| 0501 | "That same year she was a semi-finalist in the ABC/Disney writer's program" | U, clear | Anchors to college period; passage puts it in 2011 after LA move |
| 0506 | "Surgery has limits, however, because the lack of musculature cannot be repaired" | U, borderline | Passage says current therapies cannot repair; "surgery has limits" is added framing |
| 0506 | "patients depend on enteral nutrition rather than feeding by mouth" | U, borderline | "Rather than feeding by mouth" is an outside gloss on enteral nutrition |
| 0506 | "Management in all cases therefore relies on several elements" | U, borderline | Causal "therefore" from survival figures to management is not stated |
| 0520 | "after the three took part in a failed coup against Krypton's government" | U, borderline | Passage says imprisoned following a failed coup; participation not stated |
| 0520 | "turning that Kryptonian weakness against them" | U, borderline | Interpretive characterisation; passage only says he depowers them with red sunlight |
| 0522 | "highlights such as Khorshid Effendi's House, the Hanafi Mosque and the Shafai Mosque remain" | U, borderline | Passage lists them as highlights; survival/standing state not stated |
| 0564 | "is run by Chef Florian Zumkeller" | U, borderline | Passage says the chef "serves" cuisine; running the restaurant is not stated |
| 0798 | "The EIP treats these extra-protocol methods as beyond its scope" | U, borderline | Scope exclusion is stated for state channels/tokens, not Pocket, Rocket Pool, VIPnode |
| 0998 | "phone lines open for emergency workers who need them" | U, borderline | "Who need them" is an added qualifier |

## Verdict

Bar "<= 2/20 examples with >= 1 unsupported-or-contradicted claim": **NOT MET (11/20)**. Excluding borderline-only items: **2/20 (0153, 0501)**, which meets the bar at its limit; both clear cases come from deleted bridge sentences.
