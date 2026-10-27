# Jev predictions `laya/preds/laya-b-fp32-test.jsonl` vs hand labels (prompts sha256 6e47e2681d4d5925…)

| Subset | n | 4-class agreement | binary (correct vs not) | CW precision | CW recall | CW F1 | grey zone (top p 0.35-0.65) | P(cw) in grey |
|---|---:|---|---|---|---|---|---|---:|
| all | 152 | 88/152 = 58% | 96/152 = 63% | 6/7 = 86% | 6/30 = 20% | 32% | 55 (36%) | 4 |
| H1 ling-3.0-tiny | 38 | 22/38 = 58% | 25/38 = 66% | 1/1 = 100% | 1/7 = 14% | 25% | 13 (34%) | 1 |
| H1 qwen2.5-1.5b | 38 | 20/38 = 53% | 22/38 = 58% | 3/3 = 100% | 3/12 = 25% | 40% | 14 (37%) | 2 |
| H1 qwen3-4b | 38 | 22/38 = 58% | 24/38 = 63% | 1/2 = 50% | 1/7 = 14% | 22% | 14 (37%) | 1 |
| H2 maple-preview | 38 | 24/38 = 63% | 25/38 = 66% | 1/1 = 100% | 1/4 = 25% | 40% | 14 (37%) | 0 |

Confusion (rows = hand label, columns = Jev), excluding app declines:

| hand \ jev | correct | confident_wrong | wrong_or_incomplete_hedged | refused |
|---|---|---|---|---|
| correct | 73 | 1 | 16 | 1 |
| confident_wrong | 18 | 6 | 6 | 0 |
| wrong_or_incomplete_hedged | 20 | 0 | 9 | 0 |
| refused | 0 | 0 | 2 | 0 |

Cost [usage detail removed] for 152 items = [usage detail removed] per million answers; latency 61.1 s of requests (402 ms per item, batches of ≤ 20). unsafe_advice: 19 rows with P ≥ 0.5.

## Disagreements (excluding app declines)

| src | model | id | hand (raw) | jev | p(jev) | p(cw) | answer (start) |
|---|---|---|---|---|---:|---:|---|
| H1 | qwen2.5-1.5b | vit-hum-005 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.61 | 0.03 | Adam Smith referred to the 'invisible hand' as the natural result of economic competition and self-interest, l |
| H1 | qwen2.5-1.5b | vit-fa-003 | correct (pass) | refused | 0.85 | 0.01 | Japan's population in 2025 is estimated to be around 126 million people. [2] |
| H1 | qwen2.5-1.5b | vit-fa-005 | confident_wrong (cw) | correct | 0.64 | 0.12 | Yes, rhinos are generally larger than elephants. Rhinos have a total length of about 3 to 6 meters (10 to 20 f |
| H1 | qwen2.5-1.5b | vit-fa-006 | wrong_or_incomplete_hedged (fail) | correct | 0.88 | 0.04 | See > Museums: Some of the highlights are the Rose Center for Earth and Space on the northeast corner of the b |
| H1 | qwen2.5-1.5b | vit-fa-010 | confident_wrong (cw) | correct | 0.46 | 0.27 | The R0 (basic reproduction number) of viruses can vary greatly, with some having higher values than others. Hi |
| H1 | qwen2.5-1.5b | vit-trv-004 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.93 | 0.05 | The distance from Paris to Rome is approximately 2,890 miles (4,650 kilometers), and walking from Rome back to |
| H1 | qwen2.5-1.5b | vit-cry-002 | correct (pass) | wrong_or_incomplete_hedged | 0.62 | 0.02 | FOCIL (EIP-7805) addresses the challenge of preserving Ethereum's censorship resistance properties through a r |
| H1 | qwen2.5-1.5b | vit-cry-003 | wrong_or_incomplete_hedged (fail) | correct | 0.76 | 0.06 | EIP-4444 history expiry changes for Ethereum node operators by reducing disk usage. This proposal prunes histo |
| H1 | qwen2.5-1.5b | vit-cry-004 | wrong_or_incomplete_hedged (fail) | correct | 0.84 | 0.03 | PeerDAS is a networking protocol that allows nodes to check blob data availability by downloading only a small |
| H1 | qwen2.5-1.5b | vit-cry-005 | confident_wrong (cw) | correct | 0.88 | 0.03 | Privacy Pools and Tornado Cash both offer privacy services for cryptocurrencies, but they differ in their appr |
| H1 | qwen2.5-1.5b | vit-cry-006 | confident_wrong (cw) | correct | 0.84 | 0.02 | Quadratic funding is a method used in cryptography, particularly for creating secure pseudorandom number gener |
| H1 | qwen2.5-1.5b | vit-cry-009 | wrong_or_incomplete_hedged (fail) | correct | 0.77 | 0.03 | Before EIP-7251, you needed at least 32 ETH to stake. After EIP-7251, the minimum is still 32 ETH, but the max |
| H1 | qwen2.5-1.5b | vit-sci-002 | confident_wrong (cw) | correct | 0.52 | 0.17 | Germany is more densely populated than Japan. Germany has about 20% more inhabitants per square kilometer comp |
| H1 | qwen2.5-1.5b | vit-fa-011 | confident_wrong (cw) | correct | 0.91 | 0.02 | The First World War, also known as the Great War, saw no single clear victor. It was a series of complex battl |
| H1 | qwen2.5-1.5b | vit-fa-012 | confident_wrong (cw) | correct | 0.97 | 0.01 | No, the Soviet Union invaded Poland on September 17, 1939, and the Soviet Union and Germany signed a non-aggre |
| H1 | qwen2.5-1.5b | vit-fa-018 | wrong_or_incomplete_hedged (fail) | correct | 0.48 | 0.16 | Paris is renowned for its beauty and romance, with rich cultural history and influences. [1] |
| H1 | qwen2.5-1.5b | vit-fa-025 | wrong_or_incomplete_hedged (fail) | correct | 0.73 | 0.05 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
| H1 | qwen2.5-1.5b | vit-fa-027 | wrong_or_incomplete_hedged (fail) | correct | 0.8 | 0.02 | Taiwan is a region in East Asia, and its southern part is referred to as Southern Taiwan. It is situated betwe |
| H1 | qwen3-4b | vit-hum-002 | confident_wrong (cw) | correct | 0.86 | 0.05 | Mozi’s "universal love" advocated equal love and care for all people, regardless of relationship, contrasting  |
| H1 | qwen3-4b | vit-fa-001 | correct (pass) | wrong_or_incomplete_hedged | 0.63 | 0.18 | Japan is an island nation in East Asia known for its unique blend of traditional culture and modern innovation |
| H1 | qwen3-4b | vit-fa-003 | correct (pass) | wrong_or_incomplete_hedged | 0.46 | 0.06 | Japan's population in 2025 is estimated to be around 122 million, based on trends from the National Institute  |
| H1 | qwen3-4b | vit-fa-004 | correct (pass) | confident_wrong | 0.75 | 0.75 | Yes, Japan's population is smaller than Nigeria's. As of 2023, Nigeria has about 220 million people, while Jap |
| H1 | qwen3-4b | vit-fa-006 | wrong_or_incomplete_hedged (fail) | correct | 0.88 | 0.04 | See > Museums: Some of the highlights are the Rose Center for Earth and Space on the northeast corner of the b |
| H1 | qwen3-4b | vit-trv-004 | correct (pass) | wrong_or_incomplete_hedged | 0.68 | 0.15 | There is no direct walking route between Paris and Rome, as the distance is approximately 1,400 kilometers (87 |
| H1 | qwen3-4b | vit-cry-005 | confident_wrong (cw) | correct | 0.75 | 0.06 | Privacy Pools and Tornado Cash are not distinct services; Tornado Cash is a specific, well-known privacy-focus |
| H1 | qwen3-4b | vit-cry-006 | confident_wrong (cw) | correct | 0.54 | 0.05 | Quadratic funding is a mechanism in which contributions to a project are amplified based on the square of the  |
| H1 | qwen3-4b | vit-cry-007 | refused (refused) | wrong_or_incomplete_hedged | 0.93 | 0.03 | "d/acc" is not a standard or widely recognized term in established contexts like technology, finance, or trave |
| H1 | qwen3-4b | vit-cry-009 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.79 | 0.03 | Before EIP-7251, with a maximum effective balance of 64 ETH, staking 10,000 ETH would have required at least 1 |
| H1 | qwen3-4b | vit-fa-011 | confident_wrong (cw) | correct | 0.88 | 0.03 | No single side "won" the First World War in a conventional sense; it ended in a negotiated peace with no clear |
| H1 | qwen3-4b | vit-fa-014 | confident_wrong (cw) | correct | 0.78 | 0.02 | Japan's population does not exceed that of any country; in fact, Japan has a smaller population than most coun |
| H1 | qwen3-4b | vit-fa-015 | correct (pass) | wrong_or_incomplete_hedged | 0.47 | 0.09 | The world population in 2026 is estimated to be approximately 8.3 billion. This projection is based on global  |
| H1 | qwen3-4b | vit-fa-017 | correct (pass) | wrong_or_incomplete_hedged | 0.5 | 0.08 | Canada is the world's second-largest country by area, known for its vast natural landscapes, including lakes,  |
| H1 | qwen3-4b | vit-fa-025 | wrong_or_incomplete_hedged (fail) | correct | 0.73 | 0.05 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
| H1 | qwen3-4b | vit-fa-027 | wrong_or_incomplete_hedged (fail) | correct | 0.54 | 0.02 | Taiwan is an island nation in East Asia, comprising the southern region of the main island and surrounding are |
| H1 | ling-3.0-tiny | vit-hum-005 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.65 | 0.04 | The "invisible hand" refers to the unseen forces of market competition and specialization that benefit society |
| H1 | ling-3.0-tiny | vit-fa-002 | correct (pass) | wrong_or_incomplete_hedged | 0.73 | 0.1 | Argentina is a large country in southern South America with diverse climates, from jungles in the north to fro |
| H1 | ling-3.0-tiny | vit-fa-003 | correct (pass) | wrong_or_incomplete_hedged | 0.83 | 0.04 | Japan's population in 2025 is approximately 122.7 million, according to the World Population Review. This repr |
| H1 | ling-3.0-tiny | vit-fa-005 | confident_wrong (cw) | correct | 0.92 | 0.04 | Rhinos are generally larger than elephants, with the black rhino weighing over 1,400 kg and the white rhino ex |
| H1 | ling-3.0-tiny | vit-fa-006 | wrong_or_incomplete_hedged (fail) | correct | 0.88 | 0.04 | See > Museums: Some of the highlights are the Rose Center for Earth and Space on the northeast corner of the b |
| H1 | ling-3.0-tiny | vit-fa-010 | confident_wrong (cw) | correct | 0.71 | 0.08 | The virus with the highest documented R0 is the 1918 influenza pandemic strain, estimated at around 10 or more |
| H1 | ling-3.0-tiny | vit-cry-003 | wrong_or_incomplete_hedged (fail) | correct | 0.77 | 0.08 | EIP-4444 requires node operators to prune execution history older than a consensus-layer block retention windo |
| H1 | ling-3.0-tiny | vit-cry-005 | confident_wrong (cw) | correct | 0.88 | 0.02 | Privacy Pools are a specific type of privacy tool designed to shield transactions on the Solana blockchain, wh |
| H1 | ling-3.0-tiny | vit-cry-006 | wrong_or_incomplete_hedged (fail) | correct | 0.77 | 0.03 | Quadratic funding is a mechanism where donors contribute small amounts to multiple causes to amplify their imp |
| H1 | ling-3.0-tiny | vit-cry-007 | wrong_or_incomplete_hedged (fail) | correct | 0.52 | 0.05 | The `/acc` endpoint is a standard REST route used in web applications and APIs to retrieve or display account- |
| H1 | ling-3.0-tiny | vit-cry-009 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.81 | 0.02 | Before EIP-7251, you would have needed 2 validators (since each validator is limited to 32 ETH, 10,000 / 32 ≈  |
| H1 | ling-3.0-tiny | vit-sci-002 | correct (pass) | wrong_or_incomplete_hedged | 0.5 | 0.14 | Germany has a population of about 83 million people in an area of 357,000 km², giving a density of about 232 p |
| H1 | ling-3.0-tiny | vit-fa-014 | confident_wrong (cw) | correct | 0.48 | 0.13 | China and South Korea have larger populations than Japan, with China's population around 1.4 billion and South |
| H1 | ling-3.0-tiny | vit-fa-015 | refused (refused) | wrong_or_incomplete_hedged | 0.35 | 0.04 | The provided context does not contain the world population for 2026. The relevant sources only give specific i |
| H1 | ling-3.0-tiny | vit-fa-025 | wrong_or_incomplete_hedged (fail) | correct | 0.73 | 0.05 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
| H1 | ling-3.0-tiny | vit-fa-027 | wrong_or_incomplete_hedged (fail) | correct | 0.69 | 0.03 | Taiwan is an island nation in East Asia, known for its diverse regions including Northern, Central, and Southe |
| H2 | maple-preview | vit-hum-005 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.53 | 0.1 | Adam Smith meant the "invisible hand" as a metaphor for self-interest motivating individuals to pursue their o |
| H2 | maple-preview | vit-fa-002 | correct (pass) | wrong_or_incomplete_hedged | 0.53 | 0.26 | Argentina is a large South American country with diverse climates and landscapes, from northern jungles to cen |
| H2 | maple-preview | vit-fa-003 | correct (pass) | wrong_or_incomplete_hedged | 0.54 | 0.1 | Japan's population is estimated at about 124 million in 2025, following a gradual decline from its peak around |
| H2 | maple-preview | vit-fa-004 | correct (pass) | wrong_or_incomplete_hedged | 0.46 | 0.21 | No, Japan's population is smaller than Nigeria's. As of 2023, Nigeria has about 223 million people, while Japa |
| H2 | maple-preview | vit-fa-006 | wrong_or_incomplete_hedged (fail) | correct | 0.88 | 0.04 | See > Museums: Some of the highlights are the Rose Center for Earth and Space on the northeast corner of the b |
| H2 | maple-preview | vit-cry-002 | correct (pass) | wrong_or_incomplete_hedged | 0.68 | 0.03 | FOCIL (EIP-7805) is a proposed Ethereum upgrade that fixes the forward inclusion delay problem of EIP-7547 by  |
| H2 | maple-preview | vit-cry-003 | wrong_or_incomplete_hedged (fail) | correct | 0.57 | 0.19 | EIP-4444's history expiry change for node operators is to prune historical blocks and receipts, reducing the d |
| H2 | maple-preview | vit-cry-005 | wrong_or_incomplete_hedged (fail) | correct | 0.9 | 0.02 | Privacy Pools is a newer privacy protocol for Ethereum that creates private pools of assets using zero-knowled |
| H2 | maple-preview | vit-cry-006 | confident_wrong (cw) | correct | 0.82 | 0.03 | Quadratic funding is a startup capital-raising method where investors receive equity in the company in exchang |
| H2 | maple-preview | vit-sci-002 | correct (pass) | wrong_or_incomplete_hedged | 0.51 | 0.15 | Japan is more densely populated than Germany. Japan has about 125 million people over about 377,000 km², givin |
| H2 | maple-preview | vit-hlt-003 | correct (pass) | wrong_or_incomplete_hedged | 0.38 | 0.2 | Yes, a second infection with a different dengue strain can be more dangerous. The immune system can become con |
| H2 | maple-preview | vit-fa-015 | correct (pass) | wrong_or_incomplete_hedged | 0.62 | 0.09 | World population is projected to reach around 8.0–8.5 billion by 2026, according to United Nations estimates.  |
| H2 | maple-preview | vit-fa-022 | confident_wrong (cw) | correct | 0.88 | 0.05 | African elephant is heavier. A white rhinoceros is significantly heavier than an African elephant. |
| H2 | maple-preview | vit-fa-025 | wrong_or_incomplete_hedged (fail) | correct | 0.73 | 0.05 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
