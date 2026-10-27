# Pack converters (T-K1)

TL;DR: `convert.mjs` turns open corpora into the input of the engine's pack builder
(`wt/packcond/scripts/build-wiki-pack.mjs`, format 2): `<out>/<name>.jsonl` (one doc per line) +
`<out>/manifest.json` (the builder's `--manifest`) + `<out>/convert-info.json` (counts, licences, snapshot,
input sha256s). Every row carries `license` and a free-text `attribution`. No dependencies (Node ≥ 22; `bsdtar`,
`unzip`, `pdftotext` from poppler). The engine tree is not touched.

```sh
cd <workspace>/shared-data/packs
C=<workspace>/rnd/kiln/packs/convert
node $C/convert.mjs stackexchange work/convert-samples/medicalsciences.stackexchange.com.7z --out work/qa-health-se --limit 200
node $C/convert.mjs medlineplus work/convert-samples/mplus_topics_compressed_2026-10-10.zip --out work/medlineplus-topics
node $C/convert.mjs pdf work/convert-samples/atp-4-02.11-2026.pdf --out work/atp-4-02-11 --manual "ATP 4-02.11" \
  --doc-title "Army Techniques Publication for Casualty Response, Tactical Combat Casualty Care, and First Aid" \
  --date 2026-03-23 --url "https://archive.org/details/army-techniques-publication-for-casualty-response-tactical-combat-casualty-care-"
node $C/convert.mjs factbook work/convert-samples/factbook --out work/factbook --snapshot "2026-09-11 (repo commit 144d6977)"
node $C/validate.mjs work/qa-health-se work/medlineplus-topics work/atp-4-02-11 work/factbook   # counts only; exit 1 on errors
cd $C && node --test test/*.test.mjs                                                            # 15 unit tests
```

Build a pack (from the engine worktree; `--source` maps new codes to existing ones until T-K2 lands):
```sh
node $C/convert.mjs stackexchange <site>.7z --out work/dryrun/se --source appropedia
cd <workspace>/wt/packcond
node scripts/build-wiki-pack.mjs --out X.sqlite --shards work/dryrun/se/*.jsonl --manifest work/dryrun/se/manifest.json --no-embed --name "…"
```
JSONL docs go through `addWikipedia → addRow` (the `.jsonl` branch of `--shards`, l.299; `addRow` l.267); there is no separate
path. Several converted dirs in one pack: pass every JSONL to `--shards` and concatenate their `manifest.json`
arrays into one file (page_id ranges below keep them disjoint).

## Common options
`--out DIR` (required) · `--limit N` (stop after N docs) · `--source CODE` (override `source`; the real family
is kept in `source_family`, which `validate.mjs` uses for its rules) · `--id-base N` (override the page_id base).

## Row schema (builder input, local-inventory §3)
| field | how the converters fill it |
|---|---|
| `page_id` | unique per pack; ranges below |
| `title` | display title (builder prepends `# Title`) |
| `text` | ≥ 200 chars (shorter docs are skipped and counted); `##`/`###` headings become the FTS section path; paragraphs blank-line separated; no line starts with `#` or `|` by accident (escaped with U+200B / `¦`) |
| `source` | family code (new codes: `stackexchange`, `medlineplus`, `factbook`; PDFs use existing `usgov`) |
| `url`, `license` | → `article_meta` |
| `attribution` | free text; **not stored by the current builder** (T-K2) |
| `aliases` | → `redirects` (case-insensitive) |
| `views` | popularity prior when no `--pageviews` |
| `infoboxes` | always `null` (Factbook writes its own "Key facts:" paragraph instead) |

page_id ranges (existing: usgov pages 4e9 + hash31 = 4.0e9…6.15e9, FM 21-76 4.5e9, EIPs 5e9, specs 6e9,
ethereum.org 7e9, BIPs 8e9): medlineplus `11e9 + topic id`; factbook `12e9 + parseInt(code, 36)`;
pdf `13e9 + (fnv32(manual) % 1000)·1e6 + section#`; stackexchange `1e14 + (fnv32(host) % 1e6)·1e8 + question Id`
(per-site bucket; validate.mjs checks uniqueness across all inputs given to it).

## Formats

### stackexchange — `<site>.7z` from archive.org item `stackexchange` (2024-04-02 dump)
- Reads `Posts.xml` and `Users.xml` with `bsdtar -xOf` (streamed). One doc per **question**.
- `text` = `Tags: a, b` + question body (HTML → text: lists as `- `/`1. ` lines, `<pre>` verbatim, inline code in
  backticks, links → text, images dropped) + `## Answers` + up to `--max-answers` (5) `### Answer (score N, accepted)`
  sections: accepted first, then score desc; kept if accepted or score ≥ `--min-score` (1). Questions with no kept
  answer are skipped unless `--keep-unanswered`.
- `url` = `https://<host>/questions/<Id>`; host from the file name, with renamed sites mapped
  (`health.stackexchange.com` → `medicalsciences.stackexchange.com`, verified 302) or `--site-host`.
- **Licence:** the post's `ContentLicense` attribute (present in the 2024 dump; it reflects the latest revision),
  else by date: < 2011-04-08 CC BY-SA 2.5; 2011-04-08…2018-05-01 CC BY-SA 3.0; ≥ 2018-05-02 CC BY-SA 4.0. Row
  `license` = the question's; `convert-info.stats.licenseDateMismatch` counts questions where the attribute and the
  date rule differ (5/200 on the sample: edited after 2018).
- **Attribution rule:** `Q by <DisplayName> (https://<host>/users/<Id>); A by <name> (<profile>); …; <question url>`
  + `; answers also under CC BY-SA 4.0` when an answer's licence differs from the question's (17/200 rows).
  Users missing from Users.xml (deleted) → `user<Id>` with the profile URL; posts with no account →
  `<OwnerDisplayName> (no profile)`.
- `views` = ViewCount; `aliases` = [].

### medlineplus — `mplus_topics_<date>.xml` or its zip (medlineplus.gov/xml.html)
- One doc per health topic with `language="English"` (`--lang` to change); `text` = `<full-summary>` (HTML → text)
  + `Also called: …` + `See also: <related topics>` + `Topic groups: …`.
- `aliases` = also-called + see-reference names (case-insensitive dedup).
- **Only NLM text.** `<site>` elements (A.D.A.M. encyclopedia `ency/`, ASHP `druginfo/`, external sites) are never
  read, so neither their text nor their URLs reach the row; validate.mjs fails any medlineplus row containing
  `ency/`, `druginfo`, `A.D.A.M`, `ASHP`.
- `license` = `Public domain (NLM); courtesy of MedlinePlus from the National Library of Medicine`;
  `attribution` = `Courtesy of MedlinePlus from the National Library of Medicine; <topic url>`; `views` = 0.

### pdf — US government manuals (pdftotext -layout)
- Required: `--manual "ATP 4-02.11" --url URL`; recommended `--doc-title`, `--date`. `source` = `usgov`,
  `license` = `US government work (17 U.S.C. §105), public release`, `attribution` = `<doc title>, <manual>, <date>; <url>`.
- Drops running headers/footers (edge lines repeated on ≥ 15 % of pages), page numbers, Word bookmark ids
  (`195B`), distribution/supersession boilerplate and all front matter before the first chapter; stops at
  `References`/`Index`.
- A chapter starts at a centred `Chapter N` / `Appendix X` / `Glossary` line whose label differs from the current
  one, followed by its centred title. Sections: ALL-CAPS lines at the left margin. When the table of contents lists
  section names (dot leaders), only those open a doc (`<manual> — Chapter N <title>: <Section>`), other caps headings
  become `## ` subsections; without a usable TOC every caps heading opens a doc. Repeated titles get ` (2)`.
- Lines are kept as lines (step lists), `•` → `- `, `▪` → `  - `, numbered paragraphs (`4-12.`) start a paragraph,
  runs of ≥ 3 spaces (layout columns) → ` · `.

### factbook — CC0 JSON archive (github.com/factbook/factbook.json)
- Input: a dir (recursive `<region>/<code>.json`) or files. One doc per country; title = conventional short form.
- `text` = `Key facts:` paragraph (one `Label: value` line each: official name, capital, location, area, population,
  languages, religions, ethnic groups, government type, independence, currency, GDP, GDP per capita, life
  expectancy, climate, internet code; values ≤ 160 chars; block ≤ 1,400 chars so it is exactly one chunk and the
  builder's lead rule embeds the next chunk) + `## Background` + one `## <Category>` section per category with every
  field flattened (`Field (sub): text`, yearly series and notes kept).
- `aliases` = long form, local short/long forms, former names, abbreviation (split on `/`, `,`, `;`, `or`).
- `license` = `CC0 (CIA World Factbook archive, data as of <--snapshot>)`; `url` = the file on GitHub.
- T-K6 (2026-10-13): `Time zone` key fact (Government > Capital > time difference, "UTC+3"); display-title overrides for 11
  entries with unusable short forms (DRC, "The Dominican", EE, "Gaza, Gaza Strip", Svalbard, US Pacific refuges, oceans
  OO/XO/XQ/ZH/ZN), the archive short form kept as an alias unless it is a 2-letter code; aliases containing brackets dropped.
  The archive has no telephone calling codes. Full archive (commit 144d6977): 261 docs, 774 alias redirects.

## Builder dry run (2026-10-12, MacBook, `--no-embed`)
- `se-only.sqlite`: 200 articles, 1,033 chunks (all indexed), `article_meta` 200 rows, 0 s.
- `convert-mix.sqlite` (200 SE + 100 MedlinePlus + 6 Factbook + 88 ATP sections): 394 articles, 2,538 chunks, all
  indexed, 222 redirects from aliases, 3.5 MB; `meta.sources`/`meta.license` from the merged manifest; FTS
  `tourniquet` → 28 chunks. Factbook chunk 0 = Key facts, chunk 1 = Background (lead rule works).
- Dry-run source mapping (until T-K2 adds the codes): `stackexchange → appropedia` (community CC BY-SA, not in
  `LAY_SOURCES`), `medlineplus → usgov`, `factbook → usgov`; PDFs are `usgov` natively. The app labels them
  "Appropedia"/"US government" until then.

## Samples (shared-data/packs/work/convert-samples/, 41 MB)
| file | bytes | rows out |
|---|---|---|
| health.stackexchange.com.7z (+ symlink medicalsciences…) | 22,447,982 | 200 (`--limit`; 7,930 questions in the dump) |
| mplus_topics_compressed_2026-10-10.zip | 4,775,535 | 1,016 English topics (of 2,033) |
| atp-4-02.11-2026.pdf (archive.org, md5 dd8a4bd5…) | 12,665,561 | 88 sections |
| factbook/{br,fr,ke,ja,us,xx}.json (repo commit 144d6977) | 0.37 MB | 6 |

## Known limits
- SE: whole Posts.xml is held in RAM (fine for site dumps ≤ ~1 GB; not for stackoverflow.com); comments,
  PostLinks (duplicates/related) and images are not used; licence = latest-revision `ContentLicense`, not per-edit.
- `attribution` is dropped by the current builder (only `url`, `license` reach `article_meta`): needs T-K2.
- PDF splitting is heuristic (tested on ATP 4-02.11 only); tables come out as ` · `-joined layout lines; figure
  captions stay as lines; hyphenated line ends are not rejoined. FM 21-76 in preparedness-v2 used its own split.
- Factbook snapshot date = repo commit date; the data's own "as of" (most fields 2024/2025 est.) is not in the JSON.
- MedlinePlus `full-summary` sometimes ends with the NIH institute name as its own paragraph (kept).
