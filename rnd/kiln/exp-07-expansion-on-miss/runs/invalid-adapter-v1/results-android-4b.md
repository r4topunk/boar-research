## android-4b

| over all 54 | T2 off | T2 on |
|---|---:|---:|
| declined | 0 | 0 |
| weak | 29 | 29 |
| declined_and_weak | 0 | 0 |
| zero_sources | 11 | 10 |

| subset: 0 shown sources with T2 off (n=11) | T2 off | T2 on |
|---|---:|---:|
| declined | 0 | 0 |
| weak | 9 | 9 |
| declined_and_weak | 0 | 0 |
| zero_sources | 11 | 10 |

- T2 fired on 9 questions; found sources on 1 (`expansion:hit`), missed on 8.
- Extra latency (expansion step, `expansion:ms`): median 1688 ms, max 2175 ms; total-time delta on fired questions: median 1545 ms.
- Regressions (T2 did not fire but the answer or the sources changed): 0 

| id | T2 terms | outcome | sources (on) | declined off→on | weak off→on | precheck off→on | Jev off→on | answer on (start) |
|---|---|---|---|---|---|---|---|---|
| vit-fa-005 | rhinoceros / size_comparison / weight / height / bulk | hit | Bitcoin BIPs: BIP 180: Block size/weight fraud proof | False→False | True→True | pass→pass | correct→correct | No, rhinos are not bigger than elephants. Elephants are significantly larger in both size  |
| vit-fa-010 |  | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

T |
| vit-fa-021 | weight_comparison / big_cat / feline / carnivore | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

T |
| vit-fa-026 |  | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

F |
| vit-hum-001 |  | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

M |
| vit-hum-002 |  | miss |  | False→False | True→True | pass→pass | confident_wrong→confident_wrong | This answer is not from an offline source on this phone; check it before relying on it.

M |
| vit-hum-003 |  | miss |  | False→False | True→True | fail-missing→fail-missing | wrong_or_incomplete_hedged→correct | This answer is not from an offline source on this phone; check it before relying on it.

M |
| vit-sci-001 | further | miss |  | False→False | True→True | fail-missing→fail-missing | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

F |
| vit-sci-003 |  | miss |  | False→False | True→True | fail-missing→fail-missing | confident_wrong→confident_wrong | This answer is not from an offline source on this phone; check it before relying on it.

T |

