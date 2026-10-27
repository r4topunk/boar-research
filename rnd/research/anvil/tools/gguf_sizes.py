import struct,sys,collections
# ggml type -> (block elems, block bytes)
T={0:(1,4),1:(1,2),2:(32,18),3:(32,20),6:(32,22),7:(32,24),8:(32,34),10:(256,84),11:(256,110),12:(256,144),13:(256,176),14:(256,210),15:(256,292),30:(1,2)}
def rd(f,fmt): return struct.unpack("<"+fmt,f.read(struct.calcsize("<"+fmt)))[0]
def rstr(f): n=rd(f,"Q"); return f.read(n).decode("utf8","replace")
def rval(f,t):
    if t in (0,1): return rd(f,"B" if t==0 else "b")
    if t in (2,3): return rd(f,"H" if t==2 else "h")
    if t in (4,5): return rd(f,"I" if t==4 else "i")
    if t==6: return rd(f,"f")
    if t==7: return rd(f,"?")
    if t==8: return rstr(f)
    if t==9:
        at=rd(f,"I"); n=rd(f,"Q"); return [rval(f,at) for _ in range(n)]
    if t in (10,11): return rd(f,"Q" if t==10 else "q")
    if t==12: return rd(f,"d")
    raise Exception(t)
f=open(sys.argv[1],"rb"); assert f.read(4)==b"GGUF"; v=rd(f,"I"); nt=rd(f,"Q"); nkv=rd(f,"Q")
meta={}
for _ in range(nkv):
    k=rstr(f); t=rd(f,"I"); val=rval(f,t)
    if not isinstance(val,list) or len(val)<8: meta[k]=val
print({k:v for k,v in meta.items() if any(s in k for s in ["architecture","block_count","context_length","embedding_length","per_layer","file_type"])})
groups=collections.Counter(); total=0
for _ in range(nt):
    name=rstr(f); nd=rd(f,"I"); dims=[rd(f,"Q") for _ in range(nd)]; ty=rd(f,"I"); off=rd(f,"Q")
    n=1
    for d in dims: n*=d
    be,bb=T.get(ty,(1,0)); sz=n//be*bb; total+=sz
    g="per_layer_token_embd" if name.startswith("per_layer_token_embd") else ("token_embd" if name=="token_embd.weight" else "other(backbone)")
    groups[g]+=sz
    if g!="other(backbone)": print(name,dims,"type",ty,round(sz/2**30,3),"GiB")
for g,s in groups.items(): print(f"{g}: {s/2**30:.3f} GiB")
print(f"total tensors: {total/2**30:.3f} GiB")
