# C1-GAP-LEDGER (2026-10-21): why the submitted app differs from our engine. 5 rows verified, 1 not established, negative controls fail as required

Frozen ledger gap-ledger-2026-10-21.json (sha d743b1d4...), checker tools/gap_ledger_check.py, last run gap-ledger-check-2026-10-21.json (exit 0).
0 LLM, 0 judge, 0 phone. The snapshot is read with git show/grep at wt/native-qa 5f8cc8f4 (never the working tree). The device evidence is
existing RC1 files (apk 2ef43258, Pixel 8a), each pinned by sha. The sentence check reuses a2_state_check.py's ships/default regex.
Every code clause carries "our reading of the app maintainer's pre-release snapshot, not of RC1". The RC1 clause in each row is a device observation
of the effect. The cause stays a snapshot reading until row 0b photographs the installed catalogs.

## The six rows (page-ready; for section 1 under the S00 headline)
| # | sentence | snapshot check | device check | status |
|---|---|---|---|---|
| 1 model | The 1.7B model behind our 8 GB numbers is not in the app's model catalog: catalog.json lists Qwen2.5-1.5B and Qwen3-4B but no Qwen3-1.7B (our reading of the app maintainer's pre-release snapshot, not of RC1). On RC1 a request for the 1.7B failed with 'matches no installed model', and the only installed model was Qwen2.5-1.5B. | catalog.json sha 18406c60, l.44, l.65; 0 hits for qwen3-1.7b in assets | rc-speed9-17b/summary.json (1f80de00) error + installedModels; RC1-SPEED.md (8736d486) | **verified** |
| 2 style | The app's evaluation hook answers in the Detailed style with a 1,024-work budget because it takes the style from personalities.json defaultId ('detailed'), not from the user setting (DeviceEvalRunner.kt lines 164 and 203; our reading of the app maintainer's pre-release snapshot, not of RC1). On RC1, 50 of 51 answers ran Detailed at maxTokens 1024; the app moved one to Succinct by its own short-answer rule. | personalities.json l.37; DeviceEvalRunner.kt l.164, l.203; AppSettings.kt l.99 | rc-cv5-51-15b rows.jsonl (df26ed79): detailed 50/51, 1024 51/51 | **verified** |
| 3 packs | The app searched only its built-in knowledge base: RC1's log reads 'knowledge base + 0 packs', and its Knowledge screen offers extra collections only as network downloads from its own catalog, none of them ours. The code has no route to add a .sqlite pack offline: a single MAIN/LAUNCHER intent filter, and the only file picker takes text, CSV, JSON and PDF notes (our reading ...). | AndroidManifest.xml 1 intent-filter, l.31; DocumentsScreen.kt l.60, l.78; 0 hits for boar-packs/crypto/wikivoyage in assets | rc-speed9-15b logcat (d761cb36) l.836; RC1-PACKS.md (69a944fa) | **verified** |
| 4 warning | The app has no 'may be wrong' line for answers that come from model memory: the warning text our engine prints occurs 0 times in the code and assets (our reading ...). On RC1 the line appeared on 0 of the 3 questions where our bench engine shows it, and on 0 of 51 answers. | 0 hits in android-native for 3 warning strings | note2-rc-ref-aunion73a.json (354bc6b5) 0/3; rows.jsonl 0/51 | **verified** |
| 5 layers | Whether the app answers fact-table questions (population, height, dates and similar) with deterministic layers is not established: on RC1's evaluation hook the 8 such questions in the 51 all went to the 1.5B (176 to 424 generated tokens each), but that hook may bypass the chat's routing. Device-day check H2a decides. | none (on purpose) | rows.jsonl: 8/8 layer ids generated tokens > 0 | **not established** |
| 6 KB cutoff | The app sends the model only knowledge-base passages with a similarity of at least 0.7 (RagPure.kt line 41, applied in Retriever.kt lines 72-73; our reading ...). On RC1, retrieval was used on 1 of 51 questions, so the answers were in effect closed-book. | RagPure.kt l.41; Retriever.kt l.72, l.73 | rows.jsonl retrievalUsed 1/51 | **verified** |
In the page, "(our reading ...)" is the full label. Context for row 6, not in the sentence: NATIVE-PARITY found that lowering the cutoff to 0.5 adds no facts (1/97). So row 6 explains the closed-book behaviour. It is not a fix.

## Negative controls (planted in the ledger; all must FAIL)
- 901: the RagPure cutoff cited at line 35 instead of 41 -> **FAILED** (expected substring not within 35 +-3).
- 902: the sentence 'the app ships packs by default' -> **FAILED** (1 hit for the a2 verb regex).
- 903: correct fact with a wrong device sha (00000000) -> **FAILED** (sha mismatch).
The checker exits 0 only if every established row verifies and every control fails. It also needs the apk precondition (readout apk_sha256 2ef43258) and the snapshot commit to resolve.

## Deviations
- Hypothesis wording '6/6 verify' was not possible: row 5 has no measurement yet. The round-7 judges' framing (5 verified + 1 not established) is used.
- Row 3's '0 packs' log line comes from the rc-speed9-15b logcat (l.836). The rc-cv5-51-15b logcat buffer begins mid-run (its first EVAL line is vit-hum-004). Same apk, same phone, same day.
- Row 5 uses an RC1 observation (8/8 layer ids generated). It stays 'not established' because the eval hook (reason code eval:fixed-model) may skip chat routing.

## What changes after runsheet row 0b and H2a
- 0b (10-22): add the Model Catalog and Knowledge catalog photo shas plus the recorded apk sha to rows 1 and 3 as device checks, then re-run the checker.
  If the apk is not 2ef43258, or the Model Catalog lists Qwen3-1.7B or any boar-packs entry: strike rows 1 and 3 and rewrite the ledger for that RC (A2 state S10/S01/S11).
  If 0b matches: rows 1 and 3 may drop "not of RC1" for the catalog clause, because the device confirms it.
- H2a (rc-layer10-4b / -15b): >= 4/5 probes matching cut 7 -> row 5 becomes 'layers present' and leaves the ledger.
  Otherwise row 5 becomes 'no deterministic layers on RC1' with the H2a rows sha. B1-LAYER-SPLICE (+0.106 projected) then prices the gap.
- Any row that fails its line check after one correction pass is cut from the page and replaced by 'not established'.
