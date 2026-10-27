# TOPICS27 aggregation + frozen verdict rule (0 LLM).
import json
P = json.load(open("judge/prep.json")); A = {json.loads(l)["key"]: json.loads(l) for l in open("judge/audit.jsonl")}
T = {o["key"]: o for o in json.load(open("aggregates/titles.json"))}
RP = {json.loads(l)["id"]: json.loads(l) for l in open("replay/t27.replay.jsonl")}
U = P["units"]; rows = []
for it in P["items"]:
    k = it["key"]; t = T[k]; anchors = {x.lower() for g in t["groups"] for x in g}
    inraw = any(x.lower() in anchors for x in it["raw"]); inkept = any(x.lower() in anchors for x in it["kept"])
    rp_kept = [x.lower() for x in RP[k]["sources"]]; parity = rp_kept == [x.lower() for x in it["kept"]]
    us = [A[u["key"]] for u in U if u["topic"] == k]
    n = len(us); uns = sum(1 for a in us if a["label"] == "UNSUPPORTED"); par = sum(1 for a in us if a["label"] == "PARTIAL")
    inv = sum(1 for a in us if a["label"] in ("UNSUPPORTED", "PARTIAL") and a["invented_specific"])
    share = uns / n if n else 1.0
    if not t["present"] or (share >= 1/3 and inv >= 1) or n == 0 or it["declined"]: v = "SWAP"
    elif not inkept: v = "FIX-PACK"
    else: v = "KEEP"
    watch = v == "KEEP" and ((share >= 1/3 and inv == 0) or (inv >= 1 and share < 1/3))
    titles_present = sum(1 for x, y in t["titles"].items() if y["vital5_chunks"] or y["corpus"]); titles_n = len(t["titles"])
    rows.append(dict(key=k, area=it["area"], present=t["present"], titles=f"{titles_present}/{titles_n}", in_raw=inraw, in_kept=inkept, replay_kept_parity=parity,
        kept=it["kept"], banner=bool(it["banner"]), sentences=n, unsupported=uns, partial=par, invented=inv, unsup_share=round(share, 3),
        num_absent=sum(it["num_absent"]), batched=any(a["mode"] == "batched" for a in us), words=it["words"], verdict=v, watch=watch))
json.dump(rows, open("aggregates/topics27.json", "w"), indent=1)
S = sum(r["sentences"] for r in rows); X = sum(r["unsupported"] for r in rows)
agg = dict(present=sum(r["present"] for r in rows), in_raw=sum(r["in_raw"] for r in rows), in_kept=sum(r["in_kept"] for r in rows),
  parity=sum(r["replay_kept_parity"] for r in rows), sentences=S, unsupported=X, unsup_share=round(X / S, 3), partial=sum(r["partial"] for r in rows),
  invented=sum(r["invented"] for r in rows), banner=sum(r["banner"] for r in rows),
  verdicts={v: [r["key"] for r in rows if r["verdict"] == v] for v in ("KEEP", "FIX-PACK", "SWAP")}, watch=[r["key"] for r in rows if r["watch"]],
  q_expect_titles=f"{sum(int(r['titles'].split('/')[0]) for r in rows if r['key'][0]=='q')}/{sum(int(r['titles'].split('/')[1]) for r in rows if r['key'][0]=='q')}")
json.dump(agg, open("aggregates/summary.json", "w"), indent=1); print(json.dumps(agg))
for r in rows: print(r["key"], r["present"], r["titles"], r["in_raw"], r["in_kept"], r["replay_kept_parity"], r["banner"], r["sentences"], r["unsupported"], r["partial"], r["invented"], r["num_absent"], r["batched"], r["verdict"], "watch" if r["watch"] else "")
