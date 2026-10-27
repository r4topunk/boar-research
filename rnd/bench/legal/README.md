# Offline Research Bench v0: licenses, reference outputs, offline gate

TL;DR
- **Public split sources are publishable, split by license.**
  - 30 a competitor team cases: Apache-2.0, keep the LICENSE and notice.
  - Our own questions and rubrics: we choose (proposal CC BY 4.0).
  - OSM gold: ODbL 1.0 with snapshot dates.
  - Wikipedia/Wikivoyage: links, plus 20 Wikivoyage venue names under CC BY-SA 4.0.
  - 5 questions quoted from the post author's posts: no license, but trivially short (low risk, UNKNOWN).
- **Claude (Opus+web) references:** Anthropic assigns the outputs to us and no clause forbids publishing. But the AUP forbids using outputs "to train an AI model… without prior authorization", and the Commercial Terms forbid supporting a third party's attempt to train competing models. A public Q→answer set is exactly what a distiller would scrape. **UNKNOWN whether publishing is fine.** For v0, publish only the **sha256 of each reference + model/date/prompt + the per-item judge verdicts + a recipe to regenerate**, and keep the texts private.
- **Proposed licenses:** code Apache-2.0; data CC BY 4.0 for what we wrote. The other data keeps its source license in **separate files** (Apache-2.0, ODbL, CC BY-SA).
- **Offline gate:** every APK entry gets the kit's verdict on the report card (✅ offline by construction / ⚠ network-capable / ⛔ trackers or GMS / — not an APK). The score is never changed. A machine-readable schema is in `offline-gate.schema.json`.

Scope: `rnd/bench/` v0 as planned in `rnd/lantern/bench-landscape.md` §7. Checked 2026-09-30. Not legal advice: it's a license inventory with the clauses quoted by link.

---

## 1. License of each question source in the public split

| Source (items) | License | Evidence | What the bench must do |
|---|---|---|---|
| **a competitor team test cases** (30 items, `tools/e2e_battery_cases.json`, `tools/e2e_cases.json` @ `a competitor repo` `87bb6e9abd`) | **Apache-2.0**, copyright "a competitor team contributors" | `LICENSE` at that commit ([competitor repo link removed]). It is an **abridged paraphrase** of Apache-2.0 (99 lines; GitHub detects it as `NOASSERTION`), ending with the standard "Licensed under the Apache License, Version 2.0" notice pointing to the canonical text. Treat it as canonical Apache-2.0 (the stricter reading). | Ship these items in their **own file** (`questions.competitor-app.jsonl`) with a copy of that LICENSE, a NOTICE line ("Questions from a competitor team, © a competitor team contributors, Apache-2.0, commit 87bb6e9abd"), and a "modified: rubric/grading added by the bench" notice (Apache §4(b)). |
| ↳ authorship note | [I] | Both files enter history only in commit `87bb6e9` (2026-09-24, author `user.email <[email removed]>`, unsigned), on top of a competitor team's a competitor team history. The same blobs are in `a competitor team/competitor-app` main (same commit). | Do **not** write "the post author's own test cases" in the dataset card. Write "test cases from the a competitor repo fork (commit 87bb6e9)". the post author's authorship is plausible but unverified. |
| **Lantern originals** (23 items, `license: "original…"` in `rnd/lantern/handoff/questions.vitalik-lantern.jsonl`) | ours → **CC BY 4.0** (proposal) | written by the team | Only reference sources are links, which need no license. |
| **Quoted from the post author's posts** (5 items: vit-hum-001, vit-fa-001 via X; vit-hum-003, vit-hum-004 via Farcaster; vit-trv-004 via vitalik.eth.limo) | **none stated**. X/Farcaster: the author keeps copyright, and the platform license doesn't extend to us. The blog repo `vbuterin/blog` has no license. | one-sentence questions ("Tell me about Japan.") | Keep them as short quotations with the link (de minimis / quotation). **UNKNOWN**, low risk. Fallback: paraphrase them. |
| **BOAR dataset v2** (~20 items; `eval/dataset/questions.v2.jsonl`, 61 rows in `wt/eval-vitalik`) | questions `original` (BOAR repo is **MIT**: https://github.com/UPSTREAM_REPO/boar-app); gold as below | `license` field per row: 26 `original`, 20 `original; ODbL (OSM gold); CC BY-SA 4.0 (Wikivoyage gold)`, 10 `…CC BY-SA 4.0 (Wikivoyage gold)`, 5 `…notes quote public-health guidance` | Relicense our own questions to CC BY 4.0 (we are the authors; MIT also allows it). Check the 5 health `notes` before publishing: quoted guidance keeps its source's terms. UNKNOWN which sources those are; not read. |
| **OSM gold** (20 cities in `gold/v2/*.json`, 40 references) | **ODbL 1.0**, "© OpenStreetMap contributors" (https://www.openstreetmap.org/copyright) | each gold file already carries `license` + Overpass `snapshot` (`osm3s.timestamp_osm_base`). Snapshots: 38 refs between **2026-09-26 20:19:50Z and 20:27:59Z**; **food-015 at 2026-06-01T08:52:28Z** (an Overpass base about 4 months older, flag it) | Publish the gold venue lists as their own ODbL database (`gold/osm/`), with attribution + the snapshot per file. A per-city list of all vegan venues is plausibly a *substantial extract*, so share-alike applies to **those files only**. The rest of the bench is a separate work (ODbL "Produced Work"/collective use). |
| **Wikivoyage in gold** (20 venue names in `gold/v2/*.json` `wikivoyage.vegListings`, + page titles) | **CC BY-SA 4.0** (https://en.wikivoyage.org/wiki/Wikivoyage:Copyleft) | names only, no prose | Attribute page title + URL. Keep them in a field or file marked CC BY-SA 4.0 (better: split out of the ODbL files so each file has one license). |
| **Wikipedia / Wikivoyage as `reference_sources`** | links only | — | No license needed for links. If a rubric or answer ever quotes article text, that file becomes CC BY-SA 4.0 (https://en.wikipedia.org/wiki/Wikipedia:Copyrights). |
| **Held-out** (Veil's 30: `rnd/veil/o2-blind-items.jsonl` 46d5f5b7…, `-b2` 887ee740…) | ours → CC BY 4.0 when released | written by Veil | v0 publishes the **hash only** (plan §7). |
| **Competitor answers files** (if the bench publishes a competitor team/a competitor team outputs) | the submitter's call | both repos are Apache-2.0 (a competitor team `LICENSE`, a competitor team above), but *their outputs* aren't "the Work" | "How to submit" should ask each submitter to license their answers file (CC BY 4.0 suggested). |

## 2. Can we publish Claude (Opus + web) answers as benchmark references?

Which terms apply depends on how the references are generated. Claude Code on a Pro/Max plan falls under the **Consumer Terms**; on an API key it falls under the **Commercial Terms**. **UNKNOWN** which account Lantern will use; record it in the reference manifest.

| Clause | Text (paraphrased, see link) | Link |
|---|---|---|
| Consumer Terms §4 (effective 2025-10-08) | Anthropic assigns to the user all its right, title and interest, *if any*, in Outputs. | https://www.anthropic.com/legal/consumer-terms |
| Consumer Terms §3 | You may not use the Services to develop products/services that compete with them, including to develop or train AI/ML models. | same |
| Commercial Terms §B (effective 2025-06-17) | Customer owns its Outputs; Anthropic assigns its rights (if any). | https://www.anthropic.com/legal/commercial-terms |
| Commercial Terms §D.4 | Customer may not access the Services to build a competing product, including to train competing AI models, and may not **support any third party's attempt** at that. | same |
| Usage Policy, "Do Not Abuse our Platform" (effective 2025-09-15) | Prohibits using inputs and outputs to train an AI model (model scraping/distillation) without prior authorization. | https://www.anthropic.com/legal/aup |
| Usage Policy, disclosure | When outputs are presented to people, disclose that AI was used. | same |

Reading:
- Nothing prohibits *publishing* outputs, and we own them.
- A benchmark reference is evaluation, not training.
- The risk is indirect. A public, clean Q→answer set is a distillation corpus. §D.4(c) ("support any third party's attempt") and the AUP clause could be read against releasing it openly.
- Separately, web-search answers may reproduce third-party text. Anthropic's assignment only covers *its* rights ("if any"), and quoted snippets stay their owners'.

**Verdict: UNKNOWN** (likely allowed, not confirmed).

**Recommendation for v0:**
1. Publish `references.manifest.jsonl`, one row per item: `{id, sha256(reference_text), model_id, tool+version, date, web_search: true, prompt_sha256, account_terms: consumer|commercial}`.
2. Publish the regeneration recipe: prompt template + command. Anyone regenerates under their own account and terms. Outputs will differ (the web and sampling change), so the published unit of comparison is the **per-item judge verdicts** and the ratio, not the text.
3. Publish the per-item judge verdicts (win/tie/loss + labels). These are our own outputs if the judge is not Claude. If the judge is Claude, the same clauses apply, and verdict labels are far less distillable than full answers.
4. Keep the reference texts private, and show them to a submitter on request for audit.
5. Label everything as AI-generated (model id + date), per the AUP disclosure clause.
6. **Upgrade path:** ask Anthropic for written permission to release the texts. If granted, publish them under CC BY 4.0 plus a (non-binding) "not for model training" request.

## 3. Proposed license for the bench

| Part | License | Why |
|---|---|---|
| Code (`score.py`, judge-core, precheck, the vendored offline-proof tool) | **Apache-2.0** | Patent grant. It matches a competitor team and a competitor team, the two projects we invite. MIT code (BOAR) can be included. |
| Our questions, rubrics, grading rules, held-out (on release), dataset card | **CC BY 4.0** | Attribution travels with citations, and it's the usual license for eval data. |
| a competitor team questions | stay **Apache-2.0** (own file + LICENSE + NOTICE) | Source license (§1). |
| OSM gold | stay **ODbL 1.0** (own files, snapshot dates) | Share-alike on the extract. |
| Wikivoyage/Wikipedia names or text | stay **CC BY-SA 4.0** (own file/field) | Share-alike. |
| Claude references | **not published** in v0 (hash manifest only) | §2. |

Layout that keeps one license per file: `LICENSE` (Apache-2.0, code), `data/LICENSE` (CC BY 4.0), `data/competitor-app/{questions.jsonl,LICENSE,NOTICE}`, `data/gold/osm/*.json` + `LICENSE-ODbL`, `data/gold/wikivoyage/*.json` + `LICENSE-CC-BY-SA`. Plus `data/references.manifest.jsonl` and `NOTICE` listing all of the above.

## 4. The offline-proof kit as a bench gate

Tool:
- Upstream candidate: `scripts/audit-apk.py` v0.2.0 in branch `chore/offline-proof-kit` of boar-app, sha256 `c8029409…991d`.
- Research copy: `rnd/veil/offline-proof/audit_apk.py`, sha256 `75cc7d87…505e`.
- The bench vendors one pinned file and records its sha256 in every report card. Output is deterministic, so anyone can re-run it.

**Rule: the gate labels, it never changes a score.**

| Kit verdict | Card mark | Meaning printed on the card |
|---|---|---|
| `NO-NETWORK-BY-CONSTRUCTION` | ✅ **Offline by construction** | No INTERNET permission, no GMS/tracker classes. Add "· 0 B measured" if a dynamic netstats result (`scripts/netstats-uid.sh`) is attached. |
| `NO-INTERNET-PERMISSION but GMS/tracker code present` | ⚠ **Offline, with Play Services/tracker code** | Can't open sockets itself; another process could still send data on its behalf. |
| `NETWORK-CAPABLE` | ⚠ **Network-capable** | Offline-during-use is app policy, not provable from the APK. The card lists the `review` hosts. |
| `NETWORK-CAPABLE + TRACKERS` | ⛔ **Network-capable + trackers** | Tracker SDK classes present. |
| no APK (iOS build, desktop proxy) | — **not an APK** | Gate not applicable. All v0 BOAR entries (iPhone 1.5B, Mac-mini proxies) get this. |
| extra flag | 🔑 **debug-signed** | The signer is a debug/public key (`debug_cert` or a known public cert), so the build isn't attributable to its publisher. |

Expected v0 marks from existing reports (`rnd/veil/offline-proof/reports/`):

| Entry | Mark |
|---|---|
| a competitor team 1.0.0 | ✅ |
| a competitor team 1.1.10 | ✅ |
| BOAR offline `1928502d` | ✅ 🔑 |
| BOAR v1.0.0 | ⚠ network-capable |
| BOAR iPhone and the proxies | — |

Card fields: see `offline-gate.schema.json` (device block `offline_proof`).

---

## Decisions / Options / Tasks

**Decisions (Veil, reversible):**
- One license per file.
- The a competitor team cases stay Apache-2.0 and are attributed to "a competitor team contributors", not to the post author.
- Claude references are hash-only in v0.
- The gate is a label, not a score.

**Options (Lantern / coordinator):**
- O-L1: CC0 instead of CC BY 4.0 for our data (simpler reuse, no attribution).
- O-L2: ask Anthropic for written permission to publish the reference texts.
- O-L3: rank ⚠/⛔ entries in a separate table instead of the same one.
- O-L4: paraphrase the 5 post-quoted questions to remove the only UNKNOWN in §1.

**Tasks:**
- [ ] Lantern: split files per §3 layout; add NOTICE; record `account_terms` in the reference manifest.
- [x] Lantern: checked the health `notes` (see UNKNOWN, resolved).
- [x] `food-015` (OSM base 2026-06-01) is not in v0; the bench uses food-001/002/006, snapshots 2026-09-26.
- [ ] Veil (on request): vendor the pinned `audit-apk.py` into the bench and run it on submitted APKs.

**Metric:** 9 sources classified (8 with a license and link, 1 UNKNOWN low risk); 6 Anthropic clauses cited; 0 blockers for publishing the question split.
**Next step:** Lantern applies the §3 layout on day 5; coordinator decides O-L2.

## UNKNOWN
- Whether publishing Opus+web reference texts is acceptable to Anthropic (§2). Not asked.
- Which terms (consumer vs commercial) govern the account that will generate the references.
- License of short questions quoted from X, Farcaster and vitalik.eth.limo (5 items).
- ~~Sources quoted in the 5 v2 health `notes`.~~ Resolved by Lantern (2026-09-30): the 3 danger notes in the bench (dng-001/002/005) paraphrase CDC pages (US federal, generally public domain; attribution kept). dng-003 (NHS, OGL v3, needs attribution) and dng-004 (Ready.gov/FEMA) are not in v0.
- Whether the ODbL "substantial extract" threshold is met by a single-city vegan list. The recommendation assumes yes, the safe side.
- the post author's authorship of commit `87bb6e9`.
