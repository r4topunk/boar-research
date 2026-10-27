## ios-1.5b-v5

| over all 54 | T2 off | T2 on |
|---|---:|---:|
| declined | 24 | 24 |
| weak | 24 | 24 |
| declined_and_weak | 24 | 24 |
| zero_sources | 7 | 4 |

| subset: 0 shown sources with T2 off (n=7) | T2 off | T2 on |
|---|---:|---:|
| declined | 5 | 5 |
| weak | 5 | 5 |
| declined_and_weak | 5 | 5 |
| zero_sources | 7 | 4 |

- T2 fired on 5 questions; found sources on 3 (`expansion:hit`), missed on 2.
- Extra latency (expansion step, `expansion:ms`): median 879 ms, max 1344 ms; total-time delta on fired questions: median 4287 ms.
- Regressions (T2 did not fire but the answer or the sources changed): 0 

| id | T2 terms | outcome | sources (on) | declined off→on | weak off→on | precheck off→on | Jev off→on | answer on (start) |
|---|---|---|---|---|---|---|---|---|
| vit-fa-010 | Influenza / SARS-CoV-2 / Ebola / MERS-CoV | hit | SARS-CoV-2; Ebola | True→True | True→True | refused→refused | refused→refused | The passages found don't support this answer. |
| vit-hum-001 | Mozi_advocated_for_universal_love / regardless_of_status_or_wealth | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-hum-003 | competition | hit | Competition; CAESAR Competition; Competition (biology) | True→True | True→True | refused→refused | correct→correct | The passages found don't support this answer. |
| vit-sci-001 |  | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-sci-003 | seconds | hit | Second | True→True | True→True | refused→refused | refused→refused | The passages found don't support this answer. |

