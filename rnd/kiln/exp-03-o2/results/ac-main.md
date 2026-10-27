# exp-03: O2 variant A (refuse) vs C (flag), per configuration, hand labels

| Config | Variant | n | O2 hits | pass | cw | flagged | refused | fail/empty | Δpass pp (A4 ≥ −5) | Δcw pp (A5 ≤ −5) | pass lost (McNemar p) | pass-flagged (UX cost) | Verdict |
|---|---|---:|---:|---|---|---:|---|---:|---:|---:|---|---:|---|
| H1 qwen3-4b | A | 38 | 9 | 26 → 18 | 7 → 6 | 0 | 1 → 10 | 4 | -21.1 | -2.6 | 8 (p=0.01) | 0 | FAIL A4 (pass −>5 pp) |
| H1 qwen3-4b | C | 38 | 9 | 26 → 26 | 7 → 6 | 1 | 1 → 1 | 4 | +0.0 | -2.6 | 0 (p=1.00) | 8 | A4 only: safe, gain below noise |
| P3 qwen2.5-1.5b@iphone | A | 52 | 7 | 17 → 16 | 8 → 2 | 0 | 18 → 25 | 9 | -1.9 | -11.5 | 1 (p=1.00) | 0 | PASS (A4+A5) |
| P3 qwen2.5-1.5b@iphone | C | 52 | 7 | 17 → 17 | 8 → 2 | 6 | 18 → 18 | 9 | +0.0 | -11.5 | 0 (p=1.00) | 1 | PASS (A4+A5) |

## O2 hits per config (hand label → A / C outcome)

| Config | id | hand label | A | C | reference reason |
|---|---|---|---|---|---|
| H1 qwen3-4b | vit-hum-005 | pass | refused | pass | no used passage is about ['invisible hand', 'Adam Smith', 'Wealth of Nations'] |
| H1 qwen3-4b | vit-fa-004 | pass | refused | pass | side(s) ["Nigeria's"] not covered by any used passage |
| H1 qwen3-4b | vit-trv-004 | pass | refused | pass | side(s) ['Paris'] not covered by any used passage |
| H1 qwen3-4b | vit-sci-002 | pass | refused | pass | side(s) ['Germany'] not covered by any used passage |
| H1 qwen3-4b | vit-fa-013 | pass | refused | pass | no used passage is class-level for 'animal' or states the superlative unqualified |
| H1 qwen3-4b | vit-fa-014 | cw | refused | flagged | no used passage is class-level for 'countries' or states the superlative unqualified |
| H1 qwen3-4b | vit-fa-015 | pass | refused | pass | no used passage is about ['world'] |
| H1 qwen3-4b | vit-fa-022 | pass | refused | pass | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| H1 qwen3-4b | vit-fa-023 | pass | refused | pass | no used passage is class-level for 'countries' or states the superlative unqualified |
| P3 qwen2.5-1.5b@iphone | vit-fa-003 | cw | refused | flagged | no used passage is about ["Japan's"] |
| P3 qwen2.5-1.5b@iphone | vit-fa-004 | cw | refused | flagged | side(s) ["Japan's", "Nigeria's"] not covered by any used passage |
| P3 qwen2.5-1.5b@iphone | vit-fa-006 | cw | refused | flagged | no used passage is class-level for 'dinosaur' or states the superlative unqualified |
| P3 qwen2.5-1.5b@iphone | vit-fa-013 | cw | refused | flagged | no used passage is class-level for 'animal' or states the superlative unqualified |
| P3 qwen2.5-1.5b@iphone | vit-fa-014 | cw | refused | flagged | no used passage is class-level for 'countries' or states the superlative unqualified |
| P3 qwen2.5-1.5b@iphone | vit-fa-022 | pass | refused | pass | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| P3 qwen2.5-1.5b@iphone | vit-fa-023 | cw | refused | flagged | no used passage is class-level for 'countries' or states the superlative unqualified |
