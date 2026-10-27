"""SMALLCLS runner (criterion 132fa1f0): python3 -I run.py <tag> '<extra json>' ; reads tasks.jsonl, writes out-<tag>.jsonl (resumable)."""
import json, os, sys, time, urllib.request
tag, extra = sys.argv[1], json.loads(sys.argv[2]); D = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(f"{D}/tasks.jsonl")]; OP = f"{D}/out-{tag}.jsonl"
done = {json.loads(l)["key"] for l in open(OP)} if os.path.exists(OP) else set()
fold = lambda s: " ".join(s.lower().replace("*", "").replace('"', "").strip().strip(".").split())
for r in rows:
    if r["key"] in done: continue
    opts = r["options"]
    if r["task"] == "A":
        sysm = "You route emergency questions to the right guidance page. Reply with exactly one option from the list, copied verbatim, and nothing else. Reply none if the message is not about an emergency or safety situation."
        user = "Options:\n" + "\n".join(opts) + "\n\nMessage: " + r["question"] + "\n\nOption:"
    else:
        sysm = "You pick the section of a safety guidance page that tells this person what to do right now. Reply with exactly one heading from the list, copied verbatim, and nothing else."
        user = "Page: " + r["page"] + "\nHeadings:\n" + "\n".join(opts) + "\n\nMessage: " + r["question"] + "\n\nHeading:"
    b = {"messages": [{"role": "system", "content": sysm}, {"role": "user", "content": user}], "max_tokens": 24, "temperature": 0, "seed": 42, "cache_prompt": True}
    b.update(extra); t = time.time()
    j = json.loads(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8192/v1/chat/completions", json.dumps(b).encode(), {"Content-Type": "application/json"}), timeout=600).read())
    out = (j["choices"][0]["message"].get("content") or "").strip().split("\n")[0]
    m = next((o for o in opts if o == out), None) or next((o for o in opts if fold(o) == fold(out)), None)
    rec = dict(key=r["key"], task=r["task"], set=r["set"], id=r["id"], gold=r["gold"], raw=out, pred=m, ok=(m == r["gold"]), ms=round((time.time() - t) * 1000), ptok=j["usage"]["prompt_tokens"])
    open(OP, "a").write(json.dumps(rec, ensure_ascii=False) + "\n")
print("done", tag)
