# CLOSING TESTS (r4to, 2026-10-23 11:5x): "chegamos onde precisávamos; agora garantir que o app entrega isso, com a experiência dele"

TL;DR: research lines close with the two arms in flight; from here every test is an acceptance test of the app maintainer's native app against what we measured. The claim number comes from the ruler run on the final RC, nothing else.

## Decisões (fixas)
1. Research closed: packs/search (SEFIX-124 adopted for delivery + W78 stack as the reading-cost answer), answer styles (Succinct for ≤ 2 GB models; Detailed, 1/3/5 paragraphs and Deep Research all worse on the 1.7B), detector (v3b stays; retrains and cheap vetoes rejected), decoder/readers/gates (closed NO). No new research arms after PLUGBATCH-SELF and STYLE-SEFIX.
2. The product = the app maintainer's native app. What it must carry (all measured, all in notes 1-8 waiting for r4to's send OK): Succinct default for small models; Deep Research hidden or relabelled for small models; personal files above Vital + a guard on the keyword bypass; the warning line; the honest "passages found don't support" wording instead of "Not found" when sources were kept; CO card EN + PT/ES; facts table r11; calculator regex; seed cue widened; Research Topics in Succinct with 6 swaps; optional: search fixes (gidf + F1/F2/F4) and the pack-format change for the reading cost.
3. Stop: PIN2 (HOLD), FMT1-SCAN / KEEP-PIN / W78b (NO), further W78 variants, detector retrains, PACK-BUILD for new domains (only if the app maintainer or r4to asks), LITE-FOCUS as a broad row (superseded by this plan).

## Últimos testes de pesquisa (em voo, fecham hoje)
- PLUGBATCH-SELF: the 110 adversarial rows on our 1.7B, base vs engfix vs SEFIX-124 (route/value 0-LLM, Haiku ≤ 150).
- STYLE-SEFIX: Succinct vs Detailed with the search advances on, delivered vs not (Haiku ≤ 400).

## Testes de experiência (r4to 12:0x: no phone; the desktop twin of the app with the adopted stack SEFIX-124)
The closing question: in each app mode, does the answer come right when the knowledge pack holds the content, and what does the user get when it does not?

| # | test | design | pass / what we learn |
|---|---|---|---|
| U1 | UXMATRIX (main) | modes Succinct / Detailed / Deep Research × pack state (the relevant pack installed / not installed), same questions; items = 40 cooking/money (the pack holds the answer by construction) + 30 keyed general items (fact in a pack vs in no pack); outcome per answer labelled by Haiku, blinded: CORRECT-WITH-SOURCE, CORRECT-FROM-MEMORY, HONEST-UNKNOWN, WRONG-CONFIDENT, WRONG-WARNED, REFUSED-WRONGLY; plus UX surface: banner / warning / sources shown / time | the matrix mode × pack-state × outcome shares; the recommendation per mode; "what happens when the pack has nothing" quantified (honest vs invented) |
| U2 | STYLE-SEFIX (in flight) | Succinct vs Detailed with the search fixes, delivered vs not | whether Detailed uses a delivered fact better |
| U3 | PLUGBATCH-SELF (in flight) | 110 adversarial rows, 3 engine arms | routes/values per app function, PT/ES |
| U4 | TOPICS27 family (done) | 27 topics with the Vital pack, Succinct vs Detailed, misses, deep mode | which suggested topics work per mode |
| U5 | Follow-up with packs | 18 pairs + LONGSESSION referents on the desktop twin with SEFIX-124: does the found source survive the next turn in OUR engine with the pack on (his rule keeps 17/18) | the multi-turn experience with packs |
| U6 | Warning / banner surface | from U1's traces: how often the user sees "Not found", the warning line, 0 sources, with the pack on vs off | the honesty surface per mode |

Phone and ruler: the app maintainer's side later (ruler v0.4 on the final RC = the claim number); not part of this closing.

## UNKNOWN
- Whether the app maintainer accepts each default change (notes 1-8 not sent; r4to's call).
- When RC2 lands and whether the Pixel is free for the acceptance days.
- The pack-format change (two tables, +11 pct) is optional; without it the search fixes still work, at the old reading cost.
