#!/bin/bash
# Per-run pack dir on the mini: APFS clones (0 extra bytes) of the 13 kit files; prints sha256 for comparison with kit13.json (= compose/verify.json = manifests; wiki-vital5 has no manifest, sha = local file).
set -eu
<on the mini> 'bash -s' <<'Y'
set -eu; D=$HOME/boar/kiln/compose/packs-k13; S=$HOME/boar/shared-data; mkdir -p $D
for f in crypto/boar-crypto packs/boar-wikivoyage-en packs/v3proto/boar-simplewiki-en packs/wave3/qa-cooking-se packs/wave3/qa-money-se packs/v3proto/boar-factbook packs/v3proto/boar-medlineplus-en packs/v3proto/boar-firstaid-en packs/wave4/boar-visa-en packs/v3proto/qa-health-se packs/v3proto/qa-travel-se packs/v3proto/qa-outdoors-se packs/wiki-vital5; do
  b=$(basename $f); [ -f $D/$b.sqlite ] || cp -cL $S/$f.sqlite $D/$b.sqlite
done
cd $D; shasum -a 256 *.sqlite
Y
