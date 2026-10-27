#!/bin/bash
# GEMMATHINK: build mini tree be-0cfd4a77-gemmathink = rsync of -deepthink (minus be-repo/runs, be-repo/.cache) + be-repo/{adapter,server}.ts from boar-eval 80a16cc; install the runner. Prints shas only.
set -u; H=MINI_HOST; E=<workspace>/boar-eval/adapters/desktop-node/runner; TO=$(cd "$(dirname "$0")" && pwd)
ssh -T -n $H 'bash -c "cd <runner>/kiln && [ -d be-0cfd4a77-gemmathink ] || rsync -a --exclude be-repo/runs --exclude be-repo/.cache be-0cfd4a77-deepthink/ be-0cfd4a77-gemmathink/ && mkdir -p be-0cfd4a77-gemmathink/be-repo/runs && echo gemmathink > be-0cfd4a77-gemmathink/ARM && echo tree-ok"'
scp -q $E/adapter.ts $H:boar/kiln/be-0cfd4a77-gemmathink/be-repo/adapter.ts && scp -q $E/server.ts $H:boar/kiln/be-0cfd4a77-gemmathink/be-repo/server.ts && scp -q $TO/remote-run.sh $H:boar/kiln/gemmathink-remote-run.sh
ssh -T -n $H 'bash -c "cd <runner>/kiln/be-0cfd4a77-gemmathink && shasum -a 256 be-repo/adapter.ts be-repo/server.ts <runner>/kiln/gemmathink-remote-run.sh | cut -c1-16,65-; cat ARM PATCH_SHA256 DEEPTHINK_PATCH_SHA256 | cut -c1-16; diff -rq --exclude runs --exclude .cache --exclude node_modules ../be-0cfd4a77-deepthink . | head"'
