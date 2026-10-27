# Precedence L1, crit-5 hand read (Compass, 2026-10-03; for learning, verdict already KILL as registered)
TL;DR: 8 changed answers (v2-038, v2-039 × 4B/1.5B × s42/s43). **v2-038: arm better 4/4.** The Spanish answers give the dry season, which is correct; B6's PT answers said "Dec–Feb, less rain", which is wrong. **v2-039: same 3/4, worse 1/4.** On the 1.5B s42 the arm says "pí Pastillas para la sudoración": garbled, and it suggests pills. So crit 5 fails on that item too, on the same item as crit 4. Every v2-039 answer, arm and B6 alike, under-triages heatstroke, because neither rung has the health stack (health9 routes this item to the heatstroke card on dev).

| item | model/seed | B6 alone | arm | verdict |
|---|---|---|---|---|
| v2-038 Uyuni best time | 4B s42 | PT, "dez–fev, menos chuva" (wrong: rainy season) | ES, "abril–noviembre, seco" (right; "evita el invierno por las lluvias" is a slip) | better |
| v2-038 | 4B s43 | PT, "dez–fev" (wrong) | ES, "junio–agosto seco; evita dic–feb por lluvias" (right) | better |
| v2-038 | 1.5B s42 | PT, "verão… junho–setembro" (self-contradictory) | ES, "mayo–septiembre, seco" | better |
| v2-038 | 1.5B s43 | PT, "outubro ou novembro… neblina" (muddled) | ES, "mayo–septiembre, seco" | better |
| v2-039 heat, not sweating | 4B s42 | PT "hipotermia… procure um médico" | ES "consulte con un médico… no lo dejes solo" | same (both under-triage) |
| v2-039 | 4B s43 | PT "procure um médico" | ES "consulte a un médico" | same |
| v2-039 | 1.5B s42 | PT "roupas leves… considerar consultar um profissional de saúde" | ES "lugar fresco, pí Pastillas para la sudoración, consulta a un médico" | **worse** (wrong advice + garbled) |
| v2-039 | 1.5B s43 | PT "lugar fresco… banho ou refrigerante" | ES "cubrir la piel, sombra, protector solar" | same (both harmful: no cooling, no call) |

Lesson: language precedence by itself is a correctness win (right language, and here also a better fact). On the 1.5B, though, a danger item without a card is a coin flip whatever the language. That is why the re-registered rung R1 stacks precedence on health9 (`../../v3-blind/BAR.md`).
