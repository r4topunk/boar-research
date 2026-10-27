"""LITEREACH2-180 gates (criterion LITEREACH2-180-criterion.md sha 0f515606...; 0 LLM).
run <pack>: 20 rows, 0 errors/empty/reasoning/<think>; kept (title, section) + appended ids = step-0 b20 replay on >= 18/20.
checkpoint: first 3 packs: fic(B20 traces) - fic(LITE5-180 ON traces) >= +4 AND paired p50 promptTokens (B20 - ON) <= +600 -> CONTINUE else KILL.
all: G0 on 180; G1 kept+appended = replay >= 170/180; G2 fic B20 > ON (reported vs step-0 119); G3 paired p50 dprompt <= +600."""
import json, sys, re, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"; L = f"{A}/litereach2"; R = f"{L}/runs/180"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
FACTS = json.load(open(f"{A}/oracle-st/tools/oracle-facts.json"))
SPLIT = {d["id"]: d for d in map(json.loads, open(f"{A}/headpass-st/runs-x2/split-x2b.jsonl"))}
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
load = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
app = lambda t: [x.split(":add:")[1] for x in t["route"]["reasonCodes"] if x.startswith(("headpass:add:", "headpass:dense:add:"))]
def fic(i, t, p):
    if SPLIT[i]["S_present"]: return True
    own = {int(m.group(2)) for x in app(t) for m in [CID.match(x)] if m and m.group(1) == p}
    return bool({int(x.rsplit(":", 1)[1]) for x in FACTS[i]["fact_chunks"]} & own)
def pack(p):
    T = load(f"{R}/litereach2-b20-180-{p}-s42.traces.jsonl"); O = load(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.traces.jsonl")
    Rp = {(l := json.loads(x))["id"]: l for x in open(f"{L}/runs/step0/b20.{p}.jsonl") if x.strip()}
    return T, O, Rp
def stats(ps):
    r = {"n": 0, "errors": 0, "empty": 0, "reasoning_items": 0, "think": 0, "kept_app_eq_replay": 0, "fic_b20": 0, "fic_on": 0, "fic_replay_b20": 0, "dprompt": []}
    for p in ps:
        T, O, Rp = pack(p)
        for i, t in T.items():
            r["n"] += 1; txt = t["answer"]["text"] or ""
            r["errors"] += t["error"] is not None; r["empty"] += not txt.strip(); r["reasoning_items"] += (t["timing"].get("reasoningTokens") or 0) > 0; r["think"] += "<think>" in txt
            r["kept_app_eq_replay"] += [[k["title"], k.get("section")] for k in t["retrieval"]["kept"]] == [[k["title"], k.get("section")] for k in Rp[i]["kept"]] and app(t) == Rp[i]["appended"]
            r["fic_b20"] += fic(i, t, p); r["fic_on"] += fic(i, O[i], p)
            own = {int(m.group(2)) for x in Rp[i]["kept"] for m in [CID.match(x.get("chunkId") or "")] if m and m.group(1) == p}
            r["fic_replay_b20"] += bool({int(x.rsplit(":", 1)[1]) for x in FACTS[i]["fact_chunks"]} & own)
            a, b = t["timing"].get("promptTokens"), O[i]["timing"].get("promptTokens")
            if a is not None and b is not None: r["dprompt"].append(a - b)
    d = r.pop("dprompt"); r["dprompt_p50"] = st.median(d) if d else None; r["dprompt_max"] = max(d) if d else None; r["n_prompt_pairs"] = len(d)
    r["dfic"] = r["fic_b20"] - r["fic_on"]; return r
mode = sys.argv[1]
if mode == "run":
    p = sys.argv[2]; r = stats([p]); r["pack"] = p
    ok = r["n"] == 20 and r["errors"] == r["empty"] == r["reasoning_items"] == r["think"] == 0 and r["kept_app_eq_replay"] >= 18
elif mode == "checkpoint":
    r = stats(PACKS[:3]); ok = r["dfic"] >= 4 and r["dprompt_p50"] is not None and r["dprompt_p50"] <= 600
    r["verdict"] = "CONTINUE" if ok else "KILL"; json.dump(r, open(f"{L}/aggregates/checkpoint-180.json", "w"), indent=1)
else:
    r = stats(PACKS); r["per_pack"] = {p: stats([p]) for p in PACKS}
    ok = r["n"] == 180 and r["errors"] == r["empty"] == r["reasoning_items"] == r["think"] == 0 and r["kept_app_eq_replay"] >= 170 and r["fic_b20"] > r["fic_on"] and r["dprompt_p50"] <= 600
    r["step0_fic_b20_expected"] = 119; r["verdict"] = "PASS" if ok else "FAIL"; json.dump(r, open(f"{L}/aggregates/gate-180.json", "w"), indent=1)
r.setdefault("verdict", "PASS" if ok else "FAIL")
print(json.dumps({k: v for k, v in r.items() if k != "per_pack"})); sys.exit(0 if ok else 8)
