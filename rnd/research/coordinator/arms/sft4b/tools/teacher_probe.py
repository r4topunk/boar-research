"""SFT4B TEACHER-PROBE (measurement only; no criterion change). Can the deep tier (Qwen3.6-35B-A3B + thinking, the product's
deep-tier sampler) write targets that pass the frozen v3 jev bars (addendum 2), where Haiku passed 38.3 %?
  sample : seed 42, 100 gold-present (train split, jev-checked; ~half Haiku-failed / half Haiku-passed, stratified by pack)
           + 20 gold-absent (<= 2 per pack) v3 contexts -> data/teacher-probe.contexts.jsonl (rendered messages, ids, Haiku verdict)
  score  : jev (v3_filter.state_of + Q_PRESENT/Q_ABSENT + TH, cache runs/jev-cache, spend runs/jev-spend.jsonl, probe cap [usage detail removed])
           on the deep answers (runs/teacher-probe/deep.jsonl, from tools/mini/teacher_probe.sh) -> aggregates/teacher-probe.json
Haiku verdicts come from the v3 cache only (0 new calls). Usage: python3 -I teacher_probe.py sample|score"""
import glob, hashlib, json, os, random, re, statistics as S, sys, time, urllib.request
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zstd_shim  # noqa: E402,F401
import filter_jev as F  # noqa: E402
import v3_filter as V  # noqa: E402
from v3_write import NOSRC  # noqa: E402

ARM = F.ARM; OUT = f"{ARM}/data/teacher-probe.contexts.jsonl"; DEEP = f"{ARM}/runs/teacher-probe/deep.jsonl"
PROBE_CAP = 0.02
SE = lambda p: p.startswith("qa-")


def cached(state, qs):
    body = json.dumps({"model": "typesafe-ai/jev", "state": state, "questions": qs}, sort_keys=True)
    f = f"{F.CACHE}/{hashlib.sha256(body.encode()).hexdigest()}.json"
    return json.load(open(f)) if os.path.exists(f) else None


def verdict(c, rec):
    a = dict(rec["answers"]); a["no_distractor_attribution"] = round(1 - a.pop("distractor_fact"), 4)
    bad = [k for k, t in V.TH[c["mode"]].items() if a[k] < t]
    return a, bad


def haiku(r):
    """Haiku's v3 round-1 outcome for a raw record: (status, jev, failed checks). status in pass/fail/prejev_drop/uncached."""
    a = r["answer"]; cites = {int(x) for x in re.findall(r"\[(\d+)\]", a)}; n = len(a.split())
    if r["mode"] == "present" and (not cites or not cites <= set(r["gold_pos"])): return "prejev_drop", None, ["citation"]
    if r["mode"] == "absent" and (r["covered"] or cites or not a.startswith(NOSRC)): return "prejev_drop", None, ["format"]
    if n < 40 or n > 60: return "prejev_drop", None, ["length"]
    st, qs = V.state_of(r); rec = cached(st, qs)
    if rec is None: return "uncached", None, []
    j, bad = verdict(r, rec)
    return ("fail" if bad else "pass"), j, bad


def sample():
    raws = [json.loads(l) for l in open(f"{ARM}/data/raw-v3-train-r1.jsonl") if l.strip()]
    for r in raws: r["h_status"], r["h_jev"], r["h_bad"] = haiku(r)
    print("haiku status (train r1):", Counter((r["mode"], r["h_status"]) for r in raws))
    rng = random.Random(42)
    packs = sorted({r["pack"] for r in raws})
    pres = defaultdict(lambda: defaultdict(list)); absn = defaultdict(list)
    for r in raws:
        if r["mode"] == "present" and r["h_status"] in ("pass", "fail"): pres[r["pack"]][r["h_status"]].append(r)
        if r["mode"] == "absent" and r["h_status"] in ("pass", "fail"): absn[r["pack"]].append(r)
    for d in list(pres.values()) + [absn]:
        for v in d.values(): v.sort(key=lambda r: r["xid"]); rng.shuffle(v)
    # 100 present: 9 per pack (+1 for one pack), split fail/pass alternately 5/4 and 4/5 -> 50/50 overall
    order = packs[:]; rng.shuffle(order)
    plan = {p: 9 for p in packs}; plan[order[0]] += 1
    nfail = {}
    tf = 0
    for i, p in enumerate(order):
        nfail[p] = plan[p] // 2 + (plan[p] % 2 if i % 2 == 0 else 0)
    # rebalance to exactly 50 fails
    diff = 50 - sum(nfail.values()); i = 0
    while diff:
        p = order[i % len(order)]; step = 1 if diff > 0 else -1; nfail[p] += step; diff -= step; i += 1
    sel, notes = [], {}
    for p in packs:
        f_, p_ = pres[p]["fail"], pres[p]["pass"]
        k_f = min(nfail[p], len(f_)); k_p = min(plan[p] - k_f, len(p_)); k_f = min(len(f_), plan[p] - k_p)
        notes[p] = {"fail": k_f, "pass": k_p, "avail_fail": len(f_), "avail_pass": len(p_)}
        sel += [(r, "haiku_failed") for r in f_[:k_f]] + [(r, "haiku_passed") for r in p_[:k_p]]
    used = {r["cid"] for r, _ in sel}
    aplan = {p: 2 for p in packs}
    for p in order[-2:]: aplan[p] = 1  # 9x2 + 2x1 = 20
    for p in packs:
        cand = [r for r in absn[p] if r["cid"] not in used] or absn[p]
        sel += [(r, "absent") for r in cand[:aplan[p]]]
    with open(OUT, "w") as f:
        for r, stratum in sel:
            f.write(json.dumps({"xid": r["xid"], "cid": r["cid"], "pack": r["pack"], "mode": r["mode"], "gold": r["mode"] == "present",
                                "stratum": stratum, "question": r["question"], "messages": r["messages"], "passages": r["passages"],
                                "kept": r["kept"], "gold_chunk_ids": r["gold_chunk_ids"], "distractor_chunk_ids": r["distractor_chunk_ids"],
                                "gold_pos": r["gold_pos"], "haiku_answer": r["answer"], "haiku_covered": r["covered"],
                                "haiku_status": r["h_status"], "haiku_jev": r["h_jev"], "haiku_failed_checks": r["h_bad"]}) + "\n")
    print(json.dumps({"n": len(sel), "strata": Counter(s for _, s in sel), "per_pack": notes}, indent=0))


def jev_live(state, qs, spent):
    rec = cached(state, qs)
    if rec is not None: return rec, 0.0
    if spent + 0.0005 > PROBE_CAP: raise RuntimeError("PROBE CAP")
    body = json.dumps({"model": "typesafe-ai/jev", "state": state, "questions": qs}, sort_keys=True)
    h = hashlib.sha256(body.encode()).hexdigest()
    for att in range(6):
        try:
            req = urllib.request.Request("https://ai-gateway.vercel.sh/v1/evaluate", data=body.encode(),
                                         headers={"authorization": f"Bearer {F.KEY}", "content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=60)); break
        except Exception:
            if att == 5: raise
            time.sleep(min(8, 2 ** att))
    ans = {k: r["answers"][k]["probability"] for k in qs}
    cost = float(((r.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
    rec = {"answers": ans, "inputTokens": (r.get("usage") or {}).get("inputTokens"), "cost": cost}
    json.dump(rec, open(f"{F.CACHE}/{h}.json", "w"))
    with open(F.SPEND, "a") as fh: fh.write(json.dumps({"at": time.strftime("%FT%T"), "hash": h[:16], "cost": cost, "tok": rec["inputTokens"], "arm": "teacher-probe"}) + "\n")
    return rec, cost


def med(xs): xs = list(xs); return S.median(xs) if xs else None


def pct(xs, q): xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None


def score():
    ctx = {json.loads(l)["xid"]: json.loads(l) for l in open(OUT)}
    deep = {}
    for l in open(DEEP):
        d = json.loads(l); deep[d["xid"]] = d
    spent = sum(json.loads(l)["cost"] for l in open(F.SPEND) if json.loads(l).get("arm") == "teacher-probe"); calls, rows = 0, []
    for xid, c in ctx.items():
        d = deep.get(xid)
        if d is None: continue
        ans = re.sub(r"<think>.*?</think>", "", d.get("content") or "", flags=re.S).strip()
        cites = sorted({int(x) for x in re.findall(r"\[(\d+)\]", ans)})
        shown = len(c["kept"])
        row = {"xid": xid, "pack": c["pack"], "mode": c["mode"], "stratum": c["stratum"], "haiku_status": c["haiku_status"],
               "answer": ans, "words": len(ans.split()), "cites": cites, "n_cites": len(cites),
               "cites_distractor": bool(set(cites) - set(c["gold_pos"])), "cites_unshown": any(i > shown or i < 1 for i in cites),
               "finished": bool(ans) and d.get("finish_reason") == "stop", "wall": d.get("wall"), "reasoning_tokens": d.get("reasoning_tokens"),
               "completion_tokens": d.get("completion_tokens")}
        if not ans:
            row.update(jev=None, failed=["no_answer"], passed=False, format_fail=["no_answer"], strict_pass=False); rows.append(row); continue
        r = {**c, "answer": ans}
        if c["mode"] == "present":
            blocks = V.split_passages(c["passages"])
            cites_ok = [i for i in cites if i in blocks]
            st = {"question": c["question"], "answer": ans, "cited_passages": "\n\n".join(blocks[i] for i in cites_ok),
                  "uncited_passages": "\n\n".join(b for i, b in blocks.items() if i not in cites_ok)}
            qs = V.Q_PRESENT
        else:
            st, qs = V.state_of(r)
        rec, cost = jev_live(st, qs, spent); spent += cost; calls += cost > 0
        a, bad = verdict(r, rec)
        if not row["finished"]: bad = ["truncated"] + bad
        row.update(jev=a, failed=bad, passed=not bad)
        # strict = also the v3 target-format pre-checks (40-60 words; present: cites only gold; absent: no citation)
        fmt = []
        if not 40 <= row["words"] <= 60: fmt.append("length")
        if c["mode"] == "present" and (not cites or row["cites_distractor"]): fmt.append("citation")
        if c["mode"] == "absent" and cites: fmt.append("cites_in_absent")
        row["format_fail"] = fmt; row["strict_pass"] = row["passed"] and not fmt
        rows.append(row)
    with open(f"{ARM}/runs/teacher-probe/scored.jsonl", "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")

    def rate(sub, key="passed"):
        return [sum(r[key] for r in sub), len(sub), round(sum(r[key] for r in sub) / max(1, len(sub)), 3)]

    def hrate(sub):  # Haiku on the same items (present: jev-checked by construction; absent: jev-checked)
        return [sum(ctx[r["xid"]]["haiku_status"] == "pass" for r in sub), len(sub), round(sum(ctx[r["xid"]]["haiku_status"] == "pass" for r in sub) / max(1, len(sub)), 3)]
    groups = {"overall": rows, "present": [r for r in rows if r["mode"] == "present"], "absent": [r for r in rows if r["mode"] == "absent"],
              "SE": [r for r in rows if SE(r["pack"])], "topic": [r for r in rows if not SE(r["pack"])],
              "SE_present": [r for r in rows if SE(r["pack"]) and r["mode"] == "present"],
              "haiku_failed": [r for r in rows if r["stratum"] == "haiku_failed"], "haiku_passed": [r for r in rows if r["stratum"] == "haiku_passed"]}
    pres = groups["present"]
    haiku_drops = Counter(k for r in rows for k in (ctx[r["xid"]]["haiku_failed_checks"] or []))
    agg = {"n_items": len(ctx), "n_deep": len(rows),
           "pass_jev": {g: rate(v) for g, v in groups.items()}, "pass_strict": {g: rate(v, "strict_pass") for g, v in groups.items() if v and "strict_pass" in v[0]},
           "haiku_pass_same_items": {g: hrate(v) for g, v in groups.items()},
           "per_pack_jev": {p: rate([r for r in rows if r["pack"] == p]) for p in sorted({r["pack"] for r in rows})},
           "deep_failed_checks": {m: dict(Counter(k for r in rows if r["mode"] == m for k in r["failed"])) for m in ("present", "absent")},
           "haiku_failed_checks": {m: dict(Counter(k for r in rows if r["mode"] == m for k in (ctx[r["xid"]]["haiku_failed_checks"] or []))) for m in ("present", "absent")},
           "format_fail": dict(Counter(k for r in rows for k in r.get("format_fail", []))),
           "words": {m: {"median": med([r["words"] for r in rows if r["mode"] == m]), "p10": pct([r["words"] for r in rows if r["mode"] == m], .1),
                         "p90": pct([r["words"] for r in rows if r["mode"] == m], .9)} for m in ("present", "absent")},
           "haiku_words_median": med(len(ctx[r["xid"]]["haiku_answer"].split()) for r in rows),
           "n_cites_present": dict(sorted(Counter(r["n_cites"] for r in pres).items())), "n_cites_absent": dict(sorted(Counter(r["n_cites"] for r in groups["absent"]).items())),
           "present_cites_distractor": sum(r["cites_distractor"] for r in pres), "present_multi_cite": sum(r["n_cites"] > 1 for r in pres),
           "present_two_gold": sum(len(ctx[r["xid"]]["gold_pos"]) == 2 for r in pres),
           "unfinished": sum(not r["finished"] for r in rows), "cites_unshown": sum(r["cites_unshown"] for r in rows),
           "wall_s": {"median": med([r["wall"] for r in rows]), "p10": pct([r["wall"] for r in rows], .1), "p90": pct([r["wall"] for r in rows], .9), "sum": sum(r["wall"] for r in rows)},
           "reasoning_tokens": {"median": med([r["reasoning_tokens"] or 0 for r in rows]), "p90": pct([r["reasoning_tokens"] or 0 for r in rows], .9)},
           "jev_new_calls_this_run": calls, "jev_probe_calls_total": sum(json.loads(l).get("arm") == "teacher-probe" for l in open(F.SPEND)), "jev_spend_usd": round(sum(json.loads(l)["cost"] for l in open(F.SPEND) if json.loads(l).get("arm") == "teacher-probe"), 5), "jev_arm_total_usd": round(F.spent_total(), 5)}
    agg["projected_full_run_h_1600"] = round((agg["wall_s"]["median"] or 0) * 1600 / 3600, 1)
    agg["projected_full_run_h_1600_mean"] = round(agg["wall_s"]["sum"] / len(rows) * 1600 / 3600, 1)
    json.dump(agg, open(f"{ARM}/aggregates/teacher-probe.json", "w"), indent=1)
    print(json.dumps(agg, indent=1))


if __name__ == "__main__":
    {"sample": sample, "score": score}[sys.argv[1]]()
