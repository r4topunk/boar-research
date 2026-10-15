# Held-out and blind set status (public, redacted)

TL;DR: this table replaces the private exposure ledger. It lists every evaluation set that was kept away from the engine builders, how many items it has, what it is today and when it was used. No item text, no item-level topic, no file path and no agent or session name appears here. The private ledger records one row per event (generation run, judge pass, script read, accidental print) and stays private because it names working paths and agent sessions.

Status words:
- **held-out**: no item read by anyone building the engine; numbers on it are claim evidence.
- **dev**: used for development or debugging; numbers on it validate no engine change.
- **burnt**: its plaintext or item details reached a place where builders could see them; treated as dev from that date.
- **spent N**: used N times as a one-shot confirmation set; no longer clean for a further confirmation.
- **clean**: never run.

| set | items | first logged use | last logged use | status today | note |
|---|---:|---|---|---|---|
| v0.2 (bench v0.2, "v0.2-new") | 110 | 2026-10-02 | 2026-10-14 | **burnt → dev** (ruling 2026-10-06) | plaintext entered the private bench repo's history; 12 full generation runs and 10 full Opus judge passes; ids and aggregates appear in this repo, item text does not |
| V-para (paraphrased public-figure-blog set) | 58 (51 judged + 7 venue) | 2026-10-03 | 2026-10-13 | **held-out for the 4B claim runs (cut 3 on 2026-10-05, cut 6 on 2026-10-06); dev-style for everything measured after 2026-10-06** (ruling 2026-10-09) | 19 full generation runs, 12 slices of 20; every deep-tier number on it is development evidence |
| health-fresh1 | 120 | 2026-10-03 | 2026-10-03 | dev (card picking) | near-duplicate with a development health set |
| health-fresh2 | 150 | 2026-10-03 | 2026-10-03 | dev (card picking) | |
| health-fresh3 | 120 | 2026-10-03 | 2026-10-03 | spent 1 | one confirmation run |
| chat-v3 | 64 | 2026-10-03 | 2026-10-03 | spent 3, not clean | |
| es-fresh1 (Spanish) | 32 | — (written 2026-10-03) | never run | unrun, style-contaminated → secondary only | Spanish line parked |
| es-fresh2 (Spanish) | 32 | — (written 2026-10-03) | never run | **clean** | Spanish line parked |
| meta-fresh1 | 36 | 2026-10-03 | 2026-10-03 | spent 1 | |
| bench v0.3 | in preparation | — | — | to be written outside the Claude model family; only hashes will be public before scoring | see the bench repo |

Smaller one-shot gate sets used by single arms (detector, route, fact-table recall sets, gate probes) were each run once and are all **dev, spent or burnt** today; none is used for any number in this repo's headline tables.

Why no item text: v0.2 and V-para are no longer held-out for new work, but their plaintext is still private so that third parties cannot tune on them and so that past held-out numbers keep their meaning. Item ids, categories (the id token) and per-set aggregates are published.

Source: redacted from the private exposure ledger (status table, backfilled 2026-10-09, updated to 2026-10-14).
