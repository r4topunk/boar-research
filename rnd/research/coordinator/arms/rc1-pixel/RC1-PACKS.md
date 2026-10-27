# RC1-PACKS: claim-kit packs into RC1 through the app (2026-10-21, device runner; 0 LLM, 0 judge)

TL;DR: **NOT RUNNABLE.** RC1 (team.sopa.aoair 2.0.0-rc1, release) has no in-app path that puts a .sqlite pack into files/corpus. Its Knowledge screen offers (a) "Pick Files & Import" for .txt/.md/.csv/.json/.pdf notes, which are chunked and embedded into a personal collection of the base knowledge base, not a pack, and (b) a catalog of 3 BOAR collections, downloadable only from the network. Crypto and Wikivoyage are not in that catalog. Stopped at the inspection step as the task rules say. Step 2 (rc-speed9-15b-packs) was not run; nothing was pushed to the phone.

## What the RC1 UI offers (UI steps, all reversible, nothing changed)
1. Chat home, tap the menu (86,210): drawer with Knowledge, Model Catalog, Boar Labs, Settings.
2. Tap Knowledge (400,1448). Section "Personal Files": "Import your own .txt, .md, .csv, .json or .pdf notes", a collection name field, "Pick Files & Import". "No custom collections yet."
3. Tap "BOAR Knowledge" (540,1268) to expand it, then scroll to the end (3 swipes). Three entries: Standard knowledge base (+1,000 topics, 1 MB, ACTIVE, indexed), Full knowledge base (+4,000 topics, 2 MB, NOT ON DISK, Download), Wikipedia Vital Articles (+50,000, 156 MB, NOT ON DISK, Download). No other packs, no "add pack file" control.
4. Back (105,196) to the chat home. Screenshots and the tap log: packs-ui/s02.png, packs-ui/s06.png, packs-ui/steps.log.

## Why there is no import route (snapshot wt/native-qa/android-native @ 5f8cc8f4, read-only; inference for RC1)
- AndroidManifest.xml: one intent filter (MAIN/LAUNCHER). No VIEW/SEND filter, so no intent or content-URI route for a pack file.
- DocumentsScreen.kt:60/78: the only file picker (OpenMultipleDocuments) asks for text/plain, markdown, csv, json, pdf, text/*. DocumentsViewModel.import reads the file as text (PDF via PDFBox) and calls DocumentImport.import into the knowledge base: a .sqlite would be read as text, and it would not land in files/corpus anyway.
- ModelsScreen.kt:105-217 (Knowledge "Topic packs"): corpus items are catalog assets with Download / remove only. BoarServices.kt:106 maps a catalog asset to files/<filename>. No code scans /sdcard/Download.
- DeviceEvalRunner.kt:244 lists packs from files/corpus/*.sqlite. On a release build, the only writer of that folder is the catalog downloader.

## Kit files that were to be imported (not pushed)
handoff/pixel8-2026-10-20/bench/kit/manifest.json: corpus/boar-crypto.sqlite 36.1 MB sha256 ae9fbd2c..31fb; corpus/boar-wikivoyage-en.sqlite 351.1 MB sha256 ff8595e3..6b8e.

## Phone state at the end
RC1 MainActivity in front (chat home), airplane_mode_on = 1, thermal status 0, battery 28.4 C, AC. Packs installed: still 0 (base KB only). Nothing in /sdcard/Download was added. Note: Wi-Fi shows enabled under airplane mode and the header reads "ONLINE" (seen, not touched; the earlier rc runs ran in the same state).

## Routes that would work (r4to's call, none taken)
- A debuggable RC (team.sopa.aoair.native or .devtest): DEVICE-DAY step 4 push loop via run-as into files/corpus, then the same request. This is the route the runsheet planned.
- The app maintainer adds crypto and Wikivoyage to the RC catalog (or a file-import for .sqlite packs); then download in-app with network on, which breaks the airplane rule for the setup step only.
- In-catalog alternative now: Wikipedia Vital Articles (156 MB) via Download (network). It is the X6 native run's "KB + wiki-vital5" state, not the claim kit; it would not reproduce the bench's Wikivoyage hits.

## Verdicts
- For the page: RC1 retrieval with the claim-kit packs is not measured; RC1 as shipped cannot load our packs, so its 1/9 retrieval stands as the release state (base KB only).
- For the app maintainer note: RC1 has no way to add a knowledge pack offline; packs arrive only through the catalog download, and the catalog carries no crypto or Wikivoyage pack. Ask: either list our packs in the catalog or accept a .sqlite through the Knowledge screen picker.
