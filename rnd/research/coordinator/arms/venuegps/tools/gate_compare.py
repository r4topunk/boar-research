"""VENUEGPS G-gate: answer text byte-identity (and route codes) of new traces vs reference traces, per id.
Prints ONLY ids, booleans and counts. Usage: python3 -I gate_compare.py <new.traces.jsonl> <ref.traces.jsonl>"""
import json, sys
new = {t["itemId"]: t for t in map(json.loads, open(sys.argv[1]))}
ref = {t["itemId"]: t for t in map(json.loads, open(sys.argv[2]))}
nt = nr = 0
for i in sorted(new):
    a, b = new[i], ref[i]
    same_text = a["answer"]["text"] == b["answer"]["text"]
    strip = lambda t: [c for c in t["route"]["reasonCodes"] if not c.startswith("detector:")]
    same_route = strip(a) == strip(b) and a["route"]["tier"] == b["route"]["tier"]
    nt += same_text; nr += same_route
    print(i, "text_identical" if same_text else "TEXT_DIFFERS", "route_identical" if same_route else "ROUTE_DIFFERS",
          "err" if a.get("error") else "")
print(f"identical text {nt}/{len(new)}; identical route (excl. detector codes) {nr}/{len(new)}")
