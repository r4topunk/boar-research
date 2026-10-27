"""SOURCEGROUP trace sets (public only): per trace -> (set, id, sources [{title, source}], text, citedShown).
Desktop traces: the last `sources` event (what the chat shows; [n] = sources[n-1]) + answer.text (final text).
X6 phone rows / native raw: retrievedTitles (titles only, no url) + answer."""
import json, glob, ast, os
B = "<workspace>"
A = f"{B}/rnd/research/coordinator/arms"
X6 = f"{B}/boar-eval/runs/device-poco-x6pro"
DESKTOP = {
    "phonefail27": sorted(glob.glob(f"{A}/phonefail/runs/w[123].traces.jsonl")),
    "st180_4b_x2b": sorted(glob.glob(f"{A}/headpass-st/gen-x2b/st-*-cut7-headpassx2b-s42.traces.jsonl")),
    "st180_1p7b_x2b": sorted(glob.glob(f"{A}/lite5/runs/180/lite5-180-on-*-s42.traces.jsonl")),
    "st180_1p7b_off": sorted(glob.glob(f"{A}/lite5/runs/180/lite5-180-off-*-s42.traces.jsonl")),
    "v01_cut7": [f"{A}/stack/runs/v01-cut7-stack-off-s42.traces.jsonl"],
}
L = lambda v: v if isinstance(v, list) else (ast.literal_eval(v) if isinstance(v, str) and v.startswith("[") else [])
def load():
    out = {}
    for name, files in DESKTOP.items():
        rows = []
        for f in files:
            for l in open(f):
                t = json.loads(l)
                ev = [e for e in t.get("events", []) if e.get("type") == "sources"]
                src = ev[-1]["sources"] if ev else []
                a = t.get("answer") or {}
                rows.append({"id": t["itemId"], "file": os.path.basename(f), "sources": [{"title": s.get("title") or "", "source": s.get("source")} for s in src],
                             "text": a.get("text") or "", "citedShown": len(a.get("cited") or []) > 0})
        out[name] = rows
    P = [json.loads(l) for l in open(f"{X6}/final-cut7-v01/rows.jsonl")]
    out["x6_phone_cut7"] = [{"id": p["queryId"], "file": "final-cut7-v01/rows.jsonl", "sources": [{"title": x} for x in L(p["retrievedTitles"])],
                             "text": p.get("answer") or "", "citedShown": len(L(p.get("citedTitles"))) > 0} for p in P]
    N = [json.loads(l) for f in sorted(glob.glob(f"{X6}/native-x6-v01/raw/eval-*.jsonl")) for l in open(f)]
    out["x6_native"] = [{"id": p["queryId"], "file": "native-x6-v01/raw", "sources": [{"title": x} for x in L(p["retrievedTitles"])],
                         "text": p.get("answer") or "", "citedShown": None} for p in N]
    return out
