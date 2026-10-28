# Coverage evidence: h1-fresh.jsonl

TL;DR: 24 items for the out-of-sample check of Kiln's H1 (subject of the passage = subject of the question, before the instant/extractive answer). Every item was checked with `rnd/kiln/tools/kit_coverage.py` (kit A packs). The pattern per type was asserted when each item was written:
- (a) look-alike COVERED, right entity MENTION-ONLY/ABSENT, so H1 should block;
- (b) the right entity's page COVERED, so H1 must not block;
- (c) health/danger: medical article COVERED, or for the 3 generic-only items (bee sting, stingray, scorpion), medical article MENTION-ONLY/ABSENT and a generic Wikivoyage guide COVERED.

Caveat (Kiln): COVERED means the page exists, not that retrieval returns it. Raw output: `h1-round/coverage*.raw.jsonl`. Not read: `rnd/kiln/exp-09-instant-tier-gap/`.

| id | type | lang | question | term (role) → verdict |
|---|---|---|---|---|
| vit-h1-001 | a | en | How long is the Little Tennessee River? | Tennessee River (lookalike) → **COVERED**; Little Tennessee River (right) → **MENTION-ONLY** |
| vit-h1-002 | a | en | What is the elevation of Mount Washington in Oregon? | Mount Washington (lookalike) → **COVERED**; Mount Washington (Oregon) (right) → **ABSENT** |
| vit-h1-003 | a | en | What is the population of Paris, Ontario? | Paris (lookalike) → **COVERED**; Paris, Ontario (right) → **MENTION-ONLY** |
| vit-h1-004 | a | en | In which years did Lake Placid, New York host the Winter Olympics? | Lake Placid, Florida (lookalike) → **COVERED**; Lake Placid, New York (right) → **MENTION-ONLY** |
| vit-h1-005 | a | pt | Em que ano um terremoto destruiu a cidade de San Juan, na Argentina? | San Juan, Puerto Rico (lookalike) → **COVERED**; San Juan, Argentina (right) → **MENTION-ONLY** |
| vit-h1-006 | a | pt | Qual é o comprimento do rio Paraíba do Sul? | Paraíba (lookalike) → **COVERED**; Paraíba do Sul River (right) → **MENTION-ONLY** |
| vit-h1-007 | a | pt | Quantos habitantes tem São José dos Pinhais? | São José dos Campos (lookalike) → **COVERED**; São José dos Pinhais (right) → **MENTION-ONLY** |
| vit-h1-008 | a | pt | Qual é a população de Nova Lima, em Minas Gerais? | Lima (lookalike) → **COVERED**; Nova Lima (right) → **MENTION-ONLY** |
| vit-h1-009 | b | en | What is the population of Switzerland? | Switzerland (right) → **COVERED** |
| vit-h1-010 | b | en | In what year did the Berlin Wall fall? | Berlin Wall (right) → **COVERED** |
| vit-h1-011 | b | en | How many moons does Mars have? | Mars (right) → **COVERED** |
| vit-h1-012 | b | en | What is the boiling point of ethanol? | Ethanol (right) → **COVERED** |
| vit-h1-013 | b | pt | Qual é a altura do Pão de Açúcar, no Rio de Janeiro? | Sugarloaf Mountain (right) → **COVERED** |
| vit-h1-014 | b | pt | Em que ano Brasília foi inaugurada? | Brasília (right) → **COVERED** |
| vit-h1-015 | b | pt | Qual é a capital da Nova Zelândia? | New Zealand (right) → **COVERED**; Auckland (lookalike) → **COVERED** |
| vit-h1-016 | b | pt | Qual é a capital da Austrália? | Australia (right) → **COVERED**; Canberra (answer_page) → **COVERED** |
| vit-h1-017 | c (generic-only) | en | I just got stung by a bee and the stinger is still in my skin. What should I do? | Bee sting (medical) → **MENTION-ONLY**; Dangerous animals (guide) → **COVERED**; Anaphylaxis (related) → **COVERED** |
| vit-h1-018 | c (generic-only) | en | I stepped on a stingray at the beach and my foot hurts badly. What should I do? | Stingray injury (medical) → **ABSENT**; Beaches (guide) → **COVERED**; Stingray (related) → **COVERED** |
| vit-h1-019 | c | en | My friend collapsed in the heat, is confused and very hot. What should I do right now? | Heat stroke (medical) → **COVERED** |
| vit-h1-020 | c | en | An adult is choking and can't speak or breathe. What should I do? | Choking (medical) → **COVERED** |
| vit-h1-021 | c (generic-only) | pt | Fui picado por um escorpião agora. O que eu faço? | Scorpion sting (medical) → **MENTION-ONLY**; Dangerous animals (guide) → **COVERED**; Scorpion (related) → **COVERED** |
| vit-h1-022 | c | pt | Uma pessoa desmaiou na minha frente. O que eu faço? | Syncope (medicine) (medical) → **COVERED** |
| vit-h1-023 | c | pt | Acho que estou com intoxicação por monóxido de carbono em casa. O que faço? | Carbon monoxide poisoning (medical) → **COVERED** |
| vit-h1-024 | c | pt | Achei um carrapato grudado na pele. Como tiro? | Tick (medical) → **COVERED** |

Rejected by the tool (right entity COVERED, so no subject mismatch possible): Newark (Delaware), Portland (Maine), Little Cayman, Lake Placid alternatives, Santa Maria (RS), Valencia (Venezuela), Córdoba (Argentina), Victoria (Seychelles), Vitória da Conquista, Novo Hamburgo, Campos dos Goytacazes, Juazeiro do Norte, Little Andaman, Lesser Sunda Islands. Dog bite was dropped from the generic-only set because the Rabies article (COVERED) covers its first aid.
