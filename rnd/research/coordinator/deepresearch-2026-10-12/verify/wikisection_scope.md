# Verify: WIKISECTION scope (group wikisection_scope, 2026-10-12)

Adversarial check of the scope claims behind "Wikipedia is closed as a source". Primary evidence: tool code (`arms/wikisection/tools/{section_gate,anywhere_gate}.py`), aggregates (`arms/wikisection/aggregates/*.json`, `arms/lossmap/aggregates/lossmap-H-*.json`; ids, labels and probabilities only), pack `meta` tables and manifests (`shared-data/packs/*.json`, `shared-data/gate-ref/boar-wiki-en-07.sqlite`, read-only), the HF API, download.kiwix.org, the Kiwix OPDS catalogue and dumps.wikimedia.org (all fetched 2026-10-12). Nothing under `blind/` or `rnd/veil/` was opened.

## Claim 1: H5/H5b searched only the top-100k pack, only absent items with a kept source; never the 15 shards, a fresh dump, or the no-kept-source items

**Evidence**
- Pack opened. `section_gate.py` line 15: `PACK = f"{ROOT}/shared-data/packs/boar-wiki-en-top100k.sqlite"`, plus `VITAL = .../wiki-vital5.sqlite`, used only as the intro control. `anywhere_gate.py` imports `section_gate as sg` and opens only `sg.PACK` (`fdb = sqlite3.connect(f"file:{sg.PACK}?mode=ro"...)`). Neither script opens a `boar-wiki-en-NN` shard, Wikivoyage, the crypto pack or any dump. "Wikivoyage: X" kept titles are stripped to X and resolved in the Wikipedia pack, so Wikivoyage text was never searched.
- Pack identity. The top-100k `meta.sources` value is `"HuggingFaceFW/finewiki (enwiki, Enterprise HTML dumps of August 2025)"`, with `pageviews-en-20250815.tsv` and `days 1`. It holds 98,389 articles, built 2026-10-02 with params `fullTop 100000` and `--drop-rest`, from 15 FineWiki EN shards at revision 8bd13e72 (manifest `build.args`).
- Item selection, identical in both scripts: the item must have `primary == "absent_knowledge"` in `lossmap-H-{vpara,v02}-s42.json`, which is arm H (deep + think 512), seed 42 only. It goes into `on_topic` if `labels.source_on_topic`, or into `off_topic_kept` if `n_kept > 0`. **Items with `n_kept == 0` are skipped by construction.**
- Counts recomputed from the lossmap aggregates:

  | set | absent items | on-topic | off-topic, kept > 0 | no kept source |
  |---|---|---|---|---|
  | V-para | 34 | 13 | 1 | 20 |
  | v0.2 | 78 | 30 | 14 | 34 |

  The gate JSONs list the same n (13/1 and 30/14).
- Loss share of arm H. On V-para the gated items carry 0.254 of total loss (on-topic 0.231 + off-topic 0.023). The ungated no-kept absent items carry **0.333**, i.e. 57 % of the absent bucket's 0.59. On v0.2 it is 0.347 gated vs 0.205 ungated.
- "29/51 no-kept" (critique §0b) is not all absent. Of those 29 V-para items, 20 are absent, 8 wrong and 1 thin. Of the 54 on v0.2, 34 are absent, 10 hedged, 6 wrong, 3 off-question and 1 thin.
- No fresh-dump or shard check exists anywhere in `rnd/`. A grep for wikifresh, kiwix, enterprise_html and wikipedia_en_all finds only sweep notes and the Sonar card. The Sonar card `full-enwiki-pack-arm.md` says "No run of any kit with `boar-wiki-en-*` exists".

**Two further scope limits that nobody reported**
- **Table chunks are invisible to H5b.** The builder (`wt/enwiki-droprest/scripts/build-wiki-pack.mjs` l.226–231) writes a chunk to FTS only `if (!isTable(piece))`. The top-100k pack has 4,019,506 chunks but only 3,235,902 indexed, so **19.5 % of chunks, the tables, cannot be reached** by `anywhere_gate.py`'s FTS. Numeric facts in tables are therefore under-tested. `section_gate.py` read all chunks of the kept article (up to 60), so the gap applies only to "elsewhere in the pack".
- **The 1/13 result is threshold-sensitive.** V-para on-topic `max_p` counts by threshold: ≥ 0.5 → 5, ≥ 0.6 → 4, ≥ 0.7 → 1, ≥ 0.8 → 0. Three items sit at 0.61–0.62. On v0.2 the counts are ≥ 0.6 → 22/30 and ≥ 0.8 → 7/30. The script's own flag is `pass_40pct: True` on v0.2 on-topic (0.433) and on off-topic (0.50); WIKISECTION.md reports this as "marginal; unverified".

**The "15 full shards" premise is wrong (CONTEXT says "≈ 3.8 M articles")**
- The 15 manifests sum to 6,124,620 articles, 21.40 GB of text and 18.03 GB of packs. Each shard's params are `fullTop 1000000, leadChars 2500`: the global top-1M articles by single-day pageviews (2025-08-15) are kept in full, and the remaining ≈ 5.1 M are leads only (≤ 2,500 chars).
- Shard 07 (local copy in `shared-data/gate-ref/`) has 403,973 articles, of which only 60,893 are longer than 2,600 chars.
- So the shards add bodies for ranks ≈ 100k–1M plus leads for the long tail. **No BOAR pack holds the full body of articles ranked below 1M.**
- Shard location: only `shared-data/gate-ref/boar-wiki-en-07.sqlite` is on disk (MacBook). The mini has none. All 15 are on the HF dataset `r4topunk/boar-packs` (public; API `private: False`) at pinned commit 6e9afe96 (`boar-app/src/rag/wikiEnPacks.ts`).

**Verdict: confirmed on every count and on the pack identity, corrected on the description of the shards.**

**Corrected claim.** H5 and H5b opened only `boar-wiki-en-top100k.sqlite`: 98,389 full articles, FineWiki enwiki from the August 2025 Enterprise HTML dumps, top-100k by pageviews of 2025-08-15. H5 also read wiki-vital5 intros as a control.
- Items gated: only arm H, seed 42, absent-knowledge items with a kept source. That is 13 + 1 of 34 on V-para and 30 + 14 of 78 on v0.2.
- Never gated: the 20 V-para and 34 v0.2 absent items with no kept source, which carry 0.333 and 0.205 of H's loss.
- Never searched: the 15 shards (6.12 M articles; the top 1M by pageviews in full, ≈ 5.1 M as leads only), Wikivoyage, any fresh dump, and the table chunks (19.5 %) of the top-100k pack.
- Threshold: the V-para 1/13 holds at p ≥ 0.7 and becomes 4/13 at p ≥ 0.6.

**Implication.** "Wikipedia closed for the bar" is established only for 43 % of the V-para absent-bucket loss (0.254 of 0.59). The untested 57 % is the larger part. Re-run the anywhere-gate over all 34 V-para absent items before committing any non-Wikipedia corpus spend.
- On disk: the full shards fit the budget. 18 GB + 12.3 GB deep model + about 6.5 GB kit ≈ 37 GB, under 50 GB.
- The real question is whether the facts are in the bodies of ranks 100k–1M or in post-Aug-2025 edits.

## Claim 2: FineWiki is the Aug-2025 Enterprise HTML snapshot, ≈ 13 months stale; a 2026-09/10 English Wikipedia is available as Kiwix `wikipedia_en_all_nopic_2026-09/-10` or as the Enterprise HTML dump

**Evidence**

| source | fact | where |
|---|---|---|
| https://huggingface.co/datasets/HuggingFaceFW/finewiki (README) | "Snapshots from August of 2025 were used." | card l.1475, plus l.1314 "Wikipedia HTML dumps … from *August of 2025*" |
| HF API, same dataset | sha 8bd13e72… (= BOAR's pinned revision in `run-en-shards.sh`), lastModified 2025-10-22; no newer FineWiki revision or successor dataset (HF search "finewiki") | `api/datasets/HuggingFaceFW/finewiki` |
| https://download.kiwix.org/zim/wikipedia/ | English "all" ZIMs, newest per flavour: **nopic 2026-06 (49G)**, **maxi 2026-08 (119G)**, mini 2026-09 (13G); also `top_nopic_2026-09` 2.6G and `top1m_nopic_2026-04` 16G. **No `wikipedia_en_all_nopic_2026-09` or `-10` exists.** | directory listing rows |
| Kiwix OPDS (library.kiwix.org/catalog/v2) | all nopic: updated 2026-06-17, 52,690,707,456 bytes. all maxi: 2026-08-25, 127.4 GB. all mini: 2026-09-09, 14.4 GB. "top" = "A selection of the best 50,000 Wikipedia articles", nopic 2026-09-14, 2.75 GB | OPDS entries |
| https://dumps.wikimedia.org/other/enterprise_html/ | Enterprise HTML mirrors "as of 24 March 2025, are no longer replicated on this site"; last public run 20250320. Current HTML is available only via the Wikimedia Enterprise Snapshot API, which needs an account | page text, `runs/` listing |
| https://dumps.wikimedia.org/enwiki/20261001/dumpstatus.json | `articlesdump` done 2026-10-08, 25.8 GB bz2 in 71 parts (wikitext, not HTML); multistream 27.2 GB. The 20260901 run is also complete (25.68 GB) | dumpstatus.json |
| https://dumps.wikimedia.org/other/cirrussearch/ | `DEPRECATED.txt`; last run 20251229; enwiki content 43.4 GB | listing |

**Verdict: corrected.**
- The FineWiki date is confirmed. Its staleness is 13–14 months.
- The named fresh sources are wrong. No 2026-09/10 nopic "all" ZIM exists (newest 2026-06, 52.7 GB). The 2026-08 maxi ZIM is 127 GB. A public 2026-09/10 Enterprise HTML dump does not exist: it is account-gated, and an account is an action only r4to can take.

**Corrected claim.** BOAR's shards come from FineWiki revision 8bd13e72, which is the dataset's latest revision, built from the August 2025 Enterprise HTML snapshots. That is ≈ 13.5 months stale on 2026-10-12. The freshest public full-text English Wikipedia sources today are:
- The **enwiki 2026-10-01 XML dump**: pages-articles, 25.8 GB bz2, 71 parts, wikitext, completed 2026-10-08.
- Kiwix `wikipedia_en_all_maxi_2026-08`: 127 GB, too big for our disk.
- Kiwix `wikipedia_en_all_nopic_2026-06`: 52.7 GB, less fresh.
- Kiwix `wikipedia_en_top_nopic_2026-09`: 2.75 GB, best 50k articles only, a same-tier freshness probe.

A fresh Enterprise HTML snapshot needs a Wikimedia Enterprise account.

**Implication.** WIKIFRESH must use the 2026-10-01 XML dump, streamed part by part: both machines are at about 25 GiB free, the alarm floor. Its wikitext needs template stripping, and infobox numbers stay readable as template parameters.
- Datastores' cost line ("one dump download ≈ 25 GB bz2") is right only for the XML dump. It cannot be landed whole on either machine without a GC first.
- Kiwix `top_nopic_2026-09` (2.75 GB) is a cheap first probe on popular articles only.

## Claim 3 (design)

Written to `verify/wikifresh-gate-design.md`. It covers:
- Stage A: the 15 Aug-2025 shards, rotated one at a time (shard 07 is already local).
- Stage B: the 2026-10-01 XML dump, streamed with no full index.
- Items: all absent items, the no-kept ones included.
- Calls: ≈ 4.5k jev requests per stage, about [usage detail removed] each. Local-model verification of hits. 0 Claude calls.
- Peak disk ≤ 3 GB. Wall ≈ 1–1.5 h (A) and 1.5–3 h (B) on the mini.
- Pass bar **WIKIFULL-REOPEN**: ≥ 14/34 V-para absent items verified present in the union of A and B. ≥ 7/34 present only in B means rebuild from the fresh dump. ≤ 6/34 closes Wikipedia at every scope.

## Reconciliations
1. **CONTEXT/critique "15 full enwiki shards (≈ 3.8 M articles)" vs the manifests.** The shards hold 6,124,620 articles: the top 1M by pageviews in full, ≈ 5.1 M as leads only. Settled by the manifests plus shard 07's meta and length counts. "Full" overstates them, and 3.8 M has no source in the files.
2. **"29/51 no-kept-source items never tested" (critique §0b) vs "20 V-para absent items with no kept source" (this claim).** Both are true for different populations. Of the 29 no-kept items, 20 are primary absent, which is the population the gate targets; the other 9 are wrong or thin, which a corpus cannot fix by presence alone.
3. **WIKISECTION "v0.2 13/30, marginal vs the 40 % bar" vs the script output `pass_40pct: True`.** The script passed v0.2 on its own bar (0.433 and 0.50). The report downgraded it because it was unverified and tangential hits were visible. Neither side verified the hits. The design requires verification before any bar is applied.
4. **Datastores' "2026-09/10 Wikipedia (Wikimedia dump or refreshed FineWiki)" vs reality.** No refreshed FineWiki exists (HF latest 2025-10-22). The only 2026-09/10 full-text source is the XML wikitext dump.
5. **Datastores/critique "re-check the same 13 + 30 items" vs the critique §0 "all absent items".** The design follows the critique. The 13 + 30 would repeat the population already measured and miss 57 % (V-para) of the absent loss.
