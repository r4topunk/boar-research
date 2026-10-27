#!/usr/bin/env bash
# mktree.sh <git-ref-or-worktree-dir> <dest>: local desktop-node engine tree (stub-replay use only)
set -e; SRC=$1; DST=$2; B=<workspace>; mkdir -p $DST
if [ -d "$SRC" ]; then (cd $SRC && tar -c src assets modules package.json tsconfig.json 2>/dev/null) | tar -x -C $DST
else git -C $B/wt/travelsel archive $SRC src assets modules package.json tsconfig.json | tar -x -C $DST; fi
mkdir -p $DST/be/vendor/node_modules
rsync -a --exclude .cache --exclude runs --exclude vendor --exclude node_modules --exclude protocol.ts --exclude '*.test.ts' $B/boar-eval/adapters/desktop-node/runner/ $DST/be/
rsync -aL $B/boar-eval/packages/protocol/src/index.ts $DST/be/vendor/protocol.ts
rsync -aL $B/boar-eval/packages/protocol/node_modules/zod/ $DST/be/vendor/node_modules/zod/
echo 'export * from "./vendor/protocol";' > $DST/be/protocol.ts
ln -sfn $B/boar-app/node_modules $DST/node_modules; ln -sfn $B/wt/eval/eval/node_modules $DST/be/node_modules
git -C $B/boar-app rev-parse 0cfd4a77 > $DST/COMMIT; echo "${3:-arm}" > $DST/ARM
