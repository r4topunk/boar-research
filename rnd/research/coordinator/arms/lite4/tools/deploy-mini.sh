#!/bin/bash
# LITE4 mini deploy (run on the mini with bash): side tree be-0cfd4a77-cut7-lite4 = cut 7 src/assets/modules copy + tools/lite4.patch,
# be-repo -> cut7's be-repo (runs/ shared), side dir be-repo-lite4 = be-repo-lite2 files + the LITE_SOURCE_BOUND adapter line; .cache shared by symlink.
set -eu
K=<runner>/kiln; B=$K/be-0cfd4a77-cut7; T=$K/be-0cfd4a77-cut7-lite4
[ -e $T ] && { echo "exists $T"; exit 1; }
mkdir $T; cd $B; cp -R COMMIT PATCH_SHA256 assets modules package.json src tsconfig.json $T/
cd $T; echo "cut7+lite4" > ARM; ln -s <runner>/official-6c3d6c6/node_modules node_modules; ln -s ../be-0cfd4a77-cut7/be-repo be-repo
patch -p1 < $K/lite4/lite4.patch; cp $K/lite4/lite4.patch LITE4.patch; shasum -a 256 LITE4.patch | cut -d' ' -f1 > LITE4_PATCH_SHA256
mkdir be-repo-lite4; cd be-repo-lite4
cp -R $B/be-repo-lite2/{adapter.ts,app-shims,gate.ts,merge-shards.mjs,parallel.sh,protocol.ts,server.ts,trace.ts} .
ln -s ../be-repo/node_modules node_modules; ln -s ../be-repo/runs runs; ln -s ../be-repo/vendor vendor; ln -s $B/be-repo-lite2/.cache .cache
python3 - <<'PY'
p='adapter.ts'; s=open(p).read(); old='    ...(emergencyScore ? { emergencyScore } : {}),\n'
assert s.count(old)==1
s=s.replace(old, old+'    // LITE4 (engine deps.liteSourceBound): the eval-side switch; the engine reads deps only.\n    ...(process.env.LITE_SOURCE_BOUND === "1" ? { liteSourceBound: true } : {}),\n')
open(p,'w').write(s)
PY
shasum -a 256 adapter.ts server.ts $T/src/routing/answer.ts $T/src/routing/context.ts; cat $T/LITE4_PATCH_SHA256; ls -la $T $T/be-repo-lite4; df -k ~ | tail -1
