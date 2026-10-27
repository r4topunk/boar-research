#!/usr/bin/env python3
"""DEVICE-DAY 2026-10-22: build every id file and request file for r4to's phone session. 0 LLM, phone untouched.
Usage: python3 -I device_day_requests.py            (writes; prints a manifest with sha256 per file)
Inputs: ruler/ids/{divergent,sentinels,deterministic}-v01.ids, the q4ba73-a bench request (question text, v0.1 dev ids),
two dev probe questions defined below (not v0.4 text). Outputs:
  ruler/ids/dd1022-*.ids (+ .sha256)
  handoff/pixel8-2026-10-20/bench/requests/rc-*.request.json   native-app (maintainer RC) format: pipeline "legacy" + own questions
  handoff/pixel8-2026-10-20/bench/requests/dd-*.request.json   BOAR Bench format (pipeline "answer"), optional controls
  bench-app/requests/dd-*.request.json                         same BOAR Bench files (identical bytes)
  arms/device-day-1022/aunion10-expected.json                  expected kept pack per AUNION10 id (desktop PK-4 replay)
Rules: deterministic-v01 ids are skipped except the 4 LAYER10 layer ids (that run tests the layers themselves);
the warm-up is first only in speed runs; every run is <= 10 questions."""
import hashlib, json, os, sys
B = "<workspace>"; C = B + "/rnd/research/coordinator"; IDS = C + "/ruler/ids/"
HB = B + "/handoff/pixel8-2026-10-20/bench/requests/"; BA = B + "/bench-app/requests/"; DD = C + "/arms/device-day-1022/"
rd = lambda f: open(IDS + f).read().split()
DET, DIV, SEN = rd("deterministic-v01.ids"), rd("divergent-v01.ids"), rd("sentinels-v01.ids")
base = json.load(open(HB + "q4ba73-a.request.json"))
Q = {q["id"]: q for q in base["questions"]}
EXTRA = {  # dev probes written for this session (not v0.4 text, not claim items)
    "epi-1021": {"id": "epi-1021", "query": "If they have an epinephrine pen, where do I inject it?", "category": "danger-situation"},  # GEMMA-SAFETY / DRIFT17 probe, verbatim
    "geo-dev-1022": {"id": "geo-dev-1022", "query": "Where can I find vegetarian food near me right now?", "category": "local-food"},
}
Q.update(EXTRA)
M4, M17, MG = "qwen3-4b-instruct-2507-q4km", "qwen3-1.7b", "gemma-4-e2b"  # native selectors: exact id, else id/label substring (DeviceEval.matchModels)

# --- id sets (fixed by rule; see DEVICE-DAY-2026-10-22.md for the why) ---
SPEED9 = ["lan-rsn-004", "lan-cmp-005", "lan-rsn-006", "lan-rsn-005", "lan-cmp-002", "lan-cmp-004", "lan-hlt-003", "lan-exp-003", "lan-exp-005"]
#   = generating on both bench 4B (q4ba73-a) and 1.7B (q17b73-a), 1.7B not declined; divergent-v01 + sentinels-v01 order; reserves lan-ref-002, lan-exp-004
LAYER5 = ["trv-002", "vit-sci-003", "saf-004", "vit-hlt-002", "epi-1021"]  # port rows 1 facts r9, 4 arithmetic, 6 card, 11 health path, 13 epinephrine
LAYER10 = LAYER5 + DIV[:4] + ["geo-dev-1022"]                               # + 4 top-D divergent + current-city probe
T1A, T1B = DIV[:10], DIV[10:20]                                               # T1-20 = divergent-v01 (all reach a model on the phone)
AUNION10 = ["lan-cmp-005", "trv-004", "vit-cry-001", "lan-hlt-003", "lan-exp-003", "lan-exp-007", "lan-hlt-002", "vit-hum-004", "vit-hum-001", "lan-rsn-004"]
PRESS = [SPEED9[0:3], SPEED9[3:6], SPEED9[6:9]]

assert not set(SPEED9) & set(DET) and not set(T1A + T1B) & set(DET) and not set(AUNION10) & set(DET)
assert set(LAYER5[:4]) <= set(DET) and set(SPEED9) <= set(DIV + SEN)
assert all(len(x) <= 10 for x in [SPEED9 + ["warmup-000"], LAYER10, T1A, T1B, AUNION10])

pk4 = json.load(open(C + "/ruler/PK4-PACK-PRUNE-2026-10-21.json"))["items"]
exp = {q: pk4[q]["kept"] for q in AUNION10}
packs = {p for k in exp.values() for p in k if p != "null"}
assert len(packs) == 6, packs

out = []
def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "w").write(text); out.append(path)
def ids(name, L):
    w(IDS + name, "\n".join(L) + "\n"); h = hashlib.sha256(open(IDS + name, "rb").read()).hexdigest(); w(IDS + name + ".sha256", f"{h}  {name}\n")
def qs(L): return [{"id": Q[i]["id"], "query": Q[i]["query"], "category": Q[i]["category"]} for i in L]
def native(rid, model, L, tag):
    r = {"requestId": rid, "pipeline": "legacy", "models": [model], "evalSetVersion": f"dd1022-{tag}", "questions": qs(L)}
    w(HB + rid + ".request.json", json.dumps(r, indent=1, ensure_ascii=False) + "\n")
def bench(rid, model, L, tag):
    r = {"requestId": rid, "pipeline": "answer", "models": [model], "answerSettings": base["answerSettings"], "evalSetVersion": f"dd1022-{tag}", "questions": qs(L)}
    t = json.dumps(r, indent=1, ensure_ascii=False) + "\n"; w(HB + rid + ".request.json", t); w(BA + rid + ".request.json", t)

ids("dd1022-speed9.ids", SPEED9); ids("dd1022-layer10.ids", LAYER10); ids("dd1022-t1a.ids", T1A); ids("dd1022-t1b.ids", T1B)
ids("dd1022-aunion10.ids", AUNION10)
for k, L in enumerate(PRESS, 1): ids(f"dd1022-press-c{k}.ids", L)

S10 = ["warmup-000"] + SPEED9
native("rc-speed9-4b", M4, S10, "speed9"); native("rc-speed9-17b", M17, S10, "speed9")
native("rc-layer10-4b", M4, LAYER10, "layer10")
native("rc-t1a-gemma", MG, T1A, "t1a"); native("rc-t1b-gemma", MG, T1B, "t1b")
native("rc-aunion10-base-17b", M17, AUNION10, "aunion10-base"); native("rc-aunion10-17b", M17, AUNION10, "aunion10")
native("rc-aunion10-base-4b", M4, AUNION10, "aunion10-base"); native("rc-aunion10-4b", M4, AUNION10, "aunion10")
for k, L in enumerate(PRESS, 1):
    native(f"rc-press-4b-c{k}", M4, L, f"press-c{k}"); native(f"rc-press-17b-c{k}", M17, L, f"press-c{k}")
bench("dd-layer10-bench4b", "qwen3-4b-instruct-2507-q4km", LAYER10, "layer10")  # optional same-day control (bench app, A-union state)
w(DD + "aunion10-expected.json", json.dumps({"source": "ruler/PK4-PACK-PRUNE-2026-10-21.json items[].kept (desktop KA replay, LITEPACKS settings; not the phone engine)",
                                            "packs": sorted(packs), "kept_by_id": exp}, indent=1) + "\n")
for p in out:
    print(hashlib.sha256(open(p, "rb").read()).hexdigest()[:16], os.path.relpath(p, B))
print(f"{len(out)} files", file=sys.stderr)
