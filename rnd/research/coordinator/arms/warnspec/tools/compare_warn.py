"""WARNSPEC-PATCH replay comparison (0 LLM). Per set (probes, v01, st):
(1) OFF (warn tree, deps.warn unset) vs pristine wt/pr1: whole trace identical (route, retrieval, answer, events; tMs/timing/ids dropped);
(2) ON vs OFF: a turn without a caution is identical; a turn with one differs only by the warn event, done.warn, the warn:<tier> code,
    the held-back non-declined weak_sources warnings and the uncited preface;
(3) ON tiers vs aggregates/warnspec.json: probes/v01 = the 4B rows' ids with the stub's tier (no-source stays, else beyond-source:
    the stub cites nothing), st = the 4B-replay rows (the same stub replay, 140 published self-tests). Usage: python3 -I compare_warn.py <out.json>"""
import json, sys, copy, re
A = "<workspace>/rnd/research/coordinator/arms/warnspec"; R = f"{A}/runs"
W = json.load(open(f"{A}/aggregates/warnspec.json"))["rows"]
PUB = ("st-boar-factbook-", "st-boar-firstaid-en-", "st-boar-medlineplus-en-", "st-boar-simplewiki-en-", "st-qa-bitcoin-se-", "st-qa-ethereum-se-", "st-qa-health-se-", "st-qa-outdoors-se-", "st-qa-travel-se-")
PREF = re.compile(r"^(?:This answer is not from an offline source[^\n]*|Esta resposta não vem de uma fonte offline[^\n]*)\n\n")
def jl(p): return {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
def norm(t):
    t = copy.deepcopy(t)
    for k in ("runId", "createdAt", "timing", "resources", "config", "engine", "runtime"): t.pop(k, None)
    t["events"] = [{k: v for k, v in e.items() if k not in ("tMs", "at", "ms")} for e in t["events"]]  # ms = a wall-clock duration (retrieve)
    for e in t["events"]:
        if e.get("type") == "done" and isinstance(e.get("receipt"), dict):
            for k in ("ttftMs", "totalMs", "retrievalMs", "loadMs", "prefillMs", "tokPerSec"): e["receipt"].pop(k, None)
    return t
def warn_of(t):
    d = [e for e in t["events"] if e.get("type") == "done"]; return ((d[-1].get("warn") or {}).get("tier")) if d else None
def strip_warn(t):
    """ON trace -> what OFF must be: warn event, done.warn and warn:* codes removed."""
    t = copy.deepcopy(t)
    t["events"] = [e for e in t["events"] if not (e.get("type") == "other" and e.get("kind") == "warn")]
    for e in t["events"]:
        if e.get("type") == "done":
            e.pop("warn", None); e["receipt"]["reasonCodes"] = [c for c in e["receipt"]["reasonCodes"] if not c.startswith("warn:")]
    t["route"]["reasonCodes"] = [c for c in t["route"]["reasonCodes"] if not c.startswith("warn:")]
    return t
def off_on_warn_turn(t):
    """OFF trace of a caution turn -> as ON shows it: weak_sources (non-declined) gone, the uncited preface gone."""
    t = copy.deepcopy(t)
    t["events"] = [e for e in t["events"] if not (e.get("type") == "warning" and e.get("code") == "weak_sources" and not e.get("declined"))]
    streamed = "".join(e.get("text", "") for e in t["events"] if e.get("type") == "token")
    for e in t["events"]:
        if e.get("type") == "done" and isinstance(e.get("finalText"), str) and PREF.match(e["finalText"]):
            e["finalText"] = PREF.sub("", e["finalText"])
            if e["finalText"] == streamed: e.pop("finalText")  # only the preface made the text differ from the stream
    if isinstance(t["answer"].get("text"), str): t["answer"]["text"] = PREF.sub("", t["answer"]["text"])
    # the adapter's summary of the held-back warning
    t["answer"]["warnings"] = [w for w in t["answer"].get("warnings", []) if w != "weak_sources"]
    if "weakSources" in t["answer"]: t["answer"]["weakSources"] = False
    return t
def diffkeys(a, b): return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
res = {"sets": {}, "fail": []}
for s in ["probes", "v01", "st"]:
    on, off, p1 = jl(f"{R}/warn-{s}-on.traces.jsonl"), jl(f"{R}/warn-{s}-off.traces.jsonl"), jl(f"{R}/warn-{s}-pr1.traces.jsonl")
    assert on.keys() == off.keys() == p1.keys(), s
    off_ne = [i for i in off if norm(off[i]) != norm(p1[i])]
    off_has_warn = [i for i in off if warn_of(off[i]) or any(e.get("kind") == "warn" for e in off[i]["events"]) or any(c.startswith("warn:") for c in off[i]["route"]["reasonCodes"])]
    tiers = {i: warn_of(on[i]) for i in on}
    bad_on = []
    for i in on:
        a = norm(strip_warn(on[i])); b = norm(off_on_warn_turn(off[i]) if tiers[i] else off[i])
        if a != b: bad_on.append((i, diffkeys(a, b)))
    # stream-start tier = done tier on the stub (no cites: beyond never moves to sourced)
    start = {i: next((e["tier"] for e in on[i]["events"] if e.get("kind") == "warn"), None) for i in on}
    start_ne_done = [i for i in on if start[i] != tiers[i]]
    held = [i for i in on if tiers[i] and any(e.get("type") == "warning" and e.get("code") == "weak_sources" and not e.get("declined") for e in off[i]["events"])]
    if s == "st":
        exp = {r["id"]: r["tier"] for r in W if r["model"] == "4B-replay" and r["set"] == "st180"}
        got = {i: t for i, t in tiers.items() if i.startswith(PUB)}
    else:
        model, st_ = ("4B", "probes64") if s == "probes" else ("4B", "v01")
        exp = {r["id"]: (None if not r["tier"] else "no-source" if r["tier"] == "no-source" else "beyond-source") for r in W if r["model"] == model and r["set"] == st_}
        got = tiers
    mism = sorted(i for i in exp if exp[i] != got.get(i))
    cnt = lambda d: {"warn": sum(1 for v in d.values() if v), **{k: sum(1 for v in d.values() if v == k) for k in ("no-source", "beyond-source", "sourced")}}
    res["sets"][s] = {"n": len(on), "off_eq_pr1": len(on) - len(off_ne), "off_ne_pr1": off_ne, "off_has_warn": off_has_warn, "on_eq_off_outside_warn": len(on) - len(bad_on), "on_bad": bad_on,
                      "warn_ids": sorted(i for i, t in got.items() if t), "got": cnt(got), "expected": cnt(exp), "n_compared": len(exp), "mismatch": mism,
                      "start_ne_done": start_ne_done, "weak_sources_held_back": held}
    res["fail"] += [f"{s}:off!=pr1:{i}" for i in off_ne] + [f"{s}:off-has-warn:{i}" for i in off_has_warn] + [f"{s}:on-diff:{i}:{k}" for i, k in bad_on] + [f"{s}:tier:{i}" for i in mism] + [f"{s}:start!=done:{i}" for i in start_ne_done]
res["verdict"] = "PASS" if not res["fail"] else "FAIL"
json.dump(res, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
for k, v in res["sets"].items(): print(k, {x: v[x] for x in ("n", "off_eq_pr1", "on_eq_off_outside_warn", "n_compared", "got", "expected", "mismatch", "weak_sources_held_back")}, "ids:", v["warn_ids"] if len(v["warn_ids"]) < 8 else len(v["warn_ids"]))
print("fail:", res["fail"][:20], "verdict:", res["verdict"])
