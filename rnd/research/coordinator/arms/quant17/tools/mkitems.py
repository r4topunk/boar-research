import json,sys,os
src,out=sys.argv[1],sys.argv[2]; os.makedirs(out,exist_ok=True)
rows=[json.loads(l) for l in open(src)][:30]
for i,r in enumerate(rows):
    p=''.join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in r['messages'])+"<|im_start|>assistant\n<think>\n\n</think>\n\n"
    open(f"{out}/{i:02d}.prompt.txt",'w').write(p)
    open(f"{out}/{i:02d}.id",'w').write(r['itemId'])
