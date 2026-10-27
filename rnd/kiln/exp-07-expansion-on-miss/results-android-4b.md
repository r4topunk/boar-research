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
- Extra latency (expansion step, `expansion:ms`): median 2612 ms, max 2967 ms; total-time delta on fired questions: median 2873 ms.
- Regressions (T2 did not fire but the answer or the sources changed): 0 

| id | T2 terms | outcome | sources (on) | declined off→on | weak off→on | precheck off→on | Jev off→on | answer on (start) |
|---|---|---|---|---|---|---|---|---|
| vit-fa-005 | size_comparison / weight / height / animal_species | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

N |
| vit-fa-010 | influenza / SARS-CoV-2 / measles / Ebola / mumps / rabies | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

T |
| vit-fa-021 | weight_comparison / big_cat / feline / animal_mass | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

T |
| vit-fa-026 | Russia / France / Croatia | hit | Wikivoyage: Russia; Wikivoyage: Russia; Wikivoyage: France | False→False | True→True | pass→pass | correct→correct | France won the 2018 FIFA World Cup final, defeating Croatia 4-2 after extra time. The matc |
| vit-hum-001 | non-aggression / mutual_aid / impartiality / benevolence | miss |  | False→False | True→True | pass→pass | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

M |
| vit-hum-002 | Confucianism / ren / benevolence / human_nature | miss |  | False→False | True→True | pass→pass | confident_wrong→confident_wrong | This answer is not from an offline source on this phone; check it before relying on it.

M |
| vit-hum-003 | mutual_benefit / impartiality / group_favoritism / social_harmony | miss |  | False→False | True→True | fail-missing→fail-missing | wrong_or_incomplete_hedged→wrong_or_incomplete_hedged | This answer is not from an offline source on this phone; check it before relying on it.

M |
| vit-sci-001 | airborne_pathogens / disinfection / UV_radiation / skin_safety / eye_safety | miss |  | False→False | True→True | fail-missing→fail-missing | correct→correct | This answer is not from an offline source on this phone; check it before relying on it.

F |
| vit-sci-003 | processing_speed / token_generation / prompt_processing / answer_length | miss |  | False→False | True→True | fail-missing→fail-missing | confident_wrong→confident_wrong | This answer is not from an offline source on this phone; check it before relying on it.

T |

