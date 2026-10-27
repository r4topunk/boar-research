# Offline knowledge packaging: what existing projects ship (research, as of 2026-10-12)

Scope: read-only web research. Kiwix download pages and openZIM wiki are behind an Anubis bot wall in this run, so catalogue data comes from the Kiwix OPDS feed and project READMEs. Anything marked UNVERIFIED was not confirmed from a primary page.

## TL;DR
1. Kiwix/ZIM is the de facto offline-content standard: 1,301 entries in the OPDS feed, Wikipedia maxi 127.4 GB, medical items from 14 MB to 3.4 GiB. ZIM is GPL, Xapian-indexed, and has no SQLite export path found (UNVERIFIED).
2. No source ranks offline modules by demand. Health and education are the stated priorities of IIAB and RACHEL, but no usage data was found.
3. On-device RAG apps are few: AnythingLLM Mobile (Android, private beta) is the only one found with documented on-device document RAG. PocketPal (MIT) and Private LLM have no pack or RAG feature.
4. Vector storage is feasible on paper: 500k x 384-d int8 is about 183 MiB. No phone latency for brute-force or HNSW at that scale was found, so BOAR must measure it.
5. Stack Exchange dumps (CC BY-SA 4.0) are the only question-shaped source in the Kiwix catalogue. Their attribution rules need to be carried into every pack row.

## 1. Kiwix / openZIM

### 1a. Catalogue (OPDS feed, sizes as listed)
Source: https://opds.library.kiwix.org/catalog/v2/entries?count=-1&lang=eng (feed `totalResults` 1301; only about 85 entries were readable, so counts below are lower bounds).

| Name (example) | Group | Size | Date | Licence |
|---|---|---|---|---|
| wikipedia_en_all_maxi_2026-08 | Wikipedia | 127.4 GB | 2026-08-25 | not in feed |
| wikivoyage_en_all_maxi_2026-09 | Wikivoyage | 1.07 GB | 2026-09-13 | not in feed |
| medlineplus.gov_en_all_2025-01 | medical | 1.94 GB | 2025-01-04 | not in feed |
| nhs.uk_en_medicines_2026-09b | medical | 14.6 MiB | 2026-09-18 | not in feed |
| libretexts.org_en_med_2025-01 | medical | 1.11 GiB | 2025-01-16 | not in feed |
| zimgit-medicine_en_2024-08 | medical | 66.9 MiB | 2024-08-29 | not in feed |
| ted_mul_medicine_2026-09 | TED | 3.36 GiB | 2026-09-14 | not in feed |
| ted_mul_ai_2026-09 | TED | 3.82 GB | 2026-09-09 | not in feed |
| gutenberg_en_lcc-q_2026-03 | Gutenberg | 17.7 GB | 2026-03-06 | not in feed |
| docs.python.org_en_all_2026-08a | docs | 3.96 GB | 2026-08-28 | not in feed |
| freecodecamp_en_all_2026-08 | tutorials | 7.9 MB | 2026-08-21 | not in feed |
| ru.stackoverflow.com_mul_all_2026-08 | Stack Exchange | 2.69 GB | 2026-08-06 | not in feed |
| medicalsciences.stackexchange.com_en_all_2026-02 | Stack Exchange | 58.0 MiB | 2026-02-02 | not in feed |
| gotquestions.org_en_all_2026-07 | Q&A (religion) | 15.18 GB | 2026-07-20 | not in feed |
| mediawiki_en_all | wiki | 6.83 GB | 2023-07-05 | not in feed |

Not seen in the readable part of the feed: Wiktionary, Wikibooks, Khan Academy, PhET, MDN, DevDocs, iFixit, wikiHow (UNVERIFIED: may sit in the truncated part of the feed). Wikimed as a named collection was not found; the medical items above are the closest.

Wikipedia size variants (mini/nopic/maxi): a German guide (search snippet only, not fetched) gives 13.39 GB / 49.98 GB / 95.2 GB, undated, UNVERIFIED. Kiwix FAQ (https://www.kiwix.org/faq/, snippet only) says mini is about 95 % smaller and nopic about 75 % smaller than full, which contradicts the guide's figures. Treat both as UNVERIFIED. Current sizes: the OPDS feed above (maxi only). Download index (redirects to https://hub.kiwix.org/downloads/) was blocked by Anubis.

Licence: Kiwix does not list licences in the feed. Wikipedia and Wikivoyage content is CC BY-SA; Stack Exchange is CC BY-SA 4.0 (see 1d).

### 1b. ZIM format and tooling
| Name | What | Size | Licence | URL | Notes |
|---|---|---|---|---|---|
| libzim | reference C++ library for ZIM read/write | n/a | GPLv2+ | https://github.com/openzim/libzim | zstd and LZMA and ICU required; Xapian optional, on by default (`-Dwith_xapian=false` removes search) |
| python-libzim | Python binding | n/a | GPLv3+ | https://github.com/openzim/python-libzim | `Archive`, `get_entry_by_path`, `Searcher`/`Query` for full-text; no iteration example shown |
| zim-tools | zimdump, zimcheck, zimsplit, zimwriterfs | n/a | GPLv3+ | https://github.com/openzim/zim-tools | zimdump "inspects or dumps (part of)" a file; no SQLite export documented |
| Kiwix for Android | ZIM reader app | app | GPL-3.0+ | https://github.com/kiwix/kiwix-android | Android 7.1 to 15; Play build only reads app folders; full-text search not stated |
| sotoki | Stack Exchange dump to ZIM | n/a | GPL-3 (tool) | https://pypi.org/project/sotoki | content licence CC BY-SA 4.0 |

Format facts: ZIM uses zstd clusters by default since 2021, with LZMA2 supported, up to about 3:1 (secondary source, Wikipedia ZIM article: https://en.wikipedia.org/wiki/ZIM_(file_format)). Xapian index is inside the file (UNVERIFIED: spec page wiki.openzim.org blocked; not confirmed from primary source).
ZIM to SQLite: no tool found. Route would be zimdump or python-libzim iteration, then FTS5 import. UNVERIFIED that it is practical at Wikipedia scale.

### 1c. Question-shaped vs encyclopedic
| Shape | Collections |
|---|---|
| Question-shaped (Q&A) | Stack Exchange sites (medicalsciences, ru.stackoverflow, others), gotquestions.org (UNVERIFIED shape) |
| Encyclopedic | Wikipedia (all variants), Wikivoyage, Wiktionary, MedlinePlus, NHS medicines, LibreTexts, Gutenberg, zimgit-medicine |
| Task or doc-shaped | docs.python.org, DevDocs, MDN (UNVERIFIED presence in feed), iFixit, wikiHow (UNVERIFIED) |

### 1d. Stack Exchange licence
Dumps are CC BY-SA 4.0 with attribution. The 2014 attribution list asks for: network name, link to original post, author names, author links. Dumps moved behind login in July 2024. Sources: https://pypi.org/project/sotoki; https://wiki.archiveteam.org/index.php/Stack_Exchange (check current terms; this list is from 2014, UNVERIFIED as current).

## 2. Internet-in-a-Box (IIAB) and RACHEL

| Name | What | Size | Licence | URL | Notes |
|---|---|---|---|---|---|
| Internet-in-a-Box (IIAB) | offline server distro (Raspberry Pi, NUC) | "multi-gigabyte" packs, no sizes | GPL-2.0 | https://github.com/iiab/iiab | content named: Wikipedia, Khan Academy videos, OpenStreetMap, e-books, WordPress, electronics projects. No categories, no ranking. |
| IIAB via Kiwix/OER2GO | ZIM packs and OER2GO/RACHEL modules | n/a | varies | https://www.bgr.com/1998047/raspberry-pi-internet-in-a-box/ (secondary) | Wikipedia, Khan, Gutenberg, WikiHow listed in secondary sources |
| RACHEL / VT-Rachel | curated OER offline server | 44 GB total (2019) | varies | https://groups.google.com/g/village-telco-dev/c/pYlnRKQdYYw/m/9Y-OGb9OAgAJ | 64 GB media needed; 4 kB block-size fix; 2019 figure |
| RACHEL-Pi | Kiwix add-on | n/a | varies | https://community.worldpossible.org/t/add-kiwix-zim-file-to-rachel-pi/674 | English RACHEL-Pi lacks Kiwix; newer ZIM does not run on bundled kiwix-serve |
| rachel.worldpossible.org | project site | n/a | n/a | https://rachel.worldpossible.org/ | no module list on the page |

Demand ranking: none found. IIAB and RACHEL position on health and education, but no usage data was found. A Columbia needs assessment of healthcare providers in the Dominican Republic exists (https://www.sipa.columbia.edu/wikipedia-project-offline-education-medicine); its findings were not retrieved (UNVERIFIED). Deployments claimed in "over 100 countries" (secondary, UNVERIFIED).

## 3. Offline / on-device LLM apps with packs or offline RAG

| App | Platform | Packaging / RAG | Licence | URL | Notes |
|---|---|---|---|---|---|
| AnythingLLM Mobile | Android only (iOS planned) | on-device RAG over user documents; private beta | not verified | https://docs.anythingllm.com/mobile/overview | 10k+ installs per a mirror (UNVERIFIED) |
| PocketPal AI | iOS, Android | GGUF models; no RAG, no packs | MIT | https://github.com/a-ghorbani/pocketpal-ai | benchmark sharing, Pals persona sharing; no pack sharing |
| Private LLM | Apple only | chat; no RAG or pack evidence found | commercial | https://privatellm.app/faq | fully offline except for model updates |
| Survive AI | Android | README: runs on 4 GB phone, Gemma 2B ~500 MB | not verified | https://github.com/s-samarth/survive-ai | single developer, claims unverified |
| iAny | browser PWA | offline-first RAG | not verified | https://github.com/sengtha/iAny | installable on Android |
| Project N.O.M.A.D. | desktop | Ollama + Kiwix offline Wikipedia + document search | not verified | https://andrew.ooo/posts/project-nomad-offline-survival-computer/ | launched March 2026 (secondary) |
| OfflineLLM | Android | llama.cpp chat; no RAG | open source | (UNVERIFIED URL: from search) | no RAG or Wikipedia |
| MLC Chat, Layla, Khoj mobile | mixed | not checked in this run | n/a | n/a | UNVERIFIED: offline pack behaviour |

Authoring and sharing of packs: none of the apps above was found to let users author or share knowledge packs. Attribution and licensing of packs: no example found (UNVERIFIED that none exists).

Domain demand from reviews/READMEs: survival and prepper framing appears in Survive AI and N.O.M.A.D.; no review data was found. A May 2026 Reddit thread estimated English text-only Wikipedia at about 24 GB (individual estimate, UNVERIFIED): https://reddit.sentinel-team.org/posts/1szqmn5/snapshots/2026-05-02T03%3A06%3A21.60641Z

## 4. Vector storage for small devices and corpora

### 4a. Engines
| Name | What | Licence | URL | Mobile notes |
|---|---|---|---|---|
| sqlite-vec | SQLite extension; `vec0` tables; float, int8, binary; KNN (brute force in docs) | Apache-2.0 / MIT | https://github.com/asg017/sqlite-vec | pre-v1; platforms listed: Linux, macOS, Windows, WASM, Raspberry Pi; Android/iOS not mentioned. IVF and DiskANN source files exist, status UNVERIFIED |
| sqlite-vector (Bambini) | alternative SQLite extension, quantized scan | n/a | https://marcobambini.substack.com/p/the-state-of-vector-search-in-sqlite | comparison post, not sqlite-vec |
| Qdrant Edge | in-process engine; Dart/Flutter SDK, Swift and Kotlin bindings | not verified | https://qdrant.tech/edge/ | iOS arm64 and Android arm64/x86_64 in the Dart package (pre-release, unverified uploader: https://pub.dev/documentation/qdrant_edge/) |
| LanceDB | embedded DB | not verified | https://lancedb.github.io/lancedb/ | SDKs listed: Python, JS/TS, Java, Rust; no mobile bindings in the docs page |

### 4b. Numbers
| Measurement | Value | Source |
|---|---|---|
| sqlite-vec full scan, 100k x 384 float32, M1 Pro | about 68 ms per query | https://marcobambini.substack.com/p/the-state-of-vector-search-in-sqlite |
| same test, quantized scan (sqlite-vector, not sqlite-vec) | 17.4 ms; preload 4.0 ms; float32 scan about 57 ms | same |
| sqlite-vec at 500k x 384 float32 | about 340 ms (linear extrapolation, mine, not measured) | derived |
| Brute force, single-core desktop, public ANN sets | 14.2 QPS, p95 71 ms; HNSW 95 to 99 % recall several hundred times faster | https://stoolap.io/docs/performance/ann-benchmarks/ (non-sqlite engine) |
| Qdrant Edge, on iPhone 16 Pro, 10k vectors | about 0.1 ms on device vs about 52 ms via cloud over cellular; 11 MB install | https://qdrant.tech/blog/qdrant-edge-on-device-vector-search/ (vendor, dimension not stated) |
| Phone-side brute force or HNSW at 500k x 384 int8 | no published number found | gap |

Storage arithmetic (mine): 500k x 384 int8 = 192 MB (183 MiB); same at float32 = 768 MB. 1M x 1024-d float32 = 4.1 GB.

### 4c. Wikipedia embedding datasets
| Dataset | Content | Size | Licence | URL |
|---|---|---|---|---|
| Cohere/wikipedia-2023-11-embed-multilingual-v3 | 247,154,006 paragraphs, 323 language subsets, Cohere embed v3, 1024-d; snapshot 2023-11-01 | size and licence not stated on card | not stated on card | https://huggingface.co/datasets/Cohere/wikipedia-2023-11-embed-multilingual-v3 |
| upstash/wikipedia-2024-06-bge-m3 | about 144M paragraphs (count inconsistent on the page), 11 languages, BGE-M3 1024-d, Parquet | about 633 GB | Apache-2.0 | https://huggingface.co/datasets/upstash/wikipedia-2024-06-bge-m3 |
| wikimedia/structured-wikipedia | 10.47M EN and FR articles, parsed infoboxes, sections, tables, references; extracted 2026-05-13 (beta) | 44.4 GiB Parquet | CC BY-SA 4.0 | https://huggingface.co/datasets/wikimedia/structured-wikipedia |

## What this implies for BOAR packs
- Demand evidence is weak everywhere. No source ranks domains by usage. Ranking below uses catalogue presence and project positioning only (UNVERIFIED as demand): (1) medical/health (MedlinePlus, NHS, LibreTexts, zimgit-medicine, IIAB and RACHEL positioning); (2) general encyclopedic (Wikipedia, Wikivoyage); (3) education (TED, Gutenberg, Khan, if present); (4) Stack Exchange Q&A for question-shaped retrieval.
- Keep SQLite + FTS5 as the pack format. It already matches the engine and is the target of the ZIM-to-SQLite conversion, which is still unverified.
- Make ZIM the upstream source where one exists: it carries licence and provenance and is maintained by openZIM. Convert at build time, not on device.
- Put licence and source URL in every row (CC BY-SA requires attribution; Stack Exchange needs network, link, author). Ship a per-pack NOTICE file.
- Size: no user-acceptance data found. Kiwix medical items (14 MB to 3.4 GiB) suggest per-domain packs in the 10 MB to 1 GB range are normal in this ecosystem (UNVERIFIED as user acceptance).
- Embeddings: 500k x 384 int8 at 192 MB fits a phone budget. Brute force at that size is plausible only with int8 and a measured latency on target device; no published phone number exists.
- Use Qdrant Edge or sqlite-vec as candidate engines to benchmark on the target device. Do not adopt either on the basis of this research.
- Avoid a community pack-sharing feature until attribution rules are in the format (no competitor shows a working model in this run).
- Follow the Kiwix Android storage constraint: store packs in app-accessible storage, not arbitrary paths (Play build restriction).

## Open questions
- Which Kiwix collections exist beyond the readable OPDS part (Wiktionary, Wikibooks, Khan, MDN, DevDocs, iFixit, wikiHow)? Needs the full OPDS feed or hub.kiwix.org access.
- Current Wikipedia mini/nopic sizes and licences per variant.
- Does zimdump or python-libzim iteration yield a practical ZIM to SQLite path for multi-GB packs?
- Are there published demand datasets for IIAB, RACHEL or Kiwix (download counts, request logs)? Columbia Dominican Republic findings?
- Phone latency for sqlite-vec brute force and HNSW at 500k x 384 int8 (needs BOAR bench on the Pixel 8a or iPhone).
- sqlite-vec mobile support and IVF/DiskANN status.
- Qdrant Edge licence and Android Swift/Kotlin status; Stack Exchange attribution terms after July 2024.
- Are there community pack formats for offline apps (MLC, Layla, Khoj mobile) to inspect?
