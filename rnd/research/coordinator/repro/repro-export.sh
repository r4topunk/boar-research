#!/usr/bin/env bash
# Build the public reproduction tree (REPRO-PLAN Option C, tasks L2-L3) from a whitelist. Plain tree, no git, no commit.
# Nothing is published or pushed by this script.
#   BOAR_ROOT  workspace root (default: derived from this script's location, 4 levels up)
#   OUT        export dir (default: ${BOAR_ROOT}/handoff/repro-staging; must end in repro-staging)
# Sources are only read. All edits (parametrisation, scrubbing) happen on the copies inside $OUT.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${BOAR_ROOT:-$(cd "$HERE/../../../.." && pwd)}"
OUT="${OUT:-$ROOT/handoff/repro-staging}"
[[ "$OUT" == */repro-staging ]] || { echo "OUT must end in /repro-staging" >&2; exit 2; }
EV="$ROOT/boar-eval"; CO="$ROOT/rnd/research/coordinator"; KL="$ROOT/rnd/kiln/l1"
[[ -d "$EV" && -d "$CO" ]] || { echo "bad BOAR_ROOT $ROOT" >&2; exit 2; }
rm -rf "$OUT"; mkdir -p "$OUT"

RS=(rsync -a --exclude node_modules --exclude __pycache__ --exclude .cache --exclude '*.log' --exclude '.DS_Store' --exclude runs --exclude fixtures)
# ---- 1. harness snapshot (boar-eval working tree)
mkdir -p "$OUT/boar-eval"
for f in package.json pnpm-workspace.yaml pnpm-lock.yaml; do cp "$EV/$f" "$OUT/boar-eval/$f"; done
"${RS[@]}" --exclude arms "$EV/adapters/desktop-node/" "$OUT/boar-eval/adapters/desktop-node/"   # dev arm patches are not part of the claim
"${RS[@]}" --exclude plans "$EV/harness/" "$OUT/boar-eval/harness/"
"${RS[@]}" --exclude tests "$EV/scorers/" "$OUT/boar-eval/scorers/"                                    # tests need the fixtures (real runs), which stay private
"${RS[@]}" "$EV/packages/protocol/" "$OUT/boar-eval/packages/protocol/"
# ---- 2. public dev bench v0.1: everything SHA256SUMS.json covers except the withheld held-out manifest; refs = manifests only
mkdir -p "$OUT/boar-eval/bench/v0.1"
# withheld (listed in SHA256SUMS.json, not shipped): heldout.manifest.json (held-out split hashes), similarity.json (held-out overlap numbers),
# build.py + validate.py (read private sources and the held-out files by absolute path), refs/gen_refs.mjs (hard-wired private paths; replaced by gen_refs.public.mjs)
"${RS[@]}" --exclude 'refs' --exclude 'heldout.manifest.json' --exclude similarity.json --exclude build.py --exclude validate.py "$EV/bench/v0.1/" "$OUT/boar-eval/bench/v0.1/"
mkdir -p "$OUT/boar-eval/bench/v0.1/refs"
cp "$EV/bench/v0.1/refs/MANIFEST.json" "$EV/bench/v0.1/refs/MANIFEST.jsonl" "$OUT/boar-eval/bench/v0.1/refs/"
cp "$EV/bench/v0.1/refs/gen_refs.mjs" "$OUT/boar-eval/bench/v0.1/refs/gen_refs.public.mjs"      # edited in step 4 (paths, origin filter, output dir)
RP="${REF_PROMPT:-$ROOT/wt/eval/eval/prompts/reference.v1.md}"                                    # judge-side reference prompt, sha pinned in MANIFEST.json
[[ "$(shasum -a 256 "$RP" | cut -d' ' -f1)" == d51443438dfebcc7d2c3a0136340c70a68f495e1214c00a3a8c56bcdbc755972 ]] || { echo "reference.v1.md sha mismatch" >&2; exit 2; }
cp "$RP" "$OUT/boar-eval/bench/v0.1/refs/reference.v1.md"
# analysis-plan scripts used for the raw / floor-removed / paired numbers (working-tree versions)
mkdir -p "$OUT/boar-eval/bench/v0.2/plan"; cp "$EV/bench/v0.2/plan/floor_metrics.py" "$EV/bench/v0.2/plan/paired_gap.py" "$OUT/boar-eval/bench/v0.2/plan/"
# v0.2: hashes of the frozen plan only (no questions, no refs, no ids)
if [[ -f "$EV/bench/v0.2/plan/SHA256SUMS" ]]; then mkdir -p "$OUT/boar-eval/bench/v0.2/plan"; cp "$EV/bench/v0.2/plan/SHA256SUMS" "$OUT/boar-eval/bench/v0.2/plan/SHA256SUMS"; fi
# ---- 3. patches, tree check, docs
mkdir -p "$OUT/engine" "$OUT/tools"
for f in cut7.vs-0cfd4a77.patch cut7.vs-0cfd4a77.patch.sha256 deep-dt512.vs-0cfd4a77.patch deep-dt512.vs-0cfd4a77.patch.sha256 tree-hash.mjs verify-trees.sh; do cp "$HERE/$f" "$OUT/engine/$f"; done
cp "$CO/arms/facts/facts-r6.vs-cut6.patch" "$CO/arms/facts/facts-r6.vs-cut6.patch.sha256" "$OUT/engine/" 2>/dev/null || cp "$CO/arms/cut7/cut7.vs-cut6.patch" "$CO/arms/cut7/cut7.vs-cut6.patch.sha256" "$OUT/engine/"
cp "$CO/arms/detfu/detmax-on-cut4.vs-0cfd4a77.patch" "$OUT/engine/cut6.vs-0cfd4a77.patch"
(cd "$OUT/engine" && shasum -a 256 cut6.vs-0cfd4a77.patch > cut6.vs-0cfd4a77.patch.sha256)
cp "$HERE/BOM.md" "$HERE/REPRODUCE.md" "$OUT/"   # leak-check.sh, leak-allow.tsv, repro-export.sh, repro-scrub.py stay in the coordinator tree (they contain the patterns)
mkdir -p "$OUT/claim-record" "$OUT/claim-scripts" "$OUT/tools"
cp "$CO/CLAIM-RUNS-cut6.md" "$CO/CLAIM-RESULTS-cut6.md" "$CO/arms/cut7/CUT7.md" "$CO/arms/cut7/CUT7-criterion.md" "$OUT/claim-record/"
cp "$KL"/cut6-claim-* "$OUT/claim-scripts/"
printf "%s\n" "Provenance only, NOT runnable: these are the scripts that produced the cut 6 claim numbers on the withheld sets (v0.2, V-para)." "Paths, hosts and item ids were replaced by placeholders (see ../PROVENANCE.tsv for original and exported hashes). Reviewers: use ../REPRODUCE.md." > "$OUT/claim-scripts/README.txt"
cp "$HERE/plain-mac-deps.sh" "$HERE/fetch-assets.sh" "$HERE/claim-config-cut7.json" "$OUT/tools/"
mv "$OUT/tools/claim-config-cut7.json" "$OUT/boar-eval/adapters/desktop-node/configs/claim-cut7-v01.json"

# ---- 4. parametrise + scrub the copies (python; every rule is asserted or counted)
python3 -I "$HERE/repro-scrub.py" "$OUT"
# ---- 5. integrity: every shipped bench v0.1 file still matches its SUMS entry; patches match their .sha256
python3 -I - "$OUT" <<'PY'
import hashlib, json, sys, os
o = sys.argv[1]; b = os.path.join(o, "boar-eval/bench/v0.1")
sums = json.load(open(os.path.join(b, "SHA256SUMS.json"))); ok = miss = bad = 0
for k, v in sums.items():
    p = os.path.join(b, k)
    if not os.path.exists(p): miss += 1; print("not shipped (hash kept in SHA256SUMS.json):", k); continue
    if hashlib.sha256(open(p, "rb").read()).hexdigest() == v: ok += 1
    else: bad += 1; print("HASH MISMATCH", k)
print(f"bench v0.1: {ok} files match SHA256SUMS.json, {miss} withheld, {bad} mismatching")
sys.exit(1 if bad else 0)
PY
(cd "$OUT/engine" && shasum -a 256 -c cut7.vs-0cfd4a77.patch.sha256 deep-dt512.vs-0cfd4a77.patch.sha256 cut6.vs-0cfd4a77.patch.sha256)
# ---- 6. manifest of the whole tree (excludes BOM.md, REPRODUCE.md, itself) and its sha256 into the BOM
(cd "$OUT" && find . -type f ! -name BOM.md ! -name REPRODUCE.md ! -name MANIFEST.sha256 | sed 's|^\./||' | LC_ALL=C sort | xargs shasum -a 256 > MANIFEST.sha256)
MSHA="$(shasum -a 256 "$OUT/MANIFEST.sha256" | cut -d' ' -f1)"
NF="$(find "$OUT" -type f | wc -l | tr -d ' ')"; NB="$(find "$OUT" -type f -exec stat -f %z {} + | awk '{s+=$1} END{print s}')"
python3 -I - "$OUT/BOM.md" "$MSHA" "$NF" "$NB" <<'PY'
import sys
p, m, n, b = sys.argv[1:]; s = open(p).read()
s = s.replace("@@MANIFEST_SHA@@", m).replace("@@EXPORT_FILES@@", n).replace("@@EXPORT_BYTES@@", f"{int(b):,}")
assert "@@" not in s; open(p, "w").write(s)
PY
echo "export: $(find "$OUT" -type f | wc -l | tr -d ' ') files, $(du -sh "$OUT" | cut -f1) at $OUT"
