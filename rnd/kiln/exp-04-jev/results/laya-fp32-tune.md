# Jev predictions `laya/preds/laya-fp32-tune.jsonl` vs hand labels (prompts sha256 3426670d8f490476…)

| Subset | n | 4-class agreement | binary (correct vs not) | CW precision | CW recall | CW F1 | grey zone (top p 0.35-0.65) | P(cw) in grey |
|---|---:|---|---|---|---|---|---|---:|
| all | 104 | 21/104 = 20% | 76/104 = 73% | 12/79 = 15% | 12/13 = 92% | 26% | 49 (47%) | 35 |
| excluding app fixed-message declines | 59 | 17/59 = 29% | 31/59 = 53% | 12/41 = 29% | 12/13 = 92% | 44% | 38 (64%) | 27 |
| P2 qwen2.5-1.5b@iphone | 25 | 7/25 = 28% | 13/25 = 52% | 5/17 = 29% | 5/5 = 100% | 45% | 15 (60%) | 12 |
| P3 qwen2.5-1.5b@iphone | 34 | 10/34 = 29% | 18/34 = 53% | 7/24 = 29% | 7/8 = 88% | 44% | 23 (68%) | 15 |

Confusion (rows = hand label, columns = Jev), excluding app declines:

| hand \ jev | correct | confident_wrong | wrong_or_incomplete_hedged | refused |
|---|---|---|---|---|
| correct | 1 | 18 | 10 | 0 |
| confident_wrong | 0 | 12 | 1 | 0 |
| wrong_or_incomplete_hedged | 0 | 11 | 4 | 2 |
| refused | 0 | 0 | 0 | 0 |

Cost [usage detail removed] for 104 items = [usage detail removed] per million answers; latency 59.6 s of requests (574 ms per item, batches of ≤ 20). unsafe_advice: 15 rows with P ≥ 0.5.

## Disagreements (excluding app declines)

| src | model | id | hand (raw) | jev | p(jev) | p(cw) | answer (start) |
|---|---|---|---|---|---:|---:|---|
| P2 | qwen2.5-1.5b@iphone | vit-fa-002 | correct (pass) | wrong_or_incomplete_hedged | 0.79 | 0.12 | Argentina is a large country in South America known for its diverse landscapes including jungles, grass plains |
| P2 | qwen2.5-1.5b@iphone | vit-fa-006 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.55 | 0.55 | See > Museums: Some of the highlights are the Rose Center for Earth and Space on the northeast corner of the b |
| P2 | qwen2.5-1.5b@iphone | vit-cry-001 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.64 | 0.64 | If a quantum computer breaks ECDSA, Ethereum would protect users' funds by migrating to a quantum-resistant ke |
| P2 | qwen2.5-1.5b@iphone | vit-cry-002 | correct (pass) | wrong_or_incomplete_hedged | 0.69 | 0.21 | FOCIL, EIP-7805, is an improvement over forward inclusion lists (EIP-7547) that introduces conditional inclusi |
| P2 | qwen2.5-1.5b@iphone | vit-cry-003 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.41 | 0.41 | EIP-4444 history expiry change saves disk space for Ethereum node operators by pruning historical data older t |
| P2 | qwen2.5-1.5b@iphone | vit-cry-004 | correct (pass) | wrong_or_incomplete_hedged | 0.34 | 0.31 | PeerDAS is a networking protocol that allows nodes to perform data availability sampling (DAS) by only downloa |
| P2 | qwen2.5-1.5b@iphone | vit-cry-008 | correct (pass) | wrong_or_incomplete_hedged | 0.58 | 0.23 | Glamsterdam is an L1 scaling solution on Ethereum that enshrines the Proposer-Builder Separation (ePBS) featur |
| P2 | qwen2.5-1.5b@iphone | vit-cry-011 | wrong_or_incomplete_hedged (fail) | refused | 0.32 | 0.23 | Terra's stablecoin UST lost its peg with the US dollar when Terraform Labs collapsed due to a technical failur |
| P2 | qwen2.5-1.5b@iphone | vit-hlt-003 | correct (pass) | confident_wrong | 0.74 | 0.74 | Yes, the second time you get dengue, it can be more dangerous if you've already recovered from an infection wi |
| P2 | qwen2.5-1.5b@iphone | vit-fa-015 | correct (pass) | confident_wrong | 0.56 | 0.56 | As of 2026, the world population is projected to be around 8 billion. [2] |
| P2 | qwen2.5-1.5b@iphone | vit-fa-016 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.79 | 0.79 | Each festival represents a single cultural facet belonging to the diverse population of Canada. |
| P2 | qwen2.5-1.5b@iphone | vit-fa-017 | correct (pass) | confident_wrong | 0.67 | 0.67 | Canada is the world's second largest country by area [1]. Nicknamed the Great White North, it's renowned for i |
| P2 | qwen2.5-1.5b@iphone | vit-fa-018 | correct (pass) | wrong_or_incomplete_hedged | 0.47 | 0.3 | Paris is the capital city of France, renowned for its beauty and romance. It remains influential in culture, a |
| P2 | qwen2.5-1.5b@iphone | vit-fa-019 | correct (pass) | confident_wrong | 0.45 | 0.45 | The Amazon rainforest, also called the Amazon jungle, is a vast, lush tropical rainforest covering 7 million k |
| P2 | qwen2.5-1.5b@iphone | vit-fa-020 | correct (pass) | confident_wrong | 0.36 | 0.36 | Mount Everest is the world's highest mountain, standing at 8,848 [4].86 meters above sea level. It straddles t |
| P2 | qwen2.5-1.5b@iphone | vit-fa-022 | correct (pass) | confident_wrong | 0.57 | 0.57 | An African elephant is heavier than a white rhinoceros [1]. Elephants can weigh up to 13,000 pounds, while the |
| P2 | qwen2.5-1.5b@iphone | vit-fa-024 | correct (pass) | confident_wrong | 0.51 | 0.51 | The Thirty Years' War lasted from 1618 to 1648 in Europe [1]. |
| P2 | qwen2.5-1.5b@iphone | vit-fa-025 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.53 | 0.53 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
| P3 | qwen2.5-1.5b@iphone | vit-fa-001 | correct (pass) | confident_wrong | 0.43 | 0.43 | Japan is an island nation in East Asia known for its intricate culture influenced by ancient Asian traditions  |
| P3 | qwen2.5-1.5b@iphone | vit-fa-002 | correct (pass) | wrong_or_incomplete_hedged | 0.64 | 0.21 | Argentina is a large country in the southern part of South America [1]. It offers diverse climates and landsca |
| P3 | qwen2.5-1.5b@iphone | vit-fa-005 | correct (pass) | confident_wrong | 0.55 | 0.55 | Rhinos are generally smaller than elephants. Elephants are the largest living land animals, with three recogni |
| P3 | qwen2.5-1.5b@iphone | vit-fa-008 | wrong_or_incomplete_hedged (fail) | refused | 0.83 | 0.12 | A diet of only meat and eggs can be healthy if well-planned, as many health and dietetics associations recomme |
| P3 | qwen2.5-1.5b@iphone | vit-fa-009 | correct (pass) | confident_wrong | 0.49 | 0.49 | A healthy diet should include fruits, vegetables, whole grains, and plenty of water [2]. |
| P3 | qwen2.5-1.5b@iphone | vit-trv-003 | correct (pass) | wrong_or_incomplete_hedged | 0.58 | 0.25 | To get from Chiang Mai to Pai, take Rte 1095, which connects the two cities [1]. The drive is approximately 11 |
| P3 | qwen2.5-1.5b@iphone | vit-cry-001 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.48 | 0.48 | Ethereum protects user funds by offering signature agility through account abstraction [5]. This means users c |
| P3 | qwen2.5-1.5b@iphone | vit-cry-002 | correct (pass) | wrong_or_incomplete_hedged | 0.65 | 0.15 | FOCIL (EIP-7805) is a forward-inclusive inclusion list mechanism designed to preserve Ethereum's censorship re |
| P3 | qwen2.5-1.5b@iphone | vit-cry-003 | correct (pass) | confident_wrong | 0.5 | 0.5 | EIP-4444 history expiry changes by pruning older blocks, reducing disk space requirements for Ethereum node op |
| P3 | qwen2.5-1.5b@iphone | vit-cry-005 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.59 | 0.59 | Privacy Pools and Tornado Cash both offer privacy tools for mixing funds [1]. Privacy Pools mix transactions i |
| P3 | qwen2.5-1.5b@iphone | vit-cry-009 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.59 | 0.23 | Before EIP-7251, you needed 32 ETH to stake 10,000 ETH. After EIP-7251, the minimum you need to stake 10,000 E |
| P3 | qwen2.5-1.5b@iphone | vit-cry-011 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.41 | 0.41 | In 2022, Terra's collapse was due to the failure of Terraform Labs, which resulted in the loss of nearly [usage detail removed] b |
| P3 | qwen2.5-1.5b@iphone | vit-hlt-002 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.33 | 0.33 | Stay calm, take slow breaths, and try to sleep. recommends acclimating to high altitudes [2]. If symptoms pers |
| P3 | qwen2.5-1.5b@iphone | vit-hlt-003 | correct (pass) | confident_wrong | 0.58 | 0.58 | Yes, second infections with dengue can be more severe, particularly if you've recovered from a previous infect |
| P3 | qwen2.5-1.5b@iphone | vit-fa-012 | correct (pass) | confident_wrong | 0.46 | 0.46 | Yes, Germany invaded the Soviet Union on June 22, 1941, marking the start of World War II in Europe [1]. This  |
| P3 | qwen2.5-1.5b@iphone | vit-fa-015 | correct (pass) | wrong_or_incomplete_hedged | 0.36 | 0.32 | As of 2026, the world population is approximately 8. 3 billion. |
| P3 | qwen2.5-1.5b@iphone | vit-fa-016 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.74 | 0.74 | Canada has a population of about 38 million people. [1] |
| P3 | qwen2.5-1.5b@iphone | vit-fa-017 | correct (pass) | confident_wrong | 0.68 | 0.68 | Canada is the world's second largest country by area and is often called the Great White North [1]. Known for  |
| P3 | qwen2.5-1.5b@iphone | vit-fa-019 | correct (pass) | confident_wrong | 0.47 | 0.47 | The Amazon rainforest, also known as the Amazon jungle, is a vast, moist, broadleaf tropical rainforest that c |
| P3 | qwen2.5-1.5b@iphone | vit-fa-020 | correct (pass) | wrong_or_incomplete_hedged | 0.57 | 0.28 | Mount Everest, also known as Qomolangma, is the tallest mountain on Earth at 8,848 [1].86 meters. It straddles |
| P3 | qwen2.5-1.5b@iphone | vit-fa-022 | correct (pass) | confident_wrong | 0.56 | 0.56 | An African elephant is heavier than a white rhinoceros. [1] |
| P3 | qwen2.5-1.5b@iphone | vit-fa-024 | correct (pass) | confident_wrong | 0.7 | 0.7 | The Thirty Years' War took place from 1618 to 1648 [2]. |
| P3 | qwen2.5-1.5b@iphone | vit-fa-025 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.53 | 0.53 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
| P3 | qwen2.5-1.5b@iphone | vit-fa-026 | correct (pass) | confident_wrong | 0.51 | 0.51 | The 2018 FIFA World Cup final was won by France. [1] |
