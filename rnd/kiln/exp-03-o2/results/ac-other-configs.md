# exp-03: O2 variant A (refuse) vs C (flag), per configuration, hand labels

| Config | Variant | n | O2 hits | pass | cw | flagged | refused | fail/empty | Δpass pp (A4 ≥ −5) | Δcw pp (A5 ≤ −5) | pass lost (McNemar p) | pass-flagged (UX cost) | Verdict |
|---|---|---:|---:|---|---|---:|---|---:|---:|---:|---|---:|---|
| P2 qwen2.5-1.5b@iphone | A | 52 | 4 | 12 → 10 | 5 → 4 | 0 | 27 → 31 | 7 | -3.8 | -1.9 | 2 (p=0.50) | 0 | A4 only: safe, gain below noise |
| P2 qwen2.5-1.5b@iphone | C | 52 | 4 | 12 → 12 | 5 → 4 | 1 | 27 → 27 | 8 | +0.0 | -1.9 | 0 (p=1.00) | 2 | A4 only: safe, gain below noise |
| H1 qwen2.5-1.5b | A | 38 | 9 | 17 → 13 | 12 → 7 | 0 | 0 → 9 | 9 | -10.5 | -13.2 | 4 (p=0.12) | 0 | FAIL A4 (pass −>5 pp) |
| H1 qwen2.5-1.5b | C | 38 | 9 | 17 → 17 | 12 → 7 | 5 | 0 → 0 | 9 | +0.0 | -13.2 | 0 (p=1.00) | 4 | PASS (A4+A5) |
| H1 ling-3.0-tiny | A | 38 | 7 | 23 → 18 | 7 → 5 | 0 | 1 → 8 | 7 | -13.2 | -5.3 | 5 (p=0.06) | 0 | FAIL A4 (pass −>5 pp) |
| H1 ling-3.0-tiny | C | 38 | 7 | 23 → 23 | 7 → 5 | 2 | 1 → 1 | 7 | +0.0 | -5.3 | 0 (p=1.00) | 5 | PASS (A4+A5) |
| H2 maple-preview | A | 38 | 8 | 25 → 20 | 4 → 2 | 0 | 0 → 8 | 8 | -13.2 | -5.3 | 5 (p=0.06) | 0 | FAIL A4 (pass −>5 pp) |
| H2 maple-preview | C | 38 | 8 | 25 → 25 | 4 → 2 | 2 | 0 → 0 | 9 | +0.0 | -5.3 | 0 (p=1.00) | 5 | PASS (A4+A5) |

## O2 hits per config (hand label → A / C outcome)

| Config | id | hand label | A | C | reference reason |
|---|---|---|---|---|---|
| P2 qwen2.5-1.5b@iphone | vit-fa-004 | cw | refused | flagged | side(s) ["Nigeria's"] not covered by any used passage |
| P2 qwen2.5-1.5b@iphone | vit-fa-006 | fail | refused | fail | no used passage is class-level for 'dinosaur' or states the superlative unqualified |
| P2 qwen2.5-1.5b@iphone | vit-fa-015 | pass | refused | pass | no used passage is about ['world'] |
| P2 qwen2.5-1.5b@iphone | vit-fa-022 | pass | refused | pass | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| H1 qwen2.5-1.5b | vit-hum-005 | cw | refused | flagged | no used passage is about ['invisible hand', 'Adam Smith', 'Wealth of Nations'] |
| H1 qwen2.5-1.5b | vit-fa-004 | cw | refused | flagged | side(s) ["Nigeria's"] not covered by any used passage |
| H1 qwen2.5-1.5b | vit-trv-004 | cw | refused | flagged | side(s) ['Paris'] not covered by any used passage |
| H1 qwen2.5-1.5b | vit-sci-002 | cw | refused | flagged | side(s) ['Germany'] not covered by any used passage |
| H1 qwen2.5-1.5b | vit-fa-013 | pass | refused | pass | no used passage is class-level for 'animal' or states the superlative unqualified |
| H1 qwen2.5-1.5b | vit-fa-014 | cw | refused | flagged | no used passage is class-level for 'countries' or states the superlative unqualified |
| H1 qwen2.5-1.5b | vit-fa-015 | pass | refused | pass | no used passage is about ['world'] |
| H1 qwen2.5-1.5b | vit-fa-022 | pass | refused | pass | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| H1 qwen2.5-1.5b | vit-fa-023 | pass | refused | pass | no used passage is class-level for 'countries' or states the superlative unqualified |
| H1 ling-3.0-tiny | vit-hum-005 | cw | refused | flagged | no used passage is about ['invisible hand', 'Adam Smith', 'Wealth of Nations'] |
| H1 ling-3.0-tiny | vit-fa-004 | pass | refused | pass | side(s) ["Nigeria's"] not covered by any used passage |
| H1 ling-3.0-tiny | vit-sci-002 | pass | refused | pass | side(s) ['Germany'] not covered by any used passage |
| H1 ling-3.0-tiny | vit-fa-013 | pass | refused | pass | no used passage is class-level for 'animal' or states the superlative unqualified |
| H1 ling-3.0-tiny | vit-fa-014 | cw | refused | flagged | no used passage is class-level for 'countries' or states the superlative unqualified |
| H1 ling-3.0-tiny | vit-fa-022 | pass | refused | pass | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| H1 ling-3.0-tiny | vit-fa-023 | pass | refused | pass | no used passage is class-level for 'countries' or states the superlative unqualified |
| H2 maple-preview | vit-hum-005 | cw | refused | flagged | no used passage is about ['invisible hand', 'Adam Smith', 'Wealth of Nations'] |
| H2 maple-preview | vit-fa-004 | pass | refused | pass | side(s) ["Nigeria's"] not covered by any used passage |
| H2 maple-preview | vit-sci-002 | pass | refused | pass | side(s) ['Germany'] not covered by any used passage |
| H2 maple-preview | vit-fa-013 | pass | refused | pass | no used passage is class-level for 'animal' or states the superlative unqualified |
| H2 maple-preview | vit-fa-014 | empty | refused | empty | no used passage is class-level for 'countries' or states the superlative unqualified |
| H2 maple-preview | vit-fa-015 | pass | refused | pass | no used passage is about ['world'] |
| H2 maple-preview | vit-fa-022 | cw | refused | flagged | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| H2 maple-preview | vit-fa-023 | pass | refused | pass | no used passage is class-level for 'countries' or states the superlative unqualified |
