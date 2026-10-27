"""Scripted checks of QFORM.md (0 LLM). python3 -I tools/check_forms.py  -> prints violations, exit 1 if any.
F1: no token of the title / entity (token equality for tokens >= 3 chars; substring for entity tokens >= 5 chars).
F2: <= 4 words.  F3: first person, >= 8 words.  F4: every content word (>= 4 letters, not a stopword) is within 2 edits of a word of F0, and F4 != F0 (typo present).
F5/F6: declarative ending in '?' (no leading interrogative).  F7: carries a comparison marker.  F8: no entity token.  All forms >= 3 words."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
items = [json.loads(l) for l in open(os.path.join(ROOT, "items/qform.jsonl"))]
facts = {f["fact_id"]: f for f in json.load(open(os.path.join(ROOT, "items/facts.json")))}
STOP = set("a an the of and or to in on at for with from by is are was were be been do does did can could should would will shall may might "
           "what when where which who whom whose why how that this these those it its it's i me my we our you your he she they them their there here "
           "as if than then so not no yes any some all more most much many very just also about into over per via up out off".split())
SLANG = set("whats wats hows wanna gonna pls plz thx abt wen wich wat dont cant wont isnt arent shouldnt couldnt wouldnt doesnt didnt hasnt havent im ive ill youre theyre thats theres lol".split())
def toks(s): return re.findall(r"[a-z0-9]+", s.lower())
def lev(a, b):
    if a == b: return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]
INTERR = {"what", "when", "how", "which", "who", "why", "is", "are", "do", "does", "did", "can", "could", "should", "would", "will", "where"}
CMP = re.compile(r"\b(compare|compared|compares|versus|vs|or|than|differ|differs|different|earlier|longer|first|stricter|harder|more|higher|sooner|better|bigger)\b", re.I)
viol = []
by = {}
for it in items: by.setdefault(it["fact_id"], {})[it["form"]] = it
for fid, forms in by.items():
    f = facts[fid]
    avoid_all = set(toks(f["title"])) | set(toks(" ".join(f["avoid"])))
    avoid_eq = {t for t in avoid_all if len(t) >= 3 and t not in STOP}
    avoid_sub = {t for t in avoid_all if len(t) >= 5 and t not in STOP}
    f0 = toks(forms[0]["question"])
    for k, it in forms.items():
        q = it["question"]; w = q.split()
        if len(w) < 3: viol.append((it["id"], "fewer than 3 words"))
        tk = toks(q)
        if k == 1:
            bad = [t for t in tk if t in avoid_eq or any(a in t for a in avoid_sub)]
            if bad: viol.append((it["id"], f"F1 entity token {bad}"))
        if k == 2 and len(w) > 4: viol.append((it["id"], f"F2 {len(w)} words"))
        if k == 3 and (len(w) < 8 or not re.search(r"\b(i|i'm|i've|my|we|we're|our|me)\b", q.lower())): viol.append((it["id"], "F3 not situational first person"))
        if k == 4:
            if q.strip().lower() == forms[0]["question"].strip().lower(): viol.append((it["id"], "F4 == F0"))
            bad = []
            typos = 0
            for t in tk:
                if len(t) < 4 or t in STOP or t in SLANG or t.isdigit(): continue
                d = min(lev(t, g) for g in f0)
                if d > 2: bad.append(t)
                if d > 0: typos += 1
            if bad: viol.append((it["id"], f"F4 content words > 2 edits from F0: {bad}"))
            if typos == 0: viol.append((it["id"], "F4 has no typo/colloquial change"))
        if k in (5, 6):
            if not q.strip().endswith("?"): viol.append((it["id"], "no '?'"))
            if tk and tk[0] in INTERR: viol.append((it["id"], "interrogative start (not declarative)"))
        if k == 7 and not CMP.search(q): viol.append((it["id"], "F7 no comparison marker"))
        if k == 8:
            GEN = {"visa", "policy", "requirements", "citizens"}  # generic title words of the visa pack, not entities
            e_eq = avoid_eq - GEN; e_sub = avoid_sub - GEN
            bad = [t for t in tk if t in e_eq or any(a in t for a in e_sub)]
            if bad: viol.append((it["id"], f"F8 entity token {bad}"))
        if k != 0 and not q.strip()[-1] in "?.": 
            pass
for v in viol: print(*v)
print(len(viol), "violations over", len(items), "items")
sys.exit(1 if viol else 0)
