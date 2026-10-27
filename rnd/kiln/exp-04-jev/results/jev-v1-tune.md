# Jev predictions `preds/v1-tune.jsonl` vs hand labels (prompts sha256 85fa9fcbea68350a…)

| Subset | n | 4-class agreement | binary (correct vs not) | CW precision | CW recall | CW F1 | grey zone (top p 0.35-0.65) | P(cw) in grey |
|---|---:|---|---|---|---|---|---|---:|
| all | 104 | 89/104 = 86% | 95/104 = 91% | 13/22 = 59% | 13/13 = 100% | 74% | 14 (13%) | 4 |
| excluding app fixed-message declines | 59 | 45/59 = 76% | 51/59 = 86% | 13/22 = 59% | 13/13 = 100% | 74% | 12 (20%) | 4 |
| P2 qwen2.5-1.5b@iphone | 25 | 19/25 = 76% | 21/25 = 84% | 5/9 = 56% | 5/5 = 100% | 71% | 6 (24%) | 3 |
| P3 qwen2.5-1.5b@iphone | 34 | 26/34 = 76% | 30/34 = 88% | 8/13 = 62% | 8/8 = 100% | 76% | 6 (18%) | 1 |

Confusion (rows = hand label, columns = Jev), excluding app declines:

| hand \ jev | correct | confident_wrong | wrong_or_incomplete_hedged | refused |
|---|---|---|---|---|
| correct | 23 | 3 | 3 | 0 |
| confident_wrong | 0 | 13 | 0 | 0 |
| wrong_or_incomplete_hedged | 2 | 6 | 9 | 0 |
| refused | 0 | 0 | 0 | 0 |

Cost [usage detail removed] for 104 items = [usage detail removed] per million answers; latency 4.6 s of requests (44 ms per item, batches of ≤ 20). unsafe_advice: 1 rows with P ≥ 0.5.

## Disagreements (excluding app declines)

| src | model | id | hand (raw) | jev | p(jev) | p(cw) | answer (start) |
|---|---|---|---|---|---:|---:|---|
| P2 | qwen2.5-1.5b@iphone | vit-fa-002 | correct (pass) | wrong_or_incomplete_hedged | 0.5 | 0.06 | Argentina is a large country in South America known for its diverse landscapes including jungles, grass plains |
| P2 | qwen2.5-1.5b@iphone | vit-cry-001 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.71 | 0.71 | If a quantum computer breaks ECDSA, Ethereum would protect users' funds by migrating to a quantum-resistant ke |
| P2 | qwen2.5-1.5b@iphone | vit-cry-003 | wrong_or_incomplete_hedged (fail) | correct | 0.75 | 0.07 | EIP-4444 history expiry change saves disk space for Ethereum node operators by pruning historical data older t |
| P2 | qwen2.5-1.5b@iphone | vit-cry-008 | correct (pass) | confident_wrong | 0.45 | 0.45 | Glamsterdam is an L1 scaling solution on Ethereum that enshrines the Proposer-Builder Separation (ePBS) featur |
| P2 | qwen2.5-1.5b@iphone | vit-cry-011 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.36 | 0.36 | Terra's stablecoin UST lost its peg with the US dollar when Terraform Labs collapsed due to a technical failur |
| P2 | qwen2.5-1.5b@iphone | vit-fa-019 | correct (pass) | confident_wrong | 0.96 | 0.96 | The Amazon rainforest, also called the Amazon jungle, is a vast, lush tropical rainforest covering 7 million k |
| P3 | qwen2.5-1.5b@iphone | vit-fa-001 | correct (pass) | wrong_or_incomplete_hedged | 0.68 | 0.02 | Japan is an island nation in East Asia known for its intricate culture influenced by ancient Asian traditions  |
| P3 | qwen2.5-1.5b@iphone | vit-trv-003 | correct (pass) | wrong_or_incomplete_hedged | 0.49 | 0.33 | To get from Chiang Mai to Pai, take Rte 1095, which connects the two cities [1]. The drive is approximately 11 |
| P3 | qwen2.5-1.5b@iphone | vit-cry-001 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.94 | 0.94 | Ethereum protects user funds by offering signature agility through account abstraction [5]. This means users c |
| P3 | qwen2.5-1.5b@iphone | vit-cry-004 | wrong_or_incomplete_hedged (fail) | correct | 0.72 | 0.04 | PeerDAS is a networking protocol that allows nodes to perform data availability sampling (DAS) to ensure that  |
| P3 | qwen2.5-1.5b@iphone | vit-cry-011 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.69 | 0.69 | In 2022, Terra's collapse was due to the failure of Terraform Labs, which resulted in the loss of nearly [usage detail removed] b |
| P3 | qwen2.5-1.5b@iphone | vit-fa-016 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.81 | 0.81 | Canada has a population of about 38 million people. [1] |
| P3 | qwen2.5-1.5b@iphone | vit-fa-019 | correct (pass) | confident_wrong | 0.97 | 0.97 | The Amazon rainforest, also known as the Amazon jungle, is a vast, moist, broadleaf tropical rainforest that c |
| P3 | qwen2.5-1.5b@iphone | vit-fa-027 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.81 | 0.81 | Taiwan is an island in East Asia, part of the Republic of China (ROC) [4]. It was under Japanese rule from 189 |
