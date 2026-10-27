#!/bin/bash
# F1b answer screen: per-run pack dir on the mini = APFS clones (0 extra bytes) of compose/packs-k13 (the 13-pack kit of ARM-G) with qa-cooking-se / qa-money-se replaced by the v3 files (chunk_vecs) from shared-data/packs/v3proto/.
set -eu
<on the mini> 'bash -s' <<'Y'
set -eu; K=$HOME/boar/kiln/compose/packs-k13; D=$HOME/boar/kiln/compose/packs-f1b; S=$HOME/boar/shared-data/packs/v3proto; mkdir -p $D
for f in $K/*.sqlite; do b=$(basename $f); [ -f $D/$b ] || cp -c $f $D/$b; done
for b in qa-cooking-se qa-money-se; do rm -f $D/$b.sqlite; cp -c $S/$b.sqlite $D/$b.sqlite; done
cd $D; shasum -a 256 *.sqlite; ls | wc -l
Y
