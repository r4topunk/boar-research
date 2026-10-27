# C1-REASON (2026-10-21): why the 16 "fact is in a pack we own" items still miss, and the cheapest fix class for each (replay-only)

0 LLM, 0 judge, 0 paid. Install replays with qa-cooking-se 81990fa9, qa-money-se 37411234, boar-vitalik-blog-en 94a7ec6e added: **I1** = phone engine (bench-app/engine 0ca54d87, 6 A-union packs + the 3, gate rules); **K3X** = desktop RAG-FUNNEL LITEPACKS tree, K3 + the 3 (stub server, detector :8094). Labels from ROUTING-R1, RAG-FUNNEL, KEEP-K1, KEEP-E, ORACLE-REAL, FACT-REACH. Ids only (dev sets).

## TL;DR (the hypothesis's two kill clauses)
- **Build-side causes: 2 clear + 1 arguable of 16** (< 5): C1 does not reopen as a pack-rebuild arm.
- **Install puts the fact in kept context on 2/9 install-only items** (cooking-008, 012; I1 article level 2/9, K3X article 2/9, chunk 1/9) < 4 -> **clause fires: C1 CLOSES.** The install also crowds: K3X changes the kept set of 27/86 other MAIN items (11 v0.1), I1 30/83 plus 21/76 safety probes + saf items (hypothesis allowed <= 3).
- **Where the rest sit:** 4 routing (closed by ROUTING-R1 as unsafe or 0 U), 7 retrieval (cross-pack fusion crowding, one article filling k, grounding drops, paraphrase misses at own-pack rank >= 10; SE packs get no dense candidates on either path), 1 reading.
- **Realistic U_8GB ceiling, all 16 fixed: +0.042 (33 % use prior) / +0.002 (ORACLE-REAL rate)** vs +0.128 perfect. 13/16 are self-tests written from these packs, so the 33 % column is an upper bound.

## Per item (where the fact chunk sits now -> after install; cheapest fix class)
| id | owner pack | where it sits (K1/K3 today; ROUTING / KEEP / KEEP-E / ORACLE) | install replay (I1 phone / K3X desktop) | cheapest fix class |
|---|---|---|---|---|
| lan-rsn-001 | simplewiki | K3 S4, kept in slot [1] ("not visible from the Moon"); ORACLE 0.43 -> 0.43. **The length was lost at pack build**: the article reads "the wall stretches ." because the {{convert}} value was dropped | n/a (simplewiki is not in A-union) | **pack-build**: the converter must keep {{convert}} output |
| st-qa-cooking-se-002 | qa-cooking | ROUTING: places route ("oil at home"), blocked before retrieval | I1 kept (raw 1) / K3X places route, no retrieval | engine route rule P (safe, 0 U in ROUTING) + install |
| st-qa-cooking-se-003 | qa-cooking | S1, pack not installed | not in raw on either path; own-pack bm25 rank 27 ("baking paper" vs "parchment lid") | **pack-build**: alias/synonym, or dense for SE packs |
| st-qa-cooking-se-008 | qa-cooking | S1, not installed | **kept on both paths** (rank 0) | install only |
| st-qa-cooking-se-012 | qa-cooking | S1, not installed | article kept on both paths; K3X keeps sibling chunks 18094/18096, not the fact chunks 18095/18097 | install (chunk-level: keep or chunking, arguable build) |
| st-qa-cooking-se-013 | qa-cooking | ROUTING: detector-only health decline (p 1.00) | I1 kept (lexical detector) / K3X fact chunk at raw 3, then health-strict grounding drops it | engine route (H fails 32 probes) + install |
| st-qa-cooking-se-015 | qa-cooking | ROUTING: detector-only decline (p 0.26) | I1 raw has other chicken threads, 0 kept / K3X health-strict drop | engine route + retrieval + install |
| st-qa-money-se-004 | simplewiki (K1), qa-money | ROUTING: detector-only decline (p 0.95); H fixed it (1.0 -> 3.5) but H is unsafe | own-pack rank 24; health drop in K3X | engine route (unsafe) |
| st-qa-money-se-007 | qa-money | S1, not installed | no money chunk in the fused raw list on either path (Wikivoyage/simplewiki win); own rank 10 | engine retrieval: per-pack quota in fusion + install |
| st-qa-money-se-009 | qa-money | S1, not installed | own rank 137 (paraphrase) | engine retrieval: dense for SE packs + install |
| st-qa-money-se-010 | qa-money | S1, not installed | raw holds 4 other HSA threads; grounding keeps 0 money (I1, K3X); own rank 0 under plain bm25 | engine retrieval (query/grounding) + install |
| st-qa-money-se-011 | qa-money | S1, not installed | own rank 13 | engine retrieval: dense for SE + install |
| st-qa-money-se-020 | qa-money | S1, not installed | own rank 14 | engine retrieval: dense for SE + install |
| vit-cry-005 | vitalik ("Why I support privacy"); a one-line mention in crypto ERC-8262 | K3 S2: the 4 raw slots are all "Tornado Cash" chunks; ORACLE with the ERC-8262 line in slot 1: 0.27 -> 0.38 | unchanged on both paths: Tornado Cash ×4 kept; vitalik own rank 14 | engine retrieval: at most 1-2 chunks per article in raw + install |
| vit-cry-007 | vitalik | RAG-FUNNEL/KEEP "S3, dense rank 4" is a **lexical false positive** (gold chunk = a football player, label N) | vitalik own rank 0, but the fused list is "Wikivoyage: Accra" ×3 ("d/acc" -> "acc") | engine retrieval: fusion quota / slash-token + install |
| vit-hum-004 | simplewiki | K3 S4 CE: "Gríma kills Saruman" is in slot [1]; the motive is absent from simplewiki; ORACLE 0.20 -> 0.20 | n/a | none (reading + partial content) |
KEEP-E (empty lexical list) covers none of the 16. Its 3 S3 items are vit-hum-003, vit-sci-001 and money-012.

## Sums per fix class (U on MAIN 97, sref 451.17; per item: perfect = (sref - s_D2S)/451.17, prior = perfect x 0.33, ORACLE = 0.015 x sref/451.17)
| class | n | ids | perfect fix | realistic, 33 % use prior | realistic, ORACLE-REAL rate | shippable? |
|---|---|---|---|---|---|---|
| engine rule: retrieval (fusion quota, per-article cap, grounding, dense for SE) | 7 | money 007/009/010/011/020, cry-005, cry-007 | +0.050 | **+0.017** | +0.001 | 6/7 also need an install; KEEP-K1 shows keep-side rules move <= 3 items within +15 % tokens |
| engine rule: routing | 4 | cooking 002/013/015, money-004 | +0.041 | +0.013 | +0.001 | no: ROUTING-R1 measured +0.011 for H and it fails 32 probes; P is safe, 0 U |
| pack-build change | 2 (+1 arguable) | lan-rsn-001 ({{convert}}), cooking-003 (alias); cooking-012 chunking | +0.014 | +0.005 | +0.000 | post-freeze; lan-rsn-001 is a converter fix that touches every simplewiki article with {{convert}} |
| install only (catalog) | 2 | cooking-008, 012 | +0.014 | +0.005 | +0.000 | crowding cost: 27-30 other items + 21 probes change |
| none (reading) | 1 | vit-hum-004 | +0.008 | +0.003 | +0.000 | T1 reader line |
| all 16 | 16 | | +0.128 | **+0.042** | +0.002 | |

## Reading
- FACT-REACH's "content is there" does not become a lever: on the shipping engine, installing the owner packs reaches 2/9 install-only facts and churns a third of other contexts plus 21 safety probes; the rest are retrieval/routing rules ROUTING-R1 and KEEP-K1 already measured as small or unsafe.
- **Pack bug found:** the simplewiki converter drops {{convert}} values (lan-rsn-001 "stretches ."). Post-freeze pack-build item; its frequency across the pack is unmeasured.
- Untested post-freeze retrieval leads, each needing its own frozen criterion + crowding gate: cap raw chunks per article (cry-005), per-pack quota in fusion (money-007, cry-007), dense candidates for SE packs (money-009/011/020).

## Caveats
- I1 fact location is article level (titles); K3X chunk level (quote-holding chunks) and article level. Own-pack rank = plain FTS5 bm25 over OR(question tokens), not the engine's query builder (indicative). I1 uses the lexical detector, so routing items retrieve there (routing-fixed ceiling).
- U priors: FACTPRESENT 33 % use rate, ORACLE-REAL +0.015 (one seed, Haiku); baseline s/sref = LITEPACKS K1 judgments, DECLINE2STAGE "no" = 0. 13/16 are pack-written self-tests (true by construction). No blind/, rnd/veil, v0.4.

Files: aggregates/c1-install.json (I1), c1-desktop.json (K3X), c1-ownrank.json, c1-ceilings.json; tools/c1_install.py, c1_desktop.py, ownrank.py. Replay traces/prompts stay out of git (scratchpad).
