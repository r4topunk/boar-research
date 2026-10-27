# FOLLOWUP r2: article-anchored neighbour fetch, STOPPED at the 0-call reach gate (2026-10-16; 0 generation, 0 judge, 0 paid; public sets; MacBook replay)

TL;DR: **G3 FAIL: gold chunk in kept context on 6/20 turn-2s with ON (OFF 1), gate needed >= 7.** Identity holds (G0, G1, G2, G4 pass). No pair loses a kept chunk. Gold article kept 2 -> 9/20, t1 fact chunk kept 0 -> 3. Per the frozen rule: no generation, no Haiku.

Criterion `FOLLOWUP-R2-criterion.md` frozen sha e76f0d46d7d623191c7654ce00801bf088f439c6a418cd414dccf333e6aa6bbc (through END FROZEN; r1 = a97b22d3). Patch `tools/followup-r2.patch` (vs r1 tree) sha256 505e1e3c89b71ef8280fb738c0a39720800f0fca1278bf788ca92040d334b54c; adapter `tools/followup-r2-adapter.eval.patch` e3c5e302…; tree kiln-local/be-cut7-followup. Data: `aggregates/gate0-r2.json`, `runs/replay-r2/`.

## Mechanism (deps.followupAnchor, off by default)
Fires on a lexical follow-up (<= 8 words, pronoun/ellipsis) whose previous assistant turn carries `sources`. Anchor = first <= 2 distinct shown titles, resolved strictly (label prefix -> that pack source; else enwiki title). Every chunk of the anchored article(s) is scored with the pack passage score against the BARE follow-up (no t1 terms); the best 2 with score > 0 not already retrieved are appended, pinned in compressContext and exempt from the off-topic/health grounding drops. Codes `followup:anchor:<n>`, `followup:anchor-kept`.

## Gates
| gate | result |
|---|---|
| G0 infra (0 missing, repeat identity) | PASS |
| G1 OFF = wt/pr1 (raw, kept, promptSha), 80/80 | PASS |
| G2 turn-1 + v0.1 ON = OFF 80/80, anchor fires 0/80 | PASS |
| **G3 gold chunk kept ON >= 7** | **FAIL 6 (OFF 1; raw top-6 1 -> 1)** |
| G4 no loss / no displacement | PASS (lost 0, displaced 0) |
Fired 17/20, anchor chunk kept 13/20, empty kept 5 -> 2. Gained: fu-03, 08, 12, 14, 19. fu-01 kept in both. Ceiling was 7 reachable (+ fu-01 = 8); ON hit 5 of the 7 (gate needed 6).

## Per pair (gold chunk OFF/ON | article OFF/ON | fired | fetched | added; gate0-r2.json has all fields)
gained (chunk 0 -> 1): fu-03 eth (art 0/1, fetched 6, +2), fu-08 health (4, +2), fu-12 firstaid (13, +2), fu-14 medline (4, +1), fu-19 simplewiki (11, +2). Already kept both: fu-01 travel (fetched 318, +2).
misses (chunk 0/0): fu-02 (art 0/0, 42, +1), 04 (0/0, 6, +0), 05 (not fired), 06 (art 0/1, 3, +2), 07 (0/0, 6, +2), 09 (0/0, 25, +2), 10 (not fired), 11 (not fired), 13 (0/0, 66, +2), 15 (art 0/1, 5, +1), 16 (art 1/1, 247, +2), 17 (0/0, 77, +0), 18 (0/0, 10, +0), 20 (0/0, 8, +0).

## The 14 misses
- Anchor did not fire (3: fu-05, 10, 11): the turn-1 OFF kept nothing or nothing resolvable, so no history `sources` to anchor on.
- Fired, nothing appended or kept (4: fu-04, 17, 18, 20): the shown title resolved to chunks already retrieved, none scoring > 0, or the title did not resolve (factbook rows show "Wikivoyage: <country>", the kit article, not the factbook one).
- Anchored the wrong article (4: fu-02, 07, 09, 13): the previous answer's shown source was not the article holding the follow-up's answer (gold article not kept; e.g. fu-02 anchored "Wikivoyage: London/Wimbledon", fu-09 a Wikivoyage page). Chunk scoring cannot fix this.
- Right article, wrong chunk (3: fu-06, 15, 16): fu-15 kept Dry Mouth chunk 950, gold is the adjacent 951; fu-06 kept 76874 (gold 76876); fu-16 article kept via Wikivoyage Austria/Danube but not the factbook chunk. Only fu-06 and fu-15 were within the strict ceiling; these two are the chunk-scoring failures.

## Reading
The mechanism does what r1's expansion could not: where the previous answer's article resolves, it lands the neighbour chunk (5/7 reachable, 0 losses, 0 turn-1/v0.1 side effects, no t1 terms). The miss budget is mostly upstream: 13 of 20 pairs were never reachable because turn 1 did not show the gold article, so a tighter rule (cited article only, top-2 -> top-3 chunks) is bounded by the same 7/20 ceiling and would at best convert fu-06/fu-15, i.e. tuning on 20 agent-written pairs after seeing the misses. Recommendation: close the strict-anchor line at r2 as a reach-limited near-miss (5/7 of what is reachable, gate was 6/7); do not run r3 on these pairs. Reopen only with real multi-turn traces carrying shown sources (the app maintainer's 140-question traces, or the app passing source titles in history turns), where the anchor fire rate and ceiling can be measured first at 0 calls.

UNKNOWN: whether the real route gate sends every turn-2 to search (replay forces search); whether real chat history will carry the shown titles; the judged effect of the 5 gained pairs (never generated).
