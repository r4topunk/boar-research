## ios-1.5b

| over all 54 | T2 off | T2 on |
|---|---:|---:|
| declined | 29 | 29 |
| weak | 29 | 29 |
| declined_and_weak | 29 | 29 |
| zero_sources | 11 | 11 |

| subset: 0 shown sources with T2 off (n=11) | T2 off | T2 on |
|---|---:|---:|
| declined | 9 | 9 |
| weak | 9 | 9 |
| declined_and_weak | 9 | 9 |
| zero_sources | 11 | 11 |

- T2 fired on 9 questions; found sources on 0 (`expansion:hit`), missed on 9.
- Extra latency (expansion step, `expansion:ms`): median 1094 ms, max 1504 ms; total-time delta on fired questions: median 1065 ms.
- Regressions (T2 did not fire but the answer or the sources changed): 0 

| id | T2 terms | outcome | sources (on) | declined off→on | weak off→on | precheck off→on | Jev off→on | answer on (start) |
|---|---|---|---|---|---|---|---|---|
| vit-fa-005 | <4_to_6_search_terms> | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-fa-010 | or_the_basic_reproduction_number | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-fa-021 | Lions_are_heavier_than_tigers | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-fa-026 | Giraffe | miss |  | True→True | True→True | refused/ok→refused/ok | refused→refused | I didn't find this in this phone's library. |
| vit-hum-001 | Mozi_advocated_for_universal_love / regardless_of_their_status_or_background | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-hum-002 | <4_to_6_search_terms> | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-hum-003 | <explain> | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-sci-001 | to_6_search_terms: | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-sci-003 | tokens/sec_generation / tokens/sec_processing / tokens_total / seconds_until_answer_is_finished | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |

