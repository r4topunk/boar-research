"""HEALTHDROP step-0 replay requests (criterion HEALTHDROP-criterion.md 63bfa747...). Items, kit, seed, settings unchanged; commit/arm
relabelled per tree. Gate sets: 9 x 20 self-tests (packs/selftest-runs S requests, kit + item pack), v0.1 60 and probes 64 (healthgap r2
replay requests, claim kit). Stress: v0.1 60 and probes 64 with the 3 health packs added to the kit (suffix -hk).
Usage: python3 -I mkreq_hd.py <out dir>"""
import json, sys
A = "<workspace>/rnd/research/coordinator/arms"; out = sys.argv[1]
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
ARMS = {"arm": "pr1+warn+healthdrop", "base": "pr1+warn"}
sets = {}
for p in PACKS:
    sets[f"st-{p}"] = [json.loads(l) for l in open(f"{A}/packs/selftest-runs/st-{p}-cut7-s42.requests.jsonl") if l.strip()]
    assert len(sets[f"st-{p}"]) == 20
hk = []
for p in ["boar-firstaid-en", "boar-medlineplus-en", "qa-health-se"]:
    k = [x for x in sets[f"st-{p}"][0]["config"]["kit"] if x["id"] == p]; assert len(k) == 1; hk += k
for s in ["v01", "probes"]:
    rows = [json.loads(l) for l in open(f"{A}/healthgap/runs/r2/hg2-replay-{s}.requests.jsonl") if l.strip()]
    sets[s] = rows
    sets[f"{s}-hk"] = [json.loads(json.dumps(r)) for r in rows]
    for r in sets[f"{s}-hk"]: r["config"]["kit"] = r["config"]["kit"] + hk
for name, rows in sets.items():
    for tag, arm in ARMS.items():
        with open(f"{out}/hd-{name}.{tag}.requests.jsonl", "w") as o:
            for r in rows:
                r = json.loads(json.dumps(r)); r["runId"] = f"hd-{name}"; r["config"]["commit"] = "8ac9eb7a"; r["config"]["arm"] = arm
                o.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(name, len(rows), [k["id"] for k in rows[0]["config"]["kit"]] if name.endswith("hk") or name.startswith("st-") and name == "st-qa-health-se" else "")
