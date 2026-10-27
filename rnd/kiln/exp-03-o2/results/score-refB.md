# O2 variant: Lantern reference, variant B

| Group | n | flagged | cw→refused | pass→refused (new false refusal) | fail→refused | pass before → after | cw before → after | refused before → after | Δpass pp | Δcw pp | McNemar p (pass) | ±5 pp |
|---|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---|
| H1 ling-3.0-tiny | 38 | 8 | 2 | 5 | 1 | 23 → 18 | 7 → 5 | 1 → 9 | -13.2 | -5.3 | 0.06 | REJECT (pass −>5 pp) |
| H1 qwen2.5-1.5b | 38 | 9 | 5 | 4 | 0 | 17 → 13 | 12 → 7 | 0 → 9 | -10.5 | -13.2 | 0.12 | REJECT (pass −>5 pp) |
| H1 qwen3-4b | 38 | 9 | 1 | 8 | 0 | 26 → 18 | 7 → 6 | 1 → 10 | -21.1 | -2.6 | 0.01 | REJECT (pass −>5 pp) |
| H2 maple-preview | 38 | 9 | 2 | 5 | 2 | 25 → 20 | 4 → 2 | 0 → 9 | -13.2 | -5.3 | 0.06 | REJECT (pass −>5 pp) |
| P2 qwen2.5-1.5b@iphone | 52 | 4 | 1 | 2 | 1 | 12 → 10 | 5 → 4 | 27 → 31 | -3.8 | -1.9 | 0.50 | keep |
| P3 qwen2.5-1.5b@iphone | 52 | 7 | 6 | 1 | 0 | 17 → 16 | 8 → 2 | 18 → 25 | -1.9 | -11.5 | 1.00 | keep |
| **all groups** | 256 | 46 | **17** | **25** | 4 | 120 → 95 | 43 → 26 | 47 → 93 | -9.8 | -6.6 | 0.00 | REJECT |

Flag precision for cw (cw among flagged non-declined answers): 17/46 = 37%. Recall of cw: 17/43 = 40%. Pass answers lost: 25/120 = 21%.

## Flagged answers

| src | model | id | hand label | why |
|---|---|---|---|---|
| H1 | ling-3.0-tiny | vit-hum-005 | cw | no used passage is about ['invisible hand', 'Adam Smith', 'Wealth of Nations'] |
| H1 | ling-3.0-tiny | vit-fa-004 | pass | side(s) ["Nigeria's"] not covered by any used passage |
| H1 | ling-3.0-tiny | vit-trv-004 | fail | side(s) ['Paris'] not covered by any used passage |
| H1 | ling-3.0-tiny | vit-sci-002 | pass | side(s) ['Germany'] not covered by any used passage |
| H1 | ling-3.0-tiny | vit-fa-013 | pass | no used passage is class-level for 'animal' or states the superlative unqualified |
| H1 | ling-3.0-tiny | vit-fa-014 | cw | no used passage is class-level for 'countries' or states the superlative unqualified |
| H1 | ling-3.0-tiny | vit-fa-022 | pass | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| H1 | ling-3.0-tiny | vit-fa-023 | pass | no used passage is class-level for 'countries' or states the superlative unqualified |
| H1 | qwen2.5-1.5b | vit-hum-005 | cw | no used passage is about ['invisible hand', 'Adam Smith', 'Wealth of Nations'] |
| H1 | qwen2.5-1.5b | vit-fa-004 | cw | side(s) ["Nigeria's"] not covered by any used passage |
| H1 | qwen2.5-1.5b | vit-trv-004 | cw | side(s) ['Paris'] not covered by any used passage |
| H1 | qwen2.5-1.5b | vit-sci-002 | cw | side(s) ['Germany'] not covered by any used passage |
| H1 | qwen2.5-1.5b | vit-fa-013 | pass | no used passage is class-level for 'animal' or states the superlative unqualified |
| H1 | qwen2.5-1.5b | vit-fa-014 | cw | no used passage is class-level for 'countries' or states the superlative unqualified |
| H1 | qwen2.5-1.5b | vit-fa-015 | pass | no used passage is about ['world'] |
| H1 | qwen2.5-1.5b | vit-fa-022 | pass | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| H1 | qwen2.5-1.5b | vit-fa-023 | pass | no used passage is class-level for 'countries' or states the superlative unqualified |
| H1 | qwen3-4b | vit-hum-005 | pass | no used passage is about ['invisible hand', 'Adam Smith', 'Wealth of Nations'] |
| H1 | qwen3-4b | vit-fa-004 | pass | side(s) ["Nigeria's"] not covered by any used passage |
| H1 | qwen3-4b | vit-trv-004 | pass | side(s) ['Paris'] not covered by any used passage |
| H1 | qwen3-4b | vit-sci-002 | pass | side(s) ['Germany'] not covered by any used passage |
| H1 | qwen3-4b | vit-fa-013 | pass | no used passage is class-level for 'animal' or states the superlative unqualified |
| H1 | qwen3-4b | vit-fa-014 | cw | no used passage is class-level for 'countries' or states the superlative unqualified |
| H1 | qwen3-4b | vit-fa-015 | pass | no used passage is about ['world'] |
| H1 | qwen3-4b | vit-fa-022 | pass | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| H1 | qwen3-4b | vit-fa-023 | pass | no used passage is class-level for 'countries' or states the superlative unqualified |
| H2 | maple-preview | vit-hum-005 | cw | no used passage is about ['invisible hand', 'Adam Smith', 'Wealth of Nations'] |
| H2 | maple-preview | vit-fa-004 | pass | side(s) ["Nigeria's"] not covered by any used passage |
| H2 | maple-preview | vit-trv-004 | fail | side(s) ['Paris'] not covered by any used passage |
| H2 | maple-preview | vit-sci-002 | pass | side(s) ['Germany'] not covered by any used passage |
| H2 | maple-preview | vit-fa-013 | pass | no used passage is class-level for 'animal' or states the superlative unqualified |
| H2 | maple-preview | vit-fa-014 | empty | no used passage is class-level for 'countries' or states the superlative unqualified |
| H2 | maple-preview | vit-fa-015 | pass | no used passage is about ['world'] |
| H2 | maple-preview | vit-fa-022 | cw | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| H2 | maple-preview | vit-fa-023 | pass | no used passage is class-level for 'countries' or states the superlative unqualified |
| P2 | qwen2.5-1.5b@iphone | vit-fa-004 | cw | side(s) ["Nigeria's"] not covered by any used passage |
| P2 | qwen2.5-1.5b@iphone | vit-fa-006 | fail | no used passage is class-level for 'dinosaur' or states the superlative unqualified |
| P2 | qwen2.5-1.5b@iphone | vit-fa-015 | pass | no used passage is about ['world'] |
| P2 | qwen2.5-1.5b@iphone | vit-fa-022 | pass | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| P3 | qwen2.5-1.5b@iphone | vit-fa-003 | cw | no used passage is about ["Japan's"] |
| P3 | qwen2.5-1.5b@iphone | vit-fa-004 | cw | side(s) ["Japan's", "Nigeria's"] not covered by any used passage |
| P3 | qwen2.5-1.5b@iphone | vit-fa-006 | cw | no used passage is class-level for 'dinosaur' or states the superlative unqualified |
| P3 | qwen2.5-1.5b@iphone | vit-fa-013 | cw | no used passage is class-level for 'animal' or states the superlative unqualified |
| P3 | qwen2.5-1.5b@iphone | vit-fa-014 | cw | no used passage is class-level for 'countries' or states the superlative unqualified |
| P3 | qwen2.5-1.5b@iphone | vit-fa-022 | pass | side(s) ['african elephant', 'white rhinoceros'] not covered by any used passage |
| P3 | qwen2.5-1.5b@iphone | vit-fa-023 | cw | no used passage is class-level for 'countries' or states the superlative unqualified |
