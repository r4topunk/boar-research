#!/usr/bin/env bash
# HEADPASS-X2: rebuild the chunk_vecs sidecar copies of the 9 published packs ON THE MINI (criterion HEADPASS-X2-criterion.md
# sha 1b70f6f3...: bge-small q8_0, text `title\nsection: text`, int8; kit packs boar-crypto / boar-wikivoyage-en are NOT
# embedded: the kit stays byte-identical). Same code path as arms/densechunk-st/tools/run_sidecars.sh + sidecar_embed.mjs
# (10-13 ST2 sidecars), paths adapted: <runner>/shared-data/packs/{wave1,wave2}/<pack>.sqlite -> <runner>/shared-data/packs/v3proto/.
# Resumable per pack (a complete chunk_vecs is skipped; the f32 cache resumes mid-pack). One heavy job at a time (run it
# only when nothing else heavy runs on the mini: after TEACHER-PROBE / SFT4B). Never touches Docker. 0 LLM / 0 judge / 0 paid.
#
# Coordinator, from the MacBook:
#   scp -r rnd/research/coordinator/arms/headpass-st/tools/mini MINI_HOST:boar/kiln/headpass-x2
#   <on the mini> 'cd <runner>/kiln/headpass-x2 && nohup bash rebuild_sidecars.sh > logs/rebuild.out 2>&1 &'
#   (watch: <on the mini> 'tail -5 <runner>/kiln/headpass-x2/logs/sidecars.log')
# then, only if the MacBook keeps >= 8 GiB free after the copy (~1.4 GB):
#   rsync -a --progress MINI_HOST:boar/shared-data/packs/v3proto/ shared-data/packs/v3proto/
#   (and check the shas against MINI_HOST:boar/kiln/headpass-x2/logs/sidecars.sha256)
#
# Time estimate (10-13 ST2 run on the MacBook M1 Pro, metal, ~110-150 chunks/s; sidecars.log of arms/densechunk-st):
#   boar-medlineplus-en 3,042 chunks ~0.5 min | boar-factbook 10,543 93 s | qa-health-se 20,656 202 s
#   boar-firstaid-en 22,500 247 s | qa-outdoors-se 31,378 326 s | qa-bitcoin-se 84,399 867 s | qa-ethereum-se 118,560 1,028 s
#   qa-travel-se 155,315 1,061 s | boar-simplewiki-en 621,682 4,187 s  ->  1,068,075 chunks, ~8,000 s = ~2.2 h on the MacBook.
#   Mini M4 (lead embeddings ~225/s in the wave-2 build): ~1.3-2.0 h expected; criterion cap 3 h (the script stops starting
#   new packs past MAX_SECONDS, default 3 h, and says so; rerun later to resume).
# Disk (criterion: mini >= 25 GiB): per pack the sidecar copy ~ pack + 388 B/chunk (clone + table) plus a transient f32
#   cache of 1,536 B/chunk (simplewiki ~0.95 GB) and the kept int8 cache 388 B/chunk. Totals: v3proto ~1.33 GB, int8 caches
#   ~0.41 GB. The floor check runs before every pack: free >= 25 GiB + that pack's need, else STOP.
set -uo pipefail
ROOT=${BOAR_ROOT:-$HOME/boar}
HERE="$(cd "$(dirname "$0")" && pwd)"
LOGD=$HERE/logs; mkdir -p "$LOGD"; LOG=$LOGD/sidecars.log; SHAF=$LOGD/sidecars.sha256
V=$ROOT/shared-data/packs/v3proto; mkdir -p "$V"
export BOAR_ROOT=$ROOT
export BOAR_SIDECAR_LIB=${BOAR_SIDECAR_LIB:-$ROOT/kiln/packs/builder}
export BOAR_SIDECAR_CACHE=${BOAR_SIDECAR_CACHE:-$ROOT/shared-data/packs/work/densechunk}
export BOAR_EMBEDDING_GGUF=${BOAR_EMBEDDING_GGUF:-$ROOT/shared-models/bge-small-en-v1.5-q8_0.gguf}
export BOAR_EMBED_GPU=${BOAR_EMBED_GPU:-metal}
EMB_SHA=ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514
# The 10-13 sidecars used wt/packcond on the MacBook; these are its shas (a mismatch is logged, and stops unless FORCE_LIB=1).
LIB_SHA_EMBEDDING=04ddbd4eac8e36f26e5b0782a9998f5129100423936df10eefd8ea1111521514
LIB_SHA_KPLIB=b02832f92dbdc04b05843cf563de12cbe6722b703de0c650b71792ffe502b654
MIN_GIB=${MIN_GIB:-25}; MAX_SECONDS=${MAX_SECONDS:-10800}
# pack|dir|chunks (chunks from the 10-13 run, for the disk need and the ETA)
PACKS="boar-medlineplus-en|wave1|3042 boar-factbook|wave2|10543 qa-health-se|wave1|20656 boar-firstaid-en|wave1|22500
qa-outdoors-se|wave1|31378 qa-bitcoin-se|wave1|84399 qa-ethereum-se|wave1|118560 qa-travel-se|wave1|155315
boar-simplewiki-en|wave2|621682"
log() { echo "[rebuild $(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
free_gib() { df -g "$ROOT" | awk 'NR==2{print $4}'; }
sha() { shasum -a 256 "$1" | cut -c1-64; }

# ---- preflight
TSX=${TSX:-}
for c in "${BOAR_SIDECAR_LIB}/node_modules/.bin/tsx" "$ROOT/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$ROOT/kiln/node_modules/.bin/tsx"; do
  [ -z "$TSX" ] && [ -x "$c" ] && TSX=$c; done
[ -n "$TSX" ] || { log "FATAL: no tsx found (set TSX=/path/to/tsx; sidecar_embed imports src/rag/wikiPack.ts)"; exit 2; }
for f in scripts/lib/embedding.mjs scripts/lib/knowledge-pack-lib.mjs src/rag/wikiPack.ts; do
  [ -s "${BOAR_SIDECAR_LIB}/$f" ] || { log "FATAL: ${BOAR_SIDECAR_LIB}/$f missing (set BOAR_SIDECAR_LIB)"; exit 2; }; done
grep -q "export function sectionAt" "${BOAR_SIDECAR_LIB}/src/rag/wikiPack.ts" || { log "FATAL: no sectionAt in ${BOAR_SIDECAR_LIB}/src/rag/wikiPack.ts"; exit 2; }
e=$(sha "${BOAR_SIDECAR_LIB}/scripts/lib/embedding.mjs"); k=$(sha "${BOAR_SIDECAR_LIB}/scripts/lib/knowledge-pack-lib.mjs")
log "lib ${BOAR_SIDECAR_LIB} embedding.mjs ${e:0:12} (10-13: ${LIB_SHA_EMBEDDING:0:12}) knowledge-pack-lib.mjs ${k:0:12} (10-13: ${LIB_SHA_KPLIB:0:12})"
if [ "$e" != "$LIB_SHA_EMBEDDING" ] || [ "$k" != "$LIB_SHA_KPLIB" ]; then
  [ "${FORCE_LIB:-0}" = 1 ] && log "WARNING: lib differs from the 10-13 sidecars (FORCE_LIB=1: continuing; diff the embedChunks/quantizeInt8 code before use)" \
    || { log "STOP: lib differs from the 10-13 sidecars; diff embedChunks/quantizeInt8 vs wt/packcond, then rerun with FORCE_LIB=1"; exit 3; }
fi
[ -s "${BOAR_EMBEDDING_GGUF}" ] || { log "FATAL: no embedding model ${BOAR_EMBEDDING_GGUF}"; exit 2; }
[ "$(sha "${BOAR_EMBEDDING_GGUF}")" = "$EMB_SHA" ] || { log "FATAL: embedding sha != ${EMB_SHA:0:12}"; exit 2; }
log "tsx $TSX; model ok ${EMB_SHA:0:12}; gpu ${BOAR_EMBED_GPU}; df before: $(free_gib) GiB free"
df -h "$ROOT" | tee -a "$LOG"

# ---- packs
T0=$SECONDS
for row in $PACKS; do
  IFS='|' read -r p dir n <<< "$row"
  src=$ROOT/shared-data/packs/$dir/$p.sqlite; out=$V/$p.sqlite
  if [ $((SECONDS - T0)) -ge "$MAX_SECONDS" ]; then log "STOP: ${MAX_SECONDS} s cap reached before $p (rerun to resume)"; break; fi
  [ -s "$src" ] || { log "FAIL $p: no $src"; continue; }
  if [ -s "$src.json" ]; then  # published manifest sha (wave builds): the source must be the published pack
    want=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('sha256',''))" "$src.json")
    if [ -n "$want" ] && [ ! -s "$out" ]; then got=$(sha "$src"); [ "$got" = "$want" ] || { log "FAIL $p: source sha ${got:0:12} != manifest ${want:0:12}"; continue; }; fi
  fi
  need_gib=$(python3 -c "import os,sys; print(int((os.path.getsize(sys.argv[1]) + int(sys.argv[2]) * (388 + 1536 + 388)) / 2**30) + 1)" "$src" "$n")
  free=$(free_gib)
  if [ "$free" -lt $((MIN_GIB + need_gib)) ]; then log "STOP: disk ${free} GiB < floor ${MIN_GIB} + ${need_gib} for $p"; exit 4; fi
  t=$SECONDS; log "start $p ($n chunks, ETA ~$((n / 150 / 60 + 1)) min at 150/s; free ${free} GiB)"
  if "$TSX" "$HERE/sidecar_embed.mini.mjs" "$src" --out "$out" --name "$p" >> "$LOG" 2>&1; then
    s=$(sha "$out"); sz=$(stat -f %z "$out" 2>/dev/null || stat -c %s "$out")
    grep -v " $p.sqlite\$" "$SHAF" 2>/dev/null > "$SHAF.tmp"; echo "$s  $p.sqlite" >> "$SHAF.tmp"; mv "$SHAF.tmp" "$SHAF"
    python3 -c "import json,sys; json.dump({'id':sys.argv[1],'file':sys.argv[1]+'.sqlite','sha256':sys.argv[2],'size':int(sys.argv[3]),'_note':'HEADPASS-X2 v3proto copy (published pack + chunk_vecs sidecar, bge-small q8_0 int8); rebuilt on the mini by arms/headpass-st/tools/mini/rebuild_sidecars.sh'}, open(sys.argv[4],'w'))" "$p" "$s" "$sz" "$out.json"
    log "done $p in $((SECONDS - t)) s sha ${s:0:12} size $sz; free $(free_gib) GiB"
  else log "FAIL $p (exit $?; rerun resumes)"; fi
done
log "df after: $(free_gib) GiB free; total $((SECONDS - T0)) s"; df -h "$ROOT" | tee -a "$LOG"
log "ALL-DONE"
