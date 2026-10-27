# TOPICS27-SUCCINCT prep (copy of prep.py, paths only) (0 LLM): split answers, attach the answer's own dumped context, count absent numbers.
import json, re, sys, hashlib
sys.path.insert(0, "tools"); from split import split
tr = {json.loads(l)["itemId"]: json.loads(l) for l in open("gen-succinct/traces.jsonl")}
pr = {}
for l in open("gen-succinct/prompts.jsonl"):
    d = json.loads(l); pr.setdefault(d["itemId"], []).append(d)
rp = {json.loads(l)["id"]: json.loads(l) for l in open("replay/t27.replay.jsonl")}
topics = json.load(open("in/topics.json")); units = []; items = []
NUM = re.compile(r"\d+(?:[.,]\d+)?%?")
for r in topics:
    k = r["key"]; t = tr[k]; text = t["answer"]["text"] or ""
    ctx, src = None, None
    for d in reversed(pr.get(k, [])):
        sysm = next((m["content"] for m in d.get("messages", []) if m["role"] == "system"), d.get("prompt", ""))
        if "\nContext:\n" in sysm: ctx = sysm.split("\nContext:\n", 1)[1]; src = "dump"; break
    if ctx is None and rp[k]["keptFull"]:
        ctx = "\n\n".join(f"[{i+1}] {c['title']}\n{c['body']}" for i, c in enumerate(rp[k]["keptFull"])); src = "replay"
    banner, sents = split(text)
    cl = (ctx or "").lower(); cnums = set(n.rstrip("%").replace(",", "") for n in NUM.findall(cl))
    na = [sum(1 for n in NUM.findall(s) if n.rstrip("%").replace(",", "") not in cnums and not re.fullmatch(r"\[?\d\]?", n)) for s in sents]
    items.append(dict(key=k, area=r["area"], ctx_src=src, ctx_chars=len(ctx or ""), banner=banner, n_sent=len(sents), num_absent=na,
                      kept=[s["title"] for s in t["retrieval"]["kept"]], raw=[s["title"] for s in t["retrieval"]["raw"]],
                      declined=t["answer"].get("declined"), warnings=t["answer"].get("warnings"), reason=t["route"]["reasonCodes"], words=len(text.split())))
    for i, s in enumerate(sents):
        units.append(dict(key=f"{k}#{i}", topic=k, idx=i, question=r["en"], chunks=ctx if ctx else "(no source chunks were given to the model)", sentence=s))
json.dump(dict(units=units, items=items), open("judge-succinct/prep.json", "w"), indent=1)
print("sentences", len(units)); [print(i["key"], i["n_sent"], i["ctx_src"], i["ctx_chars"], "kept", i["kept"], "banner", bool(i["banner"]), "numabs", sum(i["num_absent"])) for i in items]
