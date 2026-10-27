#!/usr/bin/env python3
"""SMALLCLS scorer (criterion 132fa1f0). python3 -I score.py"""
import json, os, re
H = os.path.dirname(os.path.abspath(__file__)); B = "<workspace>"
MAP = {"drinking water": "Water (Ready.gov)", "earthquake": "Earthquakes (Ready.gov)", "evacuation": "Evacuation (Ready.gov)", "extreme heat": "Extreme Heat (Ready.gov)",
       "flood": "Floods (Ready.gov)", "gas leak": "Safety Skills (Ready.gov)", "hazardous materials chemical": "Chemicals and Hazardous Materials Incidents (Ready.gov)",
       "home fire": "Home Fires (Ready.gov)", "household chemical emergency": "Household Chemical Emergencies (Ready.gov)", "hurricane": "Hurricanes (Ready.gov)",
       "power outage": "Power Outages (Ready.gov)", "radiation emergency": "Radiation Emergencies (Ready.gov)", "tornado": "Tornadoes (Ready.gov)", "tsunami": "Tsunamis (Ready.gov)",
       "wildfire": "Wildfires (Ready.gov)", "winter weather": "Winter Weather (Ready.gov)"}
tasks = [json.loads(l) for l in open(f"{H}/tasks.jsonl")]
hand = {x["id"]: MAP.get(x["term"], "none") if x["term"] else "none" for f in ("hand-s30.json", "hand-f.json") for x in json.load(open(f"{H}/{f}"))}
# engine's section choice on S30 = the heading the E' extract quoted
ep = {json.loads(l)["itemId"]: json.loads(l)["answer"]["text"] for l in open(f"{B}/rnd/research/coordinator/arms/safepack/gen/safepack-cut7-x2-saferoute-s42.traces.jsonl")}
def eng_sec(t, opts):
    m = re.match(r"From the offline source:\s*(.+?)(?: >|:)", ep.get(t["id"], ""))
    return next((o for o in opts if m and o.lower() == m.group(1).strip().lower()), None)
def stats(pred, rows):
    a = [r for r in rows if r["task"] == "A"]; b = [r for r in rows if r["task"] == "B"]
    out = {}
    for s in ("S30", "F"):
        aa = [r for r in a if r["set"] == s]; bb = [r for r in b if r["set"] == s]
        if aa:
            em = [r for r in aa if r["gold"] != "none"]; ng = [r for r in aa if r["gold"] == "none"]
            p = lambda r: pred(r)
            out[s] = dict(A_acc=f"{sum(p(r) == r['gold'] for r in aa)}/{len(aa)}", A_recall=f"{sum(p(r) not in (None, 'none') for r in em)}/{len(em)}",
                          A_false_alarm=f"{sum(p(r) not in (None, 'none') for r in ng)}/{len(ng)}" if ng else "n/a",
                          B_acc=(f"{sum(p(r) == r['gold'] for r in bb)}/{len(bb)}" if bb else "n/a"))
    return out
print("HAND rules:", stats(lambda r: hand[r["id"]] if r["task"] == "A" else (eng_sec(r, r["options"]) if r["set"] == "S30" else None), tasks))
for tag in ("Q17", "M4"):
    p = f"{H}/out-{tag}.jsonl"
    if not os.path.exists(p): continue
    o = {json.loads(l)["key"]: json.loads(l) for l in open(p)}
    ms = sorted(x["ms"] for x in o.values()); print(f"{tag}: n={len(o)} p50 {ms[len(ms)//2] if ms else 0} ms", stats(lambda r: o.get(r["key"], {}).get("pred"), [r for r in tasks if r["key"] in o]))
