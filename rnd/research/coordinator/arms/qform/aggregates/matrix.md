# QFORM matrix (replay/qform.replay.jsonl, 0 LLM)

hit@kept = gold chunk in the engine's final `sources` (a skipped/empty retrieval counts as a miss). raw = retrieve() result at the engine's k (3-4); wide = a separate retrieve(q, 12).

## Per form (n 48)

| form | hit@raw % | hit@wide12 % | hit@kept % | kept 95% CI (Wilson) | median gold rank (wide12) [n found] | mean top score | no retrieval |
|---|---|---|---|---|---|---|---|
| F0 base | 54 | 60 | 50 (24/48) | 36-64 | 1 [29] | 0.594 | 0 |
| F1 entity-free | 27 | 33 | 10 (5/48) | 5-22 | 1.0 [16] | 0.500 | 4 |
| F2 keywords | 65 | 69 | 62 (30/48) | 48-75 | 1 [33] | 0.521 | 0 |
| F3 situational | 31 | 33 | 25 (12/48) | 15-39 | 1.5 [16] | 1.676 | 9 |
| F4 typos | 44 | 46 | 42 (20/48) | 29-56 | 1.0 [22] | 0.575 | 8 |
| F5 yes/no true | 83 | 85 | 83 (40/48) | 70-91 | 1 [41] | 0.564 | 1 |
| F6 false premise | 65 | 71 | 50 (24/48) | 36-64 | 1.0 [34] | 0.564 | 1 |
| F7 comparison | 44 | 54 | 42 (20/48) | 29-56 | 1.0 [26] | 1.044 | 0 |
| F8 follow-up | 12 | 19 | 8 (4/48) | 3-20 | 3 [9] | 0.511 | 1 |

## Secondary reads per form (n 48)

| form | article@raw % | article@kept % (right article, any chunk) | hit@kept any of the self-test/authored facts % | kept lists empty |
|---|---|---|---|---|
| F0 base | 67 | 65 | 56 | 4 |
| F1 entity-free | 38 | 15 | 10 | 23 |
| F2 keywords | 79 | 73 | 65 | 2 |
| F3 situational | 52 | 44 | 25 | 19 |
| F4 typos | 56 | 52 | 46 | 13 |
| F5 yes/no true | 94 | 92 | 83 | 1 |
| F6 false premise | 77 | 62 | 54 | 10 |
| F7 comparison | 56 | 52 | 42 | 4 |
| F8 follow-up | 12 | 8 | 8 | 12 |

## hit@kept % by form x pack (n 8 each)

| form | factbook | firstaid-en | medlineplus-en | crypto | wikivoyage-en | visa-en |
|---|---|---|---|---|---|---|
| F0 base | 12 (1) | 12 (1) | 50 (4) | 75 (6) | 100 (8) | 50 (4) |
| F1 entity-free | 12 (1) | 12 (1) | 12 (1) | 12 (1) | 12 (1) | 0 (0) |
| F2 keywords | 50 (4) | 25 (2) | 62 (5) | 75 (6) | 88 (7) | 75 (6) |
| F3 situational | 25 (2) | 12 (1) | 25 (2) | 12 (1) | 38 (3) | 38 (3) |
| F4 typos | 0 (0) | 0 (0) | 38 (3) | 75 (6) | 50 (4) | 88 (7) |
| F5 yes/no true | 50 (4) | 75 (6) | 88 (7) | 88 (7) | 100 (8) | 100 (8) |
| F6 false premise | 25 (2) | 25 (2) | 38 (3) | 38 (3) | 75 (6) | 100 (8) |
| F7 comparison | 12 (1) | 12 (1) | 75 (6) | 50 (4) | 50 (4) | 50 (4) |
| F8 follow-up | 0 (0) | 0 (0) | 0 (0) | 25 (2) | 12 (1) | 12 (1) |

## Paired drop F0 - Fi (points; bootstrap 95% CI over the 48 facts, B 2000, seed 11)

| form | kept drop [CI] | raw drop [CI] | wide12 drop [CI] | hole (kept drop >= 20 and CI > 0) |
|---|---|---|---|---|
| F1 entity-free | +39.6 [+23, +54] | +27.1 [+10, +44] | +27.1 [+8, +44] | YES |
| F2 keywords | -12.5 [-27, +0] | -10.4 [-25, +4] | -8.3 [-23, +6] | no |
| F3 situational | +25.0 [+8, +42] | +22.9 [+6, +40] | +27.1 [+10, +44] | YES |
| F4 typos | +8.3 [-6, +23] | +10.4 [-4, +25] | +14.6 [+4, +27] | no |
| F5 yes/no true | -33.3 [-48, -19] | -29.2 [-44, -15] | -25.0 [-40, -10] | no |
| F6 false premise | +0.0 [-15, +15] | -10.4 [-25, +2] | -10.4 [-25, +2] | no |
| F7 comparison | +8.3 [-6, +23] | +10.4 [-4, +25] | +6.2 [-8, +21] | no |
| F8 follow-up | +41.7 [+27, +56] | +41.7 [+27, +56] | +41.7 [+27, +56] | YES |

## Paired kept drop F0 - Fi by pack (points; n 8, CIs wide)

| form | factbook | firstaid-en | medlineplus-en | crypto | wikivoyage-en | visa-en |
|---|---|---|---|---|---|---|
| F1 entity-free | +0 [-38,+38] | +0 [-38,+38] | +38 [+12,+75] | +62 [+12,+100] | +88 [+62,+100] | +50 [+12,+88] |
| F2 keywords | -38 [-75,-12] | -12 [-38,+0] | -12 [-50,+25] | +0 [-38,+38] | +12 [+0,+38] | -25 [-62,+0] |
| F3 situational | -12 [-38,+0] | +0 [-38,+38] | +25 [-25,+62] | +62 [+25,+100] | +62 [+25,+100] | +12 [-38,+62] |
| F4 typos | +12 [+0,+38] | +12 [+0,+38] | +12 [-38,+50] | +0 [+0,+0] | +50 [+12,+88] | -38 [-88,+12] |
| F5 yes/no true | -38 [-75,-12] | -62 [-88,-25] | -38 [-75,-12] | -12 [-50,+25] | +0 [+0,+0] | -50 [-88,-12] |
| F6 false premise | -12 [-38,+0] | -12 [-38,+0] | +12 [-25,+50] | +38 [-12,+88] | +25 [+0,+62] | -50 [-88,-12] |
| F7 comparison | +0 [-38,+38] | +0 [-38,+38] | -25 [-62,+0] | +25 [+0,+50] | +50 [+12,+88] | +0 [-38,+38] |
| F8 follow-up | +12 [+0,+38] | +12 [+0,+38] | +50 [+12,+88] | +50 [+12,+88] | +88 [+62,+100] | +38 [-12,+88] |

## Keep step vs raw (counts of 48 per form)

| form | gold in wide12 not in raw (cut by k) | gold in raw not kept (keep step drops it) | kept but not raw |
|---|---|---|---|
| F0 base | 3 | 2 | 0 |
| F1 entity-free | 3 | 8 | 0 |
| F2 keywords | 2 | 1 | 0 |
| F3 situational | 1 | 3 | 0 |
| F4 typos | 1 | 1 | 0 |
| F5 yes/no true | 1 | 0 | 0 |
| F6 false premise | 3 | 7 | 0 |
| F7 comparison | 5 | 1 | 0 |
| F8 follow-up | 3 | 2 | 0 |

## 10 example misses (F0 hit @kept, this form missed)

| id | form | question | engine search query | gold title | kept titles |
|---|---|---|---|---|---|
| qf-boar-wikivoyage-en-04-F1 | F1 | Which waterway did the cheese town dig in 1225 to link its river to the Rhine delta? | Which waterway did the cheese town dig in 1225 to link its river to the Rhine delta? | Gouda | (none) |
| qf-boar-crypto-07-F2 | F2 | ECPP history who invented | ECPP history who invented | Elliptic curve primality | (none) |
| qf-boar-firstaid-en-07-F3 | F3 | My apartment has no AC and it's 38 degrees and humid, I have two fans running, is that eno | My apartment has no AC and it's 38 degrees and humid, I have two fans running, is that eno | Get #SummerReady (Ready.gov) | (none) |
| qf-boar-wikivoyage-en-08-F4 | F4 | when is the rainy seson at lagunas de chacahua national park | when is the rainy seson at lagunas de chacahua national park | Lagunas de Chacahua National Park | Wikivoyage: Lagunas de Chacahua National; Wikivoyage: Lagunas de Chacahua National; Wikivoyage: Lagunas de Chacahua National |
| qf-boar-crypto-08-F5 | F5 | PKCS #10 is the most common format for certificate signing requests, right? | PKCS #10 is the most common format for certificate signing requests, right? | Certificate signing request | Certificate signing request; Certificate signing request; X.509 |
| qf-boar-crypto-07-F6 | F6 | Elliptic curve primality proving was proposed by Rivest and Shamir in 1978, right? | Elliptic curve primality proving was proposed by Rivest and Shamir in 1978, right? | Elliptic curve primality | (none) |
| qf-boar-firstaid-en-07-F7 | F7 | Do fans protect better in a dry heat wave than in humid heat? | Do fans protect better in a dry heat wave than in humid heat? | Get #SummerReady (Ready.gov) | Heat wave; Wikivoyage: Hot weather |
| qf-boar-crypto-04-F8 | F8 | and who beat it in the final round? | and who beat it in the final round? | BLAKE (hash function) | NIST hash function competition |
| qf-boar-wikivoyage-en-08-F1 | F1 | When does it pour in that Oaxaca lagoon reserve near Puerto Escondido? | When does it pour in that Oaxaca lagoon reserve near Puerto Escondido? | Lagunas de Chacahua National Park | Wikivoyage: Oaxaca (state); Wikivoyage: Puerto Escondido; Wikivoyage: Oaxaca (state) |
| qf-boar-medlineplus-en-04-F2 | F2 | low saliva causes | low saliva causes | Dry Mouth | (none) |

## Holes (pooled and per pack)

- F1: kept drop 40 points, CI [23, 54] (pooled)
- F1 / boar-medlineplus-en: kept drop 38 points, CI [12, 75] (pack)
- F1 / boar-crypto: kept drop 62 points, CI [12, 100] (pack)
- F1 / boar-wikivoyage-en: kept drop 88 points, CI [62, 100] (pack)
- F1 / boar-visa-en: kept drop 50 points, CI [12, 88] (pack)
- F3: kept drop 25 points, CI [8, 42] (pooled)
- F3 / boar-crypto: kept drop 62 points, CI [25, 100] (pack)
- F3 / boar-wikivoyage-en: kept drop 62 points, CI [25, 100] (pack)
- F4 / boar-wikivoyage-en: kept drop 50 points, CI [12, 88] (pack)
- F7 / boar-wikivoyage-en: kept drop 50 points, CI [12, 88] (pack)
- F8: kept drop 42 points, CI [27, 56] (pooled)
- F8 / boar-medlineplus-en: kept drop 50 points, CI [12, 88] (pack)
- F8 / boar-crypto: kept drop 50 points, CI [12, 88] (pack)
- F8 / boar-wikivoyage-en: kept drop 88 points, CI [62, 100] (pack)
