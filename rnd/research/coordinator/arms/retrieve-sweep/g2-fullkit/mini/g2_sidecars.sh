#!/usr/bin/env bash
# G2-FULLKIT step 1 (mini): chunk_vecs sidecar copies of boar-visa-en, boar-crypto, boar-wikivoyage-en into shared-data/packs/v3proto/.
# Adapted from kiln/headpass-x2/rebuild_sidecars.sh (same lib, tsx, model, sidecar_embed.mini.mjs). Resumable (complete chunk_vecs skipped, f32 cache resumes).
set -uo pipefail
export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH
ROOT=${BOAR_ROOT:-$HOME/boar}
H=$ROOT/kiln/headpass-x2
G=$ROOT/kiln/g2-fullkit; mkdir -p "$G"; LOG=$G/sidecars.log; SHAF=$G/sidecars.sha256; ST=$G/STATUS
V=$ROOT/shared-data/packs/v3proto
export BOAR_ROOT=$ROOT BOAR_SIDECAR_LIB=$H/lib BOAR_SIDECAR_CACHE=$ROOT/shared-data/packs/work/densechunk
export BOAR_EMBEDDING_GGUF=$ROOT/shared-models/bge-small-en-v1.5-q8_0.gguf BOAR_EMBED_GPU=metal
EMB_SHA=ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514
LIB_E=04ddbd4eac8e36f26e5b0782a9998f5129100423936df10eefd8ea1111521514; LIB_K=b02832f92dbd
TSX=$ROOT/kiln/be-0cfd4a77-cut7/be-repo/node_modules/.bin/tsx
log(){ echo "[g2 $(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
sha(){ shasum -a 256 "$1" | cut -c1-64; }
free(){ df -g "$ROOT" | awk 'NR==2{print $4}'; }
echo "RUNNING started $(date +%H:%M:%S)" > $ST
[ "$(sha ${BOAR_EMBEDDING_GGUF})" = "$EMB_SHA" ] || { log "FATAL embedding sha"; echo "FAILED model sha" > $ST; exit 2; }
[ "$(sha $H/lib/scripts/lib/embedding.mjs)" = "$LIB_E" ] || { log "FATAL lib embedding.mjs sha"; echo "FAILED lib" > $ST; exit 2; }
[ "$(sha $H/lib/scripts/lib/knowledge-pack-lib.mjs | cut -c1-12)" = "$LIB_K" ] || { log "FATAL lib kp-lib sha"; echo "FAILED lib" > $ST; exit 2; }
log "tsx $TSX; model ok; gpu ${BOAR_EMBED_GPU}; free $(free) GiB"
T0=$SECONDS
for row in "boar-visa-en|packs/wave4|10830" "boar-crypto|crypto|54998" "boar-wikivoyage-en|packs|548051"; do
  IFS='|' read -r p dir n <<< "$row"
  src=$ROOT/shared-data/$dir/$p.sqlite; out=$V/$p.sqlite
  need=$(python3 -c "import os,sys; print(int((os.path.getsize(sys.argv[1]) + int(sys.argv[2]) * (388+1536+388)) / 2**30) + 1)" "$src" "$n")
  f=$(free); if [ "$f" -lt $((25 + need)) ]; then log "STOP disk $f < 25+$need for $p"; echo "STOPPED disk before $p" > $ST; exit 4; fi
  t=$SECONDS; echo "RUNNING $p ($n chunks) since $(date +%H:%M:%S)" > $ST; log "start $p ($n chunks; free $f GiB; src sha $(sha $src | cut -c1-12))"
  if "$TSX" "$H/sidecar_embed.mini.mjs" "$src" --out "$out" --name "$p" >> "$LOG" 2>&1; then
    s=$(sha "$out"); echo "$s  $p.sqlite  src=$(sha $src)  secs=$((SECONDS-t))" >> "$SHAF"
    log "done $p in $((SECONDS-t)) s sha ${s:0:12} size $(stat -f %z $out); free $(free) GiB"
  else log "FAIL $p (rerun resumes)"; echo "FAILED $p" > $ST; exit 5; fi
done
log "ALL-DONE total $((SECONDS-T0)) s; free $(free) GiB"; echo "DONE $(date +%H:%M:%S) total $((SECONDS-T0)) s" > $ST
