#!/usr/bin/env bash
# VENUEGPS: MacBook copy of the cut 7 engine tree with the desktop-node runner, as setup.sh builds it on the mini
# (git archive of wt/cut7 HEAD; wt/cut7 itself is never touched). be-repo = working-copy runner (with the patch),
# be-orig = committed runner (HEAD, adapter sha 7a0282ae) for the same-machine OFF gate. Usage: build-tree.sh <dir>
set -euo pipefail; B=<workspace>; R=$B/boar-eval; T=$1
mkdir -p $T; git -C $B/wt/cut7 archive HEAD src assets modules package.json tsconfig.json | tar -x -C $T
git -C $B/wt/cut7 rev-parse HEAD > $T/COMMIT; echo cut7 > $T/ARM; ln -sfn $B/wt/detmax/node_modules $T/node_modules
mkdir -p $T/be-repo/vendor/node_modules $T/be-repo/runs
rsync -a --exclude .cache --exclude runs --exclude vendor --exclude node_modules --exclude protocol.ts --exclude '*.test.ts' $R/adapters/desktop-node/runner/ $T/be-repo/
rsync -aL $R/packages/protocol/src/index.ts $T/be-repo/vendor/protocol.ts
rsync -aL $R/packages/protocol/node_modules/zod/ $T/be-repo/vendor/node_modules/zod/
printf '%s\n' 'export * from "./vendor/protocol";' > $T/be-repo/protocol.ts; ln -sfn $B/wt/eval/eval/node_modules $T/be-repo/node_modules
cp -a $T/be-repo $T/be-orig; rm -rf $T/be-orig/.cache; git -C $R show HEAD:adapters/desktop-node/runner/adapter.ts > $T/be-orig/adapter.ts
