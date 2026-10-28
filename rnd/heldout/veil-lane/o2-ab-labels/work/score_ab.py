#!/usr/bin/env python3
"""Score the O2 A/B (off vs on, paired by question) from the panel majority, AFTER the labels were hashed.

    python3 rnd/veil/o2-ab-labels/work/score_ab.py       # from <workspace>

Acceptance (rnd/kiln/exp-03-o2/README.md §5.4):
  A4  device 52: Δpass >= -5 pp            A5  device 52: Δcw <= -5 pp
  F   fresh in-scope items (vit-o2b-*): new false refusals <= 1 per 10 O2 hits
      O2 hit = refused with O2 on, not refused with O2 off; false = that question was pass with O2 off.
Also reported per rater (sensitivity) and with the alternative reading "<= 1 per 10 correct answers (off)".
Writes ../results.json.
"""
import collections, json, re

D = "rnd/veil/o2-ab-labels"
MAP = "rnd/plumb/data/o2-ab-blind/o2-ab.map-SEALED.json"


def score(labels, arm, qid, subset):
    by = collections.defaultdict(dict)
    for i, lab in labels.items():
        if subset(qid[i]):
            by[qid[i]][arm[i]] = lab
    qs = sorted(q for q, v in by.items() if {"off", "on"} <= v.keys())
    n = len(qs)
    pct = lambda a, c: 100 * sum(by[q][a] == c for q in qs) / n
    hits = [q for q in qs if by[q]["on"] == "refused" and by[q]["off"] != "refused"]
    false_ref = [q for q in hits if by[q]["off"] == "pass"]
    transitions = collections.Counter(f"{by[q]['off']}->{by[q]['on']}" for q in qs if by[q]["off"] != by[q]["on"])
    off_pass = sum(by[q]["off"] == "pass" for q in qs)
    r = {"n": n}
    for c in ("pass", "fail", "cw", "refused"):
        r[f"{c}_off"], r[f"{c}_on"] = round(pct("off", c), 1), round(pct("on", c), 1)
        r[f"d_{c}_pp"] = round(pct("on", c) - pct("off", c), 1)
    r.update({"o2_hits": len(hits), "new_false_refusals": len(false_ref), "false_refusal_ids": false_ref,
              "correct_refusals_from": dict(collections.Counter(by[q]["off"] for q in hits if by[q]["off"] != "pass")),
              "pass_off_count": off_pass, "transitions": dict(transitions)})
    return r


def verdict(dev, fresh):
    a4 = dev["d_pass_pp"] >= -5
    a5 = dev["d_cw_pp"] <= -5
    f = fresh["o2_hits"] == 0 or fresh["new_false_refusals"] * 10 <= fresh["o2_hits"]
    f_alt = fresh["new_false_refusals"] * 10 <= max(fresh["pass_off_count"], 1)
    return {"A4": a4, "A5": a5, "F_per10hits": f, "F_alt_per10correct": f_alt, "VALIDATED": a4 and a5 and f}


def main():
    arm = json.load(open(MAP, encoding="utf-8"))
    qid = {json.loads(l)["id"]: json.loads(l)["queryId"] for l in open("rnd/plumb/data/o2-ab-blind/o2-ab.blind.jsonl", encoding="utf-8")}
    maj = json.load(open(f"{D}/majority.json", encoding="utf-8"))["items"]
    raters = {"majority": {i: v["majority"] for i, v in maj.items()}}
    for n in ("opus-1", "opus-2", "opus-3", "jev"):
        raters[n] = {i: v["votes"][n] for i, v in maj.items()}
    dev = lambda q: not q.startswith("vit-o2b-")
    fresh = lambda q: q.startswith("vit-o2b-")
    out = {}
    for name, labels in raters.items():
        d, f, a = score(labels, arm, qid, dev), score(labels, arm, qid, fresh), score(labels, arm, qid, lambda q: True)
        out[name] = {"device52": d, "fresh30": f, "all82": a, "verdict": verdict(d, f)}
    # O2-attributable view: O2's own refusal text marks the rows where the rule fired; every other ON/OFF difference is
    # run-to-run variance (two non-deterministic runs). Effect = ON label where O2 fired, OFF label elsewhere.
    o2re = re.compile(r"^(The passages found are about .+, not .+|Os trechos encontrados falam de .+, não de .+)", re.S)
    text = {json.loads(l)["id"]: " ".join(json.loads(l)["answer"].split()) for l in open("rnd/plumb/data/o2-ab-blind/o2-ab.blind.jsonl", encoding="utf-8")}
    plumb = {k: v[0] for k, v in json.load(open("rnd/plumb/data/hand-labels-o2ab-blind.json", encoding="utf-8")).items() if k.startswith("o-")}
    def attributable(labels, subset):
        by = collections.defaultdict(dict)
        for i, lab in labels.items():
            if subset(qid[i]): by[qid[i]][arm[i]] = (lab, bool(o2re.match(text[i])))
        qs = sorted(by); n = len(qs)
        eff = lambda c: round(100 * (sum((by[q]["on"][0] if by[q]["on"][1] else by[q]["off"][0]) == c for q in qs) - sum(by[q]["off"][0] == c for q in qs)) / n, 1)
        hits = [q for q in qs if by[q]["on"][1]]
        noise = [q for q in qs if not by[q]["on"][1] and by[q]["off"][0] != by[q]["on"][0]]
        return {"n": n, "o2_text_in_off_arm": sum(by[q]["off"][1] for q in qs), "o2_hits": len(hits),
                "hit_off_labels": dict(collections.Counter(by[q]["off"][0] for q in hits)),
                "false_refusals": [q for q in hits if by[q]["off"][0] == "pass"], "d_pass_pp": eff("pass"), "d_cw_pp": eff("cw"),
                "d_refused_pp": eff("refused"), "noise_label_changes_without_o2": len(noise), "questions_without_o2": n - len(hits)}
    for name, labels in (("majority", raters["majority"]), ("plumb", plumb)):
        d, f = attributable(labels, dev), attributable(labels, fresh)
        out.setdefault("o2_attributable", {})[name] = {"device52": d, "fresh30": f, "verdict": {
            "A4": d["d_pass_pp"] >= -5, "A5": d["d_cw_pp"] <= -5,
            "F_per10hits": len(f["false_refusals"]) * 10 <= max(f["o2_hits"], 1),
            "VALIDATED": d["d_pass_pp"] >= -5 and d["d_cw_pp"] <= -5 and len(f["false_refusals"]) * 10 <= max(f["o2_hits"], 1)}}
        print(f"attributable/{name}: {out['o2_attributable'][name]['verdict']} dev {d['d_pass_pp']}/{d['d_cw_pp']} fresh hits {f['o2_hits']} false {f['false_refusals']}")
    ids = sorted(plumb)
    out["plumb_agreement"] = {"n": len(ids), "agree_4class": sum(plumb[i] == raters["majority"][i] for i in ids),
                              "agree_binary": sum((plumb[i] == "pass") == (raters["majority"][i] == "pass") for i in ids),
                              "disagreements": {i: [raters["majority"][i], plumb[i], qid[i]] for i in ids if plumb[i] != raters["majority"][i]}}
    json.dump(out, open(f"{D}/results.json", "w", encoding="utf-8"), indent=1)
    for name in raters:
        r = out[name]
        d, f = r["device52"], r["fresh30"]
        print(f"{name:9s} dev52 pass {d['pass_off']}->{d['pass_on']} (Δ{d['d_pass_pp']}) cw {d['cw_off']}->{d['cw_on']} (Δ{d['d_cw_pp']}) "
              f"ref {d['refused_off']}->{d['refused_on']} | fresh30 pass Δ{f['d_pass_pp']} cw Δ{f['d_cw_pp']} hits {f['o2_hits']} "
              f"falseRef {f['new_false_refusals']} | {r['verdict']}")


if __name__ == "__main__":
    main()
