# A vocabulary-free "personal situation asking what to do" shape, frozen here before looking at hits (one try).
import json, re, collections
SIT = re.compile(r"\b(what (should|do|can|must) (i|we) do|what do i do|what now|should i\b|should we\b|how do i (stop|treat|get rid|remove|help)|"
                 r"o que (eu |a gente )?(fa[çc]o|devo fazer|fazer)|devo\b|como (eu )?(tiro|paro|trato|ajudo)|e agora)", re.I)
T = json.load(open("tasks.json"))
C = collections.Counter()
for t in T:
    hit = bool(SIT.search(t["q"])); C[(t["label"], t["task"], hit)] += 1
for k, v in sorted(C.items(), key=str): print(k, v)
print("danger not matched:", [t["id"] for t in T if t["label"] == "danger" and not SIT.search(t["q"])])
print("non-danger matched:", [(t["id"], t["task"], t["q"][:70]) for t in T if t["label"] != "danger" and SIT.search(t["q"])])
