# Redaction

TL;DR: the copied files went through one deterministic redaction pass (a rule table applied in a fixed order, no randomness and no clock in the rules), followed by a competitor-score pass, a few hand fixes, and a re-pinning of every sha256 that the record quotes for a changed file. The rules never touch numbers of our own experiments.

## Policy

| what | becomes |
|---|---|
| the app maintainer's real name or handle | "the app maintainer" |
| the volunteer tester | "a volunteer tester" |
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

Frozen criteria, patches and manifests quote sha256 values. When redaction changed a file, every quoted sha256 (and unique 8 to 64 character prefix) of its original bytes was rewritten to the released bytes, repeated until stable. `docs/REDACTION-HASHES.tsv` lists, for every changed file (10,878 files), its path, the **original sha256** (of the private file) and the **released sha256**. So a criterion that says "frozen with sha X" is checked against the released file by following the `.sha256` file next to it, and against the private original by the table's original column. Frozen criteria were not edited in meaning: only names, paths, hosts and usage lines changed.

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

