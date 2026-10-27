"""VENUEGPS step 2: V-para items have no location field; derive {id, lat, lon} for the 7 venue items from the gold
file's `user_location` (the point the gold venue list was drawn around). Writes blind/V-para/venue-locations.json.
Prints only ids and coordinates."""
import json
V = "<private held-out dir>"
Q = [json.loads(l) for l in open(f"{V}/items.jsonl") if l.strip()]
out = []
for q in Q:
    if q.get("grading", {}).get("type") != "venue-list":
        continue
    g = json.load(open(f"{V}/{q['grading']['gold_file']}"))
    loc = g["user_location"]
    out.append({"id": q["id"], "lat": float(loc["lat"]), "lon": float(loc["lon"])})
json.dump(out, open(f"{V}/venue-locations.json", "w"), indent=1)
for r in out:
    print(r["id"], r["lat"], r["lon"])
