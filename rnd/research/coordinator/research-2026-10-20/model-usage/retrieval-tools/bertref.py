import json,struct,numpy as np,glob,unicodedata,math
S=glob.glob('<home>/.cache/huggingface/hub/models--BAAI--bge-small-en-v1.5/snapshots/*/')[0]
raw=open('/tmp/rmaudit/dl/model.safetensors','rb').read(); n=struct.unpack('<Q',raw[:8])[0]; H=json.loads(raw[8:8+n]); base=8+n
W={}
for k,v in H.items():
    if k=='__metadata__': continue
    a,b=v['data_offsets']
    if v['dtype']!='F32': continue
    W[k.replace('bert.','')]=np.frombuffer(raw[base+a:base+b],dtype=np.float32).reshape(v['shape'])
# tokenizer (BERT uncased basic + wordpiece)
vocab=[l.rstrip('\n') for l in open(S+'vocab.txt')]; V={t:i for i,t in enumerate(vocab)}
def is_punct(c):
    cp=ord(c)
    if (33<=cp<=47) or (58<=cp<=64) or (91<=cp<=96) or (123<=cp<=126): return True
    return unicodedata.category(c).startswith('P')
def basic(t):
    t=''.join(' ' if (c in '\t\n\r' or unicodedata.category(c)=='Zs') else c for c in t if not (ord(c)==0 or ord(c)==0xfffd or (unicodedata.category(c).startswith('C') and c not in '\t\n\r')))
    out=''
    for c in t:
        cp=ord(c)
        if (0x4E00<=cp<=0x9FFF) or (0x3400<=cp<=0x4DBF) or (0xF900<=cp<=0xFAFF): out+=' '+c+' '
        else: out+=c
    toks=[]
    for w in out.lower().split():
        w=''.join(c for c in unicodedata.normalize('NFD',w) if unicodedata.category(c)!='Mn')
        cur=''
        for c in w:
            if is_punct(c):
                if cur: toks.append(cur); cur=''
                toks.append(c)
            else: cur+=c
        if cur: toks.append(cur)
    return toks
def wp(w):
    if len(w)>100: return [V['[UNK]']]
    out=[];s=0
    while s<len(w):
        e=len(w);f=None
        while s<e:
            sub=w[s:e]; sub=('##'+sub) if s>0 else sub
            if sub in V: f=V[sub];break
            e-=1
        if f is None: return [V['[UNK]']]
        out.append(f); s=e
    return out
def tok(t): return [101]+[i for w in basic(t) for i in wp(w)]+[102]
def ln(x,g,b,eps=1e-12): m=x.mean(-1,keepdims=True); v=((x-m)**2).mean(-1,keepdims=True); return (x-m)/np.sqrt(v+eps)*g+b
erf=np.vectorize(math.erf)
def gelu(x): return 0.5*x*(1+erf(x/math.sqrt(2)))
def embed(ids):
    ids=np.array(ids); L=len(ids)
    x=W['embeddings.word_embeddings.weight'][ids]+W['embeddings.position_embeddings.weight'][:L]+W['embeddings.token_type_embeddings.weight'][0]
    x=ln(x,W['embeddings.LayerNorm.weight'],W['embeddings.LayerNorm.bias'])
    for i in range(12):
        p=f'encoder.layer.{i}.'
        lin=lambda h,n: h@W[p+n+'.weight'].T+W[p+n+'.bias']
        q=lin(x,'attention.self.query').reshape(L,12,32).transpose(1,0,2)
        k=lin(x,'attention.self.key').reshape(L,12,32).transpose(1,0,2)
        v=lin(x,'attention.self.value').reshape(L,12,32).transpose(1,0,2)
        a=[email removed](0,2,1)/math.sqrt(32); a=np.exp(a-a.max(-1,keepdims=True)); a/=a.sum(-1,keepdims=True)
        c=(a@v).transpose(1,0,2).reshape(L,384)
        x=ln(lin(c,'attention.output.dense')+x,W[p+'attention.output.LayerNorm.weight'],W[p+'attention.output.LayerNorm.bias'])
        h=gelu(lin(x,'intermediate.dense'))
        x=ln(lin(h,'output.dense')+x,W[p+'output.LayerNorm.weight'],W[p+'output.LayerNorm.bias'])
    return x
G=json.load(open('/tmp/rmaudit/out/ref_gguf.json'))
cos=[];tokmatch=0;meancos=[]
for g in G:
    t=tok(g['text']); tokmatch+= (t==g['ids'])
    X=embed(t); cls=X[0]/np.linalg.norm(X[0]); mean=X.mean(0); mean/=np.linalg.norm(mean)
    v=np.array(g['vec']); v/=np.linalg.norm(v)
    cos.append(float(cls@v)); meancos.append(float(mean@v))
cos=np.array(cos)
print('token ids identical HF-style vs llama.cpp:',tokmatch,'/',len(G))
print('cos(fp32 CLS ref, q8_0 GGUF): min %.5f median %.5f'%(cos.min(),np.median(cos)))
print('cos(fp32 MEAN ref, q8_0 GGUF): median %.4f (should be clearly lower if GGUF is CLS)'%np.median(meancos))
json.dump({'cos_cls':cos.tolist(),'cos_mean':meancos},open('/tmp/rmaudit/out/ref_cmp.json','w'))
# also: does fp32-vs-q8 change ranking? compare query-passage sims
