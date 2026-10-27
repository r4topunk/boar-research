# K-FULL funnel read (2026-10-22, 0 LLM): MAIN 92 keyed, replay of answer() up to generation, five kits

Stages: S1 fact in no installed pack (lexical pool rule; cm: oracle = the item's own source article) · S2 in a pack, not retrieved (raw + wide-12) · S3 retrieved, not kept · K kept (= funnel S4+S5; no generation). cm stage = best of oracle and lexical.

| kit | packs | MAIN 92 S1/S2/S3/K | v0.1 52 S1/S2/S3/K | cm 40 S1/S2/S3/K | v0.1 kept gained / lost vs K3 | mean kept | ms/q |
|---|---|---|---|---|---|---|---|
| K3 | 6 | 52/11/6/23 | 12/11/6/23 | 40/0/0/0 | +0 [] / -0 [] | 2.88 | 1816 |
| K3CM | 8 | 12/32/19/29 | 12/11/6/23 | 0/21/13/6 | +0 [] / -0 [] | 3.54 | 521 |
| K3W | 7 | 43/10/14/25 | 4/10/13/25 | 39/0/1/0 | +7 ['lan-cmp-004', 'lan-cmp-005', 'vit-cry-010', 'vit-hlt-003', 'vit-hum-001', 'vit-hum-005', 'vit-hum-006'] / -5 ['lan-exp-004', 'lan-exp-005', 'lan-rsn-006', 'vit-cry-006', 'vit-trv-003'] | 3.33 | 585 |
| KSE | 17 | 10/33/24/25 | 10/10/10/22 | 0/23/14/3 | +2 ['vit-cry-009', 'vit-hlt-003'] / -3 ['lan-exp-005', 'lan-hlt-003', 'vit-cry-006'] | 3.47 | 2312 |
| KFULL | 18 | 4/38/22/28 | 4/11/12/25 | 0/27/10/3 | +7 ['lan-cmp-004', 'lan-cmp-005', 'vit-cry-010', 'vit-hlt-003', 'vit-hum-001', 'vit-hum-005', 'vit-hum-006'] / -5 ['lan-exp-004', 'lan-exp-005', 'lan-rsn-006', 'vit-cry-006', 'vit-trv-003'] | 3.63 | 2541 |

Kept-slot share by pack (top 5):
- K3: boar-simplewiki-en 69%, boar-crypto 11%, boar-firstaid-en 9%, boar-wikivoyage-en 8%, boar-factbook 2%
- K3CM: boar-simplewiki-en 54%, qa-money-se 14%, qa-cooking-se 10%, boar-crypto 9%, boar-firstaid-en 7%
- K3W: boar-wiki-en-top100k 55%, boar-simplewiki-en 29%, boar-crypto 8%, boar-firstaid-en 6%, boar-wikivoyage-en 2%
- KSE: boar-simplewiki-en 38%, qa-money-se 9%, qa-ethereum-se 9%, qa-travel-se 8%, qa-cooking-se 7%
- KFULL: boar-wiki-en-top100k 47%, boar-simplewiki-en 17%, qa-bitcoin-se 5%, qa-travel-se 5%, qa-cooking-se 5%

Per item (v0.1 + cm): stage per kit

| id | set | funnel K1 / K3 | K3 | K3CM | K3W | KSE | KFULL | KFULL kept packs |
|---|---|---|---|---|---|---|---|---|
| vit-hum-001 | v0.1 | S1 / S1 | S1 | S1 | K | S1 | K | boar-simplewiki-en, boar-wiki-en-top100k |
| lan-exp-001 | v0.1 | S4 / S4 | K | K | K | K | K | boar-simplewiki-en, boar-wikivoyage-en, qa-ethereum-se |
| lan-ref-001 | v0.1 | S2 / S2 | S2 | S2 | S2 | S2 | S2 |  |
| vit-cry-001 | v0.1 | S3 / S3 | S3 | S3 | S3 | S2 | S2 | qa-bitcoin-se, qa-ethereum-se |
| vit-cry-007 | v0.1 | S3 / S3 | S3 | S3 | S3 | S3 | S3 | boar-simplewiki-en |
| vit-sci-002 | v0.1 | S1 / S1 | S1 | S1 | S2 | S1 | S2 | boar-simplewiki-en, boar-wiki-en-top100k |
| lan-ref-003 | v0.1 | S4 / S4 | K | K | K | K | K | boar-wiki-en-top100k |
| lan-exp-004 | v0.1 | S5 / S5 | K | K | S3 | K | S3 | boar-wiki-en-top100k |
| lan-rsn-006 | v0.1 | S5 / S5 | K | K | S3 | K | S3 | boar-wiki-en-top100k |
| st-qa-cooking-se-003 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S3 | boar-wiki-en-top100k, qa-cooking-se |
| st-qa-cooking-se-009 | cm | S1 / S1 | S1 | K | S1 | K | K | boar-simplewiki-en, boar-wiki-en-top100k, qa-cooking-se |
| st-qa-cooking-se-015 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 |  |
| st-qa-money-se-001 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-simplewiki-en, boar-wiki-en-top100k, qa-travel-se |
| st-qa-money-se-007 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-wiki-en-top100k, qa-travel-se |
| st-qa-money-se-013 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S2 | boar-simplewiki-en, boar-wiki-en-top100k |
| st-qa-money-se-019 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-wiki-en-top100k |
| vit-hum-002 | v0.1 | S3 / S3 | S1 | S1 | S3 | S3 | S3 | boar-simplewiki-en |
| lan-exp-002 | v0.1 | S4 / S5 | K | K | K | K | K | boar-simplewiki-en, boar-wiki-en-top100k |
| lan-hlt-001 | v0.1 | S4 / S4 | K | K | K | K | K | boar-simplewiki-en, boar-wiki-en-top100k, qa-health-se |
| vit-cry-002 | v0.1 | S4 / S4 | K | K | K | K | K | boar-crypto, qa-bitcoin-se, qa-ethereum-se, qa-travel-se |
| vit-cry-008 | v0.1 | S4 / S4 | K | K | K | K | K | boar-crypto, boar-simplewiki-en, qa-travel-se |
| vit-sci-003 | v0.1 | S1 / S1 | S1 | S1 | S1 | S1 | S1 |  |
| lan-rsn-003 | v0.1 | S4 / S4 | K | K | K | K | K | boar-simplewiki-en, boar-wiki-en-top100k, qa-travel-se |
| lan-exp-005 | v0.1 | S4 / S5 | K | K | S3 | S3 | S3 | boar-wiki-en-top100k |
| lan-rsn-007 | v0.1 | S2 / S2 | S2 | S2 | S2 | S2 | S2 |  |
| st-qa-cooking-se-004 | cm | S1 / S1 | S1 | K | S1 | K | K | boar-firstaid-en, qa-cooking-se |
| st-qa-cooking-se-010 | cm | S1 / S1 | S1 | S3 | S1 | S2 | S2 | boar-wiki-en-top100k |
| st-qa-cooking-se-016 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-simplewiki-en, boar-wiki-en-top100k |
| st-qa-money-se-002 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-simplewiki-en, qa-travel-se |
| st-qa-money-se-008 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S2 | boar-wiki-en-top100k |
| st-qa-money-se-014 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | qa-bitcoin-se |
| st-qa-money-se-020 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-simplewiki-en, boar-wiki-en-top100k |
| vit-hum-003 | v0.1 | S3 / S3 | S1 | S1 | S1 | S1 | S1 |  |
| lan-rsn-001 | v0.1 | S4 / S4 | K | K | K | K | K | boar-simplewiki-en, boar-wiki-en-top100k, qa-cooking-se |
| lan-hlt-002 | v0.1 | S3 / S5 | K | K | K | K | K | boar-medlineplus-en, boar-wiki-en-top100k |
| vit-cry-003 | v0.1 | S4 / S4 | K | K | K | K | K | boar-crypto, boar-vitalik-blog-en, qa-ethereum-se |
| vit-cry-009 | v0.1 | S2 / S3 | S2 | S2 | S2 | K | S3 | boar-crypto, boar-wiki-en-top100k |
| vit-hlt-001 | v0.1 | S3 / S3 | S3 | S3 | S3 | S3 | S3 |  |
| lan-cmp-003 | v0.1 | S3 / S3 | S2 | S2 | S2 | S2 | S2 | boar-simplewiki-en, qa-bitcoin-se |
| lan-exp-006 | v0.1 | S2 / S2 | S2 | S2 | S2 | S2 | S2 |  |
| lan-ref-005 | v0.1 | S2 / S2 | S2 | S2 | S2 | S2 | S2 |  |
| st-qa-cooking-se-005 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S3 |  |
| st-qa-cooking-se-011 | cm | S1 / S1 | S1 | S3 | S1 | S2 | S2 | boar-firstaid-en, boar-simplewiki-en, qa-outdoors-se |
| st-qa-cooking-se-017 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S3 |  |
| st-qa-money-se-003 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-wiki-en-top100k, qa-money-se |
| st-qa-money-se-009 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-wiki-en-top100k, qa-ethereum-se |
| st-qa-money-se-015 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | qa-travel-se |
| vit-hum-004 | v0.1 | S4 / S4 | K | K | K | K | K | boar-simplewiki-en, boar-wiki-en-top100k |
| lan-cmp-001 | v0.1 | S2 / S2 | S2 | S2 | S2 | S2 | S2 |  |
| lan-hlt-003 | v0.1 | S5 / S5 | K | K | K | S3 | K | boar-firstaid-en, boar-simplewiki-en, boar-wiki-en-top100k, qa-health-se |
| vit-cry-004 | v0.1 | S4 / S4 | K | K | K | K | K | boar-crypto, boar-simplewiki-en, qa-bitcoin-se |
| vit-cry-010 | v0.1 | S3 / S3 | S3 | S3 | K | S3 | K | boar-simplewiki-en, boar-wiki-en-top100k, qa-bitcoin-se, qa-ethereum-se |
| vit-hlt-002 | v0.1 | S3 / S3 | S3 | S3 | S3 | S3 | S3 |  |
| lan-rsn-004 | v0.1 | S4 / S4 | K | K | K | K | K | boar-simplewiki-en |
| lan-cmp-004 | v0.1 | S3 / S3 | S1 | S1 | K | S1 | K | boar-simplewiki-en, boar-wiki-en-top100k |
| lan-exp-007 | v0.1 | S4 / S4 | K | K | K | K | K | boar-simplewiki-en, boar-wiki-en-top100k |
| st-qa-cooking-se-006 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | qa-cooking-se, qa-outdoors-se |
| st-qa-cooking-se-012 | cm | S1 / S1 | S1 | K | S1 | S3 | S3 | boar-wiki-en-top100k |
| st-qa-cooking-se-018 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S2 |  |
| st-qa-money-se-004 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 |  |
| st-qa-money-se-010 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S3 | qa-travel-se |
| st-qa-money-se-016 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S3 | qa-bitcoin-se, qa-money-se, qa-travel-se |
| vit-hum-005 | v0.1 | S3 / S3 | S1 | S1 | K | S1 | K | boar-simplewiki-en, boar-wiki-en-top100k |
| lan-cmp-002 | v0.1 | S3 / S3 | S2 | S2 | S3 | S2 | S3 | boar-wiki-en-top100k |
| vit-trv-003 | v0.1 | S4 / S4 | K | K | S3 | K | S3 | boar-wiki-en-top100k, boar-wikivoyage-en |
| vit-cry-005 | v0.1 | S2 / S2 | S1 | S1 | S1 | S1 | S1 | boar-crypto, qa-ethereum-se |
| vit-cry-011 | v0.1 | S4 / S4 | K | K | K | K | K | boar-crypto, boar-wiki-en-top100k, qa-bitcoin-se |
| vit-hlt-003 | v0.1 | S3 / S3 | S2 | S2 | K | K | K | boar-wiki-en-top100k, qa-health-se |
| lan-ref-004 | v0.1 | S1 / S2 | S2 | S2 | S2 | S2 | S2 |  |
| lan-cmp-005 | v0.1 | S3 / S3 | S3 | S3 | K | S3 | K | boar-simplewiki-en, boar-wiki-en-top100k |
| st-qa-cooking-se-001 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-firstaid-en, boar-simplewiki-en, qa-health-se |
| st-qa-cooking-se-007 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | qa-money-se |
| st-qa-cooking-se-013 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S3 |  |
| st-qa-cooking-se-019 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S2 | boar-wiki-en-top100k |
| st-qa-money-se-005 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-wiki-en-top100k |
| st-qa-money-se-011 | cm | S1 / S1 | S1 | K | S1 | S3 | S3 | boar-wiki-en-top100k, qa-ethereum-se |
| st-qa-money-se-017 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-simplewiki-en, boar-wiki-en-top100k, qa-travel-se |
| vit-hum-006 | v0.1 | S1 / S1 | S1 | S1 | K | S1 | K | boar-simplewiki-en, boar-wiki-en-top100k |
| lan-rsn-002 | v0.1 | S2 / S2 | S1 | S1 | S1 | S1 | S1 |  |
| vit-trv-004 | v0.1 | S1 / S1 | S2 | S2 | S2 | S2 | S2 |  |
| vit-cry-006 | v0.1 | S4 / S4 | K | K | S3 | S3 | S2 | boar-wiki-en-top100k, qa-bitcoin-se |
| vit-sci-001 | v0.1 | S3 / S3 | S1 | S1 | S3 | S3 | S3 | boar-wiki-en-top100k |
| lan-ref-002 | v0.1 | S5 / S5 | K | K | K | K | K | boar-simplewiki-en, boar-wiki-en-top100k, boar-wikivoyage-en |
| lan-exp-003 | v0.1 | S5 / S5 | K | K | K | K | K | boar-wiki-en-top100k |
| lan-rsn-005 | v0.1 | S3 / S3 | S1 | S1 | S3 | S1 | S3 | boar-wiki-en-top100k |
| st-qa-cooking-se-002 | cm | S1 / S1 | S1 | K | S1 | S3 | S3 | boar-firstaid-en |
| st-qa-cooking-se-008 | cm | S1 / S1 | S1 | K | S1 | K | K | boar-wiki-en-top100k, qa-cooking-se, qa-health-se |
| st-qa-cooking-se-014 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | qa-cooking-se, qa-outdoors-se |
| st-qa-cooking-se-020 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | boar-simplewiki-en, boar-wiki-en-top100k |
| st-qa-money-se-006 | cm | S1 / S1 | S1 | S3 | S1 | S3 | S2 | boar-simplewiki-en, boar-wiki-en-top100k, qa-travel-se |
| st-qa-money-se-012 | cm | S3 / S3 | S1 | S2 | S3 | S2 | S3 | boar-wiki-en-top100k |
| st-qa-money-se-018 | cm | S1 / S1 | S1 | S2 | S1 | S2 | S2 | qa-money-se, qa-travel-se |
