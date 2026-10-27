# exp-02 kill criterion: blind hand labels (Plumb) on the factual 38

## all 38 (n=38)

| Model | pass (95% CI) | cw | fail | refused | empty |
|---|---|---:|---:|---:|---:|
| maple-preview | 25/38 = 66% (50%–79%) | 4 | 7 | 0 | 2 |
| qwen3-4b | 26/38 = 68% (53%–81%) | 7 | 4 | 1 | 0 |
| ling-3.0-tiny | 23/38 = 61% (45%–74%) | 7 | 7 | 1 | 0 |

- Maple vs qwen3-4b: Maple-only pass 3 ['vit-fa-011', 'vit-fa-027', 'vit-hum-002']; qwen3-4b-only pass 4 ['vit-cry-003', 'vit-fa-022', 'vit-hum-005', 'vit-trv-004']; exact McNemar p = 1.00
- Maple vs ling-3.0-tiny: Maple-only pass 4 ['vit-fa-005', 'vit-fa-010', 'vit-fa-015', 'vit-fa-027']; ling-3.0-tiny-only pass 2 ['vit-cry-011', 'vit-fa-022']; exact McNemar p = 0.69
- Ling vs qwen3-4b: Ling-only 3; 4B-only 6; p = 0.51

**Kill rule (all 38):** Maple pass 66% vs 4B 68%; Maple cw 11% vs 4B 18% → **KILLED** (pass lower)

## without Maple's 2 empty answers (vit-cry-009, vit-fa-014) (n=36)

| Model | pass (95% CI) | cw | fail | refused | empty |
|---|---|---:|---:|---:|---:|
| maple-preview | 25/36 = 69% (53%–82%) | 4 | 7 | 0 | 0 |
| qwen3-4b | 26/36 = 72% (56%–84%) | 5 | 4 | 1 | 0 |
| ling-3.0-tiny | 23/36 = 64% (48%–78%) | 5 | 7 | 1 | 0 |

- Maple vs qwen3-4b: Maple-only pass 3 ['vit-fa-011', 'vit-fa-027', 'vit-hum-002']; qwen3-4b-only pass 4 ['vit-cry-003', 'vit-fa-022', 'vit-hum-005', 'vit-trv-004']; exact McNemar p = 1.00
- Maple vs ling-3.0-tiny: Maple-only pass 4 ['vit-fa-005', 'vit-fa-010', 'vit-fa-015', 'vit-fa-027']; ling-3.0-tiny-only pass 2 ['vit-cry-011', 'vit-fa-022']; exact McNemar p = 0.69
- Ling vs qwen3-4b: Ling-only 3; 4B-only 6; p = 0.51

**Kill rule (without Maple's 2 empty answers (vit-cry-009, vit-fa-014)):** Maple pass 69% vs 4B 72%; Maple cw 11% vs 4B 14% → **KILLED** (pass lower)

