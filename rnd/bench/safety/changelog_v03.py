#!/usr/bin/env python3
"""Re-score every bench card under safety v0.2 and v0.3 and list item-by-item label changes (for CHANGELOG.md).
Then (with --write) re-writes the cards in place under v0.3 (the default in score.py). Cards: v0 common-instrument (4),
v0 agent-labelled (1), D10 package card, night 2026-10-01 runs (7) + the night safety10 run on the track.
  python3 changelog_v03.py            # diff only (JSON to stdout + changelog-v03.json)
  python3 changelog_v03.py --write    # also re-render the cards under v0.3
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = HERE.parent
ROOT = B.parent.parent
sys.path.insert(0, str(B / "score"))
import score  # noqa: E402

N = B / "night-2026-10-01"
CARDS = []
for f in sorted((B / "results/v0/common-instrument").glob("*.report.json")) + [B / "results/v0/boar-p3-iphone13-qwen1.5b.report.json"]:
    r = json.load(open(f))
    p = dict(r["input_paths"])  # keep the original (repo-relative) paths; main() runs from the repo root
    CARDS.append({"card": str(f.relative_to(B)), "system": r["system"], "out": f.parent, **p})
D = N / "d10-package"; P = "boar-main-fd24992-iphone13-qwen1.5b"
CARDS.append({"card": str((D / f"{P}.report.json").relative_to(B)), "system": P, "out": D, "answers": str(D / f"{P}.answers.jsonl"),
              "judgments": str(D / f"{P}__vs__refs-v0.jsonl"), "device": str(D / "device-iphone13-qwen2.5-1.5b-main-611a4b9-bench60.json"),
              "jev_cw": str(D / f"{P}.jev.labels.jsonl")})
for run, v in json.load(open(N / "runs.json")).items():
    if run == "q3-thermal150":
        continue
    j = N / "judge" / f"{run}__vs__refs-v0.jsonl"
    CARDS.append({"card": f"night-2026-10-01/cards/{run}.report.json", "system": run, "out": N / "cards", "answers": v["answers"],
                  "judgments": str(j) if j.exists() else None, "device": v["device"], "jev_cw": v.get("jev")})
CARDS.append({"card": "night-2026-10-01/cards/safety10-main-o2off.report.json", "system": "safety10-main-o2off", "out": N / "cards",
              "answers": str(N / "answers/safety10-main-o2off.answers.jsonl"), "questions": str(HERE / "track.v0.3.jsonl")})


def run(c, version):
    return score.score(c["system"], c["answers"], c.get("questions"), c.get("judgments"), c.get("hand"), c.get("device"),
                       jev_cw=c.get("jev_cw"), safety_version=version)


def main():
    import os
    os.chdir(ROOT)
    write = "--write" in sys.argv
    out = []
    for c in CARDS:
        a, b = run(c, "v0.2"), run(c, "v0.3")
        ia = {x["id"]: x for x in a["items"]}
        ch = [{"id": x["id"], "before": f"{ia[x['id']]['label']} ({ia[x['id']]['source']}, {ia[x['id']]['points']:+g})",
               "after": f"{x['label']} ({x['source']}, {x['points']:+g})",
               "hits_before": [h["rule"] for h in ia[x["id"]].get("safety_hits", [])], "hits_after": [h["rule"] for h in x.get("safety_hits", [])]}
              for x in b["items"] if (x["label"], x["points"], [h["rule"] for h in x.get("safety_hits", [])]) !=
              (ia[x["id"]]["label"], ia[x["id"]]["points"], [h["rule"] for h in ia[x["id"]].get("safety_hits", [])])]
        band = lambda r: (r.get("truthfulness_band") or {}).get("judge_plus_jev_cw")
        out.append({"card": c["card"], "changes": ch, "safety": [a["safety"]["line"], b["safety"]["line"]],
                    "truth": [a["truthfulness"]["score_mean"], b["truthfulness"]["score_mean"]], "band_low": [band(a), band(b)],
                    "ratio_same": a["quality"].get("quality_ratio") == b["quality"].get("quality_ratio")})
        if write:
            c["out"].mkdir(parents=True, exist_ok=True)
            (Path(c["out"]) / f"{c['system']}.report.md").write_text(score.render_md(b))
            (Path(c["out"]) / f"{c['system']}.report.json").write_text(json.dumps(b, indent=1, ensure_ascii=False, default=str) + "\n")
    (HERE / "changelog-v03.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    for o in out:
        print(o["card"], "| changes:", len(o["changes"]), "|", " → ".join(o["safety"]), "| truth", " → ".join(f"{t:+.3f}" for t in o["truth"]),
              "| ratio same:", o["ratio_same"])
        for x in o["changes"]:
            print("   ", x["id"], x["before"], "→", x["after"], x["hits_before"], "→", x["hits_after"])


if __name__ == "__main__":
    main()
