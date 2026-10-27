#!/usr/bin/env bash
# Kiln overnight 2026-10-04, MacBook side: judge.v1-med = judge.mjs --effort medium (Opus, claude -p --effort medium). Separate judge version:
# NEVER compare -med numbers with judge.v1 numbers in one table.
# (e) calibration first: re-judge bigpack-A-s42 v0.1 part (cut-2-era arm A s42, already judged with v1) with -med -> agreement report.
# (d) then wait for the mini's overnight DONE, pull + validate the 6 new trace files, judge them with -med (v0.1 bench), 3 in parallel.
# Rate limit (judge rc 3): wait 30 min and resume (judge.mjs resumes from its output), max 4 tries per file.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/overnight; CAL=$OUT/calib; mkdir -p $OUT/traces $CAL
LOG=$OUT/JUDGE-LOG.txt; log() { echo "$(date '+%F %T') $*" >> $LOG; }
judge() { # traces out system
  local i rc; for i in 1 2 3 4; do
    (cd $E && node harness/judge.mjs --traces "$1" --out "$2" --bench bench/v0.1 --system "$3" --effort medium >> "${2%.jsonl}.log" 2>&1); rc=$?
    [ $rc = 3 ] || break; log "rate limited $3 (try $i) -> sleep 30 min"; sleep 1800
  done; log "judge $3 rc=$rc rows=$(wc -l < "$2" 2>/dev/null || echo 0)"; return $rc
}
log "=== judge driver start (CLAUDE_CONFIG_DIR=${CLAUDE_CONFIG_DIR:-default})"
SRC=$E/runs/kiln/bigpack-l1/bigpack-A-s42
judge $SRC.v01.traces.jsonl $CAL/bigpack-A-s42.v01.judgments.v1-med.jsonl calib-bigpack-A-s42-med
python3 - $SRC.v01.judgments.jsonl $CAL/bigpack-A-s42.v01.judgments.v1-med.jsonl > $CAL/CALIBRATION.md <<'PY'
import json, sys, collections
K = ("correctness", "completeness", "usefulness"); pt = lambda m: sum(m[k] for k in K) / 3
def load(f):
    R = {}
    for l in open(f):
        r = json.loads(l)
        if r.get("ok"): R[(r["queryId"], r["order"])] = r
    return R
v1, md = load(sys.argv[1]), load(sys.argv[2]); keys = sorted(set(v1) & set(md))
a = [v1[k]["mapped"]["winner"] for k in keys]; b = [md[k]["mapped"]["winner"] for k in keys]; n = len(keys)
po = sum(x == y for x, y in zip(a, b)) / n; ca, cb = collections.Counter(a), collections.Counter(b)
pe = sum(ca[c] * cb[c] for c in set(a) | set(b)) / n / n; kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
def ratio(R):
    it = collections.defaultdict(list)
    for (q, _), r in R.items():
        if (q, "boarA") in R and (q, "boarB") in R: it[q].append((pt(r["mapped"]["boar"]), pt(r["mapped"]["ref"])))
    return sum(x for v in it.values() for x, _ in v) / sum(y for v in it.values() for _, y in v), len(it)
items = {q for q, _ in keys}; r1, n1 = ratio({k: v1[k] for k in keys}); r2, n2 = ratio({k: md[k] for k in keys})
print("# judge.v1-med calibration vs judge.v1 (bigpack-A-s42, v0.1 EN)\n")
print(f"paired verdicts {n} ({len(items)} items) · same winner {po:.1%} · Cohen kappa {kappa:.3f}")
print(f"winners v1 {dict(ca)} · v1-med {dict(cb)}")
print(f"ratio (sum BOAR pts / sum ref pts, items with both orders) v1 {r1:.3f} · v1-med {r2:.3f} · delta {r2 - r1:+.3f} (n {n1}/{n2})")
print(f"median duration ms v1 {sorted(r['durationMs'] or 0 for r in v1.values())[len(v1)//2]} · med {sorted(r['durationMs'] or 0 for r in md.values())[len(md)//2]}")
PY
log "calibration -> $CAL/CALIBRATION.md: $(sed -n 3p $CAL/CALIBRATION.md)"
# (d) wait for the mini (max 10 h)
for i in $(seq 1 120); do <on the mini> 'test -f <runner>/kiln/overnight/DONE' && break; sleep 300; done
scp -q 'MINI_HOST:boar/kiln/overnight/traces/*' $OUT/traces/ ; scp -q MINI_HOST:boar/kiln/overnight/{summary.md,LOG.txt} $OUT/ 2>/dev/null
log "pulled $(ls $OUT/traces/*.traces.jsonl 2>/dev/null | wc -l | tr -d ' ') trace files"
SP=$B/rnd/kiln/l1/.ov-req; mkdir -p $SP; scp -q 'MINI_HOST:boar/kiln/overnight/req/*' $SP/
for f in $OUT/traces/*.traces.jsonl; do l=$(basename $f .traces.jsonl)
  pnpm -s -C $E/adapters/desktop-node exec tsx scripts/validate.ts $f --requests $SP/$l.requests.jsonl >> $LOG 2>&1 || log "VALIDATE FAIL $l"; done
n=0; for f in $OUT/traces/*.traces.jsonl; do l=$(basename $f .traces.jsonl)
  judge $f $OUT/$l.judgments.v1-med.jsonl $l-med & n=$((n + 1)); [ $((n % 3)) = 0 ] && wait
done; wait
python3 - $OUT > $OUT/JUDGED-v1-med.md <<'PY'
import json, sys, glob, os
K = ("correctness", "completeness", "usefulness"); pt = lambda m: sum(m[k] for k in K) / 3
print("# judge.v1-med results (do NOT compare with judge.v1 tables)\n\n| run | items | ratio | win | tie | loss |\n|---|---|---|---|---|---|")
for f in sorted(glob.glob(os.path.join(sys.argv[1], "*.judgments.v1-med.jsonl"))):
    R = [json.loads(l) for l in open(f) if json.loads(l).get("ok")]; n = len(R) or 1
    b = sum(pt(r["mapped"]["boar"]) for r in R); rf = sum(pt(r["mapped"]["ref"]) for r in R) or 1
    w = lambda x: sum(r["mapped"]["winner"] == x for r in R) / n
    print(f"| {os.path.basename(f).split('.')[0]} | {len({r['queryId'] for r in R})} | {b / rf:.3f} | {w('boar'):.2f} | {w('tie'):.2f} | {w('ref'):.2f} |")
PY
log "=== judge driver DONE -> $OUT/JUDGED-v1-med.md"
