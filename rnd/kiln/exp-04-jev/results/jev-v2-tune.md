# Jev predictions `preds/v2-tune.jsonl` vs hand labels (prompts sha256 3426670d8f490476…)

| Subset | n | 4-class agreement | binary (correct vs not) | CW precision | CW recall | CW F1 | grey zone (top p 0.35-0.65) | P(cw) in grey |
|---|---:|---|---|---|---|---|---|---:|
| all | 104 | 92/104 = 88% | 96/104 = 92% | 12/18 = 67% | 12/13 = 92% | 77% | 19 (18%) | 6 |
| excluding app fixed-message declines | 59 | 48/59 = 81% | 52/59 = 88% | 12/18 = 67% | 12/13 = 92% | 77% | 15 (25%) | 6 |
| P2 qwen2.5-1.5b@iphone | 25 | 22/25 = 88% | 23/25 = 92% | 4/6 = 67% | 4/5 = 80% | 73% | 6 (24%) | 2 |
| P3 qwen2.5-1.5b@iphone | 34 | 26/34 = 76% | 29/34 = 85% | 8/12 = 67% | 8/8 = 100% | 80% | 9 (26%) | 4 |

Confusion (rows = hand label, columns = Jev), excluding app declines:

| hand \ jev | correct | confident_wrong | wrong_or_incomplete_hedged | refused |
|---|---|---|---|---|
| correct | 23 | 3 | 3 | 0 |
| confident_wrong | 0 | 12 | 1 | 0 |
| wrong_or_incomplete_hedged | 1 | 3 | 13 | 0 |
| refused | 0 | 0 | 0 | 0 |

Cost [usage detail removed] for 104 items = [usage detail removed] per million answers; latency 4.8 s of requests (46 ms per item, batches of ≤ 20). unsafe_advice: 1 rows with P ≥ 0.5.

## Disagreements (excluding app declines)

| src | model | id | hand (raw) | jev | p(jev) | p(cw) | answer (start) |
|---|---|---|---|---|---:|---:|---|
| P2 | qwen2.5-1.5b@iphone | vit-fa-001 | confident_wrong (cw) | wrong_or_incomplete_hedged | 0.5 | 0.45 | Japan is an island nation known for its unique culture that has developed from its close ties with ancient Eas |
| P2 | qwen2.5-1.5b@iphone | vit-cry-008 | correct (pass) | confident_wrong | 0.67 | 0.67 | Glamsterdam is an L1 scaling solution on Ethereum that enshrines the Proposer-Builder Separation (ePBS) featur |
| P2 | qwen2.5-1.5b@iphone | vit-fa-019 | correct (pass) | confident_wrong | 0.82 | 0.82 | The Amazon rainforest, also called the Amazon jungle, is a vast, lush tropical rainforest covering 7 million k |
| P3 | qwen2.5-1.5b@iphone | vit-fa-001 | correct (pass) | wrong_or_incomplete_hedged | 0.7 | 0 | Japan is an island nation in East Asia known for its intricate culture influenced by ancient Asian traditions  |
| P3 | qwen2.5-1.5b@iphone | vit-trv-003 | correct (pass) | wrong_or_incomplete_hedged | 0.72 | 0.16 | To get from Chiang Mai to Pai, take Rte 1095, which connects the two cities [1]. The drive is approximately 11 |
| P3 | qwen2.5-1.5b@iphone | vit-cry-001 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.68 | 0.68 | Ethereum protects user funds by offering signature agility through account abstraction [5]. This means users c |
| P3 | qwen2.5-1.5b@iphone | vit-cry-004 | wrong_or_incomplete_hedged (fail) | correct | 0.55 | 0.02 | PeerDAS is a networking protocol that allows nodes to perform data availability sampling (DAS) to ensure that  |
| P3 | qwen2.5-1.5b@iphone | vit-cry-008 | correct (pass) | wrong_or_incomplete_hedged | 0.41 | 0.25 | Glamsterdam is an L1 scaling solution for Ethereum that includes the headline feature ePBS, which separates th |
| P3 | qwen2.5-1.5b@iphone | vit-cry-011 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.61 | 0.61 | In 2022, Terra's collapse was due to the failure of Terraform Labs, which resulted in the loss of nearly [usage detail removed] b |
| P3 | qwen2.5-1.5b@iphone | vit-fa-019 | correct (pass) | confident_wrong | 0.82 | 0.82 | The Amazon rainforest, also known as the Amazon jungle, is a vast, moist, broadleaf tropical rainforest that c |
| P3 | qwen2.5-1.5b@iphone | vit-fa-027 | wrong_or_incomplete_hedged (fail) | confident_wrong | 0.81 | 0.81 | Taiwan is an island in East Asia, part of the Republic of China (ROC) [4]. It was under Japanese rule from 189 |
