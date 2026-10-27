#!/usr/bin/env bash
# HEADPASS-X2 step 0 replays (criterion HEADPASS-X2-criterion.md sha 1b70f6f3...; 0 LLM / 0 judge / 0 paid; MacBook).
# Tree kiln-local/be-0cfd4a77-cut7-headpass-x2 (cut 7 + headpass-x2.vs-cut7.patch + the env-gated prompt dump).
# Resumable: each cell writes <out>.tmp and renames it on success; a finished <out> is skipped. One pack at a time.
#
#   nohup rnd/research/coordinator/arms/headpass-st/tools/run_x2.sh [phase ...] > .../headpass-st/logs/run_x2.log 2>&1 &
#
# Phases (default: identity x2 v01):
#   identity  off,x1,off on the 180 with --no-sidecars -> runs-x2/st-<pack>.id.jsonl   (off = cut 7 / x1 = HEADPASS-ST X1)
#   x2        off,x1,x2,off on the 180, kit (originals) + the item's pack SIDECAR copy -> runs-x2/st-<pack>.x2.jsonl
#             (a pack whose sidecar copy is missing or incomplete is SKIPPED, never run on the original)
#   v01       v0.1 public kit-only (off,x1,x2,off; kit never gets sidecars -> must be byte-identical) -> runs-x2/v01-kit.x2.jsonl
#             v0.1 public + boar-simplewiki-en sidecar copy (off,x1,x2,off)                          -> runs-x2/v01-sw.x2.jsonl
#   v02       v0.2 kit-only identity counts (off,x1,x2,off), SCRIPT-ONLY: output under blind/bench-v02/runs-packs/,
#             stderr reduced to the summary line (ids only on DIFF lines are dropped too). Opt-in only; log an
#             EXPOSURES row + QUEUE entry when it runs. NOT part of the default phases.
# Sidecars: shared-data/packs/v3proto/<pack>.sqlite (filled by tools/mini/rebuild_sidecars.sh on the mini, then copied).
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/headpass-st; R=$A/tools/replay-x2.sh; O=$A/runs-x2; mkdir -p $O
TREE=kiln-local/be-0cfd4a77-cut7-headpass-x2
V=${BOAR_X2_SIDECARS:-shared-data/packs/v3proto}
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
C=(--gate search --k 6 --tree $TREE)
disk_ok() { local free; free=$(df -g <home> | awk 'NR==2{print $4}'); [ "$free" -ge 8 ] || { echo "[$1] SKIP disk ${free} GiB < 8"; return 1; }; }
# A sidecar copy is usable when chunk_vecs exists and covers every chunk.
sidecar_ok() { local f=$V/$1.sqlite; [ -s "$f" ] || { echo "[$1] SKIP no sidecar copy $f"; return 1; }
  local n; n=$(sqlite3 -readonly "$f" "SELECT (SELECT count(*) FROM chunk_vecs) = (SELECT count(*) FROM chunks)" 2>/dev/null)
  [ "$n" = 1 ] || { echo "[$1] SKIP sidecar incomplete in $f"; return 1; }; }
cell() { # tag out modes packs questions gold [extra replay args...]
  local tag=$1 out=$2 modes=$3 packs=$4 q=$5 g=$6; shift 6
  [ -s "$out" ] && { echo "[$tag] done (skip)"; return 0; }
  disk_ok "$tag" || return 0
  local t0=$SECONDS
  if $R "${C[@]}" --modes "$modes" --packs "$packs" --questions "$q" --gold "$g" --out "$out.tmp" "$@" 2>&1 \
       | grep -E '^\{|app dir|FATAL|error' | sed "s/^/[$tag] /"; then :; fi
  local want; want=$(( $(grep -c . "$q") * $(echo "$modes" | tr ',' '\n' | grep -c .) ))
  if [ -s "$out.tmp" ] && [ "$(grep -c . "$out.tmp")" -eq "$want" ]; then mv "$out.tmp" "$out"; echo "[$tag] ok $want lines $((SECONDS - t0)) s"
  else echo "[$tag] INCOMPLETE ($(grep -c . "$out.tmp" 2>/dev/null || echo 0)/$want lines); kept $out.tmp"; fi
}
st_q() { echo rnd/research/packs/selftest/$1.jsonl; }
phase_identity() { for p in $PACKS; do
  cell "id $p" $O/st-$p.id.jsonl off,x1,off $KIT,$(pub $p) $(st_q $p) none --no-sidecars; done; }
phase_x2() { for p in $PACKS; do sidecar_ok $p || continue
  cell "x2 $p" $O/st-$p.x2.jsonl off,x1,x2,off $KIT,$(pub $p) $(st_q $p) none --sidecars $V; done; }
phase_v01() {
  cell "v01-kit" $O/v01-kit.x2.jsonl off,x1,x2,off $KIT boar-eval/bench/v0.1/questions.public.jsonl boar-eval/bench/v0.1/gold/sources.json --no-sidecars
  sidecar_ok boar-simplewiki-en && cell "v01-sw" $O/v01-sw.x2.jsonl off,x1,x2,off $KIT,$(pub boar-simplewiki-en) \
    boar-eval/bench/v0.1/questions.public.jsonl boar-eval/bench/v0.1/gold/sources.json --sidecars $V
}
phase_v02() { # script-only: never print item content; the summary line only
  local O2=$B/blind/bench-v02/runs-packs out=$B/blind/bench-v02/runs-packs/headpass-x2-v02-kit.jsonl
  [ -s $out ] && { echo "[v02-kit] done (skip)"; return 0; }
  disk_ok v02-kit || return 0
  mkdir -p $O2
  $R "${C[@]}" --modes off,x1,x2,off --packs $KIT --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl \
     --gold boar-eval/bench/v0.2/gold/sources.json --no-sidecars --out $out.tmp 2>&1 | grep -E '^\{"n"' | sed 's/^/[v02-kit] /'
  [ -s $out.tmp ] && mv $out.tmp $out
  python3 -I $A/tools/gate_x2.py --v02-counts $out 2>&1 | sed 's/^/[v02-kit] /'
}
# HEADPASS-X2b (addendum 1, sha 4b3578e7...): same cells with modes off,x1,x2,x2b,off (x2 re-run in the x2b tree = identity
# check against the X2 files; x2b = packDense2 "append-budget"). Outputs *.x2b.jsonl; v02b script-only as v02.
X2B=off,x1,x2,x2b,off
phase_x2b() { for p in $PACKS; do sidecar_ok $p || continue
  cell "x2b $p" $O/st-$p.x2b.jsonl $X2B $KIT,$(pub $p) $(st_q $p) none --sidecars $V; done; }
phase_v01b() {
  cell "v01b-kit" $O/v01-kit.x2b.jsonl $X2B $KIT boar-eval/bench/v0.1/questions.public.jsonl boar-eval/bench/v0.1/gold/sources.json --no-sidecars
  sidecar_ok boar-simplewiki-en && cell "v01b-sw" $O/v01-sw.x2b.jsonl $X2B $KIT,$(pub boar-simplewiki-en) \
    boar-eval/bench/v0.1/questions.public.jsonl boar-eval/bench/v0.1/gold/sources.json --sidecars $V
}
phase_v02b() { # script-only: never print item content; the summary line only
  local O2=$B/blind/bench-v02/runs-packs out=$B/blind/bench-v02/runs-packs/headpass-x2b-v02-kit.jsonl
  [ -s $out ] && { echo "[v02b-kit] done (skip)"; return 0; }
  disk_ok v02b-kit || return 0
  mkdir -p $O2
  $R "${C[@]}" --modes $X2B --packs $KIT --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl \
     --gold boar-eval/bench/v0.2/gold/sources.json --no-sidecars --out $out.tmp 2>&1 | grep -E '^\{"n"' | sed 's/^/[v02b-kit] /'
  [ -s $out.tmp ] && mv $out.tmp $out
  python3 -I $A/tools/gate_x2b.py --v02-counts $out 2>&1 | sed 's/^/[v02b-kit] /'
}
for ph in ${*:-identity x2 v01}; do echo "== phase $ph $(date +%H:%M:%S)"; phase_$ph; done
echo RUN-X2-DONE $(date +%H:%M:%S)
