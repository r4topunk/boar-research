# Jev predictions `laya/preds/laya-fp32-test.jsonl` vs hand labels (prompts sha256 3426670d8f490476…)

| Subset | n | 4-class agreement | binary (correct vs not) | CW precision | CW recall | CW F1 | grey zone (top p 0.35-0.65) | P(cw) in grey |
|---|---:|---|---|---|---|---|---|---:|
| all | 152 | 37/152 = 24% | 60/152 = 39% | 19/105 = 18% | 19/30 = 63% | 28% | 98 (64%) | 79 |
| H1 ling-3.0-tiny | 38 | 11/38 = 29% | 16/38 = 42% | 6/27 = 22% | 6/7 = 86% | 35% | 20 (53%) | 17 |
| H1 qwen2.5-1.5b | 38 | 13/38 = 34% | 19/38 = 50% | 8/25 = 32% | 8/12 = 67% | 43% | 26 (68%) | 21 |
| H1 qwen3-4b | 38 | 5/38 = 13% | 11/38 = 29% | 2/24 = 8% | 2/7 = 29% | 13% | 25 (66%) | 18 |
| H2 maple-preview | 38 | 8/38 = 21% | 14/38 = 37% | 3/29 = 10% | 3/4 = 75% | 18% | 27 (71%) | 23 |

Confusion (rows = hand label, columns = Jev), excluding app declines:

| hand \ jev | correct | confident_wrong | wrong_or_incomplete_hedged | refused |
|---|---|---|---|---|
| correct | 9 | 70 | 12 | 0 |
| confident_wrong | 6 | 19 | 5 | 0 |
| wrong_or_incomplete_hedged | 4 | 15 | 9 | 1 |
| refused | 0 | 1 | 1 | 0 |

Cost [usage detail removed] for 152 items = [usage detail removed] per million answers; latency 85.0 s of requests (559 ms per item, batches of ≤ 20). unsafe_advice: 28 rows with P ≥ 0.5.

## Disagreements (excluding app declines)

| src | model | id | hand (raw) | jev | p(jev) | p(cw) | answer (start) |
|---|---|---|---|---|---:|---:|---|
| H1 | qwen2.5-1.5b | vit-hum-001 | correct (pass) | confident_wrong | 0.51 | 0.51 | Mozi, a Chinese philosopher, advocated for universal love, stating that humans should extend their love to all |
| H1 | qwen2.5-1.5b | vit-hum-002 | correct (pass) | confident_wrong | 0.52 | 0.52 | Mozi's idea of universal love emphasized equality and non-violence, viewing all life as valuable. Confucius, o |
| H1 | qwen2.5-1.5b | vit-fa-001 | correct (pass) | confident_wrong | 0.4 | 0.4 | Japan is an island nation in East Asia known for its unique and intricate culture, closeness to ancient East A |
| H1 | qwen2.5-1.5b | vit-fa-002 | correct (pass) | wrong_or_incomplete_hedged | 0.9 | 0.06 | Argentina is a large country in the southern part of South America known for its diverse landscapes from jungl |
| H1 | qwen2.5-1.5b | vit-fa-003 | correct (pass) | confident_wrong | 0.56 | 0.56 | Japan's population in 2025 is estimated to be around 126 million people. [2] |
| H1 | qwen2.5-1.5b | vit-fa-006 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.53 | 0.53 | See > Museums: Some of the highlights are the Rose Center for Earth and Space on the northeast corner of the b |
| H1 | qwen2.5-1.5b | vit-trv-004 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.71 | 0.29 | The distance from Paris to Rome is approximately 2,890 miles (4,650 kilometers), and walking from Rome back to |
| H1 | qwen2.5-1.5b | vit-cry-002 | correct (pass) | confident_wrong | 0.44 | 0.44 | FOCIL (EIP-7805) addresses the challenge of preserving Ethereum's censorship resistance properties through a r |
| H1 | qwen2.5-1.5b | vit-cry-003 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.51 | 0.51 | EIP-4444 history expiry changes for Ethereum node operators by reducing disk usage. This proposal prunes histo |
| H1 | qwen2.5-1.5b | vit-cry-004 | wrong_or_incomplete_hedged (fail) | correct | 0.36 | 0.31 | PeerDAS is a networking protocol that allows nodes to check blob data availability by downloading only a small |
| H1 | qwen2.5-1.5b | vit-cry-005 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.77 | 0.05 | Privacy Pools and Tornado Cash both offer privacy services for cryptocurrencies, but they differ in their appr |
| H1 | qwen2.5-1.5b | vit-cry-006 | confident_wrong (cw) | correct | 0.53 | 0.29 | Quadratic funding is a method used in cryptography, particularly for creating secure pseudorandom number gener |
| H1 | qwen2.5-1.5b | vit-cry-010 | correct (pass) | confident_wrong | 0.39 | 0.39 | The 2016 DAO hack highlighted the importance of careful contract development and the need for continuous secur |
| H1 | qwen2.5-1.5b | vit-hlt-003 | correct (pass) | confident_wrong | 0.69 | 0.69 | Dengue is more dangerous the second time you get it, as people who have recovered from an infection with one s |
| H1 | qwen2.5-1.5b | vit-fa-012 | confident_wrong (cw) | correct | 0.56 | 0.33 | No, the Soviet Union invaded Poland on September 17, 1939, and the Soviet Union and Germany signed a non-aggre |
| H1 | qwen2.5-1.5b | vit-fa-013 | correct (pass) | confident_wrong | 0.83 | 0.83 | The tallest animal in the world is the giraffe, standing up to 5.5 meters tall. [1] |
| H1 | qwen2.5-1.5b | vit-fa-015 | correct (pass) | confident_wrong | 0.53 | 0.53 | As of 2026, the world population is estimated to have reached 8 billion. |
| H1 | qwen2.5-1.5b | vit-fa-017 | correct (pass) | wrong_or_incomplete_hedged | 0.48 | 0.43 | Canada is the world's second largest country by area, known for its stunning natural landscapes and diverse mu |
| H1 | qwen2.5-1.5b | vit-fa-019 | correct (pass) | confident_wrong | 0.43 | 0.43 | The Amazon rainforest, also called the Amazon jungle, is a moist broadleaf tropical rainforest covering 7 mill |
| H1 | qwen2.5-1.5b | vit-fa-021 | correct (pass) | confident_wrong | 0.78 | 0.78 | Lions and tigers are both large cats, but tigers are typically heavier. Tigers can weigh up to 500 pounds (227 |
| H1 | qwen2.5-1.5b | vit-fa-022 | correct (pass) | confident_wrong | 0.45 | 0.45 | An African elephant is generally heavier than a white rhinoceros. While both are large animals, elephants typi |
| H1 | qwen2.5-1.5b | vit-fa-023 | correct (pass) | confident_wrong | 0.62 | 0.62 | The most populated countries in the world are China, India, and the United States. |
| H1 | qwen2.5-1.5b | vit-fa-024 | correct (pass) | confident_wrong | 0.73 | 0.73 | The Thirty Years' War lasted from 1618 to 1648 in Europe. |
| H1 | qwen2.5-1.5b | vit-fa-025 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.54 | 0.54 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
| H1 | qwen2.5-1.5b | vit-fa-027 | wrong_or_incomplete_hedged (fail) | refused | 0.4 | 0.2 | Taiwan is a region in East Asia, and its southern part is referred to as Southern Taiwan. It is situated betwe |
| H1 | qwen3-4b | vit-hum-005 | correct (pass) | confident_wrong | 0.73 | 0.73 | Adam Smith's "invisible hand" refers to the idea that individuals, pursuing their own self-interest in a free  |
| H1 | qwen3-4b | vit-fa-001 | correct (pass) | confident_wrong | 0.45 | 0.45 | Japan is an island nation in East Asia known for its unique blend of traditional culture and modern innovation |
| H1 | qwen3-4b | vit-fa-002 | correct (pass) | wrong_or_incomplete_hedged | 0.78 | 0.16 | Argentina is a large southern South American country known for its diverse landscapes, from jungles in the nor |
| H1 | qwen3-4b | vit-fa-003 | correct (pass) | confident_wrong | 0.52 | 0.52 | Japan's population in 2025 is estimated to be around 122 million, based on trends from the National Institute  |
| H1 | qwen3-4b | vit-fa-004 | correct (pass) | confident_wrong | 0.95 | 0.95 | Yes, Japan's population is smaller than Nigeria's. As of 2023, Nigeria has about 220 million people, while Jap |
| H1 | qwen3-4b | vit-fa-006 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.53 | 0.53 | See > Museums: Some of the highlights are the Rose Center for Earth and Space on the northeast corner of the b |
| H1 | qwen3-4b | vit-fa-010 | correct (pass) | confident_wrong | 0.56 | 0.56 | The highest R0 values are seen in viruses like measles (R0 ≈ 15–18), which is among the most contagious. Some  |
| H1 | qwen3-4b | vit-trv-004 | correct (pass) | confident_wrong | 0.71 | 0.71 | There is no direct walking route between Paris and Rome, as the distance is approximately 1,400 kilometers (87 |
| H1 | qwen3-4b | vit-cry-002 | correct (pass) | confident_wrong | 0.38 | 0.38 | FOCIL (Fork-choice enforced Inclusion Lists) is a proposed Ethereum improvement (EIP-7805) that ensures timely |
| H1 | qwen3-4b | vit-cry-004 | correct (pass) | wrong_or_incomplete_hedged | 0.41 | 0.26 | PeerDAS (Peer Data Availability Sampling) is a protocol that enables nodes to verify blob data availability by |
| H1 | qwen3-4b | vit-cry-005 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.88 | 0.06 | Privacy Pools and Tornado Cash are not distinct services; Tornado Cash is a specific, well-known privacy-focus |
| H1 | qwen3-4b | vit-cry-006 | confident_wrong (cw) | correct | 0.46 | 0.26 | Quadratic funding is a mechanism in which contributions to a project are amplified based on the square of the  |
| H1 | qwen3-4b | vit-cry-007 | refused (refused) | wrong_or_incomplete_hedged | 0.99 | 0.0 | "d/acc" is not a standard or widely recognized term in established contexts like technology, finance, or trave |
| H1 | qwen3-4b | vit-cry-009 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.77 | 0.09 | Before EIP-7251, with a maximum effective balance of 64 ETH, staking 10,000 ETH would have required at least 1 |
| H1 | qwen3-4b | vit-cry-010 | correct (pass) | confident_wrong | 0.5 | 0.5 | The 2016 DAO hack highlighted critical vulnerabilities in Solidity smart contract code, including recursive ca |
| H1 | qwen3-4b | vit-cry-011 | wrong_or_incomplete_hedged (fail) | correct | 0.43 | 0.33 | Terra’s stablecoin UST collapsed in May 2022 due to a loss of confidence and massive sell-offs, causing it to  |
| H1 | qwen3-4b | vit-sci-002 | correct (pass) | confident_wrong | 0.71 | 0.71 | Japan is more densely populated than Germany. As of recent data, Japan’s population density is about 340 peopl |
| H1 | qwen3-4b | vit-hlt-003 | correct (pass) | confident_wrong | 0.72 | 0.72 | Yes, dengue can be more dangerous upon reinfection. A second infection, especially with a different dengue vir |
| H1 | qwen3-4b | vit-fa-011 | confident_wrong (cw) | correct | 0.46 | 0.39 | No single side "won" the First World War in a conventional sense; it ended in a negotiated peace with no clear |
| H1 | qwen3-4b | vit-fa-012 | correct (pass) | confident_wrong | 0.46 | 0.46 | Yes, Germany invaded the Soviet Union on June 22, 1941, in an operation codenamed Operation Barbarossa [1]. Th |
| H1 | qwen3-4b | vit-fa-013 | correct (pass) | confident_wrong | 0.88 | 0.88 | There is no known animal that is the tallest in the world in a universally accepted sense, as height varies by |
| H1 | qwen3-4b | vit-fa-014 | confident_wrong (cw) | correct | 0.48 | 0.32 | Japan's population does not exceed that of any country; in fact, Japan has a smaller population than most coun |
| H1 | qwen3-4b | vit-fa-015 | correct (pass) | wrong_or_incomplete_hedged | 0.56 | 0.39 | The world population in 2026 is estimated to be approximately 8.3 billion. This projection is based on global  |
| H1 | qwen3-4b | vit-fa-017 | correct (pass) | confident_wrong | 0.46 | 0.46 | Canada is the world's second-largest country by area, known for its vast natural landscapes, including lakes,  |
| H1 | qwen3-4b | vit-fa-018 | correct (pass) | wrong_or_incomplete_hedged | 0.54 | 0.16 | Paris is the capital of France, renowned for its romantic ambiance, rich cultural heritage, and iconic landmar |
| H1 | qwen3-4b | vit-fa-019 | correct (pass) | confident_wrong | 0.54 | 0.54 | The Amazon rainforest is the world's largest tropical rainforest, spanning parts of nine South American countr |
| H1 | qwen3-4b | vit-fa-020 | correct (pass) | confident_wrong | 0.43 | 0.43 | Mount Everest, at 8,848.86 m (29,032 ft), is the world's tallest mountain, straddling the border of Nepal and  |
| H1 | qwen3-4b | vit-fa-021 | correct (pass) | confident_wrong | 0.74 | 0.74 | Tigers are heavier than lions. An adult male tiger can weigh up to 306 pounds (139 kg), while a male lion typi |
| H1 | qwen3-4b | vit-fa-022 | correct (pass) | confident_wrong | 0.6 | 0.6 | An African elephant is heavier than a white rhinoceros. Adult elephants can weigh between 4,000 and 12,000 pou |
| H1 | qwen3-4b | vit-fa-023 | correct (pass) | confident_wrong | 0.82 | 0.82 | The most populated countries in the world are China and India, followed by the United States, Indonesia, and P |
| H1 | qwen3-4b | vit-fa-024 | correct (pass) | confident_wrong | 0.88 | 0.88 | The Thirty Years' War took place from 1618 to 1648 in Europe [1]. It was one of the most destructive conflicts |
| H1 | qwen3-4b | vit-fa-025 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.54 | 0.54 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
| H1 | qwen3-4b | vit-fa-027 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.43 | 0.43 | Taiwan is an island nation in East Asia, comprising the southern region of the main island and surrounding are |
| H1 | ling-3.0-tiny | vit-hum-002 | correct (pass) | confident_wrong | 0.71 | 0.71 | Mozi's universal love was a universal, impartial care for all people regardless of kinship or social status. M |
| H1 | ling-3.0-tiny | vit-fa-002 | correct (pass) | wrong_or_incomplete_hedged | 0.88 | 0.07 | Argentina is a large country in southern South America with diverse climates, from jungles in the north to fro |
| H1 | ling-3.0-tiny | vit-fa-003 | correct (pass) | confident_wrong | 0.95 | 0.95 | Japan's population in 2025 is approximately 122.7 million, according to the World Population Review. This repr |
| H1 | ling-3.0-tiny | vit-fa-004 | correct (pass) | confident_wrong | 0.66 | 0.66 | Japan's population is approximately 125 million, while Nigeria's population is around 220 million [1]. Nigeria |
| H1 | ling-3.0-tiny | vit-fa-006 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.53 | 0.53 | See > Museums: Some of the highlights are the Rose Center for Earth and Space on the northeast corner of the b |
| H1 | ling-3.0-tiny | vit-trv-004 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.77 | 0.77 | The distance between Paris and Rome is roughly 1,100 kilometers, so a round trip would be around 2,200 kilomet |
| H1 | ling-3.0-tiny | vit-cry-002 | correct (pass) | confident_wrong | 0.58 | 0.58 | FOCIL (EIP-7805) is a Fork-choice enforced Inclusion List mechanism that ensures transaction inclusion in ever |
| H1 | ling-3.0-tiny | vit-cry-003 | wrong_or_incomplete_hedged (fail) | correct | 0.37 | 0.37 | EIP-4444 requires node operators to prune execution history older than a consensus-layer block retention windo |
| H1 | ling-3.0-tiny | vit-cry-004 | correct (pass) | wrong_or_incomplete_hedged | 0.4 | 0.31 | PeerDAS (Peer Data Availability Sampling) is a networking protocol that allows nodes to perform data availabil |
| H1 | ling-3.0-tiny | vit-cry-006 | wrong_or_incomplete_hedged (fail) | correct | 0.28 | 0.27 | Quadratic funding is a mechanism where donors contribute small amounts to multiple causes to amplify their imp |
| H1 | ling-3.0-tiny | vit-cry-009 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.78 | 0.15 | Before EIP-7251, you would have needed 2 validators (since each validator is limited to 32 ETH, 10,000 / 32 ≈  |
| H1 | ling-3.0-tiny | vit-cry-010 | correct (pass) | confident_wrong | 0.43 | 0.43 | The 2016 DAO hack exposed critical vulnerabilities in smart contract design, particularly in the Ethereum Virt |
| H1 | ling-3.0-tiny | vit-cry-011 | correct (pass) | confident_wrong | 0.31 | 0.31 | Terra's collapse was driven by a massive, coordinated sell-off of the UST stablecoin, which was partially coll |
| H1 | ling-3.0-tiny | vit-sci-002 | correct (pass) | confident_wrong | 0.68 | 0.68 | Germany has a population of about 83 million people in an area of 357,000 km², giving a density of about 232 p |
| H1 | ling-3.0-tiny | vit-hlt-003 | correct (pass) | wrong_or_incomplete_hedged | 0.75 | 0.21 | Dengue fever is more likely to progress to severe dengue, or hemorrhagic fever, the second time you're infecte |
| H1 | ling-3.0-tiny | vit-fa-011 | correct (pass) | confident_wrong | 0.59 | 0.59 | The Allied Powers, primarily the United Kingdom, France, and later the United States, won World War I. Germany |
| H1 | ling-3.0-tiny | vit-fa-013 | correct (pass) | confident_wrong | 0.85 | 0.85 | The tallest animal in the world is the giraffe, with an average height of 4.5–5.5 meters (14–18 feet) from hoo |
| H1 | ling-3.0-tiny | vit-fa-015 | refused (refused) | confident_wrong | 0.73 | 0.73 | The provided context does not contain the world population for 2026. The relevant sources only give specific i |
| H1 | ling-3.0-tiny | vit-fa-017 | correct (pass) | confident_wrong | 0.51 | 0.51 | Canada is the world's second-largest country by area, known for its vast natural landscapes and multicultural  |
| H1 | ling-3.0-tiny | vit-fa-018 | correct (pass) | confident_wrong | 0.37 | 0.37 | Paris is the cosmopolitan capital of France, renowned for its beauty, culture, art, fashion, food, and design. |
| H1 | ling-3.0-tiny | vit-fa-019 | correct (pass) | confident_wrong | 0.47 | 0.47 | The Amazon rainforest is a moist broadleaf tropical rainforest covering most of the Amazon basin in South Amer |
| H1 | ling-3.0-tiny | vit-fa-020 | correct (pass) | confident_wrong | 0.35 | 0.35 | Mount Everest is the world's tallest mountain at 8,848.86 m (29,032 ft) and straddles the border of China/Tibe |
| H1 | ling-3.0-tiny | vit-fa-021 | correct (pass) | confident_wrong | 0.76 | 0.76 | Tigers are generally heavier than lions, with the Siberian tiger being the largest cat species. However, indiv |
| H1 | ling-3.0-tiny | vit-fa-022 | correct (pass) | confident_wrong | 0.54 | 0.54 | The African elephant typically weighs between 4,000 and 14,000 pounds, with males reaching over 14,000 pounds. |
| H1 | ling-3.0-tiny | vit-fa-023 | correct (pass) | confident_wrong | 0.56 | 0.56 | The most populated countries in the world are China, India, the United States, Indonesia, and Pakistan. These  |
| H1 | ling-3.0-tiny | vit-fa-024 | correct (pass) | confident_wrong | 0.87 | 0.87 | The Thirty Years' War took place from 1618 to 1648 in Europe [1]. It was one of the most destructive wars in E |
| H1 | ling-3.0-tiny | vit-fa-025 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.54 | 0.54 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
| H2 | maple-preview | vit-hum-001 | correct (pass) | confident_wrong | 0.4 | 0.4 | Mozi advocated for universal love (jian ai) as a foundational virtue, arguing that all humans share the same b |
| H2 | maple-preview | vit-hum-002 | correct (pass) | confident_wrong | 0.57 | 0.57 | Mozi's universal love advocated for all people treated equally, rejecting war and hierarchy. Confucianism, in  |
| H2 | maple-preview | vit-fa-001 | correct (pass) | confident_wrong | 0.49 | 0.49 | Japan's culture is rooted in a unique blend of East Asian influences and its own emphasis on inner balance, tr |
| H2 | maple-preview | vit-fa-002 | correct (pass) | wrong_or_incomplete_hedged | 0.56 | 0.36 | Argentina is a large South American country with diverse climates and landscapes, from northern jungles to cen |
| H2 | maple-preview | vit-fa-003 | correct (pass) | confident_wrong | 0.53 | 0.53 | Japan's population is estimated at about 124 million in 2025, following a gradual decline from its peak around |
| H2 | maple-preview | vit-fa-004 | correct (pass) | confident_wrong | 0.77 | 0.77 | No, Japan's population is smaller than Nigeria's. As of 2023, Nigeria has about 223 million people, while Japa |
| H2 | maple-preview | vit-fa-005 | correct (pass) | confident_wrong | 0.74 | 0.74 | Rhinos are generally smaller than elephants. The largest rhinos, like the white and black rhino, stand around  |
| H2 | maple-preview | vit-fa-006 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.53 | 0.53 | See > Museums: Some of the highlights are the Rose Center for Earth and Space on the northeast corner of the b |
| H2 | maple-preview | vit-fa-010 | correct (pass) | confident_wrong | 0.54 | 0.54 | Measles virus has the highest R0, around 12–18, among known viruses. SARS-CoV-2 has R0 around 2.5–3.0. Other h |
| H2 | maple-preview | vit-trv-004 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.85 | 0.85 | Walking from Paris to Rome would take roughly 13–14 days at a moderate pace of about 20–25 km per day, dependi |
| H2 | maple-preview | vit-cry-002 | correct (pass) | wrong_or_incomplete_hedged | 0.38 | 0.37 | FOCIL (EIP-7805) is a proposed Ethereum upgrade that fixes the forward inclusion delay problem of EIP-7547 by  |
| H2 | maple-preview | vit-cry-003 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.56 | 0.56 | EIP-4444's history expiry change for node operators is to prune historical blocks and receipts, reducing the d |
| H2 | maple-preview | vit-cry-004 | correct (pass) | confident_wrong | 0.39 | 0.39 | PeerDAS is a data availability sampling (DAS) protocol that lets nodes verify blob data availability by downlo |
| H2 | maple-preview | vit-cry-006 | confident_wrong (cw) | correct | 0.44 | 0.24 | Quadratic funding is a startup capital-raising method where investors receive equity in the company in exchang |
| H2 | maple-preview | vit-cry-010 | correct (pass) | confident_wrong | 0.44 | 0.44 | The DAO hack exposed critical security flaws in Solidity contracts, highlighting the need for thorough auditin |
| H2 | maple-preview | vit-cry-011 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.44 | 0.44 | The collapse was driven by a market-wide sell-off in late 2021 and early 2022, coupled with TerraLuna's sharp  |
| H2 | maple-preview | vit-sci-002 | correct (pass) | confident_wrong | 0.59 | 0.59 | Japan is more densely populated than Germany. Japan has about 125 million people over about 377,000 km², givin |
| H2 | maple-preview | vit-hlt-003 | correct (pass) | confident_wrong | 0.54 | 0.54 | Yes, a second infection with a different dengue strain can be more dangerous. The immune system can become con |
| H2 | maple-preview | vit-fa-011 | correct (pass) | confident_wrong | 0.57 | 0.57 | The Allies, led by the United States, Britain, France, Russia, and later Italy, won World War I. The Central P |
| H2 | maple-preview | vit-fa-013 | correct (pass) | confident_wrong | 0.95 | 0.95 | The tallest animal in the world is the giraffe, with males reaching up to 20 feet (6 meters) at the shoulder.  |
| H2 | maple-preview | vit-fa-014 | wrong_or_incomplete_hedged (empty) | confident_wrong | 0.66 | 0.66 |  |
| H2 | maple-preview | vit-fa-015 | correct (pass) | confident_wrong | 0.81 | 0.81 | World population is projected to reach around 8.0–8.5 billion by 2026, according to United Nations estimates.  |
| H2 | maple-preview | vit-fa-017 | correct (pass) | confident_wrong | 0.54 | 0.54 | Canada is the world's second-largest country by area, known for its vast landscapes of forests, lakes, and mou |
| H2 | maple-preview | vit-fa-019 | correct (pass) | wrong_or_incomplete_hedged | 0.6 | 0.28 | The Amazon rainforest is a vast tropical rainforest covering much of the Amazon basin of South America, spanni |
| H2 | maple-preview | vit-fa-020 | correct (pass) | confident_wrong | 0.41 | 0.41 | Mount Everest is the world's highest mountain at 8,848.86 meters (29,032 feet). It straddles the border betwee |
| H2 | maple-preview | vit-fa-021 | correct (pass) | confident_wrong | 0.7 | 0.7 | Tigers are generally heavier than lions, especially males. Male lions weigh 150–250 kg, while male tigers weig |
| H2 | maple-preview | vit-fa-023 | correct (pass) | confident_wrong | 0.68 | 0.68 | India is the most populous country in the world, followed by China, the United States, Indonesia, and Pakistan |
| H2 | maple-preview | vit-fa-024 | correct (pass) | confident_wrong | 0.8 | 0.8 | The Thirty Years' War took place from 1618 to 1648. |
| H2 | maple-preview | vit-fa-025 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.54 | 0.54 | Most Western chronicles consider World War II to have started with Germany's invasion of Poland on 1 September |
| H2 | maple-preview | vit-fa-027 | correct (pass) | confident_wrong | 0.45 | 0.45 | Taiwan is an island nation with a democratic government, often referred to as the Republic of China, situated  |
