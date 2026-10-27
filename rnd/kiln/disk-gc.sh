#!/usr/bin/env bash
# disk-gc.sh: Kiln's disk GC for rnd/DISK-POLICY.md. Reads the class map (disk-gc.map, reviewed in git at rnd/kiln/) and
# deletes ONLY classes A and B, only the exact paths the map lists for this host. Dry run by default.
#   <runner>/kiln/disk-gc.sh [--dry-run]                     # list every map line for this host with size and state
#   <runner>/kiln/disk-gc.sh --apply A,B                     # delete A+B (standing approval, r4to 2026-10-02)
#   rnd/kiln/disk-gc.sh --host macbook --map rnd/kiln/disk-gc.map --apply A,B   # MacBook side (builds/, wt/)
# Never: Docker, anything outside <runner> (mini) or <workspace>/{builds,wt} (MacBook), blind/, veil/, globs, classes C/D/E.
# A path in use (any process whose command line names it) is skipped. Every deletion is one TSV line in the log
# (date host path KB class kind queue restore extra); copy them into rnd/kiln/DISK-LOG.md.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MAP="$HERE/disk-gc.map"; APPLY=""; HOSTTAG=""
while [[ $# -gt 0 ]]; do case "$1" in
  --dry-run) APPLY=""; shift ;;
  --apply) APPLY="$2"; shift 2 ;;
  --map) MAP="$2"; shift 2 ;;
  --host) HOSTTAG="$2"; shift 2 ;;
  *) echo "disk-gc: unknown argument $1" >&2; exit 2 ;; esac; done
if [[ -z "$HOSTTAG" ]]; then if [[ -d <workspace> ]]; then HOSTTAG=macbook; else HOSTTAG=mini; fi; fi
[[ "$HOSTTAG" == mini || "$HOSTTAG" == macbook ]] || { echo "disk-gc: --host mini|macbook" >&2; exit 2; }
for c in ${APPLY//,/ }; do [[ "$c" == A || "$c" == B ]] || { echo "disk-gc: only A and B can be applied (got $c)" >&2; exit 2; }; done
[[ -f "$MAP" ]] || { echo "disk-gc: no map at $MAP" >&2; exit 2; }
LOG="$HERE/disk-gc.$HOSTTAG.log"
ARCH="$HOME/boar/kiln/gc-archive"
free_gib() { df -g "$HOME" | awk 'NR==2{print $4}'; }

# Absolute path for a map entry, or empty when the entry is outside this host's scope.
resolve() {
  local p="$1"
  case "$p" in *..*|*'*'*|*'?'*) return 0 ;; esac
  if echo "$p" | grep -qiE '(^|/)(blind|veil)(/|$)|docker'; then return 0; fi
  if [[ "$HOSTTAG" == mini ]]; then [[ "$p" == boar/* ]] && echo "$HOME/$p"
  else [[ "$p" == <workspace>/builds/* || "$p" == <workspace>/wt/* ]] && echo "$p"; fi
}
in_use() { pgrep -f -- "$1" >/dev/null 2>&1; }

echo "disk-gc host=$HOSTTAG map=$MAP mode=${APPLY:+apply $APPLY}${APPLY:-dry-run} free=$(free_gib) GiB"
before=$(free_gib); freed_kb=0
while IFS=$'\t' read -r host path class kind queue restore extra; do
  [[ -z "${host:-}" || "$host" == \#* || "$host" != "$HOSTTAG" ]] && continue
  abs="$(resolve "$path" || true)"
  if [[ -z "$abs" ]]; then
    [[ "$kind" == keep ]] && printf '%s\t%s\t%s\t-\t%s\n' "$class" "$kind" "$path" "$queue" || echo "REFUSED (out of scope / pattern): $path"
    continue
  fi
  if [[ ! -e "$abs" ]]; then printf '%s\t%s\t%s\tgone\n' "$class" "$kind" "$path"; continue; fi
  kb=$(du -sk "$abs" 2>/dev/null | cut -f1)
  printf '%s\t%s\t%s\t%s MB\t%s\n' "$class" "$kind" "$path" "$((kb / 1024))" "$queue"
  [[ ",$APPLY," == *",$class,"* && ( "$class" == A || "$class" == B ) && "$kind" != keep ]] || continue
  if in_use "$abs"; then echo "  SKIP in use: $abs"; continue; fi
  note=""
  case "$kind" in
    rm) rm -rf -- "$abs" ;;
    apk)
      [[ "$abs" == *.apk && -f "$abs" ]] || { echo "  SKIP not an apk file"; continue; }
      note="sha256=$(shasum -a 256 "$abs" | cut -d' ' -f1)"; rm -f -- "$abs" ;;
    archive-rm)
      mkdir -p "$ARCH"; name="$(basename "$abs")"
      if [[ -d "$abs/kiln" ]]; then tar -czf "$ARCH/$name.tgz" -C "$abs" --exclude node_modules kiln; note="archive=$ARCH/$name.tgz"; fi
      rm -rf -- "$abs" ;;
    wt)
      d=$(git -C "$abs" diff HEAD --binary | shasum -a 256 | cut -c1-12)
      if [[ "$d" != "${extra:-none}" ]] || [[ -n "$(git -C "$abs" status --porcelain | grep '^??' || true)" ]]; then
        echo "  SKIP worktree diff $d != map ${extra:-none} or untracked files"; continue; fi
      common="$(git -C "$abs" rev-parse --path-format=absolute --git-common-dir)"
      git -C "$(dirname "$common")" worktree remove --force "$abs"; note="diff=$d" ;;
    *) echo "  SKIP unknown kind $kind"; continue ;;
  esac
  freed_kb=$((freed_kb + kb))
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "$HOSTTAG" "$path" "$kb" "$class" "$kind" "$queue" "$restore" "$note" | tee -a "$LOG" | sed 's/^/  DELETED /'
done < "$MAP"
echo "disk-gc done: freed $((freed_kb / 1024 / 1024)) GiB (${freed_kb} KB), free $before -> $(free_gib) GiB"
