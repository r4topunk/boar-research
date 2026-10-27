# What was excluded, and why

TL;DR: the source is the private lab's working tree (51,614 files, 1.36 GB). 31,810 files (1136 MB) are in this record; the rest is excluded for the reasons below. Held-out and burnt evaluation sets are never published as text, so the record keeps their **ids, categories, aggregates and the exposure ledger** (`rnd/research/coordinator/EXPOSURES.md`), and the bench repository keeps the **sha256 hashes** of the frozen files. Nothing excluded was opened by the release scripts beyond its path, for anything under a `blind/` or `veil/` segment.

## 1. Exclusion classes from the inventory (by path and content class)

| class | files | MB | what it is |
|---|---:|---:|---|
| generated cache | 8,947 | 22.5 | caches, locks, pycache, run logs (.log/.err/.out), symlinks |
| usage ledger | 6,679 | 1.9 | spend files and paid-gateway caches (usage, not method) |
| third-party licence unclear | 1,805 | 63.0 | competitor-derived cases, third-party model directories, training data derived from CLAPnq, HAGRID and Wikipedia plus provider outputs, scraped third-party pages |
| maintainer data | 373 | 5.4 | the app maintainer's questions, traces, judgments and correspondence |
| veil (quarantine) | 340 | 10.8 | old held-out sets and quarantine, classified by path only |
| blind / held-out | 215 | 55.1 | path or name says blind or held-out, or a data file whose content carries held-out ids together with item or answer text |
| binary, opaque | 131 | 8.5 | images, git bundles, archives that cannot be scrubbed |
| duplicate of bench | 122 | 3.6 | early bench v0 material superseded by `boar-bench` |
| relay | 56 | 0.7 | session handoffs, goal and night memos, chat drafts, notes written for a person |
| infra ops | 22 | 0.1 | queue, watchdog, hook and auth automation of the author's machines |
| secret risk | 1 | 5.7 | content with credential-like patterns |
| model files | 2 | 0.0 | listed in `BOM.md` instead (`bom-only`) |

## 2. Exclusions applied at redaction time (after copying)

| reason | files |
|---|---:|
| longsession run traces: blind longsession runs are mixed in; exclude unless a run is shown to be dev-only | 140 |
| held-out set names in paths | 83 |
| held-out sets and quarantine (any segment containing blind/veil, incl. file names like hand-labels-o2ab-blind.json) | 36 |
| competitor-landscape web sweeps: competitor scores and claims | 16 |
| competitor-landscape notes: competitor scores | 5 |
| question sets built from a competitor repo's cases (licence unclear); the public v0.1 items live in boar-bench | 4 |
| previous release scrub tooling (carries private match patterns); superseded by docs/ | 3 |
| scrub tooling (private match patterns) | 3 |
| competitor-landscape notes | 2 |
| held-out v0.2/v0.4 item text and references (v0.4 only if the author has not published it) | 2 |

The competitor-landscape web sweeps and notes were removed whole: they mix literature with other teams' scores. Raw third-party HTML snapshots were removed because they embed site tokens and are third-party copyright (the extracted facts and the URLs stay).

## 3. Withheld evaluation sets (what the record keeps instead)

| set | status | what stays public |
|---|---|---|
| bench v0.2 (110 items) | burnt: its plaintext reached a builder-visible place; treated as development data | ids, aggregates, plan hashes (bench repo) |
| V-para (58 = 51 judged + 7 venue) | held-out for the two 4B claim runs; development-style after 2026-10-06 | ids, aggregates, exposure rows |
| health-fresh1-3, hm-fresh1-3, chat-v3, es-fresh1-2, meta-fresh1, longsession blind runs | held-out sets | ids, aggregates, exposure rows |
| bench v0.3 / v0.4 items and references | final held-out sets, written outside the Claude family; not published unless the author published them | hashes and the plan |
| traces and judgments of runs on any of the above | withheld: they embed item text | the aggregates computed from them |

Status of every set and every exposure: `rnd/research/coordinator/EXPOSURES.md`. Public dev material (bench v0.1 questions, frozen references, the 180 pack self-tests) is in this record or in `boar-bench`.

## Second leak pass (2026-10-27)

An adversarial leak hunt and an outsider usability review ran on the first build. Everything below was removed **whole** (exclusion over edits). Counts by reason, then every path.

| reason | paths |
|---|---:|
| held-out id with content (heldout-exclude.txt) | 268 |
| competitor test-case questions (>= 3 of the 27, denylist match) | 23 |
| bench v0 runs/calibration on the competitor-derived split (P0-5) | 5 |
| aggregates of the app maintainer's traces + attachment ids (P1-3, P2) | 2 |
| competitor 72-question set (P0-5) | 2 |
| the app maintainer's test questions (P0-3) | 1 |
| timing aggregates of the app maintainer's traces (P2) | 1 |
| built on the app maintainer's prompts and traces; relayed to him (P1-3, heldout-exclude) | 1 |
| provenance: maintainer-facing handoff rows in held-out-like id spaces (USABILITY P1-7) | 1 |
| spend, quota and competitor-score residue in mined session logs (P0-4, P1-2) | 1 |
| maintainer-run scores in raw reviewer output (P0-2) | 1 |
| maintainer-run scores inside edit strings (P0-2) | 1 |
| raw shell-history fixture (private paths, competitor numbers) | 1 |
| code/data file with private correspondence or maintainer-run numbers | 1 |

Line-level edits in the same pass: queue and timeline entries of the private correspondence lanes (`[dm]`, `[liaison]`, rows quoting the app maintainer's messages, channel or thread names, chat ids) and every line that reported a score of a run on the app maintainer's devices were replaced by one line, "[private correspondence with the app maintainer, or a result of a run on his device, removed]"; competitor scores in sentences about the competitor became "[competitor score removed]"; chat attachment ids became `<maintainer file>`; spend and quota residue became "[usage detail removed]"; a device UDID, private page links and an ENS name were removed.

Kept on purpose: 1-2 generic questions of a competitor team's public test set (for example "tell me about japan") inside engine patches and traces where they appear as ordinary test inputs; the competitor's own published speed and size figures (decode tok/s, places DB size), which are engineering reference points, not scores of their answers; held-out set *names* and relative `blind/...` paths (layout only, no content); retrieval titles keyed by held-out ids in a few aggregates (topic-level only, v0.2 is burnt and V-para is dev-style).

<details><summary>All removed paths</summary>

**aggregates of the app maintainer's traces + attachment ids (P1-3, P2)**

- `research/rnd/research/coordinator/arms/cap512`
- `research/rnd/research/coordinator/arms/succinct17`

**bench v0 runs/calibration on the competitor-derived split (P0-5)**

- `research/rnd/bench/calibration`
- `research/rnd/bench/jev`
- `research/rnd/bench/judge/v0`
- `research/rnd/bench/main-6b53ee83`
- `research/rnd/bench/night-2026-10-01`

**built on the app maintainer's prompts and traces; relayed to him (P1-3, heldout-exclude)**

- `research/rnd/research/coordinator/arms/honestprompt`

**code/data file with private correspondence or maintainer-run numbers**

- `research/rnd/research/coordinator/ruler/hypotheses-round5-2026-10-21.json`

**competitor 72-question set (P0-5)**

- `research/rnd/research/coordinator/arms/pack-visa/replay/rival-base.jsonl`
- `research/rnd/research/coordinator/arms/pack-visa/replay/rival-boar-visa-en.jsonl`

**competitor test-case questions (>= 3 of the 27, denylist match)**

- `research/rnd/archive/wt-dirty/cmpsplit-v21.patch`
- `research/rnd/bench/calibration/agents-v0/jev_items.jsonl`
- `research/rnd/bench/calibration/agents-v0/neutral/jev_items.jsonl`
- `research/rnd/bench/calibration/agents-v0/neutral/rater_input.md`
- `research/rnd/bench/calibration/agents-v0/rater_input.md`
- `research/rnd/bench/calibration/human-v0/SHEET.md`
- `research/rnd/kiln/exp-07-expansion-on-miss/diag-expansion.txt`
- `research/rnd/lantern/o2-weak-support-spec.md`
- `research/rnd/lantern/tools/build_evalset.py`
- `research/rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-bench-v0-kitB.request.json`
- `research/rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-bench-v0.request.json`
- `research/rnd/plumb/vitalik-eval-14de107.md`
- `research/rnd/research/compass/exp/health-embed/results.txt`
- `research/rnd/research/compass/exp/pt-recall/emb-extra.json`
- `research/rnd/research/compass/exp/pt-recall/emb.json`
- `research/rnd/research/coordinator/arms/synthdeep/synthdeep.vs-dt512.patch`
- `research/rnd/research/sonar/exp/01-comparison-entity-gate/run.mjs`
- `research/rnd/research/sonar/exp/01-comparison-entity-gate/trace.mts`
- `research/rnd/research/sonar/exp/01-comparison-entity-gate/trace.txt`
- `research/rnd/research/sonar/exp/02-wikivoyage-noise-gate/result.txt`
- `research/rnd/research/sonar/exp/29-instant-offtopic/instid.json`
- `research/rnd/research/sonar/exp/30-learned-detector/anvilpool/turns.json`
- `research/rnd/research/sonar/exp/30-learned-detector/probes/long-adversarial.json`

**held-out id with content (heldout-exclude.txt)**

- `research/rnd/bench/calibration/sheet.json`
- `research/rnd/bench/jev/items.jsonl`
- `research/rnd/bench/judge/v0/boar-p3-iphone13-qwen1.5b__vs__refs-v0.jsonl`
- `research/rnd/bench/judge/v0/proxy-macmini-ling-3.0-tiny__vs__refs-v0.jsonl`
- `research/rnd/bench/judge/v0/proxy-macmini-maple-preview__vs__refs-v0.jsonl`
- `research/rnd/bench/judge/v0/proxy-macmini-qwen3-4b__vs__refs-v0.jsonl`
- `research/rnd/bench/main-6b53ee83/answers/boar-main-6b53ee83-desktop-1.5b.answers.jsonl`
- `research/rnd/bench/main-6b53ee83/answers/probe-main-6b53ee83-desktop-4b.answers.jsonl`
- `research/rnd/bench/main-6b53ee83/jev/boar-main-6b53ee83-desktop-1.5b.items.jsonl`
- `research/rnd/bench/main-6b53ee83/jev/probe-main-6b53ee83-desktop-4b.items.jsonl`
- `research/rnd/bench/main-6b53ee83/judge/boar-main-6b53ee83-desktop-1.5b__vs__refs-v0.jsonl`
- `research/rnd/bench/main-6b53ee83/judge/probe-main-6b53ee83-desktop-4b__vs__refs-v0.jsonl`
- `research/rnd/bench/night-2026-10-01/answers/boar-main-611a4b9-o2off-kitA.answers.jsonl`
- `research/rnd/bench/night-2026-10-01/answers/main-o2off-kitB.answers.jsonl`
- `research/rnd/bench/night-2026-10-01/answers/o2ab-o2off.answers.jsonl`
- `research/rnd/bench/night-2026-10-01/answers/o2ab-o2on.answers.jsonl`
- `research/rnd/bench/night-2026-10-01/answers/q1-v5off-o2off.answers.jsonl`
- `research/rnd/bench/night-2026-10-01/answers/q1-v5off-o2on.answers.jsonl`
- `research/rnd/bench/night-2026-10-01/answers/q4-retest-bench60.answers.jsonl`
- `research/rnd/bench/night-2026-10-01/d10-package/boar-main-fd24992-iphone13-qwen1.5b-run2.answers.jsonl`
- `research/rnd/bench/night-2026-10-01/d10-package/boar-main-fd24992-iphone13-qwen1.5b-run2__vs__refs-v0.jsonl`
- `research/rnd/bench/night-2026-10-01/d10-package/boar-main-fd24992-iphone13-qwen1.5b.answers.jsonl`
- `research/rnd/bench/night-2026-10-01/d10-package/boar-main-fd24992-iphone13-qwen1.5b__vs__refs-v0.jsonl`
- `research/rnd/bench/night-2026-10-01/jev/boar-main-611a4b9-o2off-kitA.items.jsonl`
- `research/rnd/bench/night-2026-10-01/jev/main-o2off-kitB.items.jsonl`
- `research/rnd/bench/night-2026-10-01/jev/o2ab-o2off.items.jsonl`
- `research/rnd/bench/night-2026-10-01/jev/o2ab-o2on.items.jsonl`
- `research/rnd/bench/night-2026-10-01/jev/q1-v5off-o2off.items.jsonl`
- `research/rnd/bench/night-2026-10-01/jev/q1-v5off-o2on.items.jsonl`
- `research/rnd/bench/night-2026-10-01/jev/q4-retest-bench60.items.jsonl`
- `research/rnd/bench/night-2026-10-01/judge/boar-main-611a4b9-o2off-kitA__vs__refs-v0.jsonl`
- `research/rnd/bench/night-2026-10-01/judge/main-o2off-kitB__vs__refs-v0.jsonl`
- `research/rnd/bench/night-2026-10-01/judge/o2ab-o2off__vs__refs-v0.jsonl`
- `research/rnd/bench/night-2026-10-01/judge/o2ab-o2on__vs__refs-v0.jsonl`
- `research/rnd/bench/night-2026-10-01/judge/q1-v5off-o2off__vs__refs-v0.jsonl`
- `research/rnd/bench/night-2026-10-01/judge/q1-v5off-o2on__vs__refs-v0.jsonl`
- `research/rnd/bench/night-2026-10-01/judge/q4-retest-bench60__vs__refs-v0.jsonl`
- `research/rnd/bench/safety/build_safety_v02.py`
- `research/rnd/bench/score/test_score.py`
- `research/rnd/bench/systems/boar-p3-iphone13-qwen1.5b.answers.jsonl`
- `research/rnd/bench/systems/proxy-macmini-ling-3.0-tiny.answers.jsonl`
- `research/rnd/bench/systems/proxy-macmini-maple-preview.answers.jsonl`
- `research/rnd/bench/systems/proxy-macmini-qwen3-4b.answers.jsonl`
- `research/rnd/kiln/bench-v0/proxy-answers.22.jsonl`
- `research/rnd/kiln/exp-01-inram-moe-reader/capture/lantern52.jsonl`
- `research/rnd/kiln/exp-01-inram-moe-reader/results/.pre.jsonl`
- `research/rnd/kiln/exp-01-inram-moe-reader/runs/ling-3.0-tiny.jsonl`
- `research/rnd/kiln/exp-01-inram-moe-reader/runs/qwen2.5-1.5b.jsonl`
- `research/rnd/kiln/exp-01-inram-moe-reader/runs/qwen3-4b.jsonl`
- `research/rnd/kiln/exp-02-maple/runs/maple-preview.jsonl`
- `research/rnd/kiln/exp-02-maple/runs/qwen3-4b-b11010.jsonl`
- `research/rnd/kiln/exp-03-o2/inputs.jsonl`
- `research/rnd/kiln/exp-04-jev/regression.jsonl`
- `research/rnd/kiln/exp-04-jev/rows-test.jsonl`
- `research/rnd/kiln/exp-04-jev/rows-tune.jsonl`
- `research/rnd/kiln/exp-06-desktop-answerer/runs/p2-iphone13-1.5b.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/android-4b-off.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/android-4b-on.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/android-4b-v5-off.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/android-4b-v5-on.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/invalid-adapter-v1/android-4b-on.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/invalid-adapter-v1/android-4b-v5-on.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/invalid-adapter-v1/ios-1.5b-on.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/invalid-adapter-v1/ios-1.5b-v5-on.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/ios-1.5b-off.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/ios-1.5b-on.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/ios-1.5b-v5-off.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/ios-1.5b-v5-on.jsonl`
- `research/rnd/kiln/exp-07-expansion-on-miss/runs/smoke-t2.jsonl`
- `research/rnd/kiln/exp-08-o2v2/analyze.py`
- `research/rnd/kiln/exp-08b-ios-main-regression/runs/x8b-14de107.jsonl`
- `research/rnd/kiln/exp-08b-ios-main-regression/runs/x8b-577912b6.jsonl`
- `research/rnd/kiln/exp-08b-ios-main-regression/runs/x8b-61558601.jsonl`
- `research/rnd/kiln/exp-08b-ios-main-regression/runs/x8b-a0b25465.jsonl`
- `research/rnd/kiln/exp-08c-health-no-source/runs/v58-01daf792.jsonl`
- `research/rnd/kiln/exp-08c-health-no-source/runs/v58-62be09d7.jsonl`
- `research/rnd/kiln/exp-08c-health-no-source/runs/v58-e7ea6e78.jsonl`
- `research/rnd/kiln/exp-10-main-baseline/questions.exp10.jsonl`
- `research/rnd/kiln/exp-10-main-baseline/runs/main-12gb-real.jsonl`
- `research/rnd/kiln/exp-10-main-baseline/runs/main-android-4b-rep.jsonl`
- `research/rnd/kiln/exp-10-main-baseline/runs/main-android-4b.jsonl`
- `research/rnd/kiln/exp-10-main-baseline/runs/main-ios-1.5b-rep.jsonl`
- `research/rnd/kiln/exp-10-main-baseline/runs/main-ios-1.5b.jsonl`
- `research/rnd/lantern/o2/o2-testset.jsonl`
- `research/rnd/plumb/data/analysis-14de107-vital5.json`
- `research/rnd/plumb/data/analysis-14de107.json`
- `research/rnd/plumb/data/claude-code__opus.jsonl`
- `research/rnd/plumb/data/q4-611a4b9-qwen1.5b-quick-kitA-o2off-bench60-retest.jsonl`
- `research/rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device-vital5.jsonl`
- `research/rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device-vital5__vs__claude-code__opus.jsonl`
- `research/rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device.jsonl`
- `research/rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device__vs__claude-code__opus.jsonl`
- `research/rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107.jsonl`
- `research/rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-bench-v0-kitB.jsonl`
- `research/rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-bench-v0.jsonl`
- `research/rnd/research/anvil/exp/best-of-n/runs/q4b-n4.medoid.pin.jsonl`
- `research/rnd/research/anvil/exp/best-of-n/runs/q4b-n4.oracle.pin.jsonl`
- `research/rnd/research/anvil/exp/best-of-n/runs/q4b-n4.s1.pin.jsonl`
- `research/rnd/research/anvil/exp/best-of-n/runs/q4b-n4.sample1.pin.jsonl`
- `research/rnd/research/anvil/exp/best-of-n/runs/q4b-n4.sample2.pin.jsonl`
- `research/rnd/research/anvil/exp/best-of-n/runs/q4b-n4.sample3.pin.jsonl`
- `research/rnd/research/anvil/exp/best-of-n/runs/q4b-n4.sample4.pin.jsonl`
- `research/rnd/research/anvil/exp/best-of-n/runs/q4b-n4.support.pin.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A0-gated.precheck-in.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A0-raw.precheck-in.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A0-t0.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A0-t07-s1-gated.pin.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A0-t07-s1-raw.pin.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A0-t07-s1.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A0-t07-s2-gated.pin.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A0-t07-s2-raw.pin.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A0-t07-s2.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A1-gated.precheck-in.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A1-raw.precheck-in.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A1-t0.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A2-gated.precheck-in.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A2-raw.precheck-in.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A2-t0.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A2-t07-s1-gated.pin.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A2-t07-s1-raw.pin.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A2-t07-s1.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A2-t07-s2-gated.pin.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A2-t07-s2-raw.pin.jsonl`
- `research/rnd/research/anvil/exp/cite-exemplar/runs/A2-t07-s2.jsonl`
- `research/rnd/research/anvil/exp/compact-minicpm5/runs/mc1b-t0-gated.pin.jsonl`
- `research/rnd/research/anvil/exp/compact-minicpm5/runs/mc1b-t0-raw.pin.jsonl`
- `research/rnd/research/anvil/exp/compact-minicpm5/runs/mc1b-t0.jsonl`
- `research/rnd/research/anvil/exp/compact-minicpm5/runs/mc1b-t07-s1-gated.pin.jsonl`
- `research/rnd/research/anvil/exp/compact-minicpm5/runs/mc1b-t07-s1-raw.pin.jsonl`
- `research/rnd/research/anvil/exp/compact-minicpm5/runs/mc1b-t07-s1.jsonl`
- `research/rnd/research/anvil/exp/compact-minicpm5/runs/mc1b-t07-s2-gated.pin.jsonl`
- `research/rnd/research/anvil/exp/compact-minicpm5/runs/mc1b-t07-s2-raw.pin.jsonl`
- `research/rnd/research/anvil/exp/compact-minicpm5/runs/mc1b-t07-s2.jsonl`
- `research/rnd/research/anvil/exp/notes-first/runs/N0-t0.jsonl`
- `research/rnd/research/anvil/exp/notes-first/runs/N0-t0.pin.jsonl`
- `research/rnd/research/anvil/exp/notes-first/runs/N1-t0.jsonl`
- `research/rnd/research/anvil/exp/notes-first/runs/N1-t0.pin.jsonl`
- `research/rnd/research/anvil/exp/persona-length/runs/P0-t0.jsonl`
- `research/rnd/research/anvil/exp/persona-length/runs/P1-t0.jsonl`
- `research/rnd/research/anvil/exp/persona-length/runs/P2-t0.jsonl`
- `research/rnd/research/compass/exp/first-aid-cards/build_cards.py`
- `research/rnd/research/compass/exp/verify/drafts.json`
- `research/rnd/research/compass/exp/verify/verified.json`
- `research/rnd/research/coordinator/arms/cryptosel/cryptosel-on-cut3.vs-0cfd4a77.patch`
- `research/rnd/research/coordinator/arms/cut7/gates/facts-check-cut7.jsonl`
- `research/rnd/research/coordinator/arms/cvs/gate3-key/key.scorer.jsonl`
- `research/rnd/research/coordinator/arms/detector-hn/ft/train.jsonl`
- `research/rnd/research/coordinator/arms/detector-hn/ft/val.jsonl`
- `research/rnd/research/coordinator/arms/detector-hn/ft2/D150/train.jsonl`
- `research/rnd/research/coordinator/arms/detector-hn/ft2/D150/val.jsonl`
- `research/rnd/research/coordinator/arms/detector-hn/ft2/D300/train.jsonl`
- `research/rnd/research/coordinator/arms/detector-hn/ft2/D300/val.jsonl`
- `research/rnd/research/coordinator/arms/detector-hn/ft2/D600/train.jsonl`
- `research/rnd/research/coordinator/arms/detector-hn/ft2/D600/val.jsonl`
- `research/rnd/research/coordinator/arms/detfu/out/detmax-result.json`
- `research/rnd/research/coordinator/arms/engfix-1023/plugfix/replay.after.json`
- `research/rnd/research/coordinator/arms/engfix-1023/plugfix/replay.before.json`
- `research/rnd/research/coordinator/arms/facts/facts-check-r11.jsonl`
- `research/rnd/research/coordinator/arms/facts/facts-check-r2.jsonl`
- `research/rnd/research/coordinator/arms/facts/facts-check-r3.jsonl`
- `research/rnd/research/coordinator/arms/facts/facts-check-r5.jsonl`
- `research/rnd/research/coordinator/arms/facts/facts-check-r6.jsonl`
- `research/rnd/research/coordinator/arms/facts/facts-check.jsonl`
- `research/rnd/research/coordinator/arms/followq/tools/mkreq.py`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-A.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-A.judgments.jsonl.preflight/arm.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-A.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-A.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-A.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-A.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-B.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-B.judgments.jsonl.preflight/arm.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-B.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-B.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-B.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D0-B.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D1-A.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D1-A.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D1-A.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D1-A.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D1-A.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D1-B.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D1-B.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D1-B.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D1-B.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D1-B.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-A.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-A.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-A.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-A.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-A.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-B.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-B.judgments.jsonl.preflight/arm.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-B.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-B.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-B.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D2-B.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D3-A.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D3-A.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D3-A.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D3-A.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D3-A.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D4-A.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D4-A.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D4-A.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D4-A.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D4-A.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D4-B.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D4-B.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D4-B.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D4-B.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-D4-B.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-A.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-A.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-A.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-A.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-A.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-B.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-B.judgments.jsonl.preflight/arm.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-B.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-B.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-B.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S0-B.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-A.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-A.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-A.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-A.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-A.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-B.judgments.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-B.judgments.jsonl.preflight/arm.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-B.judgments.shards/shard-0.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-B.judgments.shards/shard-1.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-B.judgments.shards/shard-2.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/judgments/honest-chat-S1-B.judgments.shards/shard-3.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-D0-A.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-D0-B.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-D1-A.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-D1-B.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-D2-A.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-D2-B.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-D3-A.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-D4-A.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-D4-B.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-S0-A.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-S0-B.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-S1-A.jsonl`
- `research/rnd/research/coordinator/arms/honestprompt/traces/traces-chat-S1-B.jsonl`
- `research/rnd/research/coordinator/arms/lite3/tools/lite3.py`
- `research/rnd/research/coordinator/arms/lossmap/tools/lossmap.py`
- `research/rnd/research/coordinator/arms/packcond/tools/packcond_p1.py`
- `research/rnd/research/coordinator/arms/packs/aggregates/crowding-wave3.json`
- `research/rnd/research/coordinator/arms/packs/aggregates/crowding.json`
- `research/rnd/research/coordinator/arms/plugbatch-self/aggregates/rows.A.json`
- `research/rnd/research/coordinator/arms/plugbatch-self/aggregates/rows.B.json`
- `research/rnd/research/coordinator/arms/plugbatch-self/aggregates/rows.C.json`
- `research/rnd/research/coordinator/arms/plugbatch-self/aggregates/rows.P.json`
- `research/rnd/research/coordinator/arms/plugbatch-self/in/pb-A-smoke.requests.jsonl`
- `research/rnd/research/coordinator/arms/plugbatch-self/in/pb-A-w1.requests.jsonl`
- `research/rnd/research/coordinator/arms/plugbatch-self/in/pb-B-smoke.requests.jsonl`
- `research/rnd/research/coordinator/arms/plugbatch-self/in/pb-B-w1.requests.jsonl`
- `research/rnd/research/coordinator/arms/plugbatch-self/in/pb-C-smoke.requests.jsonl`
- `research/rnd/research/coordinator/arms/plugbatch-self/in/pb-C-w1.requests.jsonl`
- `research/rnd/research/coordinator/arms/plugbatch-self/in/pb-P-smoke.requests.jsonl`
- `research/rnd/research/coordinator/arms/plugbatch-self/in/pb-P-w1.requests.jsonl`
- `research/rnd/research/coordinator/arms/validation-1024/s3/replay.json`
- `research/rnd/research/coordinator/arms/vitalpack/aggregates/gate-v02-gold.json`
- `research/rnd/research/coordinator/arms/wikisection/tools/section_gate.py`
- `research/rnd/research/coordinator/bench-v03/writer-prompts.md`

**maintainer-run scores in raw reviewer output (P0-2)**

- `research/rnd/research/coordinator/review-direction-2026-10-21/raw-results.json`

**maintainer-run scores inside edit strings (P0-2)**

- `research/rnd/research/coordinator/CLAIM-REVIEW-v4.2-edits.py`

**provenance: maintainer-facing handoff rows in held-out-like id spaces (USABILITY P1-7)**

- `research/rnd/research/coordinator/arms/plugbatch-self`

**raw shell-history fixture (private paths, competitor numbers)**

- `research/rnd/research/coordinator/arms/_lib/tests/fixtures/deny/last200-bash-2026-10-14.jsonl`

**spend, quota and competitor-score residue in mined session logs (P0-4, P1-2)**

- `research/rnd/research/coordinator/retro-2026-10-14`

**the app maintainer's test questions (P0-3)**

- `research/rnd/research/coordinator/arms/ux-tests-1023`

**timing aggregates of the app maintainer's traces (P2)**

- `research/rnd/research/coordinator/arms/native-partime`

</details>
