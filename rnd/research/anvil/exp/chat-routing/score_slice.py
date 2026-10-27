"""Score chat-routing runs on Compass chat-slice v0 (expected_search yes/no; 'either' excluded), C = Compass decisions.main.jsonl."""
import json, sys, statistics as st
SL = "<workspace>/rnd/research/compass/chat-slice/"
lab = {json.loads(l)["id"]: json.loads(l) for l in open("slice.items.jsonl")}
C = {}
for l in open(SL + "decisions.main.jsonl"):
    d = json.loads(l); C[d["id"]] = "SEARCH" if d.get("search", d.get("searched", d.get("decision") in ("search", "SEARCH"))) in (True, "yes", "SEARCH") else "ANSWER"
def score(name, dec):
    sc = [i for i in lab if lab[i]["label"] != "EITHER" and i in dec]
    no = [i for i in sc if lab[i]["label"] == "ANSWER"]; yes = [i for i in sc if lab[i]["label"] == "SEARCH"]
    fs = [i for i in no if dec[i] == "SEARCH"]; ms = [i for i in yes if dec[i] == "ANSWER"]
    acc = 1 - (len(fs) + len(ms)) / len(sc)
    print(f"{name:28s} acc {acc:.0%} ({len(sc)-len(fs)-len(ms)}/{len(sc)})  false-search {len(fs)}/{len(no)}  missed-search {len(ms)}/{len(yes)}  missed={ms}")
    return fs, ms
score("C main (smallTalk+classify)", C)
for tag in sys.argv[1:]:
    rows = [json.loads(l) for l in open(f"runs-{tag}.jsonl")]
    for k in ("A", "B"):
        if k in rows[0]:
            score(f"{tag} {k}", {r["id"]: r[k]["decision"] for r in rows})
    if "A" in rows[0]:
        calls = [r for r in rows if "<tool_call>" in r["A"]["text"]]
        print(f"   A calls {len(calls)}, format ok {sum(bool(r['A']['formatOk']) for r in calls)}, call-like text {sum(r['A']['looksLikeCallInText'] for r in rows)}, gen tokens p50 {st.median([r['A']['genTokens'] for r in calls]) if calls else None}")
        print("   A queries (multi-turn):", [(r["id"], r["A"]["query"]) for r in calls if lab[r["id"]].get("history")])
        score(f"{tag} A or B", {r["id"]: "SEARCH" if "SEARCH" in (r["A"]["decision"], r["B"]["decision"]) else "ANSWER" for r in rows})
    new = [r["B"]["promptTokens"] - r["B"]["staticPrefix"] for r in rows]
    print(f"   B prompt p50 {st.median(r['B']['promptTokens'] for r in rows)} static {rows[0]['B']['staticPrefix']} new p50 {st.median(new)} max {max(new)}")
