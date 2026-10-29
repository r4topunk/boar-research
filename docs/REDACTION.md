# Redaction

TL;DR: the copied files went through one deterministic redaction pass (a rule table applied in a fixed order, no randomness and no clock in the rules), followed by a competitor-score pass, a few hand fixes, and a re-pinning of every sha256 that the record quotes for a changed file. The rules never touch numbers of our own experiments.

## Policy

| what | becomes |
|---|---|
| the app maintainer's real name or handle | "the app maintainer" in the record; since v1.1.2 the README and NOTICE credit him by his chosen public handle, @vaipraonde. His app's data stays unpublished |
| the volunteer tester's name, in prose and logs only | "a volunteer tester"; matched as the full name on word boundaries. Data files (dictionaries, title lists, retrieved text, usernames) are not rewritten, so place names, artworks and other people who share the word stay as they are |
| any other private person | a role |
| the author's handle in prose | stays as the byline "r4to"; no e-mail addresses anywhere |
| absolute local paths | repo-relative or `<workspace>/...`, `<home>/...` |
| host names and ssh or infrastructure commands | "the mini" (the Mac mini that ran experiments), "the MacBook"; ssh lines made neutral |
| internal agent names (Sonar, Anvil, Compass, Forge, Kiln, Summit, Maestri, Lantern, Plumb) | kept as lane names; explained once in `docs/HOW-THE-LAB-WORKED.md` |
| lines about plan usage, quotas, account limits, session windows and dollar spend | removed or replaced by "[usage detail removed]"; judge **call counts** (method) stay |
| competitor names | "a competitor team"; competitor scores in prose replaced by "[competitor score removed]" (best effort, sentence level) |
| the author of the post that inspired the bounty | named only as that author; other mentions are "the post author" |
| the cross-family judge | "OpenAI gpt-5.6-sol via the Codex CLI" |
| paid-gateway per-call cost fields in judge outputs | dropped when numeric |
| NHS (UK National Health Service) guidance text | withheld (v1.1.1): the quoted wording is replaced by a marker (`quotes_withheld` / `quote_withheld` with `note_licence` in JSON; `[NHS quote withheld]` in prose, tables and scripts); the organisation name and the source URL stay |
| copyright first-aid and health guidance text (MedlinePlus encyclopedia (A.D.A.M.), healthdirect, St John Ambulance, British and American Red Cross, ASCIA, Poison Control, American Burn Association, AAFP/WMS, Resuscitation Council UK, ERC) | withheld (v1.1.2), with the same markers: `quotes_withheld` / `quote_withheld` and `note_licence` ("copyright wording not redistributed; see url") in JSON, `[quote withheld ...]` in prose, tables and scripts, `[quote withheld: <org>]` inside retrieved web snippets in traces; the organisation name and the URL stay. US federal text (CDC, NIOSH, NWS/NOAA, Ready.gov, EPA, MedlinePlus non-encyclopedia pages) is public domain and stays |

## Rule hits in this build (rule id, files, hits)

| kind | rule | files | hits |
|---|---|---:|---:|
| line | acct-limit | 6 | 12 |
| line | acct-account | 26 | 32 |
| line | relay-chat | 8 | 31 |
| line | spend-line | 19 | 26 |
| line | maintainer-msg | 1 | 2 |
| rule | scratch-path | 111 | 578 |
| rule | heldout-abs-path | 110 | 122 |
| rule | session-dir | 1 | 13 |
| rule | ws-path | 2271 | 6034 |
| rule | mini-path | 422 | 962 |
| rule | home-path | 101 | 165 |
| rule | tilde-boar | 446 | 1350 |
| rule | ssh-mini | 107 | 498 |
| rule | host-mini-code | 103 | 134 |
| rule | host-mini-prose | 9 | 13 |
| rule | host-mini-slug | 329 | 554 |
| rule | author-email | 25 | 26 |
| rule | any-email | 10 | 25 |
| rule | sopa-account | 5 | 10 |
| rule | maintainer-name-poss | 29 | 43 |
| rule | maintainer-name | 33 | 72 |
| rule | upstream-repo | 41 | 61 |
| rule | maintainer-handle | 8 | 11 |
| rule | maintainer-role | 123 | 393 |
| rule | tester | 7 | 20 |
| rule | own-repos-rnd | 1 | 1 |
| rule | own-repos-eval | 2 | 2 |
| rule | author-handle | 18 | 122 |
| rule | heldout-setname | 108 | 272 |
| rule | vitalik-test | 28 | 50 |
| rule | comp-link-a | 17 | 25 |
| rule | comp-a-poss | 38 | 68 |
| rule | comp-a | 46 | 148 |
| rule | comp-a-handle | 2 | 2 |
| rule | comp-b | 35 | 79 |
| rule | comp-b-handle | 4 | 5 |
| rule | session-word | 29 | 35 |
| rule | session-word | 3 | 28 |
| rule | session-word | 5 | 13 |
| rule | money-usd | 126 | 540 |
| rule | usage-word | 44 | 60 |
| rule | usage-eq | 4 | 6 |
| rule | email-anthropic | 27 | 115 |
| rule | email-invalid | 26 | 27 |
| rule | email-any | 40 | 61 |
| rule | ssh-neutral | 73 | 306 |
| rule | ssh-neutral-N | 4 | 4 |
| rule | session-word | 4 | 10 |
| rule | sub-code | 18 | 27 |
| rule | boar-env-comment | 9 | 9 |
| rule | maint-path | 1 | 1 |
| rule | maint-grep | 1 | 1 |
| rule | usage-paths | 16 | 35 |
| rule | tester-lower | 11 | 167 |
| rule | mdm-container | 3 | 5 |
| rule | comp-names | 18 | 56 |
| rule | example-key | 5 | 9 |
| rule | comp-url-http | 7 | 12 |
| rule | comp-url-bare | 1 | 1 |
| rule | comp-handle2 | 1 | 1 |
| rule | own-gh | 14 | 94 |
| rule | own-pages | 1 | 3 |
| rule | own-hf | 1 | 2 |
| rule | volume-name | 7 | 88 |
| rule | heavy-wrapper | 70 | 91 |
| rule | scratch-jobs | 6 | 6 |
| rule | private-tmp | 5 | 5 |
| rule | users-dir | 10 | 11 |
| rule | boar-env | 33 | 59 |
| rule | vitalik-poss | 76 | 170 |
| rule | vitalik-name | 79 | 194 |
| rule | fa-link | 3 | 4 |
| rule | fa-slug | 8 | 15 |
| rule | fa-word | 18 | 33 |
| rule | competitor-name-2 | 3 | 33 |
| json | json-drop | 5797 | 72426 |

## Hashes

Frozen criteria, patches and manifests quote sha256 values. When redaction changed a file, every quoted sha256 (and unique 8 to 64 character prefix) of its original bytes was rewritten to the released bytes, repeated until stable. `docs/REDACTION-HASHES.tsv` lists, for every changed file (10,964 files), its path, the **original sha256** (of the private file) and the **released sha256**. So a criterion that says "frozen with sha X" is checked against the released file by following the `.sha256` file next to it, and against the private original by the table's original column. Frozen criteria were not edited in meaning: only names, paths, hosts and usage lines changed.

### v1.1.1 (2026-10-28): remaining NHS quotations withheld

The v1.0 and v1.1 passes left verbatim NHS wording in 52 files (safety rule files `rules.v0.1`..`v0.9.1` and their build scripts and READMEs, the first-aid-cards source tables and review sheets, `fa-cards` and `co-hazard` source notes, `rnd/bench/safety`, the condition-card evidence table, `sc-REVIEW.md`). Each NHS quotation is now a marker that keeps "NHS" and the URL, as for the held-out safety sets in `boar-bench`. In the JSON rule files 130 NHS source entries carry `quotes_withheld` (a count) and `note_licence` instead of the quote list; in the other files the quoted wording is `[NHS quote withheld]`. Quotes from other organisations, our own card wording, the OGL attribution sentence and the licence-terms excerpts are unchanged. Short fragments of two words or fewer (for example "go outside") were left in running prose. Rule matching is unaffected: no rule pattern, test or score changed.

Re-pin: 52 edited files plus 20 `SHA256SUMS*` and `REVIEWER-DECISIONS-6.*` files that quote their hashes (72 files in all). `docs/REDACTION-HASHES.tsv` has one row per file with the v1.1 released sha256 in the original column and the new one in the released column (3 rows already present had only their released value replaced: `rnd/research/compass/LOG.md`, `rnd/research/compass/exp/co-hazard/SHA256SUMS`, `rnd/research/compass/exp/first-aid-cards/SHA256SUMS`; 69 rows added). Quoted sha256 values and 12-character prefixes of the old bytes inside the record were rewritten to the new ones.

### v1.1.2 (2026-10-29): copyright quotations withheld

A licence review found verbatim wording of copyright health pages left by the NHS-only pass. The same rule now covers them (policy row above): the quote is replaced by a marker, the organisation and URL stay, nothing else in the file changes.

- `boar-research`: safety rule files (`compass/exp/safety-*`, `rnd/bench/safety`) and their build scripts and READMEs; the first-aid-cards source tables, review sheets, round scripts and reviewer files (`SOURCES*.md`, `REVIEW*.md`, `REVIEWER-DECISIONS*`, `round*.py`, `reviewer6.py`, `reviewer_sources.py`); `fa-cards`; `coordinator/arms/sc-REVIEW.md`; the hypothermia safety note in `rnd/lantern/safety/` (its guideline points are now paraphrased). The test sentence that quoted healthdirect in `safety-v083`..`v086/tests.v0.8.3.json` is a paraphrase with the same expected result (all safety test suites v0.8.3..v0.8.11 still pass). Scripts whose source check needs the original snapshot (`reviewer6.py`, `reviewer_sources.py`) skip withheld rows; the snapshots were never published.
- `boar-bench`: the vendored safety rules and `bench/v0.1/safety/rules.v0.3.json`, and 30 healthdirect and St John quotations in the held-out sets hm-fresh2, hm-fresh3 and hm-loc1 (`quote_withheld: true`, as for NHS).
- `boar-traces`: retrieved web snippets from healthdirect, NHS and the American Red Cross inside the oracle context files and the deepread/complete request files (`[quote withheld: <org>]`; JSON stays valid; model answers are unchanged).
- Not withheld: official government pages of Brazil and Mexico (Ministério da Saúde, state health departments) and WHO fact sheets are short attributed quotations under their sources' terms; `compass/exp/firstaidqa/firstaidqa_v1.json` is the third-party synthetic FirstAidQA set (Hugging Face `i-am-mushfiq/FirstAidQA`, CC BY 4.0, source row in `rnd/research/SHELF.md`), not a quotation file; a 9-word overlap scan against every withheld quote finds only stock phrases.

Re-pin: every edited file is re-pinned in `docs/REDACTION-HASHES.tsv` and in the `SHA256SUMS*` files that quote it.

## Known residuals (documented, not hidden)

- Third-party text inside traces, replays and fulltext samples is kept as retrieved. It can contain words that look like our policy words (an economist's surname, a newsletter sign-up line, a token-economics topic) or public chain addresses and contact lines of public pages; these are not ours and not private data.
- Experiment identifiers that name the maintainer's data set (for example arm names that start with `MAINT`) remain as identifiers; the data behind them is excluded.
- Competitor numbers written without a percent sign or a leading `0.` (for example a plain [competitor score removed]) may remain in prose; the sentence-level pass catches percentages, ratios and 0-10 or 1-5 scores.
- Hash-pinned files that were changed by redaction are re-pinned, so `sha256sum -c` over the shipped `.sha256` and `SHA256SUMS` files passes except where a listed file was excluded (those entries are missing, not wrong) and 6 entries that were already stale in the private source (`BAR-TABLE.sha256`, `LITE5-criterion.v1.sha256`, `confirm-health11.sha256`, `fa-cards/FROZEN.sha256`, `card-mismatch/SHA256SUMS`, `exp-08-o2v2/FROZEN-v2c.sha256`).

## Placeholders in scripts

- `<workspace>` = the directory that contained `rnd/` on the author's machine; `<runner>` = the runner's work directory on the second machine; `<home>` = a home directory. Substitute your own path to run a script (for example `sed "s#<workspace>#$PWD#g"`).
- `the-mini` is the second machine (a Mac mini that ran long jobs). Scripts that `ssh` to it were neutralised (host replaced), not removed: they are a record of what ran, not runnable as is.
- `<maintainer file>` replaces chat attachment and message ids; `<DEVICE_UDID>` replaces a phone identifier.

`docs/REDACTION-HASHES.tsv`: for 979 released files under 512 bytes the original sha256 is withheld (a short original could be confirmed by guessing).

