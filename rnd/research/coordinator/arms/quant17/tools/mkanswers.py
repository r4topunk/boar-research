import json,sys,os
src,out=sys.argv[1],sys.argv[2]; os.makedirs(out,exist_ok=True)
for l in open(src):
    r=json.loads(l); open(f"{out}/{r['i']:02d}.answer.txt",'w').write(r['text'])
