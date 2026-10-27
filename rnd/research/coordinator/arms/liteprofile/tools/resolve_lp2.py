import re
p="src/routing/answer.test.ts"; s=open(p).read()
pat=re.compile(r"<<<<<<< ours\n(.*?)=======\n(.*?)>>>>>>> theirs\n", re.S)
m=list(pat.finditer(s)); assert len(m)==1
s=s[:m[0].start()]+m[0].group(1)+"  });\n});\n\n"+m[0].group(2)+s[m[0].end():]
open(p,"w").write(s); print("ok")
