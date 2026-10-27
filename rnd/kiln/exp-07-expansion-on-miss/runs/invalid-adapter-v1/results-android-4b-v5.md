## android-4b-v5

| over all 54 | T2 off | T2 on |
|---|---:|---:|
| declined | 0 | 0 |
| weak | 26 | 26 |
| declined_and_weak | 0 | 0 |
| zero_sources | 7 | 7 |

| subset: 0 shown sources with T2 off (n=7) | T2 off | T2 on |
|---|---:|---:|
| declined | 0 | 0 |
| weak | 5 | 5 |
| declined_and_weak | 0 | 0 |
| zero_sources | 7 | 7 |

- T2 fired on 5 questions; found sources on 0 (`expansion:hit`), missed on 5.
- Extra latency (expansion step, `expansion:ms`): median 1744 ms, max 2141 ms; total-time delta on fired questions: median 1504 ms.
- Regressions (T2 did not fire but the answer or the sources changed): 0 

| id | T2 terms | outcome | sources (on) | declined off→on | weak off→on | precheck off→on | Jev off→on | answer on (start) |
|---|---|---|---|---|---|---|---|---|
| vit-fa-010 |  | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

T |
| vit-hum-001 |  | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

M |
| vit-hum-003 |  | miss |  | False→False | True→True | fail-missing→fail-missing | wrong_or_incomplete_hedged→wrong_or_incomplete_hedged | This answer is not from an offline source on this phone; check it before relying on it.

M |
| vit-sci-001 | further | miss |  | False→False | True→True | fail-missing→fail-missing | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

F |
| vit-sci-003 |  | miss |  | False→False | True→True | fail-missing→fail-missing | confident_wrong→confident_wrong | This answer is not from an offline source on this phone; check it before relying on it.

T |

