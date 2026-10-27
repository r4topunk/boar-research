# FOLLOWQ - history-aware retrieval query, retrieval-only diagnostic on cut 5 (2026-10-06)

TL;DR: **Decision rule NOT met** (rule: Q1 or Q2 adds sources on >= 8 follow-ups AND changes retrieval on <= 2 non-follow-ups among the 192). Criterion `FOLLOWQ-criterion.md` sha256 3988132d... verified, not edited. Diagnostic only; no adopt decision here.

| variant | follow-ups gaining sources (of 21) | non-follow-ups whose kept passages change (of 171) | bar |
|---|---|---|---|
| Q1 previous user turn + current | **10** (9 expected-search) | **11** (raw top-k changes: 17) | >= 8 and <= 2 |
| Q2 current + carried entities/nouns | **9** (9 expected-search) | **11** (raw top-k changes: 14) | >= 8 and <= 2 |

- Gain side passes for both variants (10 and 9 >= 8); the non-follow-up side fails for both (11 > 2).
- All 11 changed non-follow-ups are items with earlier turns (the other 153 single-turn items are identical across variants, as they must be). They are history items the frozen follow-up rule does not flag: those that name an entity ("¿y Buenos Aires?", "and what's the weather like there in January?", "¿y cómo lo evito si voy a La Paz?") or are history-dependent chat commands ("resume em uma frase", "tradúcelo al portugués", "ok" style). Changes there are mostly the intended kind (v1-034 Illinois -> Kazakhstan, v1-039 Q2 keeps Buenos Aires + Argentina, v2-034 adds Vietnam) but Q1 also breaks v1-039 (4 -> 0 passages) and the translate/summarise items now retrieve on the earlier topic. Read: the "non-follow-up" side is a property of applying the variant to every message. If a FOLLOWQ arm applied Q1/Q2 only to messages the rule flags, non-follow-up change is 0 by construction and the gain side (10 / 9) would be the number that matters; that is a design choice for the coordinator, not tested here.
- Follow-ups losing sources under both Q1 and Q2: cs-038, v1-033, v1-035 (Q0 passages there were off-topic noise: Sanamahism, EIP-8130, Tamil Nadu; Q1/Q2 return nothing).
- Coverage context: with Q0, 81/192 messages have >= 1 passage (expected-search 32/69, follow-ups 6/21). Q1 and Q2: 89/192 (expected-search 38/69 each); follow-ups 13/21 (Q1), 12/21 (Q2).

## What was run
- Where: Mac mini (`<on the mini>`), cut 5 tree `be-0cfd4a77-cut5lite` (the kit packs, embedder and detector live there; not run locally). Same kit as CHATGATE (boar-crypto + boar-wikivoyage-en, shas pinned in the requests), Android 12 GB profile, seed 44, node backend, heavy lock (HEAVY_CLASS=normal), learned detector v3b on :8094 as in CHATGATE (started and stopped by this run, port verified closed), disk 37 GiB before/after, `be-fq` runner dir removed afterwards. No Docker touched, no judge, no generation, no blind/, no rnd/veil/, chat-v3 not touched.
- How: the committed desktop-node adapter (`be-repo`, byte-identical to boar-eval) copied to a side dir `be-fq` and patched by `tools/patch_adapter.py` in two places only: the route gate always returns SEARCH, and `generate()` throws. So the engine's real `createAnswerer` runs unchanged up to and including retrieval, `isSubstantive`, `compressContext` and the on-subject grounding filter; "passages" below = the last `sources` event = what the engine would put in the prompt (same k = plan.retrieveK and the engine's own relevance cutoff/grounding). Only the query string differs per variant; the earlier turns are passed as history identically for all three (as the app does). Items the engine answers before search (small talk) or by fixed card never retrieve; they show 0 for every variant.
- Fidelity check: Q0 here vs CHATGATE's `retrieval.kept` for the same 192 messages: identical on 157; all 35 differences are messages the real gate sent to CONVERSATION (CHATGATE retrieved nothing, here SEARCH is forced) except v2-052 (health path: CHATGATE's final `kept` was emptied by the seizure card after the sources event; here the event still lists Mecca). Treat v2-052 as 0 passages in practice.
- Requests: 192 messages x 3 variants = 576 (`<id>@Q0|Q1|Q2`); 39 messages carry earlier turns (24 expected yes, 9 no, 6 either); 153 are single-turn, so Q1 = Q2 = Q0 for them.

## Variants and rules (deterministic, no LLM; `tools/mkreq.py`)
- Q0: the current user turn (today's `searchQuery` input).
- Q1: previous user turn + space + current turn.
- Q2: current turn + up to 6 terms carried from the last 2 earlier user turns: named entities first (capitalised word after position 0, ALL-CAPS word, digit-bearing or hyphenated identifier), then content nouns (proxy: lowercase words of >= 5 letters not in an EN/PT/ES stoplist), most recent turn first, skipping words already in the current turn. Known noise: the noun proxy also carries verbs ("wrote", "painted", "treat").
- Follow-up flag (current turn): the item has an earlier user turn AND the turn contains no named entity (same entity rule) AND it contains a pronoun/deictic (it, that, there, he/she, ele/ela, isso/esse/lá, eso/ese/allí, le/les, ...) or an ellipsis opener (and/e/y/but/what about/how about/e se/...). No length rule. 21 messages flagged (16 expected-search yes). Limits of the rule: misses context-dependent turns that name an entity (v1-034, v1-039) or lack a marker (v1-038, v2-031, v2-037, v2-038, v2-039); flags 5 turns that are not expected-search (cs-041 "ok gracias", v2-036 "make it shorter", and the either-label cs-034, v1-040, v2-041); v2-036 is the 10th Q1 gain (a no-search item that now retrieves).
- "Gaining sources" = Q0 has 0 passages and the variant has >= 1. "Retrieval changes" = the kept (title, section) list differs from Q0.

## Informal skim of the gains (NOT a labeller; the criterion defers on-topic judgement to a later read)
On-topic at first sight under Q1: cs-030 (Dengue fever), cs-032 (Guernica), cs-035 (Canberra), cs-036 (Immune system, Vaccine), cs-039 (Machu Picchu), v2-029 (Brazil). Doubtful: v1-037 (Gili Islands, bee sting), v2-032 (Curitiba/Uberlandia for Niemeyer), v2-035 (Secure multi-party computation, telephone). Q2 is noisier on cs-035 (Coptic Australians). So of 10 Q1 gains perhaps 6 are plausibly on-topic; the kit (no Wikipedia pack) still lacks Niemeyer, the telephone, Rembrandt/Night Watch, scorpions, hypothermia (cs-040: 0/0/0 under all variants).

## Per-item table: the 69 expected-search messages (n = passages Q0/Q1/Q2; follow-up y/n by the rule, "(hist)" = has earlier turns but not flagged; top-2 distinct titles)
| id | follow-up | n Q0/Q1/Q2 | Q0 top-2 | Q1 top-2 | Q2 top-2 |
|---|---|---|---|---|---|
| cs-029 | y | 1/3/3 | Wikivoyage: Biomes and ecosystems | Wikivoyage: Lisbon | Wikivoyage: Lisbon |
| cs-030 | y | 0/3/4 | - | Wikivoyage: Dengue fever | Wikivoyage: Dengue fever |
| cs-032 | y | 0/2/2 | - | Wikivoyage: Guernica | Wikivoyage: Guernica |
| cs-035 | y | 0/1/3 | - | Wikivoyage: Canberra | Coptic Australians; Wikivoyage: Capital Region |
| cs-036 | y | 0/2/2 | - | Immune system; Vaccine | Immune system; Vaccine |
| cs-038 | y | 2/0/0 | Wikivoyage: Sanamahism; Ethereum EIPs/ERCs: EIP-8025: Optional Execution Proofs | - | - |
| cs-039 | y | 0/4/4 | - | Wikivoyage: Machu Picchu | Wikivoyage: Machu Picchu |
| cs-040 | y | 0/0/0 | - | - | - |
| cs-042 | n | 0/0/0 | - | - | - |
| cs-043 | n | 2/2/2 | Wikivoyage: Elephants | Wikivoyage: Elephants | Wikivoyage: Elephants |
| cs-044 | n | 0/0/0 | - | - | - |
| cs-045 | n | 0/0/0 | - | - | - |
| cs-046 | n | 2/2/2 | Wikivoyage: East Africa; Wikivoyage: Africa | Wikivoyage: East Africa; Wikivoyage: Africa | Wikivoyage: East Africa; Wikivoyage: Africa |
| cs-047 | n | 0/0/0 | - | - | - |
| cs-048 | n | 0/0/0 | - | - | - |
| cs-049 | n | 0/0/0 | - | - | - |
| cs-050 | n | 2/2/2 | Wikivoyage: Santos Dumont | Wikivoyage: Santos Dumont | Wikivoyage: Santos Dumont |
| cs-051 | n | 0/0/0 | - | - | - |
| cs-052 | n | 0/0/0 | - | - | - |
| cs-053 | n | 2/2/2 | Wikivoyage: Jellyfish | Wikivoyage: Jellyfish | Wikivoyage: Jellyfish |
| cs-054 | n | 3/3/3 | Wikivoyage: Berlin Wall | Wikivoyage: Berlin Wall | Wikivoyage: Berlin Wall |
| cs-055 | n | 0/0/0 | - | - | - |
| cs-056 | n | 0/0/0 | - | - | - |
| v1-029 | y | 0/0/0 | - | - | - |
| v1-031 | y | 0/0/0 | - | - | - |
| v1-033 | y | 1/0/0 | Wikivoyage: Tamil Nadu | - | - |
| v1-034 | n (hist) | 2/2/2 | Wikivoyage: Illinois; Short Weather Cipher | Wikivoyage: Kazakhstan | Wikivoyage: Kazakhstan |
| v1-035 | y | 3/0/0 | ethereum.org: Anatomy of smart contracts; Ethereum EIPs/ERCs: EIP-8130: Keystore Accounts | - | - |
| v1-037 | y | 0/1/1 | - | Wikivoyage: Gili Islands | Wikivoyage: Diving the west coast of South Africa |
| v1-038 | n (hist) | 4/3/3 | Wikivoyage: La Paz; Wikivoyage: La Paz (Mexico) | Wikivoyage: La Paz | Wikivoyage: La Paz |
| v1-039 | n (hist) | 4/0/4 | Wikivoyage: Buenos Aires; Wikivoyage: Buenos Aires (disambiguation) | - | Wikivoyage: Buenos Aires; Wikivoyage: Argentina |
| v1-042 | n | 0/0/0 | - | - | - |
| v1-043 | n | 4/4/4 | Wikivoyage: Bahia; Wikivoyage: Flying to South America | Wikivoyage: Bahia; Wikivoyage: Flying to South America | Wikivoyage: Bahia; Wikivoyage: Flying to South America |
| v1-044 | n | 2/2/2 | ethereum.org: Proof-of-stake vs proof-of-work | ethereum.org: Proof-of-stake vs proof-of-work | ethereum.org: Proof-of-stake vs proof-of-work |
| v1-045 | n | 1/1/1 | Wikivoyage: Moon | Wikivoyage: Moon | Wikivoyage: Moon |
| v1-046 | n | 1/1/1 | Wikivoyage: Arctic wildlife | Wikivoyage: Arctic wildlife | Wikivoyage: Arctic wildlife |
| v1-047 | n | 0/0/0 | - | - | - |
| v1-048 | n | 1/1/1 | Wikivoyage: Hierve el Agua | Wikivoyage: Hierve el Agua | Wikivoyage: Hierve el Agua |
| v1-049 | n | 0/0/0 | - | - | - |
| v1-050 | n | 0/0/0 | - | - | - |
| v1-051 | n | 1/1/1 | Wikivoyage: Porto | Wikivoyage: Porto | Wikivoyage: Porto |
| v1-052 | n | 1/1/1 | Typhoon | Typhoon | Typhoon |
| v1-053 | n | 1/1/1 | Wikivoyage: Vinicunca | Wikivoyage: Vinicunca | Wikivoyage: Vinicunca |
| v1-054 | n | 3/3/3 | Ethereum | Ethereum | Ethereum |
| v1-055 | n | 3/3/3 | Wikivoyage: Bolivia | Wikivoyage: Bolivia | Wikivoyage: Bolivia |
| v1-056 | n | 0/0/0 | - | - | - |
| v2-029 | y | 0/3/3 | - | Wikivoyage: Brazil; Human rights and encryption | Wikivoyage: Brazil |
| v2-031 | n (hist) | 2/2/2 | Wikivoyage: Flash floods; Wikivoyage: Findlay | Wikivoyage: Flash floods; Wikivoyage: Findlay | Wikivoyage: Flash floods; Wikivoyage: Findlay |
| v2-032 | y | 0/2/4 | - | Wikivoyage: Curitiba; Wikivoyage: Uberlândia | Wikivoyage: Curitiba; Wikivoyage: Uberlândia |
| v2-034 | n (hist) | 2/2/2 | Wikivoyage: Hanoi | Wikivoyage: Vietnam; Wikivoyage: Hanoi | Wikivoyage: Vietnam; Wikivoyage: Hanoi |
| v2-035 | y | 0/1/1 | - | Secure multi-party computation | Secure multi-party computation |
| v2-037 | n (hist) | 0/0/0 | - | - | - |
| v2-038 | n (hist) | 0/4/0 | - | Wikivoyage: Uyuni; Wikivoyage: Salar de Uyuni | - |
| v2-039 | n (hist) | 0/0/0 | - | - | - |
| v2-042 | n | 0/0/0 | - | - | - |
| v2-043 | n | 4/4/4 | Wikivoyage: Fernando de Noronha | Wikivoyage: Fernando de Noronha | Wikivoyage: Fernando de Noronha |
| v2-044 | n | 2/2/2 | ethereum.org: Timeline of all Ethereum forks (2014 to present); ethereum.org: Introduction to Ethereum governance | ethereum.org: Timeline of all Ethereum forks (2014 to present); ethereum.org: Introduction to Ethereum governance | ethereum.org: Timeline of all Ethereum forks (2014 to present); ethereum.org: Introduction to Ethereum governance |
| v2-045 | n | 3/3/3 | Wikivoyage: Southwest Iceland; Wikivoyage: Iceland | Wikivoyage: Southwest Iceland; Wikivoyage: Iceland | Wikivoyage: Southwest Iceland; Wikivoyage: Iceland |
| v2-046 | n | 3/3/3 | Wikivoyage: Mexico City | Wikivoyage: Mexico City | Wikivoyage: Mexico City |
| v2-047 | n | 0/0/0 | - | - | - |
| v2-048 | n | 0/0/0 | - | - | - |
| v2-049 | n | 0/0/0 | - | - | - |
| v2-050 | n | 0/0/0 | - | - | - |
| v2-051 | n | 0/0/0 | - | - | - |
| v2-052 | n | 1/1/1 | Wikivoyage: Mecca | Wikivoyage: Mecca | Wikivoyage: Mecca |
| v2-053 | n | 2/2/2 | Ethereum EIPs/ERCs: EIP-7918: Blob base fee bounded by execution cost | Ethereum EIPs/ERCs: EIP-7918: Blob base fee bounded by execution cost | Ethereum EIPs/ERCs: EIP-7918: Blob base fee bounded by execution cost |
| v2-054 | n | 3/3/3 | Wikivoyage: Andorra; Wikivoyage: Spanish phrasebook | Wikivoyage: Andorra; Wikivoyage: Spanish phrasebook | Wikivoyage: Andorra; Wikivoyage: Spanish phrasebook |
| v2-055 | n | 0/0/0 | - | - | - |
| v2-056 | n | 1/1/1 | Wikivoyage: Camino de Santiago | Wikivoyage: Camino de Santiago | Wikivoyage: Camino de Santiago |

Files: `tools/mkreq.py` (variants + requests), `tools/patch_adapter.py` (retrieval-only runner), `tools/followq-run.sh` (run), `tools/analyze.py`, `analysis-output.txt` (all numbers + the 39 history-item variants), `variants.json` (the 192 x 3 query strings and flags). Traces: `boar-eval/runs/kiln/followq/` (not committed).
