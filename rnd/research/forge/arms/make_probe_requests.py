# Requests for the probe legs of the phone session (forge/PHONE-SESSION.md), from frozen inputs:
#   gate-<leg>-items1-5 / gate-<leg>-items6-10: Anvil's ABAB block design (relay 2026-10-03): each block = 1 unmeasured
#     warm-up (spare cs-010, id "cs-010-warmup") + 5 measured items of anvil/specs/probe-gate-items.json, in file order.
#     The same request serves the gate-ON (A) and gate-OFF (B) block: ON/OFF is the Metro edit, the tag says which.
#     <leg> = A (1.5B) or B (4B). Multi-turn items carry history (forge-eval-history.patch).
#   gate-<leg>-spare: cs-054, for an item that showed no [gate] line (smallTalk answered first).
#   probeb-4b10: Probe B's 10 answers = the first 10 questions of the P3a request (and-qwen3-4b-quick-p3speed).
# Usage: python3 make_probe_requests.py   (writes requests/*.request.json, prints sha256 prefixes)
import hashlib, json, pathlib
R = pathlib.Path("<workspace>")
gate = json.loads((R / "rnd/research/anvil/specs/probe-gate-items.json").read_text())
slice_v0 = {j["id"]: j for j in map(json.loads, (R / "rnd/research/anvil/exp/chat-routing/slice.items.jsonl").read_text().splitlines()) if j}
p3 = json.loads((R / "boar-eval/devices/requests/and-qwen3-4b-quick-p3speed.request.json").read_text())
Q15, Q4B = "qwen2.5-1.5b-instruct-q4km", "qwen3-4b-instruct-2507-q4km"
OFF = {"nativeZstd": False, "vectorCache": False, "sqlBatch": False}

def text_of(it):  # spares may be ids or objects without "msg": take the text from chat-slice v0
    i = it if isinstance(it, str) else it["id"]
    src = it if isinstance(it, dict) and "msg" in it else slice_v0[i]
    return i, src["msg"], src.get("history")

def q(it, suffix=""):
    i, msg, hist = text_of(it)
    d = {"id": i + suffix, "query": msg, "category": "chat"}
    if hist:  # [[role, text], ...]
        d["history"] = hist
    return d

spares = {text_of(s)[0]: s for s in gate["spares"]}
warm = q(spares["cs-010"], "-warmup")
items = gate["items"]
assert len(items) == 10

def req(rid, model, qs):
    return {"requestId": rid, "pipeline": "answer", "models": [model], "evalSetVersion": "chat-slice-v0-gate-probe-b5",
            "questions": qs, "confirmLargeModels": model == Q4B, "perf": OFF}

out = {}
for leg, model in (("A", Q15), ("B", Q4B)):
    out[f"gate-{leg}-items1-5"] = req(f"fg-gate-{leg.lower()}1", model, [warm] + [q(i) for i in items[:5]])
    out[f"gate-{leg}-items6-10"] = req(f"fg-gate-{leg.lower()}2", model, [warm] + [q(i) for i in items[5:]])
    out[f"gate-{leg}-spare"] = req(f"fg-gate-{leg.lower()}s", model, [q(spares["cs-054"])])
out["probeb-4b10"] = {**{k: v for k, v in p3.items() if k != "install"}, "requestId": "fg-probeb-4b10", "questions": p3["questions"][:10], "perf": OFF}
d = pathlib.Path(__file__).parent / "requests"
for name, r in out.items():
    p = d / f"{name}.request.json"
    p.write_text(json.dumps(r, ensure_ascii=False) + "\n")
    print(hashlib.sha256(p.read_bytes()).hexdigest()[:16], p.name, r["models"][0], [x["id"] for x in r["questions"]] if len(r["questions"]) < 8 else f"{len(r['questions'])} items")
