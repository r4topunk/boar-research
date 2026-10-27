#!/bin/bash
# WIKIFULL stage A loop: for each shard (00..14 minus 07): disk check -> download (curl, HF public resolve URL,
# no HF cache) -> sha256 verify (retry once) -> gate vpara + v02 -> delete shard. Resumable: skips shards whose two
# aggregates exist. Logs ids/counts/timings/costs only to tools/stageA.log. Usage: tools/stageA.sh [XX ...]
set -u
ARM=<workspace>/rnd/research/coordinator/arms/wikifull
WD=<workspace>/shared-data/packs/work/wikifull-stageA
META=<workspace>/shared-data/packs
LOG=$ARM/tools/stageA.log
URL=https://huggingface.co/datasets/r4topunk/boar-packs/resolve/main/wiki/en
MINFREE_G=8; MINBAL=0.75; CAP=2.4
mkdir -p "$WD"
log(){ echo "$(date '+%F %T') $*" >> "$LOG"; }
TAGS="${*:-00 01 02 03 04 05 06 08 09 10 11 12 13 14}"
KEY="${VERCEL_AI_GATEWAY:-${AI_GATEWAY_API_KEY:-}}"
[ -z "$KEY" ] && { log "FATAL no gateway key"; exit 1; }
balance(){ curl -s -m 20 -H "Authorization: Bearer $KEY" https://ai-gateway.vercel.sh/v1/credits | python3 -I -c 'import json,sys;print(json.load(sys.stdin)["balance"])' 2>/dev/null || echo NA; }
spent(){ python3 -I -c 'import json,glob;print(round(sum(json.load(open(p)).get("gateway_cost_usd",0) for p in glob.glob("'"$ARM"'/aggregates/stageA-*-*.json")),4))'; }
log "START tags=[$TAGS] pid=$$"
for T in $TAGS; do
  [ "$T" = "07" ] && continue
  if [ -s "$ARM/aggregates/stageA-vpara-$T.json" ] && [ -s "$ARM/aggregates/stageA-v02-$T.json" ]; then log "skip $T (done)"; continue; fi
  F=boar-wiki-en-$T.sqlite; P=$WD/$F
  SHA=$(python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1]))["sha256"])' "$META/$F.json")
  SZ=$(python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1]))["sizeBytes"])' "$META/$F.json")
  B=$(balance); S=$(spent)
  if [ "$B" != NA ] && python3 -I -c "import sys;sys.exit(0 if float('$B')<$MINBAL else 1)"; then log "STOP balance $B < $MINBAL before $T"; exit 2; fi
  if python3 -I -c "import sys;sys.exit(0 if $S>$CAP else 1)"; then log "STOP stage spend \$$S > \$$CAP before $T"; exit 2; fi
  ok=0
  for attempt in 1 2; do
    # remove any other shard left over (one shard on disk at a time)
    find "$WD" -maxdepth 1 -name 'boar-wiki-en-*.sqlite' ! -name "$F" -delete
    FREE=$(df -g ~ | awk 'NR==2{print $4}'); NEED=$(( MINFREE_G + 2 ))
    [ -f "$P" ] || { if [ "$FREE" -lt "$NEED" ]; then log "STOP free ${FREE}G < ${NEED}G before $T"; exit 3; fi; }
    t0=$(date +%s)
    curl -sL --fail -C - --retry 5 --retry-delay 5 -o "$P" "$URL/$F" || log "curl rc=$? $T attempt $attempt"
    t1=$(date +%s); BY=$(stat -f %z "$P" 2>/dev/null || echo 0)
    GOT=$(shasum -a 256 "$P" 2>/dev/null | cut -d' ' -f1)
    if [ "$GOT" = "$SHA" ] && [ "$BY" = "$SZ" ]; then ok=1; log "dl $T bytes=$BY s=$((t1-t0)) MBps=$(( BY / 1048576 / (t1-t0+1) )) sha=ok free=$(df -g ~ | awk 'NR==2{print $4}')G bal=$B stage_spent=\$$S"; break; fi
    log "sha MISMATCH $T attempt $attempt bytes=$BY"; rm -f "$P"
  done
  [ $ok = 1 ] || { log "MISSING $T (sha failed twice)"; continue; }
  for SET in vpara v02; do
    g0=$(date +%s)
    python3 -I "$ARM/tools/wikifull_gate.py" --set $SET --shard "$P" --tag $T >> "$LOG" 2>&1 || log "gate FAIL $T $SET rc=$?"
    log "gate $T $SET s=$(( $(date +%s) - g0 ))"
  done
  rm -f "$P"; rm -rf "$WD/.cache"
  log "deleted $T free=$(df -g ~ | awk 'NR==2{print $4}')G"
done
log "END bal=$(balance) stage_spent=\$$(spent)"
