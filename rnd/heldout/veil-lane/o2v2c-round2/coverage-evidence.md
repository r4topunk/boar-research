# Coverage evidence: o2v2c-fresh2.jsonl

TL;DR: every item was checked with `rnd/kiln/tools/kit_coverage.py` against the 4 packs of kit A (essential app 611a4b92, wiki-vital5, boar-crypto, boar-wikivoyage-en). The required pattern per type was asserted when each item was written: (a) one side COVERED, the other MENTION-ONLY/ABSENT; (b) concept article and entity both COVERED; (c) look-alike COVERED, right entity MENTION-ONLY/ABSENT. Raw tool output: `o2v2c-round2/coverage*.raw.jsonl`.

Caveat (from Kiln): COVERED means the article exists, not that retrieval brings it for this question. For (b), the tool cannot show that the entity article lacks the answer; that part is my judgement.

| id | type | lang | question | term (role) → verdict |
|---|---|---|---|---|
| vit-o2c-023 | a | en | Which is taller, the Burj Khalifa or Merdeka 118? | Burj Khalifa (present) → **COVERED**; Merdeka 118 (absent) → **MENTION-ONLY** |
| vit-o2c-024 | a | en | Which is taller, Taipei 101 or the Shanghai Tower? | Taipei 101 (present) → **COVERED**; Shanghai Tower (absent) → **MENTION-ONLY** |
| vit-o2c-025 | a | en | Which is taller, the Petronas Towers or the Lotte World Tower? | Petronas Towers (present) → **COVERED**; Lotte World Tower (absent) → **MENTION-ONLY** |
| vit-o2c-026 | a | en | Which hydroelectric dam has the larger installed capacity, Itaipu or Belo Monte? | Itaipu Dam (present) → **COVERED**; Belo Monte Dam (absent) → **ABSENT** |
| vit-o2c-027 | a | pt | Qual ponte é mais longa, a Golden Gate ou a Ponte Rio–Niterói? | Golden Gate Bridge (present) → **COVERED**; Rio–Niterói Bridge (absent) → **MENTION-ONLY** |
| vit-o2c-028 | a | pt | O que é mais alto, o Monte Fuji ou o Pico da Bandeira? | Mount Fuji (present) → **COVERED**; Pico da Bandeira (absent) → **MENTION-ONLY** |
| vit-o2c-029 | a | pt | O que é maior em área, o Lago Titicaca ou a Lagoa Mirim? | Lake Titicaca (present) → **COVERED**; Lagoa Mirim (absent) → **ABSENT** |
| vit-o2c-030 | a | pt | Qual cachoeira tem a queda mais alta, as Cataratas do Niágara ou a Cascata do Caracol? | Niagara Falls (present) → **COVERED**; Caracol Falls (absent) → **MENTION-ONLY** |
| vit-o2c-031 | b | en | What is the half-life of carbon-14, the isotope used to radiocarbon-date the Shroud of Turin? | Radiocarbon dating (concept) → **COVERED**; Shroud of Turin (entity) → **COVERED** |
| vit-o2c-032 | b | en | What escape velocity does an object need to leave Earth's surface without further propulsion? | Escape velocity (concept) → **COVERED**; Earth (entity) → **COVERED** |
| vit-o2c-033 | b | en | Every how many blocks does Bitcoin adjust its mining difficulty? | Bitcoin network (concept) → **COVERED**; Bitcoin (entity) → **COVERED** |
| vit-o2c-034 | b | en | About how many million years ago did the asteroid impact that ended the age of the non-avian dinosaurs happen? | Cretaceous–Paleogene extinction event (concept) → **COVERED**; Dinosaur (entity) → **COVERED** |
| vit-o2c-035 | b | pt | Quantos cromossomos tem uma célula humana comum (não reprodutiva)? | Chromosome (concept) → **COVERED**; Human (entity) → **COVERED** |
| vit-o2c-036 | b | pt | A que velocidade a superfície da Terra gira na linha do equador? | Earth's rotation (concept) → **COVERED**; Earth (entity) → **COVERED** |
| vit-o2c-037 | b | pt | Quanto tempo a luz refletida pela Lua leva para chegar à Terra? | Speed of light (concept) → **COVERED**; Moon (entity) → **COVERED** |
| vit-o2c-038 | b | pt | Qual é a frequência da rede elétrica no Brasil? | Utility frequency (concept) → **COVERED**; Brazil (entity) → **COVERED** |
| vit-o2c-039 | c | en | How long is the Little Colorado River? | Colorado River (lookalike) → **COVERED**; Little Colorado River (right) → **MENTION-ONLY** |
| vit-o2c-040 | c | en | How long is the Little Missouri River that flows through North Dakota? | Missouri River (lookalike) → **COVERED**; Little Missouri River (right) → **MENTION-ONLY** |
| vit-o2c-041 | c | en | What is the elevation of the Klein Matterhorn? | Matterhorn (lookalike) → **COVERED**; Klein Matterhorn (right) → **MENTION-ONLY** |
| vit-o2c-042 | c | en | How tall is the Eiffel Tower replica in Paris, Texas? | Eiffel Tower (lookalike) → **COVERED**; Eiffel Tower (Paris, Texas) (right) → **ABSENT** |
| vit-o2c-043 | c | pt | Qual é a altitude do Pequeno Ararat? | Mount Ararat (lookalike) → **COVERED**; Little Ararat (right) → **MENTION-ONLY** |
| vit-o2c-044 | c | pt | Qual é o comprimento do rio Negro da Argentina, na Patagônia? | Rio Negro (Amazon) (lookalike) → **COVERED**; Río Negro (Argentina) (right) → **MENTION-ONLY** |
| vit-o2c-045 | c | pt | Qual é a altitude do Pico Paraná, o ponto mais alto do Sul do Brasil? | Paraná (state) (lookalike) → **COVERED**; Pico Paraná (right) → **MENTION-ONLY** |

Candidates rejected by the tool (both sides COVERED, or the right entity COVERED), from `o2v2c-round2/candidates.jsonl`:
- (a) Eiffel×Tokyo Skytree, Danube×Dniester, Kilimanjaro×Mount Stanley, Greenland×Baffin Island, Harvard×Coimbra, Panama×Kiel Canal, Iceland×Hokkaido, Salvador×São Vicente (Wikivoyage has 'São Vicente'), Japão×Minas Gerais, Nilo×São Francisco, Canadá×SP estado; second pool: Corcovado×Pão de Açúcar, Colosseum×Pont du Gard, Crater Lake×Tahoe, Mont Blanc×Monte Rosa (all COVERED).
- (b) GPS relativity (concept ABSENT), sound barrier, food energy, Ethereum address, karyotype (MENTION-ONLY only).
- (c) Republic of the Congo, Guinea-Bissau, Tokyo Tower, Washington (state), Equatorial Guinea, South Sudan, Northern Ireland, Dominica, Western Sahara, Niger (the right entity is COVERED).
