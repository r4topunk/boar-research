# Jev predictions `preds/v2-test.jsonl` vs hand labels (prompts sha256 3426670d8f490476…)

| Subset | n | 4-class agreement | binary (correct vs not) | CW precision | CW recall | CW F1 | grey zone (top p 0.35-0.65) | P(cw) in grey |
|---|---:|---|---|---|---|---|---|---:|
| all | 152 | 117/152 = 77% | 130/152 = 86% | 25/38 = 66% | 25/30 = 83% | 74% | 44 (29%) | 15 |
| H1 ling-3.0-tiny | 38 | 28/38 = 74% | 33/38 = 87% | 6/10 = 60% | 6/7 = 86% | 71% | 10 (26%) | 5 |
| H1 qwen2.5-1.5b | 38 | 25/38 = 66% | 29/38 = 76% | 11/17 = 65% | 11/12 = 92% | 76% | 10 (26%) | 5 |
| H1 qwen3-4b | 38 | 31/38 = 82% | 33/38 = 87% | 5/6 = 83% | 5/7 = 71% | 77% | 10 (26%) | 3 |
| H2 maple-preview | 38 | 33/38 = 87% | 35/38 = 92% | 3/5 = 60% | 3/4 = 75% | 67% | 14 (37%) | 2 |

Confusion (rows = hand label, columns = Jev), excluding app declines:

| hand \ jev | correct | confident_wrong | wrong_or_incomplete_hedged | refused |
|---|---|---|---|---|
| correct | 70 | 5 | 16 | 0 |
| confident_wrong | 0 | 25 | 5 | 0 |
| wrong_or_incomplete_hedged | 1 | 8 | 20 | 0 |
| refused | 0 | 0 | 0 | 2 |

Cost [usage detail removed] for 152 items = [usage detail removed] per million answers; latency 7.1 s of requests (47 ms per item, batches of ≤ 20). unsafe_advice: 0 rows with P ≥ 0.5.

## Disagreements (excluding app declines)

| src | model | id | hand (raw) | jev | p(jev) | p(cw) | answer (start) |
|---|---|---|---|---|---:|---:|---|
| H1 | qwen2.5-1.5b | vit-hum-002 | correct (pass) | wrong_or_incomplete_hedged | 0.57 | 0.05 | Mozi's idea of universal love emphasized equality and non-violence, viewing all life as valuable. Confucius, o |
| H1 | qwen2.5-1.5b | vit-fa-001 | correct (pass) | wrong_or_incomplete_hedged | 0.78 | 0.01 | Japan is an island nation in East Asia known for its unique and intricate culture, closeness to ancient East A |
| H1 | qwen2.5-1.5b | vit-fa-002 | correct (pass) | wrong_or_incomplete_hedged | 0.48 | 0.11 | Argentina is a large country in the southern part of South America known for its diverse landscapes from jungl |
| H1 | qwen2.5-1.5b | vit-fa-003 | correct (pass) | wrong_or_incomplete_hedged | 0.63 | 0.34 | Japan's population in 2025 is estimated to be around 126 million people. [2] |
| H1 | qwen2.5-1.5b | vit-cry-007 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.97 | 0.97 | In the context of Ethereum, "d/acc" likely stands for "deployed account," referring to an instance of a contra |
| H1 | qwen2.5-1.5b | vit-cry-009 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.73 | 0.73 | Before EIP-7251, you needed at least 32 ETH to stake. After EIP-7251, the minimum is still 32 ETH, but the max |
| H1 | qwen2.5-1.5b | vit-cry-010 | correct (pass) | wrong_or_incomplete_hedged | 0.83 | 0 | The 2016 DAO hack highlighted the importance of careful contract development and the need for continuous secur |
| H1 | qwen2.5-1.5b | vit-cry-011 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.56 | 0.56 | Terra's collapse in 2022 was due to the subsequent failure of Terraform Labs, which led to the loss of nearly  |
| H1 | qwen2.5-1.5b | vit-fa-014 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.68 | 0.04 | The populations of China and South Korea exceed Japan's. |
| H1 | qwen2.5-1.5b | vit-fa-015 | correct (pass) | wrong_or_incomplete_hedged | 0.57 | 0.13 | As of 2026, the world population is estimated to have reached 8 billion. |
| H1 | qwen2.5-1.5b | vit-fa-019 | correct (pass) | confident_wrong | 0.56 | 0.56 | The Amazon rainforest, also called the Amazon jungle, is a moist broadleaf tropical rainforest covering 7 mill |
| H1 | qwen2.5-1.5b | vit-fa-021 | correct (pass) | confident_wrong | 0.85 | 0.85 | Lions and tigers are both large cats, but tigers are typically heavier. Tigers can weigh up to 500 pounds (227 |
| H1 | qwen2.5-1.5b | vit-fa-023 | correct (pass) | confident_wrong | 0.56 | 0.56 | The most populated countries in the world are China, India, and the United States. |
| H1 | qwen3-4b | vit-fa-003 | correct (pass) | wrong_or_incomplete_hedged | 0.73 | 0.02 | Japan's population in 2025 is estimated to be around 122 million, based on trends from the National Institute  |
| H1 | qwen3-4b | vit-trv-004 | correct (pass) | confident_wrong | 0.72 | 0.72 | There is no direct walking route between Paris and Rome, as the distance is approximately 1,400 kilometers (87 |
| H1 | qwen3-4b | vit-cry-009 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.59 | 0.41 | Before EIP-7251, with a maximum effective balance of 64 ETH, staking 10,000 ETH would have required at least 1 |
| H1 | qwen3-4b | vit-cry-011 | wrong_or_incomplete_hedged (fail) | correct | 0.64 | 0.04 | Terra’s stablecoin UST collapsed in May 2022 due to a loss of confidence and massive sell-offs, causing it to  |
| H1 | qwen3-4b | vit-fa-013 | correct (pass) | wrong_or_incomplete_hedged | 0.58 | 0.01 | There is no known animal that is the tallest in the world in a universally accepted sense, as height varies by |
| H1 | qwen3-4b | vit-fa-014 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.85 | 0.01 | Japan's population does not exceed that of any country; in fact, Japan has a smaller population than most coun |
| H1 | qwen3-4b | vit-fa-022 | correct (pass) | wrong_or_incomplete_hedged | 0.51 | 0.1 | An African elephant is heavier than a white rhinoceros. Adult elephants can weigh between 4,000 and 12,000 pou |
| H1 | ling-3.0-tiny | vit-hum-002 | correct (pass) | wrong_or_incomplete_hedged | 0.61 | 0.25 | Mozi's universal love was a universal, impartial care for all people regardless of kinship or social status. M |
| H1 | ling-3.0-tiny | vit-fa-001 | correct (pass) | wrong_or_incomplete_hedged | 0.57 | 0.22 | Japan is an island nation in East Asia known for its unique culture and historical influence from China. Despi |
| H1 | ling-3.0-tiny | vit-fa-003 | correct (pass) | wrong_or_incomplete_hedged | 0.46 | 0.12 | Japan's population in 2025 is approximately 122.7 million, according to the World Population Review. This repr |
| H1 | ling-3.0-tiny | vit-trv-004 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.79 | 0.79 | The distance between Paris and Rome is roughly 1,100 kilometers, so a round trip would be around 2,200 kilomet |
| H1 | ling-3.0-tiny | vit-cry-003 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.73 | 0.73 | EIP-4444 requires node operators to prune execution history older than a consensus-layer block retention windo |
| H1 | ling-3.0-tiny | vit-cry-006 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.61 | 0.61 | Quadratic funding is a mechanism where donors contribute small amounts to multiple causes to amplify their imp |
| H1 | ling-3.0-tiny | vit-cry-007 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.95 | 0.95 | The `/acc` endpoint is a standard REST route used in web applications and APIs to retrieve or display account- |
| H1 | ling-3.0-tiny | vit-cry-010 | correct (pass) | wrong_or_incomplete_hedged | 0.81 | 0.01 | The 2016 DAO hack exposed critical vulnerabilities in smart contract design, particularly in the Ethereum Virt |
| H1 | ling-3.0-tiny | vit-fa-014 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.48 | 0.47 | China and South Korea have larger populations than Japan, with China's population around 1.4 billion and South |
| H1 | ling-3.0-tiny | vit-fa-023 | correct (pass) | wrong_or_incomplete_hedged | 0.44 | 0.36 | The most populated countries in the world are China, India, the United States, Indonesia, and Pakistan. These  |
| H2 | maple-preview | vit-hum-005 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.78 | 0.16 | Adam Smith meant the "invisible hand" as a metaphor for self-interest motivating individuals to pursue their o |
| H2 | maple-preview | vit-fa-001 | correct (pass) | wrong_or_incomplete_hedged | 0.77 | 0.03 | Japan's culture is rooted in a unique blend of East Asian influences and its own emphasis on inner balance, tr |
| H2 | maple-preview | vit-cry-007 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.89 | 0.89 | `acc` is an account variable holding an account object, typically from a blockchain or user system. The code l |
| H2 | maple-preview | vit-cry-010 | correct (pass) | wrong_or_incomplete_hedged | 0.64 | 0 | The DAO hack exposed critical security flaws in Solidity contracts, highlighting the need for thorough auditin |
| H2 | maple-preview | vit-fa-019 | correct (pass) | confident_wrong | 0.59 | 0.59 | The Amazon rainforest is a vast tropical rainforest covering much of the Amazon basin of South America, spanni |
