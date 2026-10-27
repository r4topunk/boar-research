import re,sys
def res(path, fn):
    s=open(path).read()
    pat=re.compile(r"<<<<<<< ours\n(.*?)=======\n(.*?)>>>>>>> theirs\n", re.S)
    n=[0]
    def r(m):
        n[0]+=1; return fn(n[0], m.group(1), m.group(2))
    s=pat.sub(r,s); open(path,"w").write(s); print(path, n[0], "hunks")
# answer.ts: 1 imports both; 2 deps both (ours then theirs); 3 theirs + sourceGroups spread
def a(i,o,t):
    if i in (1,2): return o+t
    assert "...(finalText !== undefined ? { finalText } : {})," in t
    return t.replace("          ...(finalText !== undefined ? { finalText } : {}),\n", "          ...(finalText !== undefined ? { finalText } : {}),\n          ...(sourceGroups ? { sourceGroups } : {}),\n")
res("src/routing/answer.ts", a)
res("src/routing/answerReducer.ts", lambda i,o,t: o+t)
