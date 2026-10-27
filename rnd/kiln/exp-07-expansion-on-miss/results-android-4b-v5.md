## android-4b-v5

| over all 54 | T2 off | T2 on |
|---|---:|---:|
| declined | 0 | 0 |
| weak | 26 | 26 |
| declined_and_weak | 0 | 0 |
| zero_sources | 7 | 5 |

| subset: 0 shown sources with T2 off (n=7) | T2 off | T2 on |
|---|---:|---:|
| declined | 0 | 0 |
| weak | 5 | 5 |
| declined_and_weak | 0 | 0 |
| zero_sources | 7 | 5 |

- T2 fired on 5 questions; found sources on 2 (`expansion:hit`), missed on 3.
- Extra latency (expansion step, `expansion:ms`): median 2712 ms, max 3138 ms; total-time delta on fired questions: median 2593 ms.
- Regressions (T2 did not fire but the answer or the sources changed): 0 

| id | T2 terms | outcome | sources (on) | declined off→on | weak off→on | precheck off→on | Jev off→on | answer on (start) |
|---|---|---|---|---|---|---|---|---|
| vit-fa-010 | influenza / SARS-CoV-2 / measles / Ebola / mumps / rabies | hit | Rabies; Ebola; Measles | False→False | True→True | pass→pass | correct→correct | The viruses with the highest R0 include measles, which has an R0 of around 12–18, making i |
| vit-hum-001 | non-aggression / mutual_aid / impartiality / benevolence | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

M |
| vit-hum-003 | mutual_benefit / impartiality / group_favoritism / social_harmony | hit | Impartiality | False→False | True→True | fail-missing→fail-missing | wrong_or_incomplete_hedged→correct | Mozi would argue that universal love is not self-defeating because it promotes mutual bene |
| vit-sci-001 | airborne_pathogens / disinfection / UV_radiation / skin_safety / eye_safety | miss |  | False→False | True→True | fail-missing→fail-missing | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

F |
| vit-sci-003 | processing_speed / token_generation / prompt_processing / answer_length | miss |  | False→False | True→True | fail-missing→fail-missing | confident_wrong→confident_wrong | This answer is not from an offline source on this phone; check it before relying on it.

T |

