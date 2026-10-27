# G2-FULLKIT reads (0 LLM; criterion sha dcac6f4b)

## Read 1: MAIN 97, K1 tree, settings {packHeadPass a2, packDense2 extra}

| kit | recovery /25 | losses /22 | kept lists changed | mean kept | ctx tok | wall ms/q (mean) |
|---|---|---|---|---|---|---|
| v2 kit (crypto, wikivoyage, simplewiki wave2; no chunk_vecs) | 0 [] | 5 ['lan-exp-005', 'lan-hlt-003', 'lan-ref-002', 'lan-rsn-006', 'vit-trv-003'] | 58 | 1.74 | 230 | 225 |
| v3 kit (crypto, wikivoyage, simplewiki v3proto) | 3 ['vit-hum-003', 'vit-cry-010', 'vit-sci-001'] | 0 [] | 70 | 2.45 | 353 | 346 |

Frozen rule (recovery >= 5/25 and losses <= 2/22): **FAIL** (recovery 3, losses 0). Reference: simplewiki v3 alone 4/0.

## Read 2: QFORM 432, six separate A-union packs (hit@kept)

| arm | hit@kept | hit@raw | hit@wide12 | junk-kept (x v2off) | mean kept | ctx tok | kept tok | kept lists changed vs v2off |
|---|---|---|---|---|---|---|---|---|
| v2 six, settings off | 117 (27.1 %) | 147 | 180 | 1.45 (1.00) | 1.59 | 288 | 169 | 0 |
| v2 six, K1 settings (a2 + append-budget) | 125 (28.9 %) | 147 | 180 | 2.06 (1.42) | 2.27 | 288 | 307 | 165 |
| v3 six, a2 + extra | 211 (48.8 %) | 265 | 180 | 3.49 (2.41) | 3.38 | 372 | 457 | 344 |

Junk set = 252 items whose gold is not in the v2off wide-12.

**v3extra-v2off pooled: +21.8 pts [item CI +18.1, +25.7] [fact-cluster CI +16.4, +27.8], gained/lost 94/0**

| form | F0 base | F1 entity-free | F2 keywords | F3 situational | F4 typos | F5 yes/no true | F6 false premise | F7 comparison | F8 follow-up |
|---|---|---|---|---|---|---|---|---|---|
| v2off -> v3extra (of 48) | 17->30 (+27) | 6->9 (+6) | 16->33 (+35) | 6->17 (+23) | 15->25 (+21) | 30->41 (+23) | 15->29 (+29) | 10->24 (+29) | 2->3 (+2) |

| pack (of 72) | factbook | firstaid-en | medlineplus-en | crypto | wikivoyage-en | visa-en |
|---|---|---|---|---|---|---|
| v2off -> v3extra | 9->22 (+18.1) | 6->20 (+19.4) | 15->30 (+20.8) | 31->39 (+11.1) | 41->51 (+13.9) | 15->49 (+47.2) |

**v3extra-v2k1 pooled: +19.9 pts [item CI +16.2, +23.8] [fact-cluster CI +14.4, +26.4], gained/lost 86/0**

| form | F0 base | F1 entity-free | F2 keywords | F3 situational | F4 typos | F5 yes/no true | F6 false premise | F7 comparison | F8 follow-up |
|---|---|---|---|---|---|---|---|---|---|
| v2k1 -> v3extra (of 48) | 20->30 (+21) | 7->9 (+4) | 16->33 (+35) | 6->17 (+23) | 16->25 (+19) | 31->41 (+21) | 17->29 (+25) | 10->24 (+29) | 2->3 (+2) |

| pack (of 72) | factbook | firstaid-en | medlineplus-en | crypto | wikivoyage-en | visa-en |
|---|---|---|---|---|---|---|
| v2k1 -> v3extra | 12->22 (+13.9) | 8->20 (+16.7) | 18->30 (+16.7) | 31->39 (+11.1) | 41->51 (+13.9) | 15->49 (+47.2) |

**v2k1-v2off pooled: +1.9 pts [item CI +0.7, +3.2] [fact-cluster CI +0.5, +3.9], gained/lost 8/0**

| form | F0 base | F1 entity-free | F2 keywords | F3 situational | F4 typos | F5 yes/no true | F6 false premise | F7 comparison | F8 follow-up |
|---|---|---|---|---|---|---|---|---|---|
| v2off -> v2k1 (of 48) | 17->20 (+6) | 6->7 (+2) | 16->16 (+0) | 6->6 (+0) | 15->16 (+2) | 30->31 (+2) | 15->17 (+4) | 10->10 (+0) | 2->2 (+0) |

| pack (of 72) | factbook | firstaid-en | medlineplus-en | crypto | wikivoyage-en | visa-en |
|---|---|---|---|---|---|---|
| v2off -> v2k1 | 9->12 (+4.2) | 6->8 (+2.8) | 15->18 (+4.2) | 31->31 (+0.0) | 41->41 (+0.0) | 15->15 (+0.0) |

## Read 3: costs

| pack | v2 bytes | v3 bytes | delta |
|---|---|---|---|
| boar-factbook | 11,624,448 | 11,829,248 | +1.8 % |
| boar-firstaid-en | 20,987,904 | 26,329,088 | +25.4 % |
| boar-medlineplus-en | 4,268,032 | 4,530,176 | +6.1 % |
| boar-crypto | 36,093,952 | 55,255,040 | +53.1 % |
| boar-wikivoyage-en | 351,092,736 | 575,864,832 | +64.0 % |
| boar-visa-en | 11,231,232 | 11,657,216 | +3.8 % |
| boar-simplewiki-en | 480,534,528 | 735,510,528 | +53.1 % |
| all 7 | 915,832,832 | 1,420,976,128 | +55.2 % |

Wall per query (replay answer() up to the stubbed generation, minus the wide-12 list; MacBook, desktop proxy, one run each, other load on the machine):

| set | v2 mean / p50 ms | v3 mean / p50 ms |
|---|---|---|
| MAIN 97 (K1 kit, a2+extra) | 225 / 237 | 346 / 364 |
| QFORM 432 v2 off vs v3 extra | 226 / 214 | 261 / 258 |
| QFORM 432 v2 K1 vs v3 extra | 211 / 212 | 261 / 258 |
