# INSTANT-SUBJ on cut 4 (engine engineer, 2026-10-05; L0 only, nothing on the mini, nothing pushed)

TL;DR: built exactly the frozen mechanism (criterion untouched). Unit tests **1297/1297** (cut 4: 1293, +4), tsc clean, patch applies to a fresh `git archive 0cfd4a77` (tsc clean, 1297/1297 there too). L0 stub replay: **0 tier changes, 0 correct instant answers lost** on v0.1 EN + V-exact and on 1,328 EN dev messages; 1 dev item only relabels its reason code (list -> subject). Lookup set #2 was never opened; the coordinator scores it with `tools/lookup2-score.py`.

## Patch
| file | sha256 | vitest | tsc |
|---|---|---|---|
| `instsubj-on-cut4.vs-0cfd4a77.patch` (cut 4 + INSTANT-SUBJ; branch `coord/instsubj`, commit 8db4927d on `coord/cut4` 84cd9c17; worktree `<workspace>/wt/instsubj`, never pushed) | `d51e844c6522cb1825e43d800626516af099ae462c85e39396f7e2a4ea04dfa3` | 1297/1297 | clean |

## Mechanism (`src/routing/context.ts`, `instantFinalBlock`; `answer.ts` unchanged)
New block reason `"subject"` (the caller turns it into `instant:not-final-subject` and falls through to the model), checked right after fragment/figurative.
- Judged question shapes only: `<wh> is/was/are/were [the] <slot> of [the] <E>` and `<wh> is <E>'s <slot>` (E at most 4 words, trailing "in/on/for..." phrases cut). Any other shape is not judged (never blocked by this rule).
- Snippet passes when E (or an alias) is the **possessor of the slot** (`<slot> ... of <E>` with no other "of" between; `<E>'s ... <slot>`; `<E> <slot>`, e.g. "the French capital") or the **subject** (E opens the sentence, optionally after "in/for/according to" and "the"). Otherwise blocked.
- Text is normalised (case, accents, "D.C."/"U.S." dots). Aliases: USA/US/United States (of America)/America/American, UK/United Kingdom/Britain/Great Britain/British, UAE, Netherlands/Holland/Dutch, Russia, South Korea, Czechia, Myanmar/Burma, Ivory Coast, France/French, Germany, Italy, Spain, China, Japan, India, Brazil, Mexico, Canada, Australia (+ adjectives), Ethereum/ETH, Bitcoin/BTC. An unlisted entity matches by its own name only; an unlisted demonym ("the Polish capital") would fall through to the model (cost, not error).
- Known limit: the check is lexical, not a parser. "Capital of Louisiana, USA" is blocked because the slot is "of Louisiana", but a sentence that names E as possessor and then answers about someone else could pass.

## Tests (4 added, `context.test.ts`)
- "capital of the usa" + "Baton Rouge is the capital of Louisiana, USA." -> `subject`; Sydney/New South Wales for Australia -> `subject`.
- Correct snippets stay final: "Washington, D.C. is the capital of the United States", "The capital of the United States of America is ...", "France's capital is Paris", Berlin/Germany, "Canada has a population of ...", an entity-free question.
- Aliases: UK vs "United Kingdom" and vs "Britain's capital"; Britain vs "UK"; Edinburgh/Scotland for UK -> `subject`.
- France/Lyon stays blocked (figurative, fragment, and "Lyon is the capital of the Auvergne-Rhone-Alpes region" -> `subject`).

## L0 (stub-LLM replay, real engine, kit A = crypto + Wikivoyage, no detector, no places; trees = cut 2 norv2 runner + `git archive` of src from `coord/cut4` and `coord/instsubj`; `tools/mkreq.py`, `replay.sh`, `cmp.py`)
| set | n | tier changes | correct instant lost | other |
|---|---|---|---|---|
| v0.1 EN public 60 + V-exact 11 + France warm-up (66 unique ids) | 72 requests | **0** | **0** (instants: 15 both arms, byte-identical text and codes) | 0 |
| France warm-up | 1 | fast in both (still `instant:not-final-fragment`) | - | - |
| Sonar EN dev messages (1,010 + 213 + 105, last user turn) | 1,328 | **0** (127 instant / 1,201 fast both arms) | 0 | 1: dev-0637 "what are the stages of sleep", fast in both; `instant:not-final-list` -> `instant:not-final-subject` (relabel, answer identical) |
So on these sets the rule never turns an instant into a model answer; its only evidence is the unit tests and the blind lookup set #2 (coordinator). Since no v0.1 answer changes, L1 reduces to adoption on L0 (criterion). `tools/mkreq.py` differs from cut 4's only in not reading any lookup set. Outputs in `l0/` (`*.traces.jsonl`, `A.cmp.txt`, `D.cmp.txt`).

## Scorer for lookup set #2: `tools/lookup2-score.py`
`python3 tools/lookup2-score.py <items.jsonl> cut4=<traces> instsubj=<traces>` (items: `{id, kind: lookup|control, question, expected}`; `|` separates alternatives). Per arm: instant-final count, WRONG instant-final count (with the items), CORRECT instant-final count, controls finishing instant; with 2+ arms also the correct instant answers lost/gained and wrong removed vs the first (baseline) arm. Exit 1 if the last arm has any wrong instant-final. Criterion check: wrong = 0 and lost <= 1. Tested on a fake file in the scratchpad only; the real set was not opened or run.

## UNKNOWN
- Real coverage on lookup set #2 (the wrong instants of other classes, e.g. wrong-attribute or wrong-slot answers where the entity is the subject, are not caught by this rule by design).
- Whether `cut4.l0` rows without a `<slot> of <E>` shape (e.g. "when was X founded") need the same treatment: out of the frozen scope, not built.
