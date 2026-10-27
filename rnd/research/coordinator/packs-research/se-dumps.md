# Stack Exchange dumps: access, licence, sizes, offline packs, evals

Research date: 2026-10-12. Read-only pass (WebSearch/WebFetch only, no downloads). Every number has a URL. UNVERIFIED = not confirmed in this pass.
Note: stackexchange.com, stackoverflow.com and api.stackexchange.com were blocked for fetching, so current SE terms are UNVERIFIED.

## TL;DR
- **Legal:** user content is CC BY-SA (3.0 or 4.0 by post date) with attribution. Since 2024-07-12 official dumps are per-site, login-gated, and carry an agreement that excludes LLM training. **Practical:** not an anonymous download from stackexchange.com.
- **Practical route:** archive.org/details/stackexchange still lists the 7z files (last item update 2025-06-24). Whether they download anonymously today is UNVERIFIED. Kiwix ZIMs for most target sites are already built and dated 2026.
- **Size:** the 22 target sites total about 3.2 GB of 7z; with Super User and Ask Ubuntu, about 5.6 GB. Kiwix ZIMs for the same sites total about 7 GB (ZIM is HTML, not SQLite).
- **Gaps:** question counts, the 2025–26 terms, and the licence of derived packs are not verified. personalfinance and medicalsciences are not in the 7z listing; use money and health.

## 1. Licence and access

| Item | Finding | Source |
|---|---|---|
| Content licence by date | before 2011-04-08: CC BY-SA 2.5; 2011-04-08 to 2018-05-01: 3.0; from 2018-05-02: 4.0 | https://huggingface.co/datasets/flymin/stackexchange_20260331 (secondary); https://wiki.archiveteam.org/index.php/Stack_Overflow |
| Attribution | "Visually display or otherwise indicate the source of the content as coming from the Stack Exchange Network" | https://archive.org/details/stackexchange |
| archive.org | Announced 2024-07-12: dumps "would no longer be publicly accessible on archive.org". Archive status: "Unknown (since 2024)" | https://wiki.archiveteam.org/index.php/Stack_Overflow |
| Access | Dumps "accessed via the user profile, which requires login" | https://www.devclass.com/development/2024/07/30/stack-exchange-restricts-access-to-dump-of-user-contributed-data-critics-complain-this-contradicts-license/1625192 |
| Agreement (quoted) | "for my own use and for projects that do not include training a large language model (LLM)"; "Stack Overflow reserves the right to decline to allow me access to future downloads of this data dump." | https://search.feep.dev/blog/post/2025-02-20-state-of-stackexchange ; Archive Team wiki (same URL as above) |
| Earlier draft | Required "non-commercial use", later narrowed to the LLM clause | devclass link above |
| Licence conflict | Archive Team: the restrictions "are not compatible with CC BY-SA" (secondary opinion) | https://wiki.archiveteam.org/index.php/Stack_Overflow |
| Volunteer mirror | 2024-12-31 dump, 95.47 GB, "Various versions of CC-By-SA", mirrored from archive.org/details/stackexchange_20241231 | https://academictorrents.com/details/9132fa0997b430e863d3e053509a263c54ce12f3 |
| Unofficial 2026 dump | Data up to 2026-03-31, 98.4 GB, excludes windowsphone; card says CC BY-SA. Provenance and legal status UNVERIFIED | https://huggingface.co/datasets/flymin/stackexchange_20260331 |
| 2025–26 terms | Any change to the 2024 terms: UNVERIFIED (no 2025–26 source found) | searched only |

## 2. Per-site sizes and question counts

7z sizes: archive.org item metadata, bytes converted to MB (1 MB = 10^6 B). Source: https://archive.org/metadata/stackexchange (item last updated 2025-06-24 per metadata; the details page tags the dump "2024-04-02"; which quarter the files come from is UNVERIFIED).
ZIM: latest listed file. Source: https://lb.download.kiwix.org/zim/stack_exchange/ (download.kiwix.org redirects here).
Question counts: UNVERIFIED for every site (data.stackexchange.com and SE domains not reachable).

| Site | 7z (MB) | Kiwix ZIM (latest) | Questions |
|---|---|---|---|
| travel | 156 | 439 M (2026-08) | UNVERIFIED |
| bitcoin | 74 | 148 M (2026-07) | UNVERIFIED |
| ethereum | 107 | 268 M (2026-08) | UNVERIFIED |
| health | 22 | n/a (medicalsciences: 58 M, 2026-02) | UNVERIFIED |
| outdoors | 31 | 135 M (2026-08) | UNVERIFIED |
| cooking | 88 | 226 M (2026-07) | UNVERIFIED |
| diy | 227 | 1.9 G (2026-08) | UNVERIFIED |
| gardening | 44 | 884 M (2026-08) | UNVERIFIED |
| pets | 27 | 83 M (2026-08) | UNVERIFIED |
| money (personalfinance not in 7z list) | 133 | 242 M (2026-08) | UNVERIFIED |
| law | 103 | 177 M (2026-08) | UNVERIFIED |
| physics | 729 | 1.7 G (2026-08) | UNVERIFIED |
| biology | 83 | 403 M (2026-07) | UNVERIFIED |
| chemistry | 126 | 398 M (2026-07) | UNVERIFIED |
| history | 93 | 306 M (2026-08) | UNVERIFIED |
| english | 451 | 735 M (2026-08) | UNVERIFIED |
| ell | 237 | 450 M (2026-08) | UNVERIFIED |
| academia | 199 | 279 M (2026-07) | UNVERIFIED |
| workplace | 201 | 234 M (2026-08) | UNVERIFIED |
| parenting | 46 | 57 M (2026-08) | UNVERIFIED |
| lifehacks | 14 | 46 M (2026-08) | UNVERIFIED |
| sustainability (closest to "preparedness") | 10 | 26 M (2026-08) | UNVERIFIED |
| Super User (reference) | 1,294 | 3.7 G (2026-08) | UNVERIFIED |
| Ask Ubuntu (reference) | 1,072 | 2.6 G (2026-06) | UNVERIFIED |

- Sum of the 22 target 7z files: about 3.2 GB.
- No site named "emergency" or "preparedness" appears in the listing.
- Uncompressed Posts.xml sizes: UNVERIFIED (not in the listing).

## 3. Offline packagings and tools

| Item | Finding | Source |
|---|---|---|
| Kiwix ZIM collection | Per-site ZIMs, two snapshots (2026-02 and 2026-08 for most) | https://lb.download.kiwix.org/zim/stack_exchange/ |
| ZIM licence notice | UNVERIFIED (the ZIM /about page returned 404). The kiwix.org footer CC-BY-SA covers the website only | https://kiwix.org/en/ |
| sotoki | GPL-3.0; scrapes IA dumps via `--mirror` and `--domain`; outputs ZIM, not SQLite | https://github.com/kiwix/sotoki |
| se-data-dump-transformer | Found in search, not verified | https://gh.nn.ci/LunarWatcher/se-data-dump-transformer |
| sotorrent, stackexchange-dump-to-postgres | Not searched or fetched: UNVERIFIED | none |

For BOAR's SQLite + FTS5 packs no existing converter was verified. Building one from Posts.xml is the default path.

## 4. Evaluations using Stack Exchange

| Benchmark | What it measures | Licence |
|---|---|---|
| LoTTE (ColBERTv2) | Retrieval over StackExchange answer posts. Five domains (writing, recreation, science, technology, lifestyle) plus pooled. 12 test sets, 500–2,000 queries, 100k–2M passages. Search queries come from GooAQ, forum queries are post titles. Metric Success@5. Source: https://arxiv.org/html/2112.01488v3 | UNVERIFIED (HF card blank in fetch: https://huggingface.co/datasets/colbertv2/lotte) |
| CQADupStack (BEIR) | Duplicate-question retrieval across StackExchange subforums (from memory, UNVERIFIED in fetch). Paper: https://arxiv.org/pdf/2104.08663 | Conflict. Apache 2.0 per BEIR appendix, via BiCA table https://arxiv.org/pdf/2511.08029 (secondary). A split card says cc-by-sa-4.0: https://huggingface.co/datasets/orgrctera/beir_cqadupstack_programmers/commit/cdd1d6b2f76bfc4cc756a25694c3cf78d8006edf |
| RAG QA on SE for explanation or comparison | None found in this pass | UNVERIFIED gap |

Neither benchmark measures answer quality for explanation or comparison questions. Both measure retrieval of similar or answer posts.

## Open questions
1. Are the 7z files anonymously downloadable from archive.org today? UNVERIFIED. Test by hand (no login).
2. Do the 2024 "own use" and LLM clauses allow distributing derived SQLite packs on phones? Needs a legal read. Accepting the agreement is a user action.
3. Licence of the Kiwix ZIMs and of the unofficial 2026 HF dump.
4. Per-site question counts: Data Explorer, PostTypeId = 1 grouped by site. Not reachable from here.
5. Attribution format for a pack: author names and links per post, as required by the 2014 SE text (not fetched directly).
6. CQADupStack licence: Apache 2.0 or CC BY-SA? Check the BEIR appendix directly.
7. Does any published RAG eval use SE answers as the corpus for explanation or comparison questions? Not found.
