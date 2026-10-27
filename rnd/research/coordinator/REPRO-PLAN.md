# REPRO-PLAN: what it takes to be "public and reproducible" (coordinator, 2026-10-06)

TL;DR
- **Recommendation: Option C (fresh public repo + squashed snapshot of the harness)**, not filter-repo and not a history push. Engine = cut 6 as a branch of the already-public `boar-app` fork (its history is public anyway); harness + claim package = a curated snapshot with a neutral author and no `blind/`, `rnd/veil/` or v0.2 plaintext. ~1 day of local prep, then one owner OK to publish.
- **Biggest blockers:** (1) the committed runner behind the claim numbers (boar-eval `d6e1e55`, `73b9d2c`) and 54 rnd commits (incl. the cut 6 patch and scripts) are **unpushed, local only**; (2) v0.2 held-out plaintext is in boar-eval history (`d8154b6`), so the private repo's history can never be made public as is; (3) the judge references (Opus+web text) are gitignored and the judge is `claude -p` Opus (paid, non-deterministic): reviewers can verify the pipeline and re-judge only with their own refs/judge; (4) the V-para headline (blind) cannot be reproduced by anyone outside; (5) no installable cut 6 Android app exists in a public repo (UI to answerService not wired; BOAR Bench is local git); (6) licences and public-doc of the kit are not written.
- Claim numbers to be reproduced: v0.2 held-out 0.512 (0.478-0.549), full view 0.533, V-para 0.413 (P1 fail). Honest scope: reviewers can re-run v0.1 (public dev set) end to end; v0.2 only the frozen hashes + our traces/judgments aggregate; V-para only aggregate.

## 1. Reproduction bill of materials (per claim number)

| Piece | Reviewer needs | Where it lives now | Public? | State |
|---|---|---|---|---|
| Engine base | boar-app `0cfd4a77` (merge of PR 61) | `boar-app/`, remotes origin (fork r4topunk/boar-app) + upstream the app maintainer | PUBLIC (200 on API); 0cfd4a77 is in upstream/main | pushed |
| Engine cut 6 | patch `824e0b35fcdfe46b25bdb824516b5ccec387247d14a461f7bbfd9fb332fb953b`, tree `b0f53fe0d30a...` | `rnd/research/coordinator/arms/detfu/detmax-on-cut4.vs-0cfd4a77.patch` (sha re-verified today); built tree `<runner>/kiln/be-0cfd4a77-detmax` | rnd private | **LOCAL ONLY** (rnd is 54 commits ahead of origin) ; tree **mini only** (rebuildable from base + patch) |
| Runner / harness | boar-eval `73b9d2c` (adapter.ts sha `7a0282ae...`), RUNNERS.md, `BOAR_RUNNER_PROFILE=ship` | `boar-eval/` | private (404 anonymous) | **2 commits unpushed** (`d6e1e55`, `73b9d2c` = the claim runner) |
| Bench v0.1 (dev, public) | `bench/v0.1` questions, gold, SHA256SUMS | boar-eval tree | private, meant public | pushed |
| Bench v0.1 references | frozen Opus+web ref text (`refs/refs.jsonl`) | boar-eval working dir only, gitignored (only MANIFEST hashes tracked) | no | **LOCAL ONLY** ; publishing text needs a licence/ToS decision |
| Bench v0.2 held-out | questions + refs sha, plan, addenda, scripts | hashes + plan in boar-eval tree; plaintext in `blind/bench-v02/live/v0.2` | hashes only | plaintext **local only (by design)**; also leaked in history (section 2) |
| V-para (blind) | items, refs, runner mapping | `blind/V-para` | never | **local only**; only aggregate reportable |
| Knowledge kit | `boar-crypto.sqlite` `ae9fbd2c...31fb`, `boar-wikivoyage-en.sqlite` `ff8595e3...b66e` (claim kit = crypto + wikivoyage-en, no places) | `shared-data/` (MacBook + mini; identical sha on mini) | **PUBLIC** HF dataset `r4topunk/boar-packs` (private=False; LFS shas match) | pushed. Note: `boar-crypto.sqlite.json` sidecar says `9ac8ad1c...` (stale, differs from file) |
| Pack build code | scripts to rebuild packs | `boar-app/scripts/build-*.mjs`, `fetch-crypto.mjs`, `shared-data/crypto/build/` | scripts public; build outputs local | partial: raw dumps (`shared-data/dumps`) local |
| Models | Qwen3-4B-Instruct-2507-Q4_K_M `3605803b...e597`; bge-small-en-v1.5-q8_0 `ec38e8da...f514` | mini + MacBook `shared-models/`; sources in `rnd/kiln/MODELS.md` (app catalog `src/models/manifest.ts`) | HF upstream, public | ok; add exact HF revisions |
| Emergency detector v3b | `sonar-mmbert-small-emergency-v3b-q8te4.gguf` `a86fe8b9...0f` + head `766434de...6c27` | `shared-models/emergency-detector/` (+ SHA256SUMS), training in `rnd/research/sonar/exp/30-learned-detector` | **no** | **LOCAL ONLY** (gguf + head); base-model licence UNKNOWN; llama-server b11010 build script `rnd/kiln/exp-01-inram-moe-reader/harness/build-b11010.sh` |
| Judge | `judge.v1` prompt/schema (`scorers/vendor/eval-lib`, `harness/judge.mjs`, plan copy sha in `bench/v0.2/plan/SHA256SUMS`), Claude Opus via `claude -p`, both orders, no --effort | boar-eval tree | code private | code ok; **model is closed, paid, not bit-reproducible**; Fable second judge agrees 453/456 |
| Seeds / stats | s42 + s43, judge seed 7, CI seed 11, 2000 resamples, D = 0.306; plan `697b4327...`, floor `fe7c70b7...` | `bench/v0.2/plan/`, `rnd/kiln/l1/cut6-claim-*.sh/.py` | private | scripts local (unpushed) |
| Claim record | CLAIM-RUNS-cut6 (sha `5cd07029...d377`), CLAIM-RESULTS-cut6, CLAIM-DRAFT v3 | `rnd/research/coordinator/` | private | local; trace shas listed in results |
| Device proof | A15 smoke (cut 3, 8 GB) + 12 GB run | `rnd/research/coordinator/device/`, `bench-app/` (local git, bundle in `rnd/archive`) | no | 12 GB run **not done**; cut 6 never on a phone |

> Note (2026-10-07, coordinator): on the Device proof row above, cut 6 ran on the 8 GB Galaxy A15 (QUEUE l.695/l.711, 73/73); the 12 GB run remains not done; cut 7 has not run on a phone.

Exact commands (from RUNNERS.md / CLAIM-RUNS-cut6; need mini + heavy lock today, document a plain-Mac variant):
1. `BOAR_EVAL_RUNNER_DIR=be-repo adapters/desktop-node/setup.sh 0cfd4a77 --patch <patch> --arm detmax`
2. `BOAR_EVAL_RUNNER_DIR=be-repo BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=<v3b head> adapters/desktop-node/run.sh --commit 0cfd4a77 --arm detmax --requests r.jsonl --out t.jsonl`
3. `node harness/judge.mjs --traces t.jsonl --out j.jsonl --bench <bench>` then `scorers/score.py` + `paired_gap.py` (plan).
Gap: `setup.sh`/`run.sh`/`adapter.ts` hard-code `<runner>/...`, `<on the mini>` and the heavy lock (`<runner>/bin/run-heavy`).

## 2. Leak / privacy hazards (paths and counts only)

| Hazard | Evidence | Action |
|---|---|---|
| v0.2 plaintext in boar-eval history | `d8154b6` added `bench/v0.2/questions.v02-new.jsonl` (110 lines, items+gold) plus `refs/MANIFEST.jsonl`, `similarity.json`, `DATASET_CARD.md`, `assemble.py`, `validate.py`; `7d392c0` deleted the file (tree clean, history not). Also gitignored since: `bench/v0.2/refs/refs.jsonl`, `refs/*.new.jsonl`, `runs/e3/` (trace scan printed 1 item, `v02-honesty-refusal-A05`, treated as seen) | never publish this history; v0.2 is burnt (audit D5) |
| v0.2 ids still in current tree | `bench/v0.2/HELD-OUT.md`, `refs/MANIFEST.jsonl`, `similarity.json` (ids/category slugs only; keys checked, text not opened) | keep hashes, drop id-bearing files or accept ids |
| Held-out/blind in rnd (private, tracked) | `veil/` 95 + 146 + more tracked paths (340 distinct in history: `veil/h1-fresh.jsonl`, `h2-fresh.jsonl`, `h2-pool*`, `crisis1.jsonl`, `quarantine`), `kiln/exp-01/blind`, `kiln/exp-02/blind`, `kiln/exp-08-o2v2/*fresh*`, `kiln/exp-09-*/*fresh*`, `kiln/l1/*blind*` | **do not publish rnd or its history**; export only whitelisted paths |
| v0.2 ids in files meant for release | 11 files in `rnd/research/coordinator` + `kiln/l1` match v02 id/vpara patterns (10 with only aggregate/key refs expected) | grep + review before export |
| Personal data, boar-eval tree (326 files) | emails: 0 files; handle `r4to/r4to`: 56 files (arms README, run.sh, setup.sh, gen_refs.mjs, DEVICE-KIT.md ...); `<home>` abs paths: 43 files (devices/DEVICE-KIT.md 20, scorers/tests/fixtures/SOURCES.json 18, scorers/vendor/SOURCE.md 8); `the app maintainer/the app maintainer`: 8; mini hostname/IP-like: 4 | scrub or placeholder |
| Personal data, rnd release subset (`research/coordinator`, `kiln/l1`) | handle: 257 files; `<users-dir>/`: 216; email-like: 2 (`arms/instsubj/l0/D.*.traces.jsonl`); name: 1 | whitelist only; scrub |
| Commit metadata | boar-eval 46 commits, 2 author names, 2 real emails; rnd 137 commits, 1 real email (boar-app history is already public, 24 real vs 365 noreply) | single squashed commit with a neutral author |
| Secrets | key-like strings (sk-, ghp_, hf_, AKIA, PEM): **0** in boar-eval tree and full history, 0 in rnd tree and in history of the release paths; full-history scan of rnd not run (UNKNOWN) | re-run on the export; use gitleaks |
| Reference text / fixtures | `refs/refs.jsonl` (Opus+web outputs), `scorers/tests/fixtures/*` (real runs incl. a competitor team cases) are gitignored on purpose | keep out; hashes only |
| Traces in rnd | 21 `*.traces.jsonl` in `research/coordinator`; may hold answer text | not exported unless reviewed |

## 3. Options for the public repo

| Option | Effort | Lost | Risk |
|---|---|---|---|
| A. `git filter-repo` on boar-eval (drop v0.2 paths, rewrite authors), push as new public repo | 2-3 h + audit | all commit hashes (claim cites `73b9d2c`, `d6e1e55`), the claim-time ordering stays but is unprovable | high: a missed path/blob (reflog, packed refs, `rnd` has 340 veil paths) leaks the burnt set; authors/paths still need scrubbing; rnd cannot be filtered cheaply (57 MB, 137 commits, held-out all over) |
| B. Full history of private repos made public | 0 | nothing | **unacceptable**: v0.2 plaintext, veil, personal data |
| C. Fresh repo + squashed snapshot (recommended): engine as branch/tag `cut6` on the public fork (patch applied as one verified commit, tree hash `b0f53fe0` checked), harness as `repro/` snapshot of boar-eval at `73b9d2c` minus v0.2 ids and gitignored data, + whitelisted rnd scripts/results | ~1 day local, 1 owner OK | commit history and exact pre-registration timestamps (mitigate: publish the SHA256SUMS + plan hashes, keep private repos intact, optionally timestamp the combined hash) | low: nothing old is reachable; must still run leak greps on the snapshot |
| D. Subset export only (patch + results, no harness) | 2 h | harness, reproducibility | fails "all code ... needed to reproduce" in the bounty |

## 4. Ordered task list

| # | Task | Owner/OK | Done-check |
|---|---|---|---|
| L1 | Push nothing; first `git bundle` backup of boar-eval and rnd (unpushed commits exist) | local | `git bundle verify` ok; bundles in `rnd/archive/` |
| L2 | Build export script `repro-export.sh`: whitelist tree from boar-eval@`73b9d2c` + `adapters/desktop-node` + `bench/v0.1` + `scorers` + `harness` + claim scripts (`kiln/l1/cut6-*`) + claim docs + patch; excludes `runs/`, fixtures, refs.jsonl, v0.2 id files | local | `find` of export shows 0 files from the exclude list |
| L3 | Parametrise paths (`<runner>`, `<on the mini>`, heavy lock) via env with defaults; strip `<home>` and handle strings; neutral author | local | greps in section 2 return 0 on the export |
| L4 | Leak gates on the export: gitleaks/regex secrets = 0, emails = 0, `v02-` ids = 0 (or accepted list), no path under `blind|veil|heldout`, `git log` has 1 commit | local | script exit 0, output saved |
| L5 | Verify cut 6 reconstruction on a clean machine: base `0cfd4a77` + patch -> tree hash `b0f53fe0`, patch sha `824e0b35` | local (mini) | hashes printed equal |
| L6 | Write `REPRODUCE.md`: BOM table (section 1) with sha256 + licence per model/pack/detector (Qwen3 Apache-2.0 per catalog, bge MIT, Wikipedia/Wikivoyage CC BY-SA, GeoNames CC BY 4.0, mmBERT base UNKNOWN), download links (HF boar-packs, HF models with revision), commands, expected numbers, "what a reviewer can and cannot reproduce" (v0.1 yes, v0.2 hashes+aggregate, V-para no) | local | a fresh-shell dry run follows it to a v0.1 trace with `validate.ts` ok |
| L7 | Decide reference/judge story: ship `refs` as hashes + `gen_refs.mjs`, document judge cost (~34 fresh calls for cut 6; full v0.1 re-judge ~hundreds) and that Opus is closed | local draft, r4to to read | doc section exists; judge-agreement report linked |
| L8 | Package the detector (v3b gguf + head, ~60 MB) with training script + licence check, or document it as optional | local; upload = OK | sha in SUMS verified |
| L9 | Android: wire ui-android to answerService (audit T4) + 12 GB device run; build a signed/unsigned APK of cut 6 with `audit-apk.py` NO-NETWORK result | local + phone | APK installs; 9 items match BOAR Bench; airplane-mode proof |
| O1 | **Owner OK:** create the public repo name/org, licence (boar-app is MIT "aoair contributors"; upstream is the app maintainer's, PR/permission to use his code publicly is already public MIT), push the snapshot + tag `cut6` | r4to | repo reachable anonymously; clean clone passes L4 greps |
| O2 | **Owner OK:** publish `refs` text or not (Opus+web outputs; ToS/copyright) and v0.2 hash files; HF packs are already public, new HF uploads (detector) need OK | r4to | decision logged in QUEUE |
| O3 | **Owner OK:** whether to rewrite or archive the private boar-eval history (`d8154b6`); never reference it publicly | r4to | decision logged |
| O4 | Fresh-clone reproduction by a second agent (read-only path of REPRODUCE.md), then X/Farcaster demo (needs repo + phone clip) | r4to for posting | second agent reproduces v0.1 ratio within CI |

UNKNOWN: whether boar-eval/rnd have private GitHub remotes that exist (anonymous API 404 = private or absent); exact HF revisions of Qwen3-4B and bge; mmBERT base-model licence; whether any researcher read `d8154b6`; rnd full-history secret scan.
