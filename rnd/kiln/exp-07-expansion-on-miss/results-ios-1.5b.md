## ios-1.5b

| over all 54 | T2 off | T2 on |
|---|---:|---:|
| declined | 29 | 29 |
| weak | 29 | 29 |
| declined_and_weak | 29 | 29 |
| zero_sources | 11 | 8 |

| subset: 0 shown sources with T2 off (n=11) | T2 off | T2 on |
|---|---:|---:|
| declined | 9 | 9 |
| weak | 9 | 9 |
| declined_and_weak | 9 | 9 |
| zero_sources | 11 | 8 |

- T2 fired on 9 questions; found sources on 3 (`expansion:hit`), missed on 6.
- Extra latency (expansion step, `expansion:ms`): median 862 ms, max 1303 ms; total-time delta on fired questions: median 1107 ms.
- Regressions (T2 did not fire but the answer or the sources changed): 0 

| id | T2 terms | outcome | sources (on) | declined off→on | weak off→on | precheck off→on | Jev off→on | answer on (start) |
|---|---|---|---|---|---|---|---|---|
| vit-fa-005 | Yes / rhinos_are_larger_than_elephants | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-fa-010 | Influenza / SARS-CoV-2 / Ebola / MERS-CoV | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-fa-021 | weight / comparison | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-fa-026 | France | hit | Wikivoyage: France; Wikivoyage: France; Wikivoyage: France | True→True | True→True | refused/ok→refused/ok | refused→refused | The passages found don't support this answer. |
| vit-hum-001 | Mozi_advocated_for_universal_love / regardless_of_status_or_wealth | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-hum-002 |  | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-hum-003 | competition | hit | CAESAR Competition; NIST hash function competition; NIST hash function competition | True→True | True→True | refused→refused | refused→refused | The passages found don't support this answer. |
| vit-sci-001 |  | miss |  | True→True | True→True | refused→refused | refused→refused | I didn't find this in this phone's library. |
| vit-sci-003 | seconds | hit | Wikivoyage: Second homes | True→True | True→True | refused→refused | refused→refused | The passages found don't support this answer. |

