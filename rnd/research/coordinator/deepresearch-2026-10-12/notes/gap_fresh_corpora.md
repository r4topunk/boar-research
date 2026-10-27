# Gap angle: fresh and permissive corpora for the absent-knowledge bucket

Researcher: gap_fresh_corpora, 2026-10-12. Method: dumps.wikimedia.org listings, Kiwix OPDS + download mirror, HF Hub API / dataset cards / datasets-server, Wikimedia REST metrics + MediaWiki API (anonymous, read-only), WebSearch/WebFetch for primary pages and arXiv HTML, and our own builder (`boar-app/scripts/build-wiki-pack.mjs`) and shard metadata (`shared-data/packs/*.sqlite.json`, `run-en-shards.log`). This extends `notes/datastores.md`, which already covers FCDO, Stack Exchange, CDC, MedlinePlus, WikEM, the Kiwix licence map, OpenStax's licence change, FineWeb-Edu "compilation-only" licensing and a competitor team's freshness run. Those items are not repeated here.

**Rule disclosure.** To build the citation histogram (Q4), I paged the public `lmarena-ai/search-arena-v1-7k` rows through the HF datasets-server API, 100 rows per call. The JSON pages came to **145 MB** on disk, over the 100 MB download rule. I did not anticipate the JSON overhead (I estimated about 80 MB). The pages held user prompts (CC-BY-4.0, PII-redacted by LMArena) and model answers. Only domain counts were kept. The cached pages were deleted right after aggregation (`scratchpad/sa_pages` removed). No BOAR bench item was touched.

## TL;DR

- **FineWiki will not refresh.** It is a one-off parse of the August 2025 Enterprise HTML (en: 6,614,655 pages, 35.1 GB), with no refresh cadence on the card, and the dataset was last modified 2025-10-22. The public Enterprise HTML mirror on dumps.wikimedia.org stopped on **2025-03-24**: the 2026 run folders exist but are empty. A newer FineWiki therefore requires someone to pull Enterprise snapshots through an account. https://huggingface.co/datasets/HuggingFaceFW/finewiki · https://dumps.wikimedia.org/other/enterprise_html/
- **The best fresh, accountless, HTML-rendered replacement is `wikimedia/structured-wikipedia`.** It was extracted **13 May 2026** from the Enterprise Structured Contents snapshot: enwiki 7,597,149 rows, 86 parquet shards, 34.61 GiB, CC BY-SA 4.0. It has abstract, sections, **infoboxes, tables and references** as JSON. It is 9 months fresher than our shards and, like FineWiki, renders templates. Needs a parquet → JSONL adapter for `build-wiki-pack.mjs`. https://huggingface.co/datasets/wikimedia/structured-wikipedia
- **The freshest accountless text is `omarkamali/wikipedia-monthly` `20261001.en`** (7,249,754 rows, 27.07 GB uncompressed, CC BY-SA 4.0, updated 2026-10-10). The trade-off is that it is parsed from wikitext with mwparserfromhell, so templates are not expanded and there are no infoboxes. That is exactly the loss FineWiki was built to avoid. https://huggingface.co/datasets/omarkamali/wikipedia-monthly
- **Size of the staleness:** enwiki added **224,682 new content pages** from Sep 2025 to Sep 2026 (≈ 3.4 % of FineWiki's 6.61 M) and edits **1.2–1.5 M distinct content pages per month**. Rebuilding our 15 shards took ≈ 14.5 min/shard on the mini (≈ 3.6 h total; 18.0 GB, 6.12 M articles, 21.4 GB text). Refresh compute is cheap; the download (≈ 12–35 GB) needs r4to's OK. https://wikimedia.org/api/rest_v1/metrics/edited-pages/new/en.wikipedia.org/user/content/monthly/2025090100/2026100100
- **Kiwix offers nothing fresher for "nopic".** `wikipedia_en_all_nopic` is **2026-06** (52.7 GB), `maxi` is 2026-08 (127 GB), and `mini` (intros only) is 2026-09 (14.4 GB). Each ZIM would also need an HTML → text pass through GPL tooling. structured-wikipedia is the better input. https://download.kiwix.org/zim/wikipedia/
- **Synthetic and "educational" corpora fail BOAR's needs:** Cosmopedia v2 is 122 GB (ODC-BY within smollm-corpus), and Cosmopedia v1 is ≈ 92 GB, Apache-2.0, written by Mixtral-8x7B. Both add no facts beyond their generator, which is the NOTES35 mechanism. Nemotron-CC v2 is gated under an "NVIDIA Data Agreement for Model Training" ("for model training purposes only"), so it **cannot ship** as a datastore. I found no published evidence that any synthetic corpus improves RAG QA as a datastore. https://huggingface.co/datasets/HuggingFaceTB/smollm-corpus · https://huggingface.co/datasets/nvidia/Nemotron-CC-v2
- **Shippable news/recency sources are few and small:**
  - Wikinews **closed read-only on 2026-05-04**: 22,237 articles, 47.5 MB bz2.
  - The Wikipedia **Current events portal** is ≈ 9–12 KB of wikitext per day (365 pages per year ≈ 3.6 MB/yr, CC BY-SA). It sits in namespace 100, so it is **not in FineWiki or in any NS0 dataset**.
  - GDELT allows free redistribution but is event/URL metadata, not text. CC-NEWS text stays under the publishers' copyright.
  - https://meta.wikimedia.org/wiki/Public_consultation_about_Wikinews · https://commoncrawl.org/terms-of-use
- **What frontier + web cites: mostly a non-shippable long tail plus UGC.**
  - Allaham & Diakopoulos (4 engines, 712 queries): Wikipedia is the #1 domain at only 3.6 % of citations, the top 25 domains hold 23.8 %, and 59.1 % of domains are cited once.
  - Ahrefs, Google AI Overviews (3 M US queries, Sep 2026): YouTube 22.9 %, Reddit 18.5 %, Facebook 10.1 %, Wikipedia 4.0 % of top-50 share.
  - My pilot over Search Arena-7k (English, link-in-text responses only) agrees: Wikipedia 5.9 % of citations, cited in 13.2 % of citing responses, and 2,682 of 3,773 domains cited once.
  - No corpus choice "by citation share" is available beyond Wikipedia, Stack Exchange and government pages.
  - https://arxiv.org/html/2605.23684v1 · https://ahrefs.com/blog/most-cited-domains-ai-overviews/

## Q1. Freshness options for the Wikipedia base, and rebuild cost

### Takeaway
There are three routes, and none needs a new pipeline beyond a small adapter.
- **(a) structured-wikipedia** (May 2026): HTML-rendered with infoboxes, needs no account. It is the closest drop-in for FineWiki.
- **(b) wikipedia-monthly** (Oct 2026): freshest, but wikitext-parsed (lossy).
- **(c) A Wikimedia Enterprise free account** (account action, r4to): Snapshot or Structured Contents NDJSON, monthly/twice-monthly. Run FineWiki's released `src/` pipeline on it to get a FineWiki-quality Oct 2026 parse.

The rebuild itself is ≈ 4 h on the mini. Do the 0-call anywhere-gate first (critique §0); the refresh only pays if the gate finds the missing facts in the newer text.

### Cited Findings

| item | date | URL | what it is | key numbers | licence | fit to our constraints | BOAR bucket | novelty vs our docs | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| FineWiki (current base) | data Aug 2025; repo last modified 2025-10-22 | https://huggingface.co/datasets/HuggingFaceFW/finewiki | HTML-dump parse, templates rendered, infoboxes as metadata, refs/notes sections stripped | en 6,614,655 pages, 35.1 GB parquet; all langs 61.6 M / 184.7 GB; pipeline code in repo `src/` (datatrove) | CC BY-SA 4.0 + GFDL | already shipped (15 shards) | absent / wrong (stale) | known (in kit; datastores.md flags staleness) | No refresh announced. The card says only "If there is interest… we might upload smaller sampled versions"; no cadence. Treat it as frozen. |
| Enterprise HTML mirror on dumps.wikimedia.org | stopped 2025-03-24 | https://dumps.wikimedia.org/other/enterprise_html/ | the public mirror FineWiki was built from | run dirs 20260801…20261001 exist but list no files; page: "as of 24 March 2025, are no longer replicated on this site" | CC BY-SA content | no public HTML dump after Mar 2025 | — | new | Closes the "just download the newest HTML dump" route. |
| **wikimedia/structured-wikipedia** | extracted 2026-05-13 (repo modified 2026-05-19) | https://huggingface.co/datasets/wikimedia/structured-wikipedia | Enterprise Structured Contents (beta): name, identifier, url, abstract, description, Wikidata QID, infoboxes, sections, tables, references | enwiki_namespace_0: **7,597,149 rows, 86 shards, 34.61 GiB** (card); duplicates possible, so keep the highest `version.identifier` | CC BY-SA 4.0 | download > 100 MB: r4to OK. Adapter: sections JSON → text, infoboxes → `infoboxText` input, `identifier` → page_id | absent (post-Aug-2025 facts), wrong (outdated values) | **new** | **WIKIFRESH-SW.** Gate (0 Claude calls): run the anywhere-check over all absent items (kept and no-kept) against this parquet with BM25 + jev. Proceed only if new hits ≥ 3 on V-para or ≥ 6 on v0.2 beyond the current 15 shards. Cost: download 37 GB; adapter ½ day; rebuild ≈ 4 h on the mini. |
| omarkamali/wikipedia-monthly `20261001.en` | updated 2026-10-10 | https://huggingface.co/datasets/omarkamali/wikipedia-monthly | monthly NS0 pages-articles → mwparserfromhell plain text | **7,249,754 rows; 27.07 GB** (datasets-server); ≥ 11.7 GB parquet (tree listing truncated at 1,000 files); configs monthly from 20250901 | CC BY-SA 4.0 | fields {id,url,title,text}; no infoboxes; templates (e.g. `{{convert}}`, dates, infobox numbers) not rendered | absent (freshest) | **new** | Use as the **gate corpus only** (freshest text for an "is the fact in Wikipedia now?" check). Do not ship as the base unless the gate shows hits that the May 2026 snapshot misses. |
| enwiki XML dump 2026-10-01 | 2026-10-01 | https://dumps.wikimedia.org/enwiki/20261001/ | pages-articles-multistream | 25.1 GB bz2 | CC BY-SA / GFDL | wikitext, same parsing loss as wikipedia-monthly | — | known (we use its redirect/index files) | Only for redirects and the Current-events portal (namespace 100), see Q3. |
| Wikimedia Enterprise free account | free-tier post 2026-06-02 | https://enterprise.wikimedia.com/blog/enhanced-free-api/ | Snapshot API (whole project NDJSON tar.gz), Structured Contents snapshot (beta), On-demand API | free tier: 30 snapshot requests/month, On-demand 50,000/month (post); help centre says twice-monthly snapshots (2nd and 21st); the API page says monthly (conflict) | content CC BY-SA; Enterprise ToS governs access | **account action: r4to only** | absent | new | Option C. If WIKIFRESH-SW passes and a fresher snapshot matters, r4to signs up. Then run FineWiki's `src/` on the Oct 2026 HTML. Cost: account + ≈ 1 day. |
| Kiwix `wikipedia_en_all_*` | nopic 2026-06-17; maxi 2026-08-25; mini 2026-09-09 | https://download.kiwix.org/zim/wikipedia/ | ZIM (HTML + Xapian) | nopic 52.7 GB / 19.19 M entries; maxi 127.4 GB; mini 14.4 GB (intro only) | CC BY-SA content; libzim GPL (build-time only) | no nopic 2026-09/10 exists; HTML → text pass needed | absent | known (datastores.md, SHELF row 42) | Not preferred: older than wikipedia-monthly and heavier than structured-wikipedia. |
| Wikimedia incremental dumps | daily, latest 2026-10-10 | https://dumps.wikimedia.org/other/incr/enwiki/20261010/ | pages-meta-hist-incr (all revisions of changed pages) | **849 MB bz2 per day** | CC BY-SA | too heavy for a monthly delta; full history | — | new | Do not use. A monthly full rebuild (≈ 4 h) is simpler than applying deltas. |
| EventStreams | live | https://stream.wikimedia.org/?doc | SSE feed of recentchange/page-change | — | CC0 metadata | online only; useful only on the build host | — | new | Not needed; monthly rebuild covers it. |
| Enwiki churn since our snapshot | Sep 2025 – Sep 2026 | https://wikimedia.org/api/rest_v1/metrics/edited-pages/new/en.wikipedia.org/user/content/monthly/2025090100/2026100100 | REST metrics | new content pages by users: 15,953–19,667/month, **224,682 total**; distinct edited content pages 1.20–1.52 M/month; live article count 7,251,940 (siteinfo 2026-10-12) | — | — | absent | new | Bounds the gain: ≤ 3.4 % new pages. Most edits are small, so freshness matters for *new events/entities* and changed values, not for most items. |
| Our rebuild cost (measured) | built 2026-10-02 | `shared-data/packs/run-en-shards.log`, `boar-wiki-en-*.sqlite.json` | 15 FineWiki shards → format-2 packs on the mini, one at a time | 18.03 GB packs, 6,124,620 articles, 21.40 GB text; sum `buildSeconds` 3,112 s; shards 08–14 took 101 min wall (≈ 14.5 min/shard) → **≈ 3.6 h for 15** | — | builder reads parquet columns `page_id,title,text,infoboxes` or JSONL `{page_id,title,text,…}` (JSONL is read whole into memory, so keep shards ≲ 1 GB) | — | new (numbers) | An adapter per source (½ day). The pageviews file and the embed-top setting carry over. |

### Inferences
- A fresh base is cheap in compute (≈ 4 h) but costs a ≥ 12 GB download. The decision should hinge on the anywhere-gate, not on a competitor team's +[competitor score removed], which is inside its own ±[competitor score removed] noise (critique §2).
- structured-wikipedia's `references` field lists the external URLs each article cites. That gives an offline, auditable map of which non-Wikipedia domains back Wikipedia's facts, a cheap proxy for "where facts live" without touching our bench (relevance 1, but zero-risk).
- The May 2026 snapshot has 7.6 M rows against FineWiki's 6.6 M. The extra ≈ 1 M are probably disambiguation pages, lists and duplicates, which FineWiki removed. A filter is needed or the shards grow ≈ 15 %.

### Gaps
- FineWiki's own refresh plans: none stated. I found no public HF statement or issue on a 2026 FineWiki.
- Whether the structured-wikipedia enwiki parquet is complete. The card warns of "duplicated, deleted, or missed articles" and "revision discrepancies… with long articles". The missing-article rate is not quantified.
- Enterprise free-tier cadence: monthly (API page, blog) vs twice-monthly (help centre). Unresolved without an account.

## Q2. Permissive synthetic and educational corpora

### Takeaway
None is a good absent-knowledge source for BOAR.
- **Synthetic corpora** restate the generator's parametric knowledge (Mixtral-8x7B, Qwen3-30B-A3B). That is the NOTES35 mechanism, and NOTES35 is closed (hit-rate 2.7 %). Their size (≥ 90 GB) exceeds our ≈ 30 GB free disk.
- **Licences:** Nemotron-CC is training-only. FineWeb-Edu licenses only the compilation (datastores.md). Khan Academy is BY-NC-SA. LibreTexts is mostly NC. Current OpenStax editions are BY-NC-SA, so only the 2024-01 snapshot is CC BY (all three in datastores.md).

### Cited Findings

| item | date | URL | what it is | key numbers | licence | fit to our constraints | BOAR bucket | novelty vs our docs | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| Cosmopedia v1 | 2024-02 (repo modified 2024-08-12) | https://huggingface.co/datasets/HuggingFaceTB/cosmopedia | Mixtral-8x7B-Instruct synthetic textbooks/blogs/stories seeded from web pages and curricula | 30 M+ files, 25 B tokens; parquet: web_samples_v1 38.98 GB, web_samples_v2 32.66, stories 11.9, auto_math 4.46, stanford 3.3, **wikihow 0.50**, openstax 0.35, khanacademy 0.05 (HF tree) | Apache-2.0 (card) | size fails except tiny subsets; content = Mixtral's knowledge (2023) | thin (explanations), not absent | new | Do not ship. At most the 0.5 GB "wikihow" subset as a how-to style source, gated on how-to misses. Prior: low, because the facts are generator-made. |
| Cosmopedia v2 (smollm-corpus) | 2024-07 (modified 2024-09-06) | https://huggingface.co/datasets/HuggingFaceTB/smollm-corpus | 39 M textbooks/blogs/stories by Mixtral-8x7B, topic-seeded | **122.36 GB** parquet (HF tree, 104 files) | corpus card ODC-BY | exceeds disk | — | new | Reject (size + NOTES35 mechanism). |
| Nemotron-CC v2 / v2.1 | v2 modified 2026-07-07; v2.1 2025-12-22 | https://huggingface.co/datasets/nvidia/Nemotron-CC-v2 | CC rewrite + synthetic Diverse-QA etc. | collection 6,585.8 B tokens: Diverse QA 692.9 B, English Synthetic CC 1,257.3 B; generators include Qwen3-30B-A3B (879.1 B tokens) and Mistral-NeMo-12B | **NVIDIA Data Agreement for Model Training**, gated, "for model training purposes only" | **cannot be redistributed in a public repo or app** | — | new | Reject (licence). |
| GenRead (generate-then-read) | ICLR 2023 | https://arxiv.org/pdf/2209.10063 | LLM-written contexts instead of retrieval | TriviaQA 71.6 / WebQ 54.4 EM vs DPR-FiD +4.0/+3.9; retrieval + generation complementary | arXiv | evidence for model-written context, for 175 B-class generators | thin | closed_family_same_mechanism (NOTES35) | Citation only. The prior for "synthetic corpus as datastore" is the closed NOTES35 result. |
| Common Pile `news` (CC BY/BY-SA news sites) | 2025-06-06 | https://huggingface.co/datasets/common-pile/news_filtered | 20+ CC-licensed outlets (Global Voices, SciDev.Net, 360info, Meduza…) | 0.1 GB of files | per-document CC BY / BY-SA | tiny; niche outlets; 16 months stale | absent (news), weak | new | Low priority; only if news items miss and the outlets match. |
| FineWeb-Edu, OpenStax, LibreTexts, Khan Academy | — | see `notes/datastores.md` (licence map) | — | — | compilation-only / CC BY 2024 snapshot / mostly NC / BY-NC-SA | — | — | known (datastores.md) | No change. |

### Inferences
- The bucket is *absent knowledge*. A synthetic corpus cannot contain a fact its generator did not know. Our deep reader (Qwen3.6-35B) is newer and larger than Mixtral-8x7B, so Cosmopedia mostly duplicates its parametric knowledge, with added hallucination risk.
- I found no 2024–2026 paper that uses Cosmopedia, Nemotron-CC or FineWeb-Edu **as a retrieval datastore** and reports a QA gain. CompactDS uses web-crawl data, not synthetic data (known).

### Gaps
- No quality audit of Cosmopedia's factual accuracy was found (the card discusses only decontamination).

## Q3. News and recency sources that could ship offline

### Takeaway
No licence-clean, broad news text corpus exists. The shippable recency signal is Wikipedia itself: fresh NS0 year articles ("2026 in …") plus the **Current events portal** (NS100, CC BY-SA). The portal is about 4 MB of wikitext for 13 months and is absent from every NS0 dataset, including ours.

### Cited Findings

| item | date | URL | what it is | key numbers | licence | fit to our constraints | BOAR bucket | novelty vs our docs | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| **Wikipedia Current events portal** (`Portal:Current events/YYYY Month D`) | daily; checked 2026-10-12 | https://en.wikipedia.org/wiki/Portal:Current_events | one page per day of one-line, sourced event summaries | 365 day-pages for 2025 (API allpages); sizes 9,028–12,216 bytes wikitext (2025-09-15, 2026-09-15, 2026-10-01) → ≈ 3.6 MB/yr | CC BY-SA 4.0 | tiny; in the XML dump (NS100) and the API; **not in FineWiki or structured-wikipedia (NS0 only)** | absent (post-cutoff events) | **new** | **CURRENTEVENTS pack:** Sep 2025 → build date from the 2026-10-01 XML dump, with one doc per day and per-event chunks carrying the date in the title. Gate: anywhere-check on absent items whose rationale says recent/event. Cost ≈ 2 h. |
| Wikinews (English) | closed read-only **2026-05-04** | https://meta.wikimedia.org/wiki/Public_consultation_about_Wikinews · https://en.wikinews.org/wiki/Wikinews:Closure_of_Wikinews | community news site | 22,237 articles (siteinfo 2026-10-12), 41 active users; dump `enwikinews-latest-pages-articles.xml.bz2` 47.5 MB (2026-10-01) | CC BY 2.5 | frozen; low coverage | — | new | Reject as a recency source (frozen since May 2026). |
| GDELT | live | https://www.gdeltproject.org/about.html | global news event/GKG metadata | — | "unlimited and unrestricted use… redistribute, rehost" with citation + link | metadata and URLs, no article text (inference: the outputs listed are events/themes/locations) | — | new | Reject (no text to retrieve). |
| CC-NEWS (Common Crawl) | daily since 2016 | https://commoncrawl.org/blog/news-dataset-available · https://commoncrawl.org/terms-of-use | news WARCs | daily releases | ToU: crawled content "may be subject to separate terms", users must respect third-party copyright | publisher copyright: not shippable in a public repo | — | new | Reject (licence). |
| HoH benchmark (outdated info in RAG) | 2025-03 (ACL 2025) | https://arxiv.org/abs/2503.04800 | QA over current + historical docs built from Wikipedia revision diffs | 96,124 QA pairs, 219,463 docs; outdated docs "significantly degrade" RAG | code/data public (github.com/0russwest0/HoH) | evidence that mixing stale and fresh versions hurts | wrong (outdated) | new | Design rule: on refresh, **replace** articles, never keep two revisions in the packs. |

### Inferences
- "Wrong fact" (21–40 % of loss) partly overlaps "outdated". A fresh base and the Current-events pack attack both. Nobody has split "wrong" from "outdated" yet (critique §1), so that split decides the expected value.
- Any news pack is stale from the day it ships. Recency claims must say "as of build date". The reference is frontier + live web, so items about the last weeks stay unwinnable offline.

### Gaps
- No open-licence general news corpus with 2026 text was found.
- I did not measure the Current-events portal's coverage of entities likely in V-para-style items (no item access).

## Q4. What frontier + web answers actually cite

### Takeaway
Every source agrees on the shape: a huge long tail, Wikipedia as one of the top domains but only ≈ 3–6 % of citations, and UGC/video (YouTube, Reddit, Facebook, Quora, Instagram) dominant on Google surfaces. News dominates for current-events queries, and government/PMC for health/environment. Except for Wikipedia, Stack Exchange (the open Q&A analog of Reddit/Quora) and government pages, the cited mass is not openly licensed. "Pick corpora by citation share" therefore reduces to the already-proposed set plus freshness. The decisive measurement remains the **coordinator-only domain histogram of our own reference answers** (critique §1).

### Cited Findings

| item | date | URL | what it is | key numbers | licence | fit to our constraints | BOAR bucket | novelty vs our docs | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| Allaham & Diakopoulos, "Synthetic Sources?" | arXiv 2605.23684 (2026-05); queries Mar–May 2025 | https://arxiv.org/html/2605.23684v1 | citation audit of ChatGPT-search, Copilot, Gemini, Perplexity | 712 queries (280 environment, 257 health, 175 politics); 26,266 unique sources over 7,675 domains; **Wikipedia #1 at 3.64 %**, PMC 3.30 %, ScienceDirect 2.05 %, Reddit 1.59 %, EPA 1.39 %, CDC 0.40 %; top-25 = 23.8 %; 59.1 % of domains cited once; Gini 0.68; ≈ 16 % of cited sources AI-generated (Perplexity 9.4 %, Copilot 27.8 %) | arXiv | topics differ from travel/practical | absent | new | Prior: no single non-Wikipedia corpus captures > 4 % of citations. |
| Search Arena (Miroyan et al., ICLR 2026) | data 2025-03-18 → 05-08 | https://arxiv.org/html/2506.05334 · https://huggingface.co/datasets/lmarena-ai/search-arena-24k | 24,069 search-LLM conversations, 12,652 votes; 9 intents; domain categories | preference coefficients: tech/code β +0.073, community β +0.061, social β +0.057, **Wikipedia β −0.071**; citation count β +0.209; mean citations: Recommendation 6.9, Info Synthesis 6.8, Factual Lookup 5.7 (19.3 % of prompts) | prompts CC-BY-4.0; outputs under provider terms (card) | the 24k parquet is 400 MB (needs OK); has full `web_search_trace` URLs | absent, hedged | new | **CITEMAP-SA** (0 Claude calls): use the 24k set's `web_search_trace` URLs and the annotated `intent` to tabulate domain shares for Recommendation/Guidance/travel-like prompts. Cost: 400 MB download (r4to OK) + 1 h. |
| My pilot over Search Arena v1-7k | run 2026-10-12 | https://huggingface.co/datasets/lmarena-ai/search-arena-v1-7k | English rows (4,200 conversations, 7,808 responses); URLs parsed from answer text only, so Perplexity's numeric citations are under-counted (2,710 responses had in-text links) | 10,889 citations; reuters.com 6.1 %, **en.wikipedia.org 5.9 %**, google.com 5.7 %, apnews 3.4 %; Wikipedia cited in **13.2 %** of citing responses; 3,773 domains, 2,682 cited once, top-25 = 26.4 %. Keyword slices are small and noisy (travel 78 queries, 266 citations: Wikipedia 8.6 %, gov 5.6 %, travel sites 3.8 %; health 82 queries: Wikipedia 7.8 %, gov 7.0 %) | as above | pilot only | absent | new | Superseded by CITEMAP-SA on 24k with trace URLs. |
| Yang, "News Source Citing Patterns in AI Search Systems" | arXiv 2507.05301 (2025-07) | https://arxiv.org/abs/2507.05301 | Search Arena analysis | > 366,000 citations; **9 % news** | arXiv | — | — | new | Citation: news is a minority even in search-LLM answers. |
| Ahrefs Brand Radar, AI Overviews top domains | updated 2026-09-02 | https://ahrefs.com/blog/most-cited-domains-ai-overviews/ | 3 M+ US queries, share of top-50 citations | YouTube 22.9 %, Reddit 18.5 %, Facebook 10.1 %, google.com 8.8 %, Instagram 5.6 %, Quora 4.7 %, **Wikipedia 4.0 %**, Amazon 3.3 %, Healthline 0.8 % | vendor | method = share of top-50 only, no topic split | — | new | Context: UGC dominates Google surfaces, and UGC is not shippable (no open licence). |
| Peec AI, most-cited domains in AI search | 2026-03 | https://docs.peec.ai/research/most-cited-domains-in-ai-search | 30 M citations across ChatGPT, AI Mode, Gemini, Perplexity, AIO | rank: Reddit, YouTube, LinkedIn, **Wikipedia #4**, Forbes, G2, Yelp…; hotels: Booking.com/Airbnb outrank Reddit | vendor | no shares published | — | new | Context only. |
| GEO "earned media" study | arXiv 2509.08919 (2025-09) | https://arxiv.org/html/2509.08919v1 | AI search vs Google sourcing | "systematic and overwhelming bias towards Earned media" (third-party) over brand/social; vertical numbers seen only in secondary summaries | arXiv | — | — | new | Citation only (consumer/product verticals). |

### Inferences
- Wikipedia's ≈ 4–6 % share is the largest single shippable slice. The rest of the reference's knowledge comes from thousands of domains, so breadth packs plateau, which matches a competitor team's flat breadth results (datastores.md). The best evidence-based levers stay (i) freshness of the largest slice and (ii) small question-shaped official sources (FCDO/CDC/NHS) that act as stand-ins for the .gov share (≈ 5–7 % on travel/health slices).
- Search Arena users prefer community/tech sources over Wikipedia (β −0.071 for Wikipedia). The reference's *style* advantage on practical items (experience-based tips) cannot be matched with encyclopedic text. That supports Stack Exchange practical sites (datastores.md) as the only licensed proxy, with the RAG-in-the-Wild warning (SE-only hurts factoid QA) attached.

### Gaps
- No published citation study covers **travel-practical** queries with numbers. Peec's hotel note is the only one and it is qualitative.
- The domain histogram of **our** reference answers (frontier + web) has not been computed. That is coordinator-only work (bench items are off-limits to researchers).

## Searched, found nothing
- A refreshed FineWiki (2026) or a public statement on FineWiki cadence (HF card, repo).
- Any public Enterprise HTML dump after 2025-03 on dumps.wikimedia.org (run dirs empty).
- A Kiwix `wikipedia_en_all_nopic` newer than 2026-06.
- Any paper using Cosmopedia/Nemotron-CC/FineWeb-Edu as a RAG **datastore** with a QA result ("Cosmopedia retrieval datastore RAG evaluation"; "LLM-generated documents as retrieval corpus vs Wikipedia").
- A permissively licensed broad news text corpus with 2026 coverage (Common Pile news is 0.1 GB, 2025-06).
- A citation-share study for travel/practical queries with numbers ("AI Overviews … travel health queries share"; Peec gives only a qualitative hotel note).
- The SSRN review "Who Does AI Cite? … (2024–2026)" (SSRN 7528060): 403 to our fetcher, numbers unread.

## UNKNOWN
- Whether the missing V-para/v0.2 facts are in *any* Wikipedia text newer than Aug 2025: this is the gate itself (critique §0), not measurable without items.
- Whether "wrong" items are actually "outdated" (needs the coordinator's LOSSMAP rationale split).
- structured-wikipedia completeness and dedup rate; how much of its 7.6 M rows are non-articles.
- Enterprise free-tier snapshot cadence (monthly vs twice-monthly; sources conflict) and whether the free tier includes the full enwiki HTML snapshot (blog silent).
- Qwen3.6-35B-A3B training cutoff, needed to know which post-Aug-2025 facts the model already knows.
- Search Arena shares per intent with trace URLs (needs the 400 MB 24k parquet).
