#!/usr/bin/env bash
# Rebuild the claim engine (cut 7) and the deep research config from the public base commit + one cumulative patch each,
# and print two hashes per tree: the git tree object id and the BOAR content hash (tree-hash.mjs).
# Usage: verify-trees.sh <boar-app clone> <empty scratch dir> <dir with the two .patch files>
#   boar-app clone: any clone containing commit 0cfd4a77 (the public upstream boar-app repository, see BOM.md).
set -euo pipefail
APP="$(cd "${1:?boar-app clone}" && pwd)"; SCR="${2:?scratch dir}"; PDIR="$(cd "${3:?patch dir}" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE=0cfd4a77
mkdir -p "$SCR"; SCR="$(cd "$SCR" && pwd)"
check() { # name patch expect_git expect_content
  local name="$1" patch="$2" eg="$3" ec="$4" wt="$SCR/wt-$1"
  ( cd "$PDIR" && shasum -a 256 -c "$patch.sha256" )
  git -C "$APP" worktree add --detach "$wt" "$BASE" >/dev/null
  ( cd "$wt" && git apply --index "$PDIR/$patch" )
  local g c; g="$(cd "$wt" && git write-tree)"; c="$(node "$HERE/tree-hash.mjs" "$wt")"
  echo "$name git-tree   got $g"; echo "$name git-tree   exp $eg"
  echo "$name content    got $c"; echo "$name content    exp $ec"
  git -C "$APP" worktree remove --force "$wt"
  [[ "$g" == "$eg" && "$c" == "$ec"* ]] && echo "$name: OK" || { echo "$name: MISMATCH"; return 1; }
}
rc=0
check cut7 cut7.vs-0cfd4a77.patch 17d42f2027bdd3b95f2956655d5e49b9924db1a1 7c96e59e001b6273baa4f8dcaa7c696c1aa8f356321914b29e38fe58a900cf79 || rc=1
[[ -f "$PDIR/deep-dt512.vs-0cfd4a77.patch" ]] && { check deep-dt512 deep-dt512.vs-0cfd4a77.patch e216bc9062fc828eb709ae0c017c9edf308345f2 8ce8b0fc572aa7909c6590f7a014e8a038f4c961decf3c01d03a6da3d9573000 || rc=1; }
exit $rc
