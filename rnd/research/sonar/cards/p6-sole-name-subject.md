# P-6: the question's sole proper name as subject, whatever its share. Replayed: ~0 genuine net gain → not proposed
TL;DR: `searchDetailed` puts a named article first only if its share of the question's term weight is ≥ `NAMED_MIN_SHARE` (0.5). Long overview questions ("Give me the essentials on Kenya: its location, capital, official languages and year of independence") push the subject's share to 0.15–0.30, so the subject's own article loses its first place. P-6 promotes it when it is the question's *only* proper name. Pack-level replay: +3 key-bearing results (Singapore, Montenegro, Kenya). But the real `and-qwen` traces already reach Singapore and Montenegro through other paths. Kenya's key is already recovered by P-1 (Nairobi §History). It also costs the Moon key (lan-ref-003) and changes 2 health items. Net ≈ 0 on v0.1 → closed without a run.
Lane: Sonar (same-model pipeline, retrieval) · Status: replayed, **not proposed** · Priority: C
Axes moved: none measurably on v0.1 (see evidence). Latency ≈ 0 (one extra `article()` read on matched questions).

Evidence (`exp/21-named-share-drops/`; engine @0cfd4a77, local copy; packs wikivoyage + crypto):
- **Audit** (`audit.txt`): over the 60 public v0.1 questions, 48 named-title candidates fall below the share bar. 15 of those articles contain the key terms somewhere (article level, loose).
- **Reach** (`reach.txt`, vs `and-qwen-s42` trace raw/kept): of those 15, the article is absent from the trace's raw for
  - vit-trv-003 Pai (fixed by **P-5**);
  - vit-trv-004 Rome (walk Paris→Rome; key loose);
  - vit-cry-001 / vit-cry-010 Ethereum (generic article, key loose);
  - vit-hlt-001 Jellyfish (health);
  - lan-ref-004 Iceland (the Iceland guide doesn't state the area: no key at passage level);
  - lan-exp-003 Kenya.
- **Replay of the rule** (`replay.txt`; fires only when no title passes the bar and the question has exactly one capitalized-name run equal to a named title): 15 of 178 pack result lists change, over the 89 public questions.

  | Change | Items |
  |---|---|
  | key gained at pack level | lan-exp-001 Singapore, lan-exp-002 Montenegro, lan-exp-003 Kenya (already in the trace for the first two) |
  | key lost | lan-ref-003 Moon (Webster (Texas) §Cope pushed out; it was cut by compression anyway), vit-hlt-001 (Langkawi §Stay healthy displaced by Thailand §, health) |
  | changed, no key either side | Iceland, India, Sahara, Nile, Greenland, Andes (health), food-001/002/006, Kyoto (key kept) |

- **Fidelity caveat:** pack-level at k = 3 without `queryVec`. The real engine also merges lexical/semantic/bundled results (which is why Singapore and Montenegro already reach the trace), so pack-level gains overstate engine gains.

What this closes: share-based named-title drops are not a recall bottleneck on v0.1 beyond the Pai case (P-5). Overview questions about a country/city reach their subject through other paths. If v0.2 confirmation shows misses on overview questions, revisit with a full `retrieveOne` replay and a health exclusion.
