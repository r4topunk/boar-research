#!/usr/bin/env python3 -I
"""DEVICE-FINAL M3/M4 label units (0 LLM). usage: m34_prep.py m3|m4 <rows.jsonl> <units.json> <answers.json>
Builds the unit format the EXISTING Haiku labellers read (packproof|uxmatrix /tools/label.mjs: key,id,question,gold,rubric,answer,sources,sources_rev),
as packproof/tools/prep.py and uxmatrix/tools/prep.py do (same Q/REF sources, same '[n] Title (cited)\\nbody' source format, key = sha256(id, answer, sources)[:16]).
Device choices (documented in DEVICE-FINAL-NOTES.md):
 - answer = shownText (fallback answer). LabRat draws the fixed line "May contain errors; check the source." under every MODEL-written answer
   (not healthFixed / calculated / exposureComputed), so it is appended to the answer text for those rows (unless shownText already has it).
   The labeller prompt's WRONG_WARNED = 'visible warning that it may be wrong', so every wrong model answer reads as WW; WU (wrong with NO warning) is
   then only possible for fixed/calculated/exposure rows. agg reports WW+WC as 'wrong_any' for comparability.
 - sources = the kept sources (retrievedTitles, one entry per chunk, in order). The phone row has no passage text, so the body of each chunk is taken from the
   DESKTOP ON trace of the same item (same title after stripping a leading 'Source: ' prefix, k-th distinct body for the k-th chunk of that title); no match -> '(passage text not recorded on device)'.
   '(cited)' = a chunk number [n] (index into retrievedTitles) appears in the answer text."""
import json, sys, os, re, hashlib
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); C = os.path.dirname(D); BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
kind, rows_f, units_f, ans_f = sys.argv[1:5]
WARN = "May contain errors; check the source."
Q, REF = {}, {}
if kind == "m3":
    P = C + "/packproof"; IT = json.load(open(P + "/in/items.json")); META = {x["id"]: dict(pack=x["pack"]) for x in IT["items"]}
    for p in IT["packs"]:
        for r in rd(f"{BE}selftest/{p}/refs/refs.jsonl"): REF[r["id"]] = r["answer"]
        for r in rd(f"{BE}selftest/{p}/questions.jsonl"): Q[r["id"]] = r
    DESK = lambda i: f"on|{i}"; DA = json.load(open(P + "/judge/answers.json")); DU = {u["key"]: u for u in json.load(open(P + "/judge/units.json"))["units"]}
    OWN = json.load(open(P + "/in/own.json"))
else:
    P = C + "/uxmatrix"; META = {x["id"]: dict(cls=x["cls"]) for x in json.load(open(P + "/items.json"))["items"]}
    for r in rd(BE + "v0.1/refs/refs.jsonl"): REF[r["id"]] = r["answer"]
    for r in rd(BE + "v0.1/questions.public.jsonl"): Q[r["id"]] = r
    for p in ("qa-cooking-se", "qa-money-se"):
        for r in rd(f"{BE}selftest/{p}/refs/refs.jsonl"): REF[r["id"]] = r["answer"]
        for r in rd(f"{BE}selftest/{p}/questions.jsonl"): Q[r["id"]] = r
    DESK = lambda i: f"succinct|on|{i}"; DA = json.load(open(P + "/judge/answers.json")); DU = {u["key"]: u for u in json.load(open(P + "/judge/units.json"))["units"]}
    OWN = {}
STRIP = lambda t: re.sub(r"^[^:]{3,40}: ", "", t).strip().lower()   # device titles carry a source prefix ("Stack Exchange: ", "Appropedia: ", ...), desktop QA titles do not
def desk_bodies(i):
    a = DA.get(DESK(i)); out = {}
    if not a: return out
    for b in re.split(r"\n\n(?=\[\d+\] )", DU[a["key"]]["sources"].strip()):
        m = re.match(r"\[\d+\] ([^\n]*)\n?(.*)", b, re.S)
        if m:
            t = re.sub(r" \(cited\)$", "", m.group(1).strip()); body = m.group(2).strip()
            for key in (t, "~" + STRIP(t)):
                if body not in out.setdefault(key, []): out[key].append(body)
    return out
units, ans, skipped = {}, {}, 0
for r in rd(rows_f):
    i = r["queryId"]
    if "#" in i or i not in META or i not in Q: skipped += 1; continue
    layer = "fixed" if r.get("healthFixed") else "exposure" if r.get("exposureComputed") else "calculated" if r.get("calculated") else "model"
    txt = (r.get("shownText") or r.get("answer") or "").strip()
    if layer == "model" and WARN not in txt: txt = txt + "\n\n" + WARN
    titles = r.get("retrievedTitles") or []; db = desk_bodies(i); seen = {}; cited_n = {int(x) for x in re.findall(r"\[(\d+)\]", r.get("shownText") or r.get("answer") or "")}
    ent, miss = [], 0
    for n, t in enumerate(titles, 1):
        k = seen.get(t, 0); seen[t] = k + 1; bl = db.get(t) or db.get("~" + STRIP(t), [])
        body = bl[k] if k < len(bl) else None
        if body is None: miss += 1; body = "(passage text not recorded on device)"
        ent.append((t, body, n in cited_n))
    fmt = lambda L: "\n\n".join(f"[{n+1}] {t}{' (cited)' if c else ''}\n{b}" for n, (t, b, c) in enumerate(L)) or "(none)"
    src, src_rev = fmt(ent), fmt(ent[::-1])
    key = hashlib.sha256(json.dumps([i, txt, src]).encode()).hexdigest()[:16]
    units[key] = dict(key=key, id=i, question=Q[i]["question"], gold=REF[i], rubric=Q[i]["rubric"], answer=txt, sources=src, sources_rev=src_rev, n_src=len(ent))
    ans[i] = dict(key=key, layer=layer, **META[i], titles=titles, cited=sorted(n for n in cited_n if n <= len(titles)), n_src=len(ent), n_src_no_text=miss, totalMs=r.get("totalLatencyMs"),
                  userTtftMs=r.get("userTtftMs"), outcome=r.get("outcome"), own=[o["title"] for o in OWN.get(i, [])])
os.makedirs(os.path.dirname(units_f), exist_ok=True)
json.dump(dict(units=list(units.values())), open(units_f, "w")); json.dump(ans, open(ans_f, "w"))
print(f"{kind}: items {len(ans)} units {len(units)} skipped(follow-up/unknown ids) {skipped} chunks without desktop text {sum(a['n_src_no_text'] for a in ans.values())}/{sum(a['n_src'] for a in ans.values())}")
