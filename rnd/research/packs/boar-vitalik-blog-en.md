# boar-vitalik-blog-en (Vitalik Buterin's blog, WTFPL)
TL;DR: all 166 English posts of vitalik.eth.limo (2016-12-10 to 2026-09-27), one doc per post with a `Published: <date>` line; 8.8 MB; built 2026-10-21; **user-selected only**; AI-built, not reviewed; no measurement done, not in any kit.

## What it is
- Domain: Ethereum, cryptography, mechanism design, governance, AI and society, as written by one author. Opinion and explainer posts; first-person, dated.
- Source: github.com/vbuterin/blog (the repository behind https://vitalik.eth.limo/), shallow clone of commit 26c517aed3072fe6f179a0f06c9e44b7ef1a3ba5 (2026-10-07), `posts/*.md`. Not scraped: the markdown was read from the repo (no site requests beyond a 3-request check of the index, feed and one post, generic User-Agent). Post date and title come from each file's `[date]` / `[title]` metadata; the canonical URL (`https://vitalik.eth.limo/general/YYYY/MM/DD/<slug>.html`) comes from the repo's published `site/` tree (166/166 matched).
- Excluded: 4 translated files named `On_Collusion_{DE,IT,Polish,Portuguese}` plus other translations (English only); images (alt text kept as `[image: ...]`); posts under 200 chars (none).
- Licence: WTFPL. Repository README, quoted: "Blog posts, including the text and all images made by myself, are released freely to the world under the WTFPL (http://www.wtfpl.net/)." The site's own HTML pages carry no licence line; the statement is the repo README (the repo has no LICENSE file; the GitHub API reports no licence). The file `LICENSE-boar-vitalik-blog-en.txt` sits next to the pack. Every row: license "WTFPL (blog text and author-made images, per the repository README)"; attribution "Vitalik Buterin, "<title>" (<date>), <url>; WTFPL; repo vbuterin/blog 2026-10-07 (repo commit 26c517ae)".
- Text handling (numbers and names kept): links reduced to their text, image embeds dropped, HTML tags dropped, entities decoded, markdown tables flattened to `a; b; c` rows (no cell dropped), `#` headings mapped to `##` sections, code blocks kept verbatim and indented, LaTeX math kept as written (`$...$` stays in the text, so formulas read as source, not rendered).
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514 (bge-small-en-v1.5 q8_0, same asset as the wave-1 packs). Params as wave 1/2: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0; Metal embedding, FTS yes.
- Counts: articles 166; chunks 6,079; indexed 6,079 (100 %); lead_vecs 166; redirects 166 (the post slug, e.g. `gluecp`); text 4,745,540 B. `articles.source` = 13 (`vitalikblog`, appended to the builder's SOURCE map; the app's source map/label does not know code 13 yet, so citations print the fallback "Wikipedia" label until the engine adds it).
- Size: 8,806,400 B (8.4 MiB). sha256 94a7ec6ea74e29461593aa1fc23bce0ea9f2aed70701f19f2303ea5e1ad9aa3e.
## Build
- Build host Apple M4. Converter `rnd/kiln/packs/wave4-scripts/vitalik-convert.mjs` (uses the shared converter helpers), then the standard `build.sh`:
  ```sh
  git clone --depth 1 https://github.com/vbuterin/blog.git dl/vitalik-src/blog     # commit 26c517ae
  node scripts/vitalik-convert.mjs dl/vitalik-src/blog work/boar-vitalik-blog-en "2026-10-07 (repo commit 26c517ae)"
  bash scripts/build.sh boar-vitalik-blog-en "Vitalik Buterin's blog (WTFPL, vbuterin/blog snapshot 2026-10-07)" work/boar-vitalik-blog-en/manifest.json work/boar-vitalik-blog-en/vitalik-blog.jsonl
  ```
  convert jsonl sha256 ab22b575e46cd945122cb501c12a294f5c06ff7732aadfb841460e6f3ff8295e; build wall 2 s.
- Files: mini `<runner>/shared-data/packs/wave4/` (pack, `.json`, `LICENSE-boar-vitalik-blog-en.txt`). Not uploaded anywhere.
## Engine check (patched engine tree WikiPack.search, k 5, lexical only, no query vector, 2026-10-21)
Long natural-language questions behave AND-like (some return 0-2 hits); keyword-style queries recover. Right post in top 3:
| # | query | top-3 | right post in top 3 |
|---|---|---|---|
| 1 | "What is d/acc and what does defensive acceleration mean?" | My techno-optimism (the d/acc origin post), Balance of power | yes |
| 2 | "What is the glue and coprocessor architecture for computation?" | Glue and coprocessor architectures (x2) | yes |
| 3 | "What are the Merge, Surge, Verge, Purge and Splurge stages of the Ethereum roadmap?" | 0 hits | no (0 hits); the keyword form "Possible futures of the Ethereum protocol" returns parts 5 (Purge), 2 (Surge), 6 (Splurge) |
| 4 | "What does the Ethereum endgame look like with block production centralized and validation decentralized?" | Endgame (x2), How do layer 2s really differ from execution sharding? | yes |
| 5 | "How can collusion break mechanism design and coordination systems?" | Plurality philosophy, Sidechains vs Plasma vs Sharding, Don't overload Ethereum's consensus | no (On Collusion is 4th); "collusion mechanism design" returns it 5th |
- Result as written: 3/5 right post in top 3 (Q1, Q2, Q4); Q3 is a 0-hit lexical miss, Q5 a rank-4 miss. A semantic re-rank with a query vector was not run (replay path only). The "d/acc: one year later" post did not surface for the d/acc queries (not investigated).
## Category gaps and caveats
- Single-author pack: opinions and predictions are the author's, dated; answers should cite the post date. Not a general Ethereum reference (the crypto pack and the Ethereum Stack Exchange pack cover specs and Q&A).
- LaTeX stays as source text; the posts' figures and diagrams are not in the pack.
- Coverage, crowding and self-test were not run (decision 2026-10-20: no measurement now). Status: user-selected only, AI-built, not reviewed; not default-eligible until the D-K3 probes are run.
