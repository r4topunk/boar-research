# Persona A-union: candidate pack set (assembled as files), 2026-10-21

Status: **candidate, pending r4to's veto on PERSONA-MAP v1.** Nothing frozen, hashed or shipped; no pack rebuilt, nothing downloaded, 0 judge calls, 0 paid. Map and approval: coordinator/PERSONA-MAP-v1-draft.md (r1) and PERSONA-MAP-v1-APPROVAL.md (APPROVE WITH EDITS; the six edits are applied in r1). This file only assembles what the draft's A-union (§3) already names.

TL;DR
- On the mini: `<runner>/shared-data/packs/persona-a-union/` = 6 symlinks to the already-built pack files + 4 manifest sidecars + cards/licence files + `MANIFEST.json` + `SHA256SUMS` (`shasum -a 256 -c SHA256SUMS` passes for all 6 packs and the gazetteer; the 6 shas equal the persona-map draft's shas).
- **6 text packs = 435,298,304 B = 435.3 MB (415.1 MiB).** With the gazetteer 458,260,480 B (458.3 MB). Mini free space after: 30 GiB (symlinks, 0 B added; the cards/MANIFEST add < 100 KB).
- Gazetteer: **exists** (world-places.sqlite, 22,962,176 B, sha 215ce466...). Area tiles for the persona: **not built** (per item location, built at freeze); 4 city tiles + 5 catalog tiles exist from earlier runs.

## 1. Table
Persona families: T = travel, Te = tech, S = science (incl. everyday health), P = place, H = humanities (none, B's kit only). Sizes = file bytes; sha256 = file sha256 (recomputed on the mini).

| pack id | file | bytes | MB | sha256 | licence | source code(s) in `articles.source` | families |
|---|---|---:|---:|---|---|---|---|
| boar-wikivoyage-en | boar-wikivoyage-en.sqlite | 351,092,736 | 351.1 | ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e | CC BY-SA 4.0 (Wikipedia, Wikivoyage) | 1 | T |
| boar-visa-en | boar-visa-en.sqlite | 11,231,232 | 11.2 | d1dd0ffb58a8e4f9b50a6a21cb164bdb314a7181eb2803c952db21e21359ad20 | CC BY-SA 4.0 | 0 | T |
| boar-crypto | boar-crypto.sqlite | 36,093,952 | 36.1 | ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb | mixed: CC0 1.0, BSD-2/3-Clause, PD, MIT, CC-BY-4.0, FSFAP variants, CC BY-SA 4.0 (per-source map in meta) | 0, 5, 6, 7, 8 | Te |
| boar-medlineplus-en | boar-medlineplus-en.sqlite | 4,268,032 | 4.3 | c9ac4dcfdae367d4502c3360bf0ffc9596d55290c0a49e0835aeedf990ba227a | PD (NLM) + credit line | **10** | S |
| boar-firstaid-en | boar-firstaid-en.sqlite | 20,987,904 | 21.0 | 8cfab0b47ec8c5cb32840b24df1054c4df1a08d600d063c95c022c58eb5bf558 | CC BY-SA 4.0 + US PD (FM 21-76, federal works, ATP 4-02.11) | 0, 1, 2, 3, 4 | S |
| boar-factbook | boar-factbook.sqlite | 11,624,448 | 11.6 | c585435354a413d04790882c4e2263f725b1024c067febad3f2a99783e663447 | CC0 (CIA World Factbook archive, data as of 2026-09-11) | **11** | P |
| **A-union text total (6)** | | **435,298,304** | **435.3** | | | | |
| companion: world-places gazetteer | companions/world-places.sqlite | 22,962,176 | 23.0 | 215ce4663b2f79dbf25e9cacab90cd8aa0a8711721663a733cb53bc49d972892 | CC BY 4.0 (GeoNames cities15000) | (places-pack format) | T (with a device location) |

Source-code values read from the pack files (`SELECT source, count(*) FROM articles GROUP BY source`, read-only). Targets of the symlinks: wikivoyage `packs/`, visa `packs/wave4/`, crypto `packs/pinned/ae9fbd2c.../` (the valid build; `shared-data/crypto/boar-crypto.sqlite` is the rejected OLD 35,962,880 B build and was not used), medlineplus/firstaid `packs/wave1/`, factbook `packs/wave2/`.
Not included (per the draft §6): boar-nist-crypto, boar-preparedness (superseded by firstaid), boar-wiki-en-07, qa-money-se. **boar-vitalik-blog-en** (built 2026-10-21 00:24, 8,806,400 B, sha 94a7ec6e..., WTFPL, user-selected only, unmeasured, source code 13) is not in the map and is not in this set (the draft's §5.1.4 exclusion logic would apply; r4to decided Q11 on 10-20).

## 2. Files in the directory
| path | what |
|---|---|
| `<id>.sqlite` (6) | symlinks to the built packs |
| `<id>.sqlite.json` (5) | symlinks to the build manifests (not for crypto: its sidecar describes the OLD build; the sidecars hold an internal build path in `file`, so they are not for publication) |
| `companions/world-places.sqlite` | symlink to the gazetteer |
| `cards/<id>.md` (6) + `cards/kit-vexact-places.md` | pack cards (copies of rnd/research/packs; visa = symlink to wave4 card) |
| `cards/LICENSE-boar-visa-en.txt` | symlink to the existing wave4 licence file |
| `cards/LICENSE-boar-{medlineplus-en,firstaid-en,factbook}.md` | rendered with publish_pack.py's `license_md()` (the same text the HF folders carry); no upload |
| `MANIFEST.json`, `SHA256SUMS` | per pack: id, file, target, bytes, sha256, licence, licence_file, card, source codes, families; plus companions and exclusions |

Licence gap: **boar-wikivoyage-en and boar-crypto have no standalone LICENSE file on disk** (no template in publish_pack.py; their licence is the `license` string in the pack `meta` table and the card). `licence_file` is null for them in the manifest. Not invented here.

## 3. What the app maintainer's app needs to load them
Evidence: native engine source read-only, local copy boar-ios/.ref/android-native/engine/.../rag/WikiPack.kt (a snapshot; its commit vs 0be84ac, the commit the draft cites, is **UNKNOWN**); persona-map §4; pack cards.
| need | state |
|---|---|
| Pack format | all 6 are `boar-knowledge-pack` formatVersion 2, dims 384, embedding model bge-small-en-v1.5 q8_0 (sha ec38e8da...f514), contentless FTS5. The native engine reads format 2 (WikiPack.kt). Embedding model required and shared (36,806,944 B per the draft). |
| Install path | the app opens any `.sqlite` in its pack dir as `local-<name>` (BoarServices.kt l.170, per the draft); whether the submitted README documents side-loading, and offers all 6 packs: **UNKNOWN** (draft §8). The packs are not in the native catalog.json (draft §4), so a catalog or side-load step is needed. |
| Source code to label | native `PackSource` enum: 0 ENWIKI, 1 ENWIKIVOYAGE, 2 ENWIKIBOOKS, 3 APPROPEDIA, 4 USGOV, 5 EIPS, 6 ETHSPECS, 7 ETHEREUMORG, 8 BIPS. Packs using only codes 0-8 (wikivoyage 1; visa 0; crypto 0,5,6,7,8; firstaid 0-4) map cleanly. **medlineplus (10) and factbook (11) are outside the enum**: `SOURCES.getOrElse(code) { ENWIKI }` (l.351) shows their rows as Wikipedia, and the `topicSources` build (l.689-691, `mapNotNull { SOURCES.getOrNull(it) }`) leaves them out, so the topic-source title handling does not apply to them. Whether the rows are otherwise retrieved and cited, or dropped, on the APK: **UNKNOWN until checked** (persona-map Q3: confirm on the APK, or ship a label patch, or record the two packs as inert in the frozen map). Codes 9 (Stack Exchange), 12 (simple wiki), 13 (the post author blog) are not used by this set. |
| Licence/attribution | CC BY-SA and the crypto mix need the per-source attribution; the app shows each article URL and license from pack meta/`article_meta` when present (PackArticle.url/license). Display behaviour on device: **UNKNOWN**. |
| Gazetteer and tiles | different format (`boar-places-pack` v1 / `boar-poi-pack` v1, runner option `--places`); the TS claim kit reads them. Whether the native APK reads places packs and the area-tile flow: **UNKNOWN** (draft §4 "area tile in B", §8). |
| Storage | 435.3 MB text (458.3 MB with the gazetteer) + B's kit 3.1 MB + embedder 36.8 MB = about 498 MB in the draft's sum, plus area tiles (UNKNOWN until built; existing city tiles 0.66-9.9 MB each). Under the ruler's 50 GB gate by a wide margin. |
| Pinned builds | the file shas are the card shas, i.e. format-2 builds from the shared-data tree, not the v3proto rebuilds used by LITEPACKS (different shas); which ones the submitted APK reads: persona-map Q3, open. |

## 4. Gazetteer / area-tile item (checked, not built)
- The persona map names "places gazetteer 22,962,176 B + per-location tiles" (draft §3 table; travel family, kit-vexact-places card).
- **Gazetteer exists as a file**: mini `<runner>/shared-data/packs/pinned/215ce466.../world-places.sqlite`, 22,962,176 B, sha 215ce4663b2f79dbf25e9cacab90cd8aa0a8711721663a733cb53bc49d972892 (verified; GeoNames cities15000, 34,149 places, 8,374-tile index). Two other world-places builds sit in pinned (21.6 MB and 21.7 MB, other shas); the card's sha is the one linked.
- **Persona area tiles: not built.** They are built at freeze from item locations (RULER-SPEC §5.2). Existing tiles on the mini under packs/pinned (information only): t-N52E013 Berlin 3,706,880 B, t-N41E012 1,818,624 B, t-S34E018 389,120 B, t-N25E103 36,864 B, berlin.sqlite 3,309,568 B, several older duplicates by sha. The card lists 4 city tiles (Berlin, Lisbon, Tokyo W/E, 39 MB with the gazetteer) plus 5 catalog tiles in kit-vgps2.

## 5. Commands
```sh
<on the mini> 'cd <runner>/shared-data/packs/persona-a-union && shasum -a 256 -c SHA256SUMS && python3 -c "import json;m=json.load(open(\"MANIFEST.json\"));print(m[\"total_text_pack_bytes\"])"'
```

Status: candidate, pending r4to's veto on PERSONA-MAP v1.
