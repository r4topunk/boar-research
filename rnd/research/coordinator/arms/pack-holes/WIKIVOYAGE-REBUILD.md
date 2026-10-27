# WIKIVOYAGE-REBUILD: candidate boar-wikivoyage-en with a template whitelist, 2026-10-21

TL;DR
- Candidate built on the mini (3 min, 0 judge, 0 paid): `<runner>/shared-data/packs/candidates/boar-wikivoyage-en-v2/boar-wikivoyage-en.sqlite`, 351,977,472 B, sha256 `080408a96ce1129546e6c936b0c1b43caf92d1f383ec5f82668e3cb391feccba` (copy on the MacBook at `shared-data/packs/candidates/boar-wikivoyage-en-v2/`, same sha). Format 2, dims 384, same embedding model, 34,002 articles, 548,468 chunks.
- Holes (holes.py unchanged, all chunks): fact **1.360 % -> 0.789 %** (7,451 -> 4,329), all strong **2.794 % -> 0.859 %** (15,312 -> 4,709); `empty_paren` 7,437 -> 12.
- Gates (criterion sha in `WIKIVOYAGE-REBUILD-criterion.sha256`, frozen before the build): **G1 PASS (0.789 % <= 0.8 %, thin margin of 60 chunks), G2 PASS, G3 PASS (+0.08 % chunks), G4 PASS (279/280 items identical), G5 PASS.** Precondition P1 holds; **P2 missed by 27 chunks** (control 548,024 vs 548,051), explained below. Literal verdict by the frozen rule: INVALID (P2); substantive reading: PASS on every gate. Nothing swapped into any kit or control.

## 1. Gate table

| gate | rule | current | candidate | verdict |
|---|---|---|---|---|
| P1 scanner reproduces | 15,312 strong / 7,451 fact | 15,312 / 7,451 | n/a | holds |
| P2 pipeline reproduces | unpatched control = 548,051 chunks | control 548,024 chunks, 34,002 articles | n/a | **missed by 27 (0.005 %)** |
| G1 fact-hole chunks | <= 0.8 % | 7,451 / 548,051 = 1.360 % | 4,329 / 548,468 = **0.789 %** | PASS |
| G2 strong-hole chunks (strict "cosmetic") | <= 1.6 % | 2.794 % | **0.859 %** | PASS |
| G3 size | chunks 520,648..575,454, articles 34,002 | 548,051 / 34,002 | **548,468** (+0.08 %) / 34,002 | PASS |
| G4 replay K1, 280 items | differing items must contain a changed Wikivoyage article; others identical | A = traces 280/280 identical raw | B = A on 279/280; the 1 diff is explained | PASS |
| G5 format | formatVersion 2, dims 384, emb sha ec38e8da..., lead_vecs = articles, FTS, integrity ok, indexed >= 99.9 % | ok | ok (`integrity_check` ok, lead_vecs 34,002, indexed 548,422 = 99.992 %) | PASS |

Per-pattern chunks (current -> candidate): empty_paren 7,437 -> 12; prep_punct 6,603 -> 3,554; unit_no_number 616 -> 608 (mostly false positives, unchanged); between_and 296 -> 160; paren_lead_punct 357 -> 24; lang_label_empty 50 -> 4; orphan_modifier 49 -> 21; line_lead_punct 392 -> 385; weak space_punct 5,550 -> 3,495. Cosmetic-class only (empty_paren, paren_lead_punct, lang_label_empty; sum of pattern chunks) 7,844 -> 40.

Why P2 missed: the current pack was built with a wiki-pack-lib.mjs that predates the `stripMediaLinks` fix now in every builder copy (md5 04776e53 on the mini and in boar-app). 80 articles differ current vs control (stray `]]` / `|450px]]` from nested-link captions), -8,926 text bytes, -27 chunks. Hole counts of control vs current are identical to 1 chunk (15,311 vs 15,312), so the baseline is not affected; the candidate carries this fix too (every G4 "changed article" set below is therefore a superset of the whitelist effect by 80 articles; the control-vs-candidate variant in `g4-control-vs-cand.json` gives the same G4 result).

## 2. Size and build

| | current | control (unpatched, pass 1) | candidate |
|---|---|---|---|
| bytes | 351,092,736 | 344,530,944 (no embeddings) | 351,977,472 (+0.25 %) |
| chunks / indexed | 548,051 / 548,005 | 548,024 / 547,978 | 548,468 / 548,422 |
| textBytes | 281,859,411 | 281,850,485 | 282,360,691 (+0.18 %) |
| build wall | 111 s | 34 s | 37 s + 118 s (embed-only) |

Articles with changed text vs current: 12,755 of 34,002 (37.5 %); vs control (whitelist alone): 12,726. Free disk on the mini stayed 28-29 GiB (floor 25), `--min-free-gb 25` passed to the builder.

## 3. Patch (never applied to boar-app)

- `tools/wikivoyage-whitelist.patch` sha256 `9117c077c2d79da47ff181317b680f822c4493cfc1a739b50d993441ee88570f` (also `.sha256`), `diff -u` of `scripts/lib/wiki-pack-lib.mjs` (md5 04776e535a12674fc7b35e16afd306a5 -> 8517d06136acbe7d5d09c9aa4c94566c; sha256 of the patched file 5c7b1a45bd13e734e0a1859e3ac1e85cad8f3f28293b1d1509cacee263ddc842). Applies with `patch -p1` in a builder tree. Builder tree on the mini: `<runner>/kiln/packs/builder-wv2/` (copy of `builder/scripts`, symlinked `node_modules`).
- Content: `renderTemplate` calls new `renderWhitelisted()` for every non-listing template (listing templates unchanged); `cleanInline` gains a tidy step (`(`+`,`/`;` -> `(`, delete empty `()`). 76 template names in these families: units (km m mi ft metre kg lb km2 mi2 m2 ha acre kmh mph mm cm in c f and aliases, 26), currencies (eur usd gbp jpy cny rub inr php egp krw thb aud cad nzd chf idr sek nok dkk huf mxn brl zar try czk pln, 26, plus `currency|CODE|n`), `convert`/`cvt` (value, ranges, first unit), `lang` (2nd positional), `unesco`, `iata icao faa lid phone email station routebox entry rbe aur nycs nowrap nobr rint european road time isbn w ipa`. Everything else still drops (dead link, flag, marker, maplink, translink...).
- Tests: `tools/wikivoyage-whitelist.test.mjs` 20/20 on the patched lib (1/20 on the original); the existing `wiki-pack-lib.test.mjs` 16/16 with vitest on the patched lib (run from a scratch copy, boar-app untouched). The mini has no vitest.

## 4. Retrieval replay (G4)

K1 = boar-crypto (ae9fbd2c) + wikivoyage + boar-simplewiki-en (99bcec30), 280 requests of lp-K1-v01/cm/st, `--tasks-from` the K1 traces, tree `kiln-local/be-0cfd4a77-cut7-litepacks`, default replay settings (no packHeadPass/X2b; those act after retrieve()), compared object = `raw` (ordered source+title). Run A (current) reproduces the traces 280/280; run B (candidate): 279/280 identical (0 order-only differences).
- 169 items have no Wikivoyage article in A or B: all 169 identical. 111 items have one, 82 of them touch a changed article; 75 items have a Wikivoyage article with a hole chunk in A (by article), only 1 of them changed.
- The one change, `st-qa-travel-se-006` ("easiest public transport route from London Gatwick to Paddington with luggage"): Chipping Campden drops out, Gatwick Airport enters (4th slot). Both are changed articles. Not judged (0 judge calls); whether the new slot helps is UNKNOWN but on topic by title.
- Limits: article-level attribution only (raw has titles, not chunk ids); packHeadPass/X2b selection not replayed.

## 5. Before/after (candidate fixes)

- Korba: `nearest airport is in Raipur ()` -> `Raipur (RPR)`.
- Banff: `heated to .` -> `heated to 300 °F.`
- Angeles: `prices starting around ,` -> `around ₱800-1000,`
- Krapinske Toplice: `costs between and .` -> `costs between €5.50 and €7.`
- Western Mongolia: `range in size from to over in height` -> `from 2 ft to over 6 ft in height`.
- Remaining fact holes (4,329 chunks): not attributed by template. Of the two dump sentences I looked up, one is an inline `{{marker|type=see|...|name=memorial}}` that the builder deliberately renders as "" (listing template with name used in prose: "In Nagu there is likewise a , near the harbour"); the other was not a marker (UNKNOWN). Likely others: `{{flag}}`, `{{maplink}}`, links to place names. Rendering the marker's `name=` inline is the obvious next whitelist entry (not done: it would move a frozen candidate; G1 margin is only 0.011 points).

## 6. UNKNOWN
- Answer-level effect (judge) of the fixed holes: not measured (0 judge by brief). Expected: small; K1 prompts carried a Wikivoyage hole chunk in only 0 of 52 (K1-st) and 2 of 21 (K1-v01) chunks (PACK-HOLES §1.3).
- Whether the converted values are semantically right for every template (e.g. `{{station|name|city=..}}` shows the name, `{{rint}}` the line label; not checked against rendered Wikivoyage HTML, only eyeballed on 6 samples each).
- Sensitivity of G1 (0.789 %) to the scanner's `unit_no_number` false positives (608 chunks, 0.11 %), which stay in both packs.
- Not tested: device size/speed, `pack-check`, pin/manifest changes. A swap needs a new sha pin (`verify-manifest-pins.mjs`), and publishing needs r4to.

## 7. Reproduce / resume
```
# builder tree (already on the mini): cp -R <runner>/kiln/packs/builder/scripts <runner>/kiln/packs/builder-wv2/scripts; ln -s ../builder/node_modules builder-wv2/node_modules; cd builder-wv2; patch -p1 < ../work/wikivoyage-whitelist.patch
<on the mini> 'bash -lc "cd <runner>/kiln/packs/work && nohup ./wv2-build.sh > wv2-build.log 2>&1 &"'     # idempotent; markers in work/wv2/*.done; copy = tools/wv2-build.sh
# scans (python 3.14, on the mini, 2m50 for the three packs):
/opt/homebrew/bin/python3.14 -I holes.py <pack.sqlite> <out.json>
/opt/homebrew/bin/python3.14 -I tools/article_diff.py <A.sqlite> <B.sqlite> <scanA.json> <diff.json>
# replay (MacBook, 55 s per run): boar-eval/adapters/desktop-node/tools/replay-retrieval.sh --questions k1.requests.jsonl --tree kiln-local/be-0cfd4a77-cut7-litepacks --tasks-from k1.traces.jsonl --packs shared-data/crypto/boar-crypto.sqlite,<wikivoyage>,shared-data/packs/v3proto/boar-simplewiki-en.sqlite --verify-sha --out replay-X.jsonl
python3 -I tools/replay_compare.py replay-A.jsonl replay-B.jsonl diff-current-vs-cand.json g4.json
```
k1.requests.jsonl / k1.traces.jsonl = concatenation of arms/litepacks/runs/req/lp-K1-{v01,cm,st}-s42.requests.jsonl and traces/lp-K1-{v01,cm,st}-s42.traces.jsonl.
Files: `wikivoyage-rebuild/` (scan-{current,control,candidate}.json, diff-*.json, replay-{A,B}.jsonl, g4-*.json, wv2-build.log), `tools/` (patch, test, wv2-build.sh, article_diff.py, replay_compare.py). Tooling note: replay_compare.py first stripped no `Wikivoyage: ` prefix from raw titles (every item looked unexplained); fixed before any verdict, criterion unchanged. holes.py sha256 47968d1cd9e68c91b6d5703d49c7ca9b5e31e8b8b7a7eb03ff54fe3f0df737ee (unchanged).
