# Chatline arm: criterion-7 hand read (4B, seeds 42 + 43)

**TL;DR**: criterion 7 **FAILs**. 16 items are worse in both seeds (the FAIL threshold is any 1), and 9 items are worse in one seed only (the threshold is 3). Totals: s42 is 11 better / 29 same / 20 worse, and s43 is 7 better / 32 same / 21 worse. The cause is almost entirely the About-BOAR facts. On greetings, thanks and goodbyes the 4B model recites the About text as an ad and usually drops the offer of help. The language line itself works: no pair moved from the right language to the wrong one. The About facts helped only on real meta questions (10 better, 2 worse). This read does not change the verdict, which is already KILL by other criteria; it is here for learning.

- Source: `changed_answers.txt` (60 items × s42/s43, Android 4B). I read nothing else: no `blind/`, no `rnd/veil/`, no engine runs.
- Reader: Compass hand read (Claude, Opus), 2026-10-03.

## Judging rules (fixed before tallying)
- **A**: The reference answered in the wrong language, and the arm answered in the right language but recited the About blurb → `same`, because the language fix and the unprompted ad cancel out. Two exceptions: `better` when the arm also fixes a second failure of the reference (for example cs-003, where the reference misread the elongated greeting), and `worse` when the arm doesn't answer the user's turn at all (a bare blurb, as in cs-009 s42 and v2-057).
- **B**: The reference answered in the wrong language, and the arm answered in the right language with no blurb or only a brief mention → `better`.
- **C**: The reference answered in the right language, and the arm added the About blurb → `worse` (worse still when it also drops the help offer or the "de nada"). A brief mention worked into an answer that still offers help → `same`.
- **D**: Meta and follow-up questions are judged on content against the `expected` line.

## Criterion-7 verdict
| bucket | items | rule | result |
|---|---|---|---|
| worse in both seeds | **16**: cs-004, cs-016, cs-018, cs-019, cs-037, cs-064, v1-001, v1-003, v1-007, v1-019, v1-027, v2-003, v2-004, v2-016, v2-018, v2-057 | ≥1 → FAIL | **FAIL** |
| worse in one seed only | **9**: cs-008, cs-009, cs-017, cs-031, v1-008, v1-018, v1-020, v2-005, v2-006 | ≥3 → FAIL | **FAIL** |

| seed | better | same | worse |
|---|---|---|---|
| s42 | 11 | 29 | 20 |
| s43 | 7 | 32 | 21 |

## Table
Verdicts are ARM compared with REF, judged against the item's `expected` line. Tags follow each verdict.

| id | lang | kind | s42 | s43 |
|---|---|---|---|---|
| cs-001 | pt | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| cs-002 | pt | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| cs-003 | pt | greeting | **better** · lang_fixed, about_unprompted, other:reads_elongation | **better** · lang_fixed, about_unprompted, other:reads_elongation |
| cs-004 | pt | greeting | **worse** · about_unprompted, content_lost | **worse** · about_unprompted, content_lost |
| cs-005 | pt | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| cs-006 | pt | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| cs-008 | pt | greeting | **worse** · about_unprompted | same · lang_fixed, about_unprompted |
| cs-009 | pt | greeting | **worse** · lang_fixed, about_unprompted, content_lost | same · lang_fixed, about_unprompted |
| cs-016 | es | greeting | **worse** · about_unprompted | **worse** · about_unprompted |
| cs-017 | es | greeting | same · about_unprompted | **worse** · about_unprompted, content_lost |
| cs-018 | es | greeting | **worse** · about_unprompted, content_lost | **worse** · about_unprompted, content_lost |
| cs-019 | es | greeting | **worse** · about_unprompted, other:wrong_word_corrige | **worse** · about_unprompted |
| cs-020 | es | greeting | same · other:no_line | same · other:no_line |
| cs-021 | pt | meta | **better** · about_answered_meta | same · about_answered_meta |
| cs-022 | pt | meta | same · about_answered_meta, content_lost | same · about_answered_meta |
| cs-023 | pt | meta | **better** · about_answered_meta, other:ref_garbled | **better** · about_answered_meta, other:ref_garbled |
| cs-027 | es | meta | same · about_answered_meta | same · about_answered_meta |
| cs-028 | es | meta | same · about_answered_meta | same · about_answered_meta |
| cs-031 | pt | followup | same · other:noise | **worse** · other:nonsense_phrase |
| cs-037 | en | followup | **worse** · about_unprompted, other:about_leaks_into_translation | **worse** · about_unprompted, false_claim |
| cs-041 | es | followup | **better** · lang_fixed | **better** · lang_fixed |
| cs-064 | es | ambiguous | **worse** · about_unprompted, content_lost, other:wrong_word_corrige | **worse** · about_unprompted, content_lost |
| v1-001 | pt | greeting | **worse** · about_unprompted | **worse** · about_unprompted, content_lost |
| v1-002 | pt | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| v1-003 | pt | greeting | **worse** · about_unprompted, content_lost | **worse** · about_unprompted, content_lost |
| v1-004 | pt | greeting | same · about_unprompted, other:ref_odd | same · about_unprompted, other:ref_odd |
| v1-006 | pt | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| v1-007 | pt | greeting | **worse** · about_unprompted | **worse** · about_unprompted |
| v1-008 | pt | greeting | **worse** · about_unprompted | same · lang_fixed, about_unprompted |
| v1-016 | es | greeting | **better** · lang_fixed, other:mild_about | same · other:mild_about |
| v1-017 | es | greeting | same · other:mild_about | same · other:mild_about |
| v1-018 | es | greeting | same · lang_fixed, about_unprompted | **worse** · about_unprompted |
| v1-019 | es | greeting | **worse** · about_unprompted | **worse** · about_unprompted |
| v1-020 | es | greeting | **worse** · about_unprompted | same · other:no_line |
| v1-021 | pt | meta | **better** · about_answered_meta, other:typo_enviato | same · about_answered_meta |
| v1-023 | pt | meta | **better** · about_answered_meta | **better** · about_answered_meta |
| v1-027 | es | meta | **worse** · about_unprompted | **worse** · about_unprompted |
| v1-028 | es | meta | same · about_answered_meta, content_lost | same · about_answered_meta, content_lost |
| v1-030 | pt | followup | **better** · other:clearer | same · other:noise |
| v1-032 | pt | followup | same · other:noise | same · other:noise |
| v1-036 | en | followup | same · other:noise | same · other:noise |
| v1-055 | es | research | **better** · lang_fixed, other:both_factually_wrong | **better** · lang_fixed, other:both_factually_wrong |
| v2-001 | pt | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| v2-002 | pt | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| v2-003 | pt | greeting | **worse** · about_unprompted, content_lost, other:cjk_glitch | **worse** · about_unprompted, content_lost |
| v2-004 | pt | greeting | **worse** · about_unprompted, content_lost | **worse** · about_unprompted, content_lost |
| v2-005 | pt | greeting | same · about_unprompted | **worse** · about_unprompted, content_lost |
| v2-006 | pt | greeting | same · other:no_line | **worse** · about_unprompted |
| v2-007 | pt | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| v2-016 | es | greeting | **worse** · about_unprompted | **worse** · about_unprompted |
| v2-017 | es | greeting | same · other:mild_about | same · other:mild_about |
| v2-018 | es | greeting | **worse** · about_unprompted, content_lost | **worse** · about_unprompted, content_lost |
| v2-019 | es | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| v2-020 | es | greeting | same · lang_fixed, about_unprompted | same · lang_fixed, about_unprompted |
| v2-021 | pt | meta | **better** · about_answered_meta, false_claim | **better** · about_answered_meta, false_claim |
| v2-022 | pt | meta | same · about_answered_meta | same · about_answered_meta |
| v2-023 | pt | meta | same · about_answered_meta, other:both_unverified | same · about_answered_meta, other:both_unverified |
| v2-027 | es | meta | **better** · about_answered_meta | **better** · about_answered_meta, other:ref_false_needs_internet |
| v2-030 | pt | followup | same · other:noise | same · other:noise |
| v2-057 | pt | ambiguous | **worse** · lang_fixed, about_unprompted, content_lost | **worse** · lang_fixed, about_unprompted, content_lost |

## Patterns
Tag counts over all 120 pairs (one pair can carry several tags):

| tag | all pairs | in worse pairs | in better pairs |
|---|---|---|---|
| about_unprompted | 72 | 40 | 2 |
| lang_fixed | 36 | 3 | 7 |
| about_answered_meta | 24 | 0 | 10 |
| content_lost | 23 | 20 | 0 |
| false_claim | 3 | 1 | 2 (the reference was more wrong) |
| other:noise (follow-ups where the line likely didn't fire) | 8 | 0 | 0 |
| other:mild_about | 6 | 0 | 1 |
| other:wrong_word_corrige / cjk_glitch / nonsense_phrase | 2 / 1 / 1 | 4 | 0 |
| lang_broke | 0 | 0 | 0 |
| truncation | 0 | 0 | 0 |

By kind:
- **Greetings, thanks and goodbyes** (74 pairs): 3 better, 32 worse. Another 26 pairs are `same` under rule A: the language was fixed, but the arm read out the ad.
- **Meta** (26 pairs): 10 better, 2 worse. Both worse pairs are v1-027, where the user asked "can you reply in PT?" and the arm added the blurb.
- **Follow-ups**: mostly noise. One exception is cs-037, where the About text leaked into a translation in both seeds.

### Most common failure: the About blurb recited as an ad, often replacing the offer of help (40 worse pairs)
- cs-004 s42 (pt→pt). REF: "Oi! Tudo bem, obrigado por perguntar. Como posso ajudar?" ARM: "Oi! Tudo bem, obrigado. O BOAR é um app de código aberto que roda um modelo de IA local no seu celular, sem precisar de internet. É totalmente offline e protege seus dados."
- v1-020 s42 (goodbye). ARM: "¡Hasta luego! BOAR ejecuta un modelo de IA local sin conexión, para que tus datos nunca salgan del teléfono."
- v2-057 s43 (the user's turn is ignored completely). ARM: "O BOAR é um app de código aberto que executa um modelo de IA local no seu celular, sem dependência de nuvem. Isso garante privacidade e desempenho offline. Ideal para uso em ambientes onde a conectividade é limitada ou não desejável."
- cs-037 s43 (the About text leaks into a translation, giving a false claim). ARM: "… O BOAR usa esse mecanismo para melhorar a eficiência local de validação."
- Fluency side effects: "corrige un modelo de IA" (cs-019 and cs-064 s42), and "obrigado pela问" with a Chinese character mid-sentence (v2-003 s42).

### Most common success: the About facts on real meta questions (10 better pairs), plus language fixes without an ad
- v2-027 s43. REF: "…Solo necesitas internet para conectarte." (false). ARM: "Sí, uso el modelo de IA local en tu teléfono, por lo que no cuesta nada ni requiere conexión a internet."
- cs-023 s42. REF: "Não, VC não é o ChatGPT. Sou o Boar…" (garbled). ARM: "Não, o BOAR não é o ChatGPT. É um app de código aberto que executa um modelo de IA local no seu celular…"
- v1-023 s42. ARM: "Sim, funciona no modo voo, pois o BOAR executa todo o processamento localmente…" The arm gives the reason; the reference doesn't.
- cs-041 (both seeds). REF: "You're welcome. Let me know if you need more…" ARM: "De nada. ¿Te ayudé con algo más?" This is a clean language fix with no ad.
- One caveat: on v2-021, the arm makes a better guess than the reference, which said "não ocupo espaço" and "assistente online". But the arm invents a number, "cerca de 100 MB a 300 MB", which is false for a 4B model. The About facts carry no figure for storage size.

## Lesson for a future 4B-only re-registration
- Split the two halves of the arm. Keep the reply-language line on every chat answer that didn't search, since it caused 0 lang_broke across 120 pairs. Inject the About facts **only when the turn is a meta question about the app or the assistant**, detected by a classifier or keyword gate. On greetings, thanks and goodbyes, the 4B model treats any About text in context as content it has to say.
- If the About facts stay, add "Só mencione isto se perguntarem sobre o app" ("Only mention this if asked about the app") together with "responda curto e ofereça ajuda" ("answer briefly and offer help"). Pre-register a check that the help offer is kept on greeting items.
- Add facts the model invents when they are missing, starting with approximate storage size, or tell the model not to give numbers it doesn't have.

UNKNOWN: whether BOAR uses location or has a button to clear chats (v2-022, v2-023), so I judged those `same`. I did not see the prompt text for cs-028 or v1-028, so I judged those on the `expected` line plus the shape of both answers.
