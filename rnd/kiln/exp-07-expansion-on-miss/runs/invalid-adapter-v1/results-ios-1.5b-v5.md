## ios-1.5b-v5

| over all 54 | T2 off | T2 on |
|---|---:|---:|
| declined | 24 | 24 |
| weak | 24 | 24 |
| declined_and_weak | 24 | 24 |
| zero_sources | 7 | 7 |

| subset: 0 shown sources with T2 off (n=7) | T2 off | T2 on |
|---|---:|---:|
| declined | 5 | 5 |
| weak | 5 | 5 |
| declined_and_weak | 5 | 5 |
| zero_sources | 7 | 7 |

- T2 fired on 5 questions; found sources on 0 (`expansion:hit`), missed on 5.
- Extra latency (expansion step, `expansion:ms`): median 1437 ms, max 1861 ms; total-time delta on fired questions: median 1373 ms.
- Regressions (T2 did not fire but the answer or the sources changed): 0 

| id | T2 terms | outcome | sources (on) | declined off→on | weak off→on | precheck off→on | Jev off→on | answer on (start) |
|---|---|---|---|---|---|---|---|---|
| vit-fa-010 | or_the_basic_reproduction_number | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-hum-001 | Mozi_advocated_for_universal_love / regardless_of_their_status_or_background | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-hum-003 | <explain> | miss |  | True→True | True→True | refused→refused | correct→correct | I didn't find this in this phone's library. |
| vit-sci-001 | to_6_search_terms: | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-sci-003 | tokens/sec_generation / tokens/sec_processing / tokens_total / seconds_until_answer_is_finished | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |

