# V-exact acceptance run: selfcheck

prompt D4, seeds 42, 43, judge Haiku 5.5-low (judge.v1, N = 4, both orders) on the 5 judged items; venues by OSM gold on the 6 venue items.

**Judged ratio (pooled, 2 seeds): 0.475** (item-bootstrap 95% CI 0.280-0.786, n = 5 items: wide)

| item | s42 | s43 | pooled |
|---|---|---|---|
| vx-001 | 0.333 | 0.333 | 0.333 |
| vx-002 | 0.433 | 0.467 | 0.450 |
| vit-hum-001 | 0.464 | 0.483 | 0.474 |
| vit-hum-004 | 0.200 | 0.200 | 0.200 |
| vit-trv-004 | 1.091 | 1.043 | 1.067 |

| seed | ratio | venues pass | GPS answers name the city | model-answered (D4-rewritten) | errored | judged rows reused |
|---|---|---|---|---|---|---|
| 42 | 0.471 | 6/6 | 3/3 | 4 (4) | 0 | 5 |
| 43 | 0.479 | 6/6 | 3/3 | 4 (4) | 0 | 5 |

Baseline `baseline` 0.475; delta **+0.000** (paired item-bootstrap +0.000..+0.000).
A1 (delta >= -0.03): PASS; A2 (venues 6/6 each seed): PASS; A3 own gate: PASS; valid run: True.
**ACCEPT**
