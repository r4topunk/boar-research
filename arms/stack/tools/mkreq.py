"""STACK request files (criterion sha 56ed7ccf…). Run: python3 -I mkreq.py
- 180: CROWDQ's all-9 requests (arms/crowdq/runs/st-<pack>-cut7-all9-s42.requests.jsonl), config.arm = "cut7-stack",
  config.settings += {packGround: "perpack", packRoute: "quota"}, runId st-<pack>-cut7-stack-s42 -> runs/<runId>.requests.jsonl
- v0.1 public 60 (stage 1b): the same claim config with the kit only (first 2 kit entries = boar-crypto, boar-wikivoyage-en),
  OFF (settings as CROWDQ) and ON (+ stack settings), runIds v01-cut7-stack-off-s42 / v01-cut7-stack-on-s42."""
import json, copy
ROOT = "$BOAR_WS"; A = f"{ROOT}/rnd/research/coordinator/arms"; O = f"{A}/stack/runs"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
STACK = {"packGround": "perpack", "packRoute": "quota"}
def write(path, rows):
    with open(path, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
base = None
for p in PACKS:
    src = [json.loads(l) for l in open(f"{A}/crowdq/runs/st-{p}-cut7-all9-s42.requests.jsonl") if l.strip()]
    assert len(src) == 20 and len(src[0]["config"]["kit"]) == 11, p
    base = base or src[0]
    out = []
    for r in src:
        r = copy.deepcopy(r); r["runId"] = f"st-{p}-cut7-stack-s42"; r["config"]["arm"] = "cut7-stack"
        r["config"]["settings"] = {**r["config"]["settings"], **STACK}; out.append(r)
    write(f"{O}/st-{p}-cut7-stack-s42.requests.jsonl", out)
cfg = copy.deepcopy(base["config"]); cfg["arm"] = "cut7-stack"; cfg["kit"] = cfg["kit"][:2]
assert [k["id"] for k in cfg["kit"]] == ["boar-crypto", "boar-wikivoyage-en"]
items = [json.loads(l) for l in open(f"{ROOT}/boar-eval/bench/v0.1/questions.public.jsonl") if l.strip()]
for tag, extra in (("off", {}), ("on", STACK)):
    c = copy.deepcopy(cfg); c["settings"] = {**c["settings"], **extra}
    rows = [{"protocol": base["protocol"], "runId": f"v01-cut7-stack-{tag}-s42",
             "item": {"id": it["id"], "question": it["question"], "lang": it.get("lang", "en"), **({"history": it["history"]} if it.get("history") else {})},
             "config": c, "seed": base["seed"]} for it in items]
    write(f"{O}/v01-cut7-stack-{tag}-s42.requests.jsonl", rows)
print("ok", len(PACKS) * 20, len(items), base["seed"])
