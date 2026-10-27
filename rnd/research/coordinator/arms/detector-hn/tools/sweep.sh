#!/bin/bash
# exploratory HN-dose sweep (diagnostic only, not eligible for ACCEPTED): tag mine rand cap
PY=<workspace>/rnd/research/sonar/exp/30-learned-detector/.venv/bin/python3
while read t m r c; do
  $PY -I tools/train_head.py $t $m $r $c 2>&1 | grep -v Warn | tail -1 | python3 -I -c "import json,sys;d=json.loads(sys.stdin.read());print(d['tag'],'mined',d['hn_mined'],'rand',d['hn_random'],'best_ep',d['best_epoch'])"
  $PY -I tools/reads.py work/$t.head.json work/reads.$t.json 2>&1 | grep -v Warn | python3 -I -c "
import json,sys;d=json.loads(sys.stdin.read());r=d['read1'];print('  lost pos',{k:len(v['lost_pos']) for k,v in r.items()},'probe lost',len(d['read3']['lost_fires']),'new',len(d['read3']['new_fires']),'titles fp',d['read2']['titles_heldout']['fp_v3b'],'->',d['read2']['titles_heldout']['fp_v3c'],'cm fires',len(d['read2']['cm40']['fires_v3c']))"
done
