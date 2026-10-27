import struct,sys
def rd(f,fmt): return struct.unpack('<'+fmt,f.read(struct.calcsize('<'+fmt)))
def rs(f): (n,)=rd(f,'Q'); return f.read(n).decode('utf8','replace')
T={0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}
def val(f,t):
    if t==8: return rs(f)
    if t==9:
        (at,)=rd(f,'I');(n,)=rd(f,'Q')
        vals=[val(f,at) for _ in range(n)]
        return f"<array {n}>" if n>8 else vals
    return rd(f,T[t])[0]
for p in sys.argv[1:]:
    with open(p,'rb') as f:
        assert f.read(4)==b'GGUF'; (v,)=rd(f,'I');(nt,)=rd(f,'Q');(nkv,)=rd(f,'Q')
        print('==',p,'v',v,'tensors',nt)
        for _ in range(nkv):
            k=rs(f);(t,)=rd(f,'I');x=val(f,t)
            if 'token' in k and isinstance(x,str) and x.startswith('<array'): print(' ',k,x); continue
            print(' ',k,'=',x)
