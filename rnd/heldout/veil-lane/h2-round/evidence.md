# Evidence: h2-fresh.jsonl

TL;DR: 24 items for Kiln's frozen H2 rule (out-of-sample), 12 EN / 12 PT, every entity page COVERED in kit A (`rnd/kiln/tools/kit_coverage.py`, asserted per item).
- (a) 10 objective-format questions whose answer is NOT in the article's first sentence, and in 8 of 10 not in the first paragraph either (the 2 comparatives have one side's figure in that page's first paragraph).
- (b) 10 same-format controls whose answer IS in the first sentence or first paragraph.
- (c) 4 open/definition questions.

Answer position was measured on the English Wikipedia plain-text extract (MediaWiki API, 2026-10-01) as a proxy for the kit's article order; the kit text itself is not readable through the tool. No health items, no look-alikes. Not read: `rnd/kiln/exp-09`.

| id | type | lang | question | page(s) → coverage | answer position |
|---|---|---|---|---|---|
| vit-h2-001 | a | en | How long is the Great Wall of China counting all of its branches? | Great Wall of China → **COVERED** | Great Wall of China: intro (after the first paragraph) |
| vit-h2-002 | a | en | In what year was the wreck of the Titanic discovered? | Titanic → **COVERED** | Titanic: body (not in the intro) |
| vit-h2-003 | a | en | What is Saturn's largest moon? | Saturn → **COVERED** | Saturn: intro (after the first paragraph) |
| vit-h2-004 | a | en | Which has the longer main span, the Golden Gate Bridge or the Brooklyn Bridge? | Golden Gate Bridge → **COVERED**; Brooklyn Bridge → **COVERED** | Golden Gate Bridge: intro (after the first paragraph); Brooklyn Bridge: first paragraph |
| vit-h2-005 | a | en | In what year was Iceland's parliament, the Althing, established? | Iceland → **COVERED** | Iceland: body (not in the intro) |
| vit-h2-006 | a | pt | Quantas entidades federativas (estados) tem o México? | Mexico → **COVERED** | Mexico: intro (after the first paragraph) |
| vit-h2-007 | a | pt | Quantas ilhas formam o Japão? | Japan → **COVERED** | Japan: body (not in the intro) |
| vit-h2-008 | a | pt | Quantos fusos horários tem o Brasil? | Brazil → **COVERED** | Brazil: body (not in the intro) |
| vit-h2-009 | a | pt | Qual rio é mais longo, o Danúbio ou o Reno? | Danube → **COVERED**; Rhine → **COVERED** | Danube: first paragraph; Rhine: intro (after the first paragraph) |
| vit-h2-010 | a | pt | Em que ano Portugal deixou de ser monarquia e virou república? | Portugal → **COVERED** | Portugal: intro (after the first paragraph) |
| vit-h2-011 | b | en | In what year did the Chernobyl nuclear disaster happen? | Chernobyl disaster → **COVERED** | Chernobyl disaster: first sentence |
| vit-h2-012 | b | en | When was the Battle of Waterloo fought? | Battle of Waterloo → **COVERED** | Battle of Waterloo: first sentence |
| vit-h2-013 | b | en | How tall is Denali? | Denali → **COVERED** | Denali: first sentence |
| vit-h2-014 | b | en | In what year did Apollo 11 land on the Moon? | Apollo 11 → **COVERED** | Apollo 11: first sentence |
| vit-h2-015 | b | en | How long is the Mississippi River? | Mississippi River → **COVERED** | Mississippi River: first paragraph |
| vit-h2-016 | b | pt | Em que ano começou a Revolução Francesa? | French Revolution → **COVERED** | French Revolution: first sentence |
| vit-h2-017 | b | pt | Qual é a altitude do Monte Kosciuszko, o ponto mais alto da Austrália continental? | Mount Kosciuszko → **COVERED** | Mount Kosciuszko: first sentence |
| vit-h2-018 | b | pt | Em que ano Constantinopla caiu diante do Império Otomano? | Fall of Constantinople → **COVERED** | Fall of Constantinople: first sentence |
| vit-h2-019 | b | pt | Qual é o comprimento do Canal de Suez? | Suez Canal → **COVERED** | Suez Canal: first paragraph |
| vit-h2-020 | b | pt | Quantas teclas tem um piano moderno padrão? | Piano → **COVERED** | Piano: first paragraph |
| vit-h2-021 | c | en | What is the Rosetta Stone? | Rosetta Stone → **COVERED** | n/a (open) |
| vit-h2-022 | c | en | Tell me about the Silk Road. | Silk Road → **COVERED** | n/a (open) |
| vit-h2-023 | c | pt | O que é o Mercosul? | Mercosur → **COVERED** | n/a (open) |
| vit-h2-024 | c | pt | Fale sobre Machu Picchu. | Machu Picchu → **COVERED** | n/a (open) |

Dropped while building: Japan's highest point (Mount Fuji is not mentioned in the Japan article), Sydney Opera House (1973 not at the start), Lei Áurea (not in the kit), the piano key count moved from (a) to (b) (it is in the first paragraph).
