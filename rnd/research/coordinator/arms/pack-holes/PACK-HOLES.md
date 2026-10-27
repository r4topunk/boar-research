# PACK-HOLES: template holes in the BOAR packs (CTX-F3 follow-up), 2026-10-20

TL;DR
- CTX-F3 confirmed and wider than "~2 %": chunks with >= 1 fact-bearing hole (a number, unit, amount, date or name missing from the sentence): **wikivoyage 1.36 %, simplewiki 1.29 %**, firstaid 1.24 %, visa 1.42 % (false positive, see §1), enwiki top100k 0.26 % (mostly false positives), factbook 0.06 %. Counting cosmetic holes too (`()` where a pronunciation / native name was): **simplewiki 4.54 %, wikivoyage 2.79 %**.
- Cause is one line: `renderTemplate` in `boar-app/scripts/lib/wiki-pack-lib.mjs:148-161` returns `""` for every template except the 9 Wikivoyage listing types. The same function builds simplewiki (`simplewiki-convert.mjs:104`) and Wikivoyage (`build-wiki-pack.mjs:392`). top100k is FineWiki rendered text (templates already expanded), so it is almost clean.
- Fix (not done, per brief): whitelist renderer for ~40 templates. Prototype on 1/8 of simplewiki: strong-hole windows 7.38 % -> 1.36 %, fact 1.67 % -> 0.37 %. For simplewiki the alternative is to rebuild from FineWiki's `simplewiki` parquet (fact 0.16 % measured, no renderer to write, but Aug-2025 snapshot).
- Impact on today's contexts is small but real: K1 self-test 6 of 546 chunks (1.1 %) and K1 v0.1 6 of 190 (3.2 %) carry a fact hole; on v0.1 5 of 40 items. See §1.3.

UNKNOWN:
- Answer-level effect (does a hole flip a judged score?) was not measured (0 LLM by brief). lan-rsn-003 (cheetah/pronghorn "speeds of up to .") is the known case (refute-1.md CTX-F3).
- Precision of the patterns is eyeballed (10 examples per pattern, EXAMPLES.md), not labelled.
- Embeddings: `lead_vecs` and FTS were built on the holey text, so retrieval for e.g. "area of X" is also affected; not measured.

Files (all in this folder; nothing was rebuilt, packs opened `mode=ro`):
`holes.py` (scanner), `attribute.py` + `dropped-templates.mjs` (which template made each hole), `kept_contexts.py` (K1/K3 prompts), `render-whitelist.mjs` + `holes-eval.py` (rebuild prototype and its score), `finewiki-sample.mjs`, `make_examples.py`, `EXAMPLES.md`, `out/*` (raw numbers; `hole_chunk_ids` lists chunk ids per pack).

## 1. Measurement (read-only)

### 1.1 Hole patterns (python regex, `holes.py:PATTERNS`)

Chunk text = `articles` text sliced by `chunks.start/end` (UTF-16 offsets, zstd blocks), i.e. exactly what retrieval returns.

| pattern | regex idea | what it catches | precision (eyeball, simplewiki / wikivoyage) |
|---|---|---|---|
| empty_paren | `\(\s*[,;:–—-]?\s*\)` | `X () is a ...` pronunciation/native name, `Airport ()` IATA | high (6/6, 6/6); code packs FP |
| paren_lead_punct | `\(\s*[,;:]` | `(; )`, `(, literally ...)`, IPA left over | high (6/6), voyage 3/5 |
| paren_dash_only | `\(\s*(born\|died\|c\.)?\s*[–—-]\s*[);,]` | `( – )` birth/death years lost | high in simple (5/6) |
| prep_punct | preposition/article/copula + `[.,;:)]` | `speeds of up to .`, `an area of .`, `is a .` | high (6/6, 6/6) |
| unit_no_number | `(is\|of\|about\|to\|from\|...) (km\|miles\|kg\|%\|million\|billion\|...)` with a deny-list (`thousands of`, `per`, ...) | `more than million people` | low in voyage (~1/5), medium simple; weakest pattern |
| between_and | `between and`, `from to` | `diameters between .`, `ranges from to per hour` | medium (3/6) |
| born_died_empty | `(born[,;)]`, `born in[,.]` | lost birth place/date | high in simple (n=120), FP-prone elsewhere (visa 154 hits are "died" in prose: ignore) |
| lang_label_empty | `(Japanese: )` | `{{lang}}`/`{{transl}}` lost | high (6/6) |
| orphan_modifier | ` -long`, ` -deep`, ` -mile` | `a -long interactive timeline` (`{{convert}}` adjective form) | medium |
| line_lead_punct | line starts with `[,.;:)] ` | noise; mostly phrasebook / table lines | low |
| space_punct, double_space | `word ,` / two spaces | weak; reported, excluded from "strong" | n/a |

Definitions: **strong** = any pattern except space_punct/double_space. **fact** = prep_punct, unit_no_number, between_and, paren_dash_only, born_died_empty or orphan_modifier (a quantity/date/name is missing). **cosmetic** = only empty_paren / paren_lead_punct / lang_label_empty (pronunciation or native-name parentheses; harmless for most questions but they make the lead read badly and waste tokens).

### 1.2 Share of chunks with >= 1 hole, per pack (local `shared-data/packs`, all chunks unless noted)

| pack | chunks scanned | strong | **fact** | top patterns (chunks) |
|---|---|---|---|---|
| boar-simplewiki-en | 621,682 (all) | **4.54 %** | **1.29 %** | empty_paren 12,189; paren_lead_punct 9,473; prep_punct 7,626; between_and 208; lang_label_empty 188; born_died 120 |
| boar-wikivoyage-en | 548,051 (all) | **2.79 %** | **1.36 %** | empty_paren 7,437; prep_punct 6,603; unit_no_number 616; paren_lead 357; between_and 296 |
| boar-wiki-en-top100k | 656,310 (every 6th article) | 0.30 % | 0.26 % | mostly FP: table rows `Story by :`, code `()`; real holes rare (see EXAMPLES.md) |
| boar-factbook | 10,543 | 0.07 % | 0.06 % | structured JSON source, no templates |
| boar-firstaid-en | 22,500 | 2.01 % | 1.24 % | prep_punct 251; empty_paren 129 (also from a wikitext-like source; not analysed further) |
| boar-medlineplus-en | 3,042 | 0.33 % | 0.33 % | prep_punct 10 |
| qa-travel / outdoors / health / cooking / money SE | 20k-155k | 0.2-0.4 % | 0.2-0.3 % | HTML-to-text packs, no template issue |
| qa-ethereum-se | 118,560 | 23.4 % | 1.05 % | FALSE POSITIVE: `f()`/`()` in Solidity code |
| qa-bitcoin-se | 84,399 | 3.9 % | 0.65 % | double spaces + code |
| boar-nist-crypto / boar-visa-en | 1.6k / 10.8k | 2.4 % / 1.5 % | 0.06 % / 1.42 % | FP (empty_paren in formulas; "died" in prose) |

Only simplewiki and wikivoyage are confirmed template-stripped packs. boar-firstaid-en mixes Appropedia (567 docs), enwikibooks (71), US-gov text and some enwiki; its holes ("approximately ." in Earthquake, "an area of ." in Moringa oleifera) look like the same MediaWiki-source stripping on the Appropedia/wikibooks part, but its converter was not traced (UNKNOWN; check `rnd/research/packs/boar-firstaid-en.md` build steps before touching it). Chunk-level rates are underestimates of "facts lost" (one chunk can hold several holes) and overestimates of "answer-relevant" (many holes are `()`).

### 1.3 Holes among the chunks actually placed in prompts (`kept_contexts.py`, cap/ LITEPACKS runs, seed 42)

Parsed `Context:` blocks of `context-tools/cap/*.prompts.jsonl`; domain from `retrieval.kept[k].source`. fact = fact-bearing pattern in the chunk; cosmetic-only holes are the difference between "core" and "fact".

| run | items | items with a hole (core) | items with a fact hole | chunks in prompts | chunks with core hole | chunks with fact hole |
|---|---|---|---|---|---|---|
| lp-K1-st-s42 (pack-matched self-test) | 129 | 13 (10 %) | 6 (4.7 %) | 546 | 14 (2.6 %) | 6 (1.1 %) |
| lp-K3-st-s42 (self-test) | 134 | 8 (6 %) | 4 (3.0 %) | 569 | 9 (1.6 %) | 4 (0.7 %) |
| lp-K1-v01-s42 (v0.1 dev) | 40 | 12 (30 %) | 5 (12.5 %) | 190 | 17 (8.9 %) | 6 (3.2 %) |
| lp-K0-v01-s42 | 30 | 2 | 1 | 73 | 3 | 1 |
| lp-K1-cm-s42 | 21 | 1 | 1 | 73 | 1 | 1 |

By source in K1-st: simple.wikipedia.org 13 of 467 chunks (2.8 %), wikivoyage 0 of 52, the one other hit is a Solidity `()` FP. In K1-v01: simple 15 of 140 (10.7 %), wikivoyage 2 of 21. Simplewiki chunks over-represent holes in the kept set (retrieved because they are lead/definition chunks, where `()` and `{{convert}}` live). Examples in kept contexts: "running a total of ." (Route 66), "elevations of to ," (simplewiki-en-005), "(pron. or )" (Curitiba), "has an area of ." (Nagaland), "can run up to , and accelerate from 0 to in less than 3" (cheetah), "Sukhumvit ... (Rayong to Border to )". Note: pronunciation `()` holes (Bishkek, Paraguay, India) are cosmetic.

## 2. Where templates are dropped, and which matter

### 2.1 Code (file:line)

| where | what |
|---|---|
| `boar-app/scripts/lib/wiki-pack-lib.mjs:148-161` `renderTemplate` | **the drop**: `if (!LISTINGS.has(name)) return "";` (line 151). Only `see/do/buy/eat/drink/sleep/listing/go` are rendered (line 158 drops `marker`). Arguments of every other template are discarded |
| `wiki-pack-lib.mjs:163-186` `stripTemplates` | brace-depth scanner, calls `renderTemplate` on each top-level `{{...}}` (line 180); nested templates inside a dropped one vanish with it |
| `wiki-pack-lib.mjs:218` `cleanInline` | calls `stripTemplates` again on field text; line 232-251 `cleanWikivoyage`, template strip at line 238, then `[ \t]+ -> " "` (line 224-ish) which hides the double space but leaves `of .` |
| `scripts/build-wiki-pack.mjs:392` | Wikivoyage pack: `cleanWikivoyage(page.text)` |
| `rnd/kiln/packs/wave2-scripts/simplewiki-convert.mjs:104` | simplewiki body = `ents(dropBoiler(cleanWikivoyage(p.text)))`, i.e. the Wikivoyage cleaner applied to Wikipedia wikitext |
| `simplewiki-convert.mjs:43-63` `split/flat/infoboxes` | infobox params are flattened by keeping **positional, non-`=`** args of nested templates (line 49): `{{convert|12|km}}` survives as `12 km`, but `{{birth date|1846|9|1}}` becomes `1846 9 1` and named args (`{{val|1|u=km}}`) are lost; dates in "Key facts:" come out as `1892 07 17` (see EXAMPLES.md double_space) |
| top100k | FineWiki parquet (`build-wiki-pack.mjs` `addWikipedia`, line ~262-290): rendered Enterprise-HTML text, no template stripping, so no holes from this path |
| builder identity | the mini's `<runner>/kiln/packs/builder/scripts/lib/wiki-pack-lib.mjs` has the same md5 (04776e53...) as boar-app's |

### 2.2 Which templates leave holes (`dropped-templates.mjs` + `attribute.py`)

Method: re-run the builder's own cleaner over the full dumps with a sentinel in place of every dropped template (simplewiki dump 20261001, 285k pages / 1.86 M dropped templates; Wikivoyage dump 26 Sep, 34k pages / 284k dropped), then count a template as "hole at seam" when a STRONG pattern spans the seam. Totals: simplewiki 40,992 hole seams, Wikivoyage 16,169 (full tables in `out/templates-*.json`, top 200 each).

simplewiki, by family (dropped / hole seams):

| family | dropped | hole seams | main members (holes / dropped) |
|---|---|---|---|
| `{{lang}}`, `{{lang-xx}}`, `{{langx}}`, `{{zh}}`, `{{script}}`, `{{nihongo}}`, `{{transl}}` | 37,570 | **24,153** | lang 3166/5678; lang-ru 2452/2785; lang-ar 1321/1677; lang-fr 923/1162; langx 908/1121; zh 775/874; script 765/779; nihongo 668/6296 |
| `{{convert}}` / `{{cvt}}` and unit templates | 21,396 | **6,484** | convert 6107/20002; cvt 321/1125; (area, height, speed, temperature: the fact holes) |
| `{{IPA}}`, `{{IPAc-en}}`, `{{IPA-xx}}` | 9,263 | 5,362 | ipac-en 2112/2673; ipa 622/1444; ipa-fr 582/682 |
| `{{ill}}` (interlanguage link) | 4,053 | 604 | ill 553/3755 |
| `{{coord}}` | 48,566 | 390 | coord 390/48454 (mostly harmless; leaves `located at .` sometimes) |
| date templates (`start date`, `birth date`, `death date`) | 1,038 | 244 | start date 91/110; val 44/211 |
| other named: isbn 336, nowrap 196, chem2 182, f1 198, escyr 159 | | | |

Wikivoyage, top: `{{IATA}}` 8,741/13,231 (all `Airport ()`), `{{lang}}` 1,065, `{{phone}}` 852, `{{php}}` 618, `{{UNESCO}}` 527, `{{km}}` 414, `{{station}}` 345, `{{eur}}` 335, `{{rub}}` 322, `{{convert}}` 299, `{{m}}` 278, `{{c}}` 269, `{{rint}}` 258, `{{f}}` 202, `{{km2}}` 160, `{{mi}}` 122, `{{ft}}` 120, `{{routebox entry}}` 117.

**Top 3 by hole count: simplewiki = `{{lang*}}` family (24k), `{{convert}}`/`{{cvt}}` (6.4k), `{{IPA*}}` (5.4k); Wikivoyage = `{{IATA}}` (8.7k), `{{lang}}` (1.1k), `{{phone}}` (0.9k) then the currency/unit templates (`{{eur}}` `{{rub}}` `{{km}}` `{{convert}}` ... ~2.3k together).** For answer quality the fact-bearing ones are `{{convert}}`/`{{cvt}}`, `{{km}}`/`{{m}}`/`{{c}}`/`{{f}}`/`{{ft}}`/`{{mi}}`, currency templates, `{{val}}`, date templates; the `{{lang*}}`/`{{IPA*}}` holes are mostly cosmetic but also strip foreign names that questions sometimes ask about. `{{birth date and age}}` / `{{death date and age}}` / `{{lang}}` / `{{coord}}` from the brief: birth/death mostly sit in infoboxes (handled by `flat()`, lossy but not a hole) and show only 37-91 hole seams in the body; `{{coord}}` is huge in count but rarely a hole.

## 3. Rebuild plan (not executed)

### 3.1 Renderer options

| option | what | verdict |
|---|---|---|
| A. In-house whitelist in `renderTemplate` (prototype `render-whitelist.mjs`) | render ~40 templates: convert/cvt + unit templates (km m mi ft kg lb km2 ha acre kmh mph c f ...), currency (eur usd gbp jpy rub php ...), lang/lang-xx/langx/zh/nihongo/transl (keep the text arg), IPA/IPAc (keep text), ill, iata/icao/phone/station, birth/death/start date, val, unesco, isbn, nowrap-likes; plus a tidy pass that deletes leftover `()` and `(; ` | **recommended for Wikivoyage**; no dependency; scored below |
| B. mwparserfromhell | robust template parsing | does not expand templates; `convert`, `lang`, `IPA` are Lua (Scribunto) modules, so the expansion logic is still ours; our brace-depth `splitTop` already handles nesting. No gain, adds Python to a Node pipeline |
| C. wikitextparser | same as B | same verdict |
| D. FineWiki rendered text | `HuggingFaceFW/finewiki` has config `simple` (`data/simplewiki/000_00000.parquet`, 521 MB, Aug-2025 Enterprise HTML dump, rendered); **no Wikivoyage** | **recommended for simplewiki** if a 14-month-older snapshot is acceptable: measured fact-hole windows 0.16 % (vs 1.67 % today), `()` 28 vs 1,962 windows. The builder already reads parquet (`build-wiki-pack.mjs` `addWikipedia`), but sets source=enwiki: needs a JSONL conversion with `source:"simplewiki"`, url, license, aliases (re-use `redir` pass 1 from `simplewiki-convert.mjs`). Keeps the infobox JSON path (`infoboxText`) which is better than `flat()` |
| E. Wikimedia Enterprise / REST HTML for Wikivoyage | rendered HTML | needs API access / large downloads; only if A is not enough |

Prototype scores (`holes-eval.py`, ~1000-char windows of cleaned body, same patterns; `line_lead_punct` noise included in "strong", so read the fact column):

| pack (sample) | builder today: strong / fact | whitelist A: strong / fact | FineWiki D |
|---|---|---|---|
| simplewiki (1/8 of pages, 61.7k windows) | 7.38 % / 1.67 % | **1.36 % / 0.37 %** (empty_paren 1962 -> 6) | 0.97 % / **0.16 %** (265k rows / 8) |
| wikivoyage (1/4 of pages, 73.8k windows) | 6.94 % / 2.48 % | 3.70 % / 1.50 % (remaining mostly `line_lead_punct` phrasebook lines + unit FPs; `{{rint}}`, `{{routebox entry}}`, `{{php}}`... not yet whitelisted) | n/a |

Whitelist caveats seen in the prototype: Celsius spelled `C` needed a lowercase map (fixed); `{{convert}}` multi-value forms and `abbr=on`/`disp=` options are only partly handled; `{{val}}` named units; `{{lang}}` second positional only. Add unit tests from the 10 examples per template in `out/templates-*.json`.

### 3.2 Steps, time, disk (estimates, mini = M4 16 GB, 31 GiB free of 228 at 2026-10-20; disk policy keeps >= 25 GiB)

| step | simplewiki (option D) | simplewiki (option A) | wikivoyage (A) |
|---|---|---|---|
| inputs | FineWiki parquet 521 MB (downloaded to /tmp here already; mini needs its own copy, CC BY-SA, covered by the autonomy rule) | dump 388 MB (sha1 8a12322b..., same size as the 20261001 file) | dump 131 MB in `shared-data/dumps` |
| code | parquet -> JSONL converter (~60 lines; reuse `redir` pass) | whitelist + tests in `wiki-pack-lib.mjs` (~150 lines, prototype is the draft) | same patch (shared function) |
| convert | ~10 s read + 1 min | 60 s (as 2026-10-13) | < 1 min |
| `build.sh` (FTS, chunks, `lead_vecs` embeddings at ~225/s with `BOAR_EMBED_GPU=metal`) | ~15 min (928 s last time, 208k articles) | ~15 min | ~5-8 min (34k articles, 548k chunks; embeddings ~2.5 min) |
| scratch disk | ~1.5 GB (parquet + JSONL parts + sqlite) | ~1.7 GB (dump + 2 JSONL parts + sqlite) | ~0.8 GB |
| output | ~480 MB sqlite (same as today) | ~480 MB | ~351 MB |
| total wall | ~20 min | ~20 min | ~10 min |

Both packs together: **~30 min wall on the mini, < 3 GB scratch**, one heavy job at a time (machine-load rules). The mini has the same builder lib (md5 verified).

Then, in order:
1. Patch `wiki-pack-lib.mjs` (renderer + tidy) in a worktree of boar-app (never the public fork), add unit tests (`wiki-pack-lib.test.mjs` exists).
2. Re-run `holes.py` on the new sqlite files; gate: fact-hole chunk share <= 0.5 % simplewiki, <= 0.8 % wikivoyage, and `pack-check` (`wave2-scripts/check-pack.test.ts`) green. Pre-register the gate (sha256) before the build.
3. Replay retrieval (8 s, no LLM) on the 180 self-tests + v0.1 to confirm the same chunks are kept (chunk ids change: `articles`/`chunks` are regenerated; kept sets will move slightly because FTS/embeddings changed).
4. Only then spend judge calls: Haiku-low triage on the 12 + 6 items whose contexts had holes (K1-v01: 12 items; K1-st: 13 items), then the 180 if the triage moves.
5. Publishing (HF `boar-packs`, new sha256 in the catalogue pin, `verify-manifest-pins.mjs`) follows the pack-publish rule; engine/app pins change (packs are versioned by sha). Needs r4to only for anything public.

Expected value: low for the bar (fact holes are ~1 % of chunks, 3-5 % of items in K1 traces), but it is cheap, lead-chunk-heavy (the chunks that answer "what is X / how big is X"), and removes a visible artefact (`X () is ...`) from every simplewiki lead the model reads.

## 4. Reproduce
```
cd <workspace>/rnd/research/coordinator/arms/pack-holes
python3 -I holes.py <pack.sqlite> out/<pack>.json [--articles-mod N]
node dropped-templates.mjs <dump.xml.bz2> <workspace>/boar-app/scripts/lib 1 > dropped.jsonl && python3 -I attribute.py dropped.jsonl out/templates-X.json
python3 -I kept_contexts.py <cap dir> out/kept-contexts.json
node render-whitelist.mjs <dump.xml.bz2> <lib dir> <pageMod> > wl.jsonl && python3 -I holes-eval.py wl.jsonl
node finewiki-sample.mjs <simplewiki parquet> <workspace>/boar-app 8 > fw.jsonl && python3 -I holes-eval.py fw.jsonl
```
(Python >= 3.14 for `compression.zstd`; dumps and the FineWiki parquet were downloaded into /tmp/ph-dl, not committed.)
