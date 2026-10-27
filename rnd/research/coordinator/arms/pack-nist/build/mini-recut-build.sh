set -e
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
df -h ~ | tail -1
W=<runner>/kiln/packs/nist/recut; S=$W/shards; cd <runner>/kiln/packs/builder
python3 -I -c "
import json,sys
a=json.load(open('$S/pack-manifest.json')); b=json.load(open('$HOME/boar/kiln/packs/nist/conv/manifest.json'))
json.dump(a+b, open('$W/manifest-B.json','w'))"
mkdir -p $W/A $W/B
for X in A B; do
  EXTRA=""; MAN=$S/pack-manifest.json
  [ $X = B ] && EXTRA=<runner>/kiln/packs/nist/conv/boar-nist-crypto.jsonl && MAN=$W/manifest-B.json
  BOAR_EMBED_GPU=metal node scripts/build-wiki-pack.mjs --out $W/$X/boar-crypto.sqlite --manifest $MAN --name "boar-crypto recut-$X (PACK-NIST measurement only)" --shards $S/eips.jsonl $S/bips.jsonl $S/specs.jsonl $S/ethereumorg.jsonl $S/wikipedia.jsonl $EXTRA 2>&1 | grep -E '"articles"|"chunks"|sizeBytes|buildSeconds|rror'
  shasum -a 256 $W/$X/boar-crypto.sqlite
done
du -sh $W
