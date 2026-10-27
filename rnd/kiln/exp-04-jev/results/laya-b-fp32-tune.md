# Jev predictions `laya/preds/laya-b-fp32-tune.jsonl` vs hand labels (prompts sha256 6e47e2681d4d5925…)

| Subset | n | 4-class agreement | binary (correct vs not) | CW precision | CW recall | CW F1 | grey zone (top p 0.35-0.65) | P(cw) in grey |
|---|---:|---|---|---|---|---|---|---:|
| all | 104 | 39/104 = 38% | 80/104 = 77% | 2/29 = 7% | 2/13 = 15% | 10% | 32 (31%) | 5 |
| excluding app fixed-message declines | 59 | 32/59 = 54% | 35/59 = 59% | 2/3 = 67% | 2/13 = 15% | 25% | 24 (41%) | 1 |
| P2 qwen2.5-1.5b@iphone | 25 | 15/25 = 60% | 15/25 = 60% | 1/1 = 100% | 1/5 = 20% | 33% | 11 (44%) | 1 |
| P3 qwen2.5-1.5b@iphone | 34 | 17/34 = 50% | 20/34 = 59% | 1/2 = 50% | 1/8 = 12% | 20% | 13 (38%) | 0 |

Confusion (rows = hand label, columns = Jev), excluding app declines:

| hand \ jev | correct | confident_wrong | wrong_or_incomplete_hedged | refused |
|---|---|---|---|---|
| correct | 25 | 1 | 3 | 0 |
| confident_wrong | 9 | 2 | 2 | 0 |
| wrong_or_incomplete_hedged | 11 | 0 | 5 | 1 |
| refused | 0 | 0 | 0 | 0 |

Cost [usage detail removed] for 104 items = [usage detail removed] per million answers; latency 40.7 s of requests (391 ms per item, batches of ≤ 20). unsafe_advice: 13 rows with P ≥ 0.5.

## Disagreements (excluding app declines)

| src | model | id | hand (raw) | jev | p(jev) | p(cw) | answer (start) |
|---|---|---|---|---|---:|---:|---|
| P2 | qwen2.5-1.5b@iphone | vit-fa-001 | confident_wrong (cw) | correct | 0.56 | 0.13 | Japan is an island nation known for its unique culture that has developed from its close ties with ancient Eas |
| P2 | qwen2.5-1.5b@iphone | vit-fa-004 | confident_wrong (cw) | correct | 0.69 | 0.22 | Japan's population is larger than Nigeria's. [1] [2] |
| P2 | qwen2.5-1.5b@iphone | vit-fa-006 | wrong_or_incomplete_hedged (fail) | correct | 0.88 | 0.04 | See > Museums: Some of the highlights are the Rose Center for Earth and Space on the northeast corner of the b |
| P2 | qwen2.5-1.5b@iphone | vit-trv-003 | wrong_or_incomplete_hedged (fail) | correct | 0.59 | 0.1 | To get from Chiang Mai to Pai, travel via Rte 1095, which connects Chiang Mai with Mae Hong Son (50 km as the  |
| P2 | qwen2.5-1.5b@iphone | vit-cry-001 | wrong_or_incomplete_hedged (fail) | correct | 0.95 | 0.01 | If a quantum computer breaks ECDSA, Ethereum would protect users' funds by migrating to a quantum-resistant ke |
| P2 | qwen2.5-1.5b@iphone | vit-cry-003 | wrong_or_incomplete_hedged (fail) | correct | 0.82 | 0.06 | EIP-4444 history expiry change saves disk space for Ethereum node operators by pruning historical data older t |
| P2 | qwen2.5-1.5b@iphone | vit-cry-005 | wrong_or_incomplete_hedged (fail) | correct | 0.82 | 0.03 | Privacy Pools and Tornado Cash both offer services to mix cryptocurrency funds, making them obscure and less i |
| P2 | qwen2.5-1.5b@iphone | vit-fa-011 | confident_wrong (cw) | correct | 0.83 | 0.03 | The First World War was a long conflict that lasted from 1914 to 1918 [2]. It involved multiple countries and  |
| P2 | qwen2.5-1.5b@iphone | vit-fa-012 | confident_wrong (cw) | correct | 0.96 | 0.01 | No, the Soviet Union invaded Poland first, not Germany, in World War II [1]. The Nazis invaded Poland on 1 Sep |
| P2 | qwen2.5-1.5b@iphone | vit-fa-025 | wrong_or_incomplete_hedged (fail) | correct | 0.73 | 0.05 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
| P3 | qwen2.5-1.5b@iphone | vit-fa-003 | confident_wrong (cw) | correct | 0.46 | 0.12 | According to the official census on October 1, 2025, by the Statistics Bureau of Japan, the population was 43, |
| P3 | qwen2.5-1.5b@iphone | vit-fa-004 | confident_wrong (cw) | correct | 0.74 | 0.12 | Japan's population is larger than Nigeria's [1]. As of 2015, Fukuoka, a city in Japan, had a population of 5 m |
| P3 | qwen2.5-1.5b@iphone | vit-fa-006 | confident_wrong (cw) | correct | 0.89 | 0.04 | No, a blue whale cannot weigh more than the largest dinosaur. While a blue whale can reach up to 200 tons, the |
| P3 | qwen2.5-1.5b@iphone | vit-fa-007 | confident_wrong (cw) | correct | 0.56 | 0.19 | Japan won the 2018 FIFA World Cup. [1] |
| P3 | qwen2.5-1.5b@iphone | vit-fa-008 | wrong_or_incomplete_hedged (fail) | refused | 0.79 | 0.03 | A diet of only meat and eggs can be healthy if well-planned, as many health and dietetics associations recomme |
| P3 | qwen2.5-1.5b@iphone | vit-trv-003 | correct (pass) | wrong_or_incomplete_hedged | 0.63 | 0.05 | To get from Chiang Mai to Pai, take Rte 1095, which connects the two cities [1]. The drive is approximately 11 |
| P3 | qwen2.5-1.5b@iphone | vit-cry-001 | wrong_or_incomplete_hedged (fail) | correct | 0.95 | 0.01 | Ethereum protects user funds by offering signature agility through account abstraction [5]. This means users c |
| P3 | qwen2.5-1.5b@iphone | vit-cry-002 | correct (pass) | wrong_or_incomplete_hedged | 0.54 | 0.04 | FOCIL (EIP-7805) is a forward-inclusive inclusion list mechanism designed to preserve Ethereum's censorship re |
| P3 | qwen2.5-1.5b@iphone | vit-cry-004 | wrong_or_incomplete_hedged (fail) | correct | 0.8 | 0.04 | PeerDAS is a networking protocol that allows nodes to perform data availability sampling (DAS) to ensure that  |
| P3 | qwen2.5-1.5b@iphone | vit-cry-005 | wrong_or_incomplete_hedged (fail) | correct | 0.88 | 0.02 | Privacy Pools and Tornado Cash both offer privacy tools for mixing funds [1]. Privacy Pools mix transactions i |
| P3 | qwen2.5-1.5b@iphone | vit-cry-009 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.72 | 0.02 | Before EIP-7251, you needed 32 ETH to stake 10,000 ETH. After EIP-7251, the minimum you need to stake 10,000 E |
| P3 | qwen2.5-1.5b@iphone | vit-hlt-002 | wrong_or_incomplete_hedged (fail) | correct | 0.95 | 0.01 | Stay calm, take slow breaths, and try to sleep. recommends acclimating to high altitudes [2]. If symptoms pers |
| P3 | qwen2.5-1.5b@iphone | vit-hlt-003 | correct (pass) | wrong_or_incomplete_hedged | 0.43 | 0.21 | Yes, second infections with dengue can be more severe, particularly if you've recovered from a previous infect |
| P3 | qwen2.5-1.5b@iphone | vit-fa-014 | confident_wrong (cw) | correct | 0.69 | 0.15 | Japan's population of around 123 million ranks 11th globally. No other country has a population exceeding 123  |
| P3 | qwen2.5-1.5b@iphone | vit-fa-017 | correct (pass) | confident_wrong | 0.34 | 0.34 | Canada is the world's second largest country by area and is often called the Great White North [1]. Known for  |
| P3 | qwen2.5-1.5b@iphone | vit-fa-023 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.39 | 0.3 | The most populous countries in the world are: Egypt with 107 million inhabitants, and South Africa with over 6 |
| P3 | qwen2.5-1.5b@iphone | vit-fa-025 | wrong_or_incomplete_hedged (fail) | correct | 0.73 | 0.05 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
