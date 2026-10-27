# exp-31 (A): pack coverage of the post author's example question classes, and where retrieval loses the answer

Sonar, 2026-10-03. Public bench v0.1 only, non-blind traces only (no `blind/`, `veil`, `fresh`, `/e3/`, `v02`, `v1-`/`v2-` items opened).

Abbreviations:
- `T/` = `<workspace>/boar-eval/runs/night-2026-10-01/`
- `X/` = `<workspace>/rnd/research/sonar/exp/31-vitalik-coverage/`
- Engine = `0cfd4a77` (`…/scratchpad/be-0cfd4a77-health13`, `be-0cfd4a77`)

Scripts and outputs (all read-only on packs and traces):
- `X/items.py` → `X/items.out.txt`, `X/items.json`: per-item coverage and traces.
- `X/probe.py` → `X/probe.out.txt`: pack probes.
- `X/f2text.py`: reader for format-2 packs, also run on the Mac mini for `boar-wiki-en-top100k`.
- `X/l1/` (`run.sh`, `analyze.py` → `analyze.out.txt`, `ios-a`/`ios-v5` `.traces.jsonl`): 12 new probe questions.

## 1. TL;DR

- **The default kit misses most of the post author's humanities and country questions. Shipped crypto and travel content is decent.**
  - Of the 23 keyed or judged items in classes 1–3 and 5:
    - 11 have the answer in kit A (crypto + Wikivoyage);
    - 3 more have it only with `wiki-vital5`;
    - 6 have it only in built packs nobody ships (`boar-wiki-en-top100k`, or the 15-shard full English Wikipedia);
    - 3 have it nowhere offline (§3).
  - Wikipedia bodies are the gap: vital5 holds only ~1.1–1.7k-character leads. Example: Japan has 1,739 characters of lead vs 54,174 characters and 8 sections in top100k (`X/probe.out.txt`).
- **Shipping the knowledge isn't enough: retrieval loses it on most items that have it.**
  - Of the 14 items whose key is installed (kit A + vital5), the exact passages shown to the model hold it in only **5** (1 of them partial: Brazil plug/volt without the 127/220 values). Source: `T/ios-main-v5-s42-kic.traces.jsonl`.
  - Where the other 9 are lost:
    - compression or section choice: Mozi comparison, quantum/ECDSA, FOCIL, DAO, Chiang Mai→Pai, Lisbon airport;
    - gates dropping the right guide: altitude sickness, Kenya;
    - crypto-pack noise taking every slot: "Explain Mozi's views…" → TrueCrypt / ethereum.org.
- **Post-quantum signatures are well covered and badly retrieved.**
  - The crypto pack has "NIST Post-Quantum Cryptography Standardization" (ML-DSA ×4, SLH-DSA ×2, FIPS 204/205), "SPHINCS+", "Lattice-based cryptography" and "Post-quantum cryptography on Ethereum".
  - "What are quantum-resistant signatures, and which ones has NIST standardized?" still declines, because 0 of 3 algorithm names survive into the passages (`X/l1/analyze.out.txt`).
  - Missing: the post author's own "quantum emergency" hard-fork post (0 hits in the pack) and the FIPS documents themselves.
- **Top missing content, by the post author-style hits:**
  1. Wikipedia article bodies (8 items + 3 probes);
  2. the post author's blog and ethresear.ch posts (d/acc, Privacy Pools, quantum emergency; 4 items);
  3. a city-to-city distance capability: no Paris–Rome passage exists anywhere, but geonames coordinates plus `distanceMeters` are already local;
  4. thin Wikivoyage "Respect" (847 of 34,002 guides) and "Climate" (4,327) sections.
- **§3b, the two priority items:**
  - **Gríma/Saruman (vit-hum-004)** is a *coverage* failure in the shipped kit. No pack it ships has the passage: vital5 has no Saruman article, and its LOTR lead lacks the death. The 4B then answers confidently wrong from memory ("Gríma does not kill Saruman…", `T/and-qwen-s42.traces.jsonl`). It is not a refusal.
    - The built-but-unshipped top100k pack has it ("Wormtongue … turn on Saruman and kill him in front of Bag End"), and that arm puts a Gríma passage in front of the model (`T/ios-enwiki-s42-kic.traces.jsonl`).
  - **Paris–Rome (vit-trv-004)** is a *no-passage + arithmetic* failure.
    - No offline text gives the Paris–Rome distance. The model guesses "~1,200 km one way, 2,400 round trip" against a key of ~2,700–2,800 km.
    - Local geonames gives 1,107 km great-circle, so ×1.25 ≈ 1,384 km one way ≈ 2,767 km round trip.

## 2. Inventory: what the kit ships vs what exists

"Kit A" is the kit of every Android device and desktop run:
- bundled corpus + `boar-crypto` + `boar-wikivoyage-en`, no vital5 (`<workspace>/boar-eval/reports/devices-2026-10-02/android-g75.md` §Setup; `T/and-qwen-s42.config.json`);
- "kit A + vital5" is the iPhone's kit (`T/ios-main-v5-s42.config.json`).

The Android setup wizard's preselected tier is `standard`: `useState<SetupTier>("standard")`, `src/ui-android/SetupWizardScreen.tsx:88`. That is the bundled corpus + `corpus-standard` only. Crypto, Wikivoyage, vital5 and preparedness are optional downloads (`required: false`).

| Pack | Size | Content | Source / license | Status |
|---|---|---|---|---|
| `corpus.json` (bundled) | in APK | 300 random Wikipedia docs (e.g. "1992 Pro Bowl"; `git show 0cfd4a77:assets/corpus/corpus.json`) | Wikipedia, CC BY-SA 4.0 | always installed |
| `corpus-standard` / `corpus-full` | 614 KB / 2.5 MB | +1,000 / +4,000 topics | Wikipedia, CC BY-SA 4.0 (`src/models/manifest.ts:216-239`) | tiers `standard` (wizard default) / `full` |
| `wiki-vital5` | 163.6 MB | **lead sections only** of 49,832 Vital Articles L5 (format 1; meta `source` = "…introductions") | Wikipedia, CC BY-SA 4.0; GitHub release `knowledge-pack-v1` (`manifest.ts:244-255`) | tier `encyclopedia`; iPhone kit |
| `boar-crypto` | 36.1 MB | 3,141 docs: 1,208 EIPs/ERCs, 180 BIPs, 156 specs/Yellow Paper, 228 ethereum.org, 1,369 enwiki crypto articles (pack `meta.sources`) | CC0 / MIT / per-BIP / CC BY-SA (`src/rag/cryptoPack.ts:23-45`); HF `r4topunk/boar-packs` | optional; **kit A** |
| `boar-wikivoyage-en` | 351.1 MB | 34,002 full travel guides (`src/rag/wikiEnPacks.ts:151-158`) | Wikivoyage, CC BY-SA 4.0; HF | optional; **kit A** |
| `boar-preparedness` | 16.5 MB | 1,754 docs (first aid, survival; Wikipedia 902, Appropedia 567, Wikibooks 71, Ready.gov/NPS 182, FM 21-76 24) | CC BY-SA + US public domain (`src/rag/preparedness.ts:13-46`) | optional; not in kit A |
| Places/POI packs | ~19 MB local (`<workspace>/shared-data/poi/packs/`) | OSM venues per city | ODbL | another agent's lane |
| **`boar-wiki-en-00…14`** | **18.03 GB** (15 × ~1.2 GB) | all ~6.2M EN articles; **top 1M by pageviews in full**, leads for the rest (`<workspace>/shared-data/packs/boar-wiki-en-00.sqlite.json`; `cards/full-enwiki-pack-arm.md`) | FineWiki (Aug 2025), CC BY-SA 4.0; pinned HF URLs in `src/rag/wikiEnPacks.ts` | **in the app catalog as optional downloads, never scored**; only shard 07 is local (`shared-data/gate-ref/`) |
| **`boar-wiki-en-top100k`** | **2.54 GB** | 98,389 full articles (top 100k by views), 1.05M redirects (`<on the mini> …/boar-wiki-en-top100k.sqlite.json`, sha `9123b372…`) | FineWiki, CC BY-SA 4.0 | **built, not in the catalog**; arms #6/#6b/#17 failed their gates (`<workspace>/boar-eval/reports/night-2026-10-01/enwiki-top100k.md`, `bigpack-g1plus.md`) |
| `boar-wiki-sample` | 1.56 GB | 1 FineWiki shard, format 2 | CC BY-SA 4.0 | dev only |

Content in no pack at all:
- Project Gutenberg primary texts (`cards/primary-texts-pack.md`);
- the post author's blog and ethresear.ch;
- the NIST FIPS documents themselves.

## 3. Per class: coverage and retrieval outcome (25 items)

Column definitions:
- **Cov:** where the answer key (precheck `must_any`/`must_k`) is found in the installed text of the item's reference article(s):
  - **a** = default kit (kit A; **a+v5** = only with vital5);
  - **b** = built-but-unshipped (`top100k`, or `full15` = the 15-shard pack, per the exp-04 pageview rank < 1M + the live article in `exp/03-intro-vs-body-coverage/fulltext/`);
  - **c** = nowhere offline.
- **raw / pre / shown:** whether the key is in the retriever output (article mode), in the **exact** passages placed before the answer (`T/ios-main-v5-s42-kic.traces.jsonl`, `--event-source-text`), and what was shown. Retrieval is seed- and model-independent (`tools/KEY_IN_CONTEXT_SPEC.md`), and raw/pre titles are identical in kit A runs (`T/ios-main-s42`, `T/and-qwen-s42`).
- **Ratio:** judged boar/ref, both orders, s42+s43, as 1.5B / 4B:
  - kit A: `T/ios-main-s4x`, `T/and-qwen-s4x` `.judgments.jsonl`;
  - kit A + vital5: `T/ios-main-v5-s4x`, `T/and-main-v5-s4x` `.judgments.jsonl`.
- **Per-item evidence:** `X/items.out.txt`.

### Class 1: Mozi / Chinese philosophy / humanities

| id | question | Cov | raw → pre (A+v5, exact) | Loss stage | Ratio A / A+v5 (1.5B/4B) |
|---|---|---|---|---|---|
| vit-hum-001 | Explain Mozi's views on universal love. | a+v5 (Mozi lead); full15 body (Mozi rank 176k: **not** in top100k) | raw = TrueCrypt, ethereum.org ×3: no key; all 4 off-topic-dropped → empty, 1.5B declines / 4B memory | **retrieval: crypto-pack noise** (`exp/06` "retrieval-miss") | .36/.56 · .36/.54 |
| vit-hum-002 | How did Mozi's … differ from the Confucian view, and how did Mencius attack it? | a+v5 (lead, loose key); full15 | kit A: raw empty (`context:0->0`). A+v5: raw Mozi ×2 has key; pre Mozi has **no key** (`context:238->101`) | compression | .36/.42 · .29/.34 |
| vit-hum-003 | How would Mozi answer the critique that universal love is self-defeating…? | b: top100k Mohism body (22k chars); vital5 lead has no key | raw empty in every run, **including the top100k arm** (`T/ios-enwiki-s42-kic`) | coverage (+ retrieval with the big pack) | .34/.45 · .31/.44 |
| vit-hum-005 | What did Adam Smith mean by the 'invisible hand', how often in Wealth of Nations? | a+v5 (lead); full15 (rank 132k); Gutenberg text: c | kit A: only "Wikivoyage: Kirkcaldy". A+v5: Invisible hand ×2 + Adam Smith → **pre key ✓** | coverage in kit A | .25/.35 · .32/.47 |
| vit-hum-006 | What is Mill's harm principle, and the main objections? | b: full15 only ("Harm principle" rank 340k; no vital5, no top100k) | A+v5: J. S. Mill + On Liberty leads; no key | coverage | .28/.37 · .25/.40 |
| vit-hum-004 | Why does Gríma kill Saruman? | see §3b | | | |

Probes (`X/l1/analyze.out.txt`):
- "How did Xunzi's view of human nature differ from Mencius's?"
  - kit A: raw = 4 ERCs (crypto noise), declined;
  - A+v5: Mencius + Xunzi leads retrieved, Xunzi dropped, declined.
- "Main ideas of Legalism": A+v5 retrieves the Legalism lead ×2, all citations removed, declined.
- Mencius, Han Fei, Legalism, Hundred Schools, Zhu Xi and Wang Yangming have **no** top100k article (`X/probe.out.txt` §1a).

### Class 2: quantum-resistant signatures / crypto research

| id | question | Cov | raw → pre | Loss stage | Ratio |
|---|---|---|---|---|---|
| vit-cry-001 | How would Ethereum protect funds if a quantum computer broke ECDSA? | a: ethereum.org "Post-quantum cryptography on Ethereum" (hard fork ×1, STARK ×3). The canonical source (ethresear.ch "quantum emergency" post): **c** (0 pack hits) | raw ✓ (PQ page, ERC-7524, EIP-8202); **pre ✗** (`context:769->492`) | compression | .30/.37 · .30/.37 |
| vit-cry-002 | What is FOCIL (EIP-7805)? | a (EIP-7805) | raw ✓; pre ✗ (`context:179->139`) | compression | .28/.20 · .28/.20 |
| vit-cry-004 | What is PeerDAS…? | a (EIP-7594 + ethereum.org) | raw ✓; **pre ✓** | generation | .35/.50 · .35/.50 |
| vit-cry-005 | Privacy Pools vs Tornado Cash? | Tornado Cash a (no key). Privacy Pools paper/blog: **c**. "association set" occurs in 1 doc (ERC-8262) | raw Tornado ×4; no key | coverage | .23/.20 · .20/.20 |
| vit-cry-006 | What is quadratic funding, main weakness? | b: full15 only (rank 683k) | raw = DeFi, Quadratic sieve, ZK page (article-mode hit is a key-proxy artifact); exact pre ✗ | coverage | .42/.48 · .41/.49 |
| vit-cry-007 | What is d/acc? | **c** (the post author blog; "defensive accelerationism" 0 hits) | raw = Wikivoyage: Accra ×3, all dropped | coverage | .33/.27 · .33/.27 |
| vit-cry-010 | Main lessons of the 2016 DAO hack? | a (ethereum.org fork timeline, article level); "The DAO" b: full15 (rank 306k) | raw ✓; pre ✗ in A+v5; **pre ✓ in top100k arm** | compression / coverage | .30/.50 · .28/.50 |

Probes:
- "Which ones has NIST standardized?": the NIST, Quantum cryptography and PQ-on-Ethereum articles are retrieved, but 0 of 3 algorithm facets are in the passages, so it declines.
- "ML-DSA vs SLH-DSA": Lattice-based ×2 is dropped as off-topic and only SPHINCS+ is kept. The answer says "ML-DSA is a modified version of the DSA", which is **wrong**.
- "SPHINCS+, why quantum-resistant": 3/3 facets, answered.
- "Ethereum survive a quantum computer breaking EC signatures": only the ethereum.org ZK page survives, and the answer is thin.

### Class 3: "Tell me about Japan" / country overviews

| id | question | Cov | raw → pre | Loss stage | Ratio |
|---|---|---|---|---|---|
| lan-exp-001 | Quick overview of Singapore… | a (Wikivoyage) + v5 + top100k | raw ✓; **pre ✓** | — | .57/.63 · .40/.67 |
| lan-exp-003 | Essentials on Kenya… | a (Wikivoyage: Kenya 64k chars) + v5 | raw = Wikivoyage Angola/Mexico/Bangladesh/Nairobi; **the Kenya guide and lead are not retrieved**; 2 dropped → empty | retrieval + gate | .75/.77 (memory) · .75/.75 |
| lan-exp-004 | What is Kyoto known for…? | a + v5 + top100k | **pre ✓**; 1.5B declines anyway | generation (1.5B) | .27/.68 · .32/.65 |
| lan-exp-007 | Describe Greenland (governance, capital, population, ice share) | b: top100k Greenland body; the vital5 lead and Wikivoyage lack population/ice share | pre ✗ | coverage | .23/.75 · .73/.78 |
| vit-sci-002 | More densely populated, Japan or Germany, by how much? | b: top100k Japan body; no vital5 lead, no Wikivoyage | raw = Wikivoyage German Empire / Pacific War / Tokyo. **top100k arm: "Population density" ×3, all dropped → empty** | coverage, then the big pack's ranking | .38/.47 · .43/.27 |

Probe "Tell me about Japan." (`X/l1/ios-v5.traces.jsonl`):
- raw = Wikivoyage: Japan ×3 + **Stablecoin**, in both kits. The vital5 "Japan" lead is **not retrieved** even when installed.
- Facets in the passages: 3 of 7 (no capital, government, history or economy).
- Top100k Japan has the 8 needed sections (Etymology … Culture), and "Demographics/History/Economy/Culture of Japan" are 33–109k chars each (`X/probe.out.txt` §1c).
- Country coverage overall: 246 of 252 geonames countries/territories have a full top100k article (median 74k chars); 228 have a vital5 lead (§1d).
- Probe "Tell me about Kenya": Wikivoyage: Kenya ×3 (+ the vital5 lead with v5). It answers with Nairobi + Swahili, but not 1963.

### Class 4: vegan restaurants (pack note only; places is another agent's lane)

| id | question | Pack coverage |
|---|---|---|
| food-006 | Best vegan restaurants in Tokyo | Routed `task=places` (no text retrieval) in all runs. Wikivoyage Tokyo has **0** "vegan" and 0 "vegetarian" mentions; Tokyo/Berlin district guides 8 in total (`X/probe.out.txt` §3; `X/items.out.txt`) |
| food-001 | Best vegan restaurants in Berlin | `task=places`. Wikivoyage Berlin: vegan ×3, vegetarian ×4. 2,400 of 34,002 guides mention vegan/vegetarian in "Eat" |

### Class 5: specialized travel (transport, altitude, visas, seasons, customs)

| id | question | Cov | raw → pre | Loss stage | Ratio |
|---|---|---|---|---|---|
| vit-trv-003 | Chiang Mai → Pai, and the road? | a: Wikivoyage Pai "Get in › By road" (Rte 1095, 135 km, accidents), Mae Hong Son Loop | raw = Chiang Mai ×3 + MHS Loop; **Pai not retrieved**; the passages shown are Chiang Mai "Buy › Groceries", "Go next" and the lead → pre ✗ | section choice | .31/.47 · .30/.51 |
| vit-hlt-002 | At 4,000 m in the Andes, headache + nausea? | a: Wikivoyage: Altitude sickness (descend, ataxia); b: top100k | raw ✓ ×3; **all dropped** (`context:691->67`, `off-topic-dropped`, `no-good-source`) | gate | .35/.48 · .35/.47 |
| trv-002 | Brazil plug type and voltage? | a: Wikivoyage Brazil (plug, volt, 220) | pre has "plug"/"volt" but not "127"/"220" | partial | .23/.33 · .23/.28 |
| trv-004 | Lisbon airport → city center? | a: Wikivoyage "Lisbon Airport" (metro, bus, taxi) | pre = 4 Lisbon Airport passages with **no** metro/Aerobus/taxi text | section choice | .32/.42 · .29/.42 |
| vit-trv-004 | Walk Paris → Rome and back? | see §3b | | | |

Probes:
- Visa: "Japan with a Brazilian passport" gets the Japan guide. It answers "no visa needed" but "Brazil" is absent from the passages, so the answer isn't grounded.
- Seasons: "best season for trekking in Patagonia" gets Patagonia (Chile), which has no months or season text. It declines.
- Customs: "customs to respect in Japan" gets the Japan guide with etiquette text; answered.
- Altitude + transport: "Cusco → Puno": the Puno guide has altitude ×5 but the passages lack it. It declines.

Wikivoyage section coverage: "Get in" 30,184 / "Get around" 28,466 / **"Respect" 847** / "Stay healthy" 972 / **"Climate" 4,327** out of 34,002 guides. There is no "Via Francigena" guide (`X/probe.out.txt` §3).

## 3b. Priority items: Gríma/Saruman (vit-hum-004) and Paris–Rome (vit-trv-004)

Scores: from `<workspace>/rnd/research/compass/exp/bounty-eval/DEMO-REPORT.v01.md` l.74-75: 4B 0.20 vs Haiku 0.47; 0.29 vs 0.65. Recomputed on `T/*.judgments.jsonl`:
- hum-004: .20 (A-1.5B), .20 (A-4B), .22 (A+v5-1.5B), .20 (A+v5-4B);
- trv-004: .27, .29, .21, .29.

**vit-hum-004: "Why does Gríma kill Saruman in The Lord of the Rings?"**

| Question | Answer | Evidence |
|---|---|---|
| Passage in the default kit? | **No.** vital5 has no "Saruman" or "Gríma Wormtongue" article. Its "The Lord of the Rings" lead (1,362 chars) mentions the Shire but not the killing. Wikivoyage only has "Lord of the Rings tourism" (filming locations) | `X/items.py`-style check, this session; `T/ios-main-v5-s42-kic.traces.jsonl` (pre = "Lord of the Rings tourism › Filming locations") |
| In a built-but-unshipped pack? | **Yes, top100k.** "The Lord of the Rings" › Plot: "Saruman reveals crimes that Wormtongue has done, causing Wormtongue to turn on Saruman and kill him in front of Bag End". "Saruman" (21k chars) and "The Scouring of the Shire" (26k) are full articles. There is no "Gríma Wormtongue" article or redirect in top100k. The 15-shard pack also holds the first two in full (day-view ranks: LOTR 4,658, Saruman 61,981; `exp/04-popularity-subset-size/bench-ranks.txt`) | `<on the mini> … f2text.py` (this session) |
| Did retrieval surface it? | Kit A / A+v5: raw = Wikivoyage "Lord of the Rings tourism" + "Fiction tourism"; 1 dropped as off-topic; key ✗. **top100k arm: yes, partly.** The pre passages include "The Return of the King › Cast: …until he is killed by his own servant, Gríma" plus LOTR Plot › The Two Towers. The *why* sentence (Plot › Return of the King) is **not** among them | `T/ios-main-s42.traces.jsonl`, `T/and-qwen-s42.traces.jsonl`, `T/ios-enwiki-s42-kic.traces.jsonl` |
| Retrieval or generation? | **In the shipped kit: coverage → generation.** With no passage, the 1.5B declines ("The passages found don't support this answer"). The 4B gives a **confident wrong memory answer**, not a refusal: "Gríma Wormtongue does not kill Saruman… killed by… Aragorn… Battle of the Black Gate" (`T/and-qwen-s42`, `T/and-main-v5-s42`; s43: "…Battle of the Fords of Isen"). **With top100k: the passage arrives, but generation garbles it.** The 1.5B says "…after stabbing Saruman's master, is shot by Legolas" (film plot); the 4B says "does not kill Saruman… killed by Treebeard" (`T/and-enwiki-s42.traces.jsonl`). The exp-31 card should read "confident-wrong", not "over-refusal", for the 4B | traces above |
| Concrete missing content | The full LOTR plot / "Scouring of the Shire" / "Saruman" article bodies (top100k already has them). Then section selection must prefer "Plot › The Return of the King" over the film "Cast" sections | |

**vit-trv-004: "How far is it to walk from Paris to Rome and back?"** (key: ~2,7xx–2,8xx km)

| Question | Answer | Evidence |
|---|---|---|
| Passage in the default kit? | **No.** Wikivoyage has no Via Francigena or Paris→Rome itinerary guide. "Florence" › Get in gives "Paris (17 hours)" by train. "Rome" › Get in mentions Paris only as a low-cost flight destination. Wikipedia Paris/Rome leads have no inter-city km | `X/probe.out.txt` §3 ("Wikivoyage 'Via Francigena': -"); scan this session |
| In a built-but-unshipped pack? | **No usable passage.** Paris/Rome full articles in top100k (120k/110k chars) give no Paris–Rome km. "Via Francigena" is not in top100k (rank 119k) but would be in the 15-shard pack; it gives Canterbury→Rome "some 1,700 km" / "~2,000 km by bicycle", not Paris→Rome. The live article has no key (`exp/03 …/fulltext/Via_Francigena.txt`; `X/items.out.txt` "live key=False") | |
| Computable offline? | **Yes.** `shared-data/poi/cities15000.txt` (geonames, already local) gives Paris 48.853, 2.349 and Rome 41.892, 12.511: **1,107 km great-circle**. With a ×1.25 road/foot detour that is ≈ 1,384 km one way, **≈ 2,767 km round trip**, which matches the key. The engine already has `distanceMeters` (`src/routing/geo.ts:197`), used only for POIs | this session |
| Did retrieval surface it? | No. raw = Wikivoyage Florence / Lozère / Paris / Algiers. pre = Florence › Do ("Great places to walk include along the Arno…"; `context:620->77`). With top100k: Florence + Bella Hadid / Heidelberg University / Bouguereau noise | `T/ios-main-v5-s42-kic.traces.jsonl`, `T/ios-enwiki-s42-kic.traces.jsonl` |
| Retrieval or generation? | **No passage exists, then the arithmetic fails.** The 1.5B declines. The 4B answers from memory: "approximately 1,200 km one way… over 2,400 km total" (`T/and-qwen-s42`, `T/and-main-v5-s42`, `T/and-enwiki-s42`). That is near the great-circle distance, but with no walking detour, so it misses the key band. More packs won't fix this; the fix is a distance tool | |
| Concrete missing content | A city-to-city distance capability (geonames coordinates + detour factor + walking pace), or a Wikivoyage/Wikipedia passage with the Paris–Rome road/walking distance (none found offline) | |

## 4. Top gaps, ranked by how often the post author-style items hit them

Counts are over the 25 items above plus the 12 probes.

| # | Gap | Hits | Concrete missing content | Where it exists |
|---|---|---|---|---|
| 1 | **Wikipedia article bodies** (vital5 is lead-only) | 8 items (hum-003, hum-004, hum-006, cry-006, cry-010, lan-exp-007, vit-sci-002, hum-001 for depth) + 3 probes (Japan, Xunzi, Legalism) | Body text of: Mohism (doctrines; Mozi's replies to critics); Mozi (rank 176k); Mencius, Xunzi, Han Fei, Legalism, Hundred Schools; Harm principle (objections); Quadratic funding (collusion/sybil); The DAO (reentrancy, fork, ETC); Greenland (population ~56k, ~80% ice); Japan (density ~330/km²; Government/Economy/History sections); LOTR plot | top100k covers Mohism, LOTR, Greenland, Japan, Kyoto (4 of 8). The rest (Mozi, Mencius, Harm principle, QF, The DAO) need the **15-shard pack or a ~top-700k subset** (`exp/04` ranks) |
| 2 | **Retrieval loses installed keys** (not a pack gap; listed because it costs more items than any missing pack) | 9 of 14 in-kit items + 6 probes | Compression/section choice: hum-002, cry-001, cry-002, cry-010, trv-003, trv-004(Lisbon), PQ-NIST probe, Puno probe. Gates: hlt-002, lan-exp-003. Noise: hum-001 (TrueCrypt), Xunzi probe (ERCs), Japan probe (Stablecoin) | kit A + vital5 already |
| 3 | **the post author's own writing / Ethereum research forum** | 4 items (cry-001 canonical, cry-005, cry-007, trv-004 origin) | vitalik.eth.limo posts (d/acc 2023/2025, Privacy Pools 2025-04-14, secure_llms 2026-04-02); ethresear.ch "How to hard-fork to save most users' funds in a quantum emergency"; the Privacy Pools paper (association sets) | nowhere offline |
| 4 | **Inter-city distance / computed travel facts** | 2 items (trv-004, sci-002 "by how much") + Puno probe | Paris–Rome walking distance; density ratio arithmetic | coordinates are already local (geonames); needs a tool, not a pack |
| 5 | **Thin Wikivoyage sections** for seasons/customs/health | 3 probes (Patagonia, Puno, visa grounding) + food-006 | "Respect" (847/34,002), "Climate" (4,327), "Stay healthy" (972); Patagonia "when to go"; Tokyo guide "vegan" 0 mentions; no Via Francigena guide | partly Wikipedia climate articles (full15); places via OSM (other lane) |
| 6 | **Standards and primary texts** | 2–3 (hum-005 phrase count, hum-006 On Liberty, PQ probes) | NIST FIPS 203/204/205 (parameter sets, sizes; Falcon/FN-DSA is 0× in the pack's NIST article); Gutenberg *Wealth of Nations* #3300 and *On Liberty* #34901 | nowhere offline (`cards/primary-texts-pack.md`) |

## 5. UNKNOWN

- What the claim build's install instructions tell users to download: the wizard default (`standard`) vs kit A vs kit A + vital5. The coverage numbers above assume kit A.
- The 15-shard pack (`boar-wiki-en-00…14`) was never run. "full15" coverage is inferred from exp-04 pageview ranks + live-article text, not from its own text. Only shard 07 is local.
- The top100k-arm traces (`T/ios-enwiki-*`, `T/and-enwiki-*`) used the **mislabeled lead vectors** (`aff5fd11`). Their retrieval rows are confounded (`cards/full-enwiki-pack-arm.md` §Status note). The fixed-pack runs (`g1plus/*`) are not on this machine.
- The key matcher is a loose substring proxy. Some article-mode "raw ✓" hits are artifacts (vit-cry-006, vit-trv-004), so the exact `pre` column is the one to trust.
- Probe facets (`X/l1/analyze.py`) are my own regexes, not frozen keys. The probes are 1 seed and the 1.5B profile only; there are no judged scores for probes.
- Licenses for vitalik.eth.limo and ethresear.ch content (needed before packing gap #3).
- Whether a ×1.25 detour factor is the right walking estimate (the post author's own figure, from the secure_llms post, is not stored offline).
- Places/vegan coverage is only noted here; OSM pack quality is another agent's study.
