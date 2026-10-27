"""SFT4B stage 0, v2 targets (coordinator 2026-10-13): 35-60-word answers (fact + one supporting detail + citation) for the
SAME disjoint candidates and, per article, the SAME question as v1 (the passing v1 question if any, else the last round's).

Unlike v1 the writer sees the prompt exactly as the 4B does: the question is fixed, so the engine-rendered context block
(cut-7 compression, numbered [1]/[2]) is shown and the writer cites those numbers directly (no letter mapping).
Writer = claude -p Haiku 5.5 effort low (write_examples.call, same isolation), 5 per call, parallelism 4, cached per batch
(runs/writer-v2/<split>-r<N>-<k>.json), every call in runs/writer-v2/calls.jsonl. Round >= 2 = articles whose v2 example failed
(data/retry-v2-<split>.txt from filter_v2.py) with a retry note.
Usage: python3 -I write_v2.py <train|holdout> [--round N]   -> data/raw-v2-<split>-r<N>.jsonl"""
import argparse, glob, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import write_examples as W  # noqa: E402
from render_prompt import render  # noqa: E402

ARM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WDIR = f"{ARM}/runs/writer-v2"; BATCH = 5; PAR = 4

SYSTEM = """You write the ideal reply of a small offline research assistant ("Boar") for supervised training. For EACH candidate you get the user's question and the numbered context passages exactly as the assistant sees them ([1], and sometimes [2]).

Write "answer":
- 35 to 60 words (aim for 40-50), 2-3 short sentences of plain prose, no preamble, no lists, no headings.
- Sentence 1: the direct answer to the question, in the passage's own wording (close paraphrase or short quote).
- Sentence 2 (and 3 if needed for length): ONE supporting detail copied almost verbatim from a passage sentence near the fact (a reason, condition, number, example or next step that the passage states in those words).
- Faithfulness is checked strictly, claim by claim: every claim, number and name must be stated in the passage text. Do not join facts with reasoning the passage does not state ("so", "because", "which means", "this also means"), do not generalise, do not add advice, do not reword a list item into a broader claim. Never list more than four items.
- Speak directly to the user; never say "the passage", "the post", "the writer", "the source says", "according to", "the list includes".
- Cite the passage(s) you actually used by number in square brackets before each sentence's final period, e.g. "... about 65% of exports [1]." Cite [2] only for a fact taken from [2]; cite both when both were used.
- If the passages answer the question only partly, answer the part they cover; do not invent the rest.

Return one item per candidate id, in the same order."""
RETRY = ("A previous answer for these candidates failed a strict check (a claim not stated in the passages, off-target, or wrong "
         "length). Stay closer to the passages' own wording; keep 35-60 words.\n\n")
SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "id": {"type": "string"}, "answer": {"type": "string"}}, "required": ["id", "answer"]}}}, "required": ["items"]}


def v1_questions(split):
    """per (pack, article): v1 question to reuse = passing one if any (train/holdout .meta), else the highest round's."""
    best = {}
    for f in sorted(glob.glob(f"{ARM}/data/raw-{split}*.jsonl")):
        for l in open(f):
            r = json.loads(l); k = (r["pack"], r["article_id"])
            if k not in best or r["round"] > best[k]["round"]: best[k] = r
    for l in open(f"{ARM}/data/{split}.meta.jsonl"):
        m = json.loads(l); k = (m["pack"], m["article_id"])
        best[k] = {**best[k], "question": m["question"], "round": m["round"], "v1_pass": True}
    return best


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("split"); ap.add_argument("--round", type=int, default=1)
    a = ap.parse_args(); os.makedirs(WDIR, exist_ok=True)
    qs = v1_questions(a.split)
    if a.split == "holdout":  # the same 100 hold-out articles as v1 (data/holdout.meta.jsonl)
        keep = {(m["pack"], m["article_id"]) for m in map(json.loads, open(f"{ARM}/data/holdout.meta.jsonl"))}
        qs = {k: v for k, v in qs.items() if k in keep}
    cands = [dict(v, cid=f"{k[0]}:{k[1]}") for k, v in sorted(qs.items())]
    if a.round > 1:
        retry = set(open(f"{ARM}/data/retry-v2-{a.split}.txt").read().split()); cands = [c for c in cands if c["cid"] in retry]
    rend = {o["id"]: o for o in render([{"id": c["cid"], "question": c["question"], "chunks": [(c["pack"], x) for x in c["chunk_ids"]]} for c in cands])}
    for c in cands:
        o = rend[c["cid"]]; c["messages"] = o["messages"]; c["kept"] = o["kept"]
        c["passages"] = o["messages"][0]["content"].split("\n\nContext:\n", 1)[1] if o["kept"] else ""
    cands = [c for c in cands if c["passages"]]
    batches = []
    for k, i in enumerate(range(0, len(cands), BATCH)):
        cs = cands[i:i + BATCH]
        body = "\n\n".join(f"### candidate id: {c['cid']}\nQuestion: {c['question']}\n\nContext:\n{c['passages']}" for c in cs)
        batches.append((f"{a.split}-r{a.round}-{k:04d}", cs, (RETRY if a.round > 1 else "") + f"Write the answer for each of these {len(cs)} candidates.\n\n" + body))

    def run(key, cs, prompt):
        f = f"{WDIR}/{key}.json"
        if os.path.exists(f): return json.load(open(f)), 0
        for att in range(2):
            W.SYSTEM, W.SCHEMA = SYSTEM, SCHEMA
            out, wall = W.call(prompt)
            ok = not out.get("is_error") and bool(out.get("structured_output"))
            with open(f"{WDIR}/calls.jsonl", "a") as fh:
                fh.write(json.dumps({"at": time.strftime("%FT%T"), "batch": key, "attempt": att, "ok": ok, "wall_s": round(wall, 1),
                                     "cost_list_usd": out.get("total_cost_usd")}) + "\n")
            if ok:
                res = {"items": out["structured_output"]["items"], "ids": [c["cid"] for c in cs]}
                json.dump(res, open(f, "w")); return res, 1
            if re.search(r"rate.?limit|usage limit|429|overloaded", str(out.get("result", "")), re.I):
                raise SystemExit(f" [usage detail removed]")
        return None, 1

    got, new = [], 0
    with ThreadPoolExecutor(PAR) as ex:
        for (key, cs, _), (res, n) in zip(batches, ex.map(lambda b: run(*b), batches)):
            new += n
            if not res: continue
            by = {it["id"]: it["answer"].strip() for it in res["items"]}
            for c in cs:
                if c["cid"] in by:
                    got.append({k: c[k] for k in ("split", "pack", "article_id", "title", "chunk_ids", "question", "messages", "kept", "passages")}
                               | {"round": a.round, "v1_round": c["round"], "answer": by[c["cid"]]})
    with open(f"{ARM}/data/raw-v2-{a.split}-r{a.round}.jsonl", "w") as f:
        for g in got: f.write(json.dumps(g) + "\n")
    n = sum(1 for _ in open(f"{WDIR}/calls.jsonl"))
    print(f"v2 {a.split} r{a.round}: candidates {len(cands)} batches {len(batches)} (new {new}) answers {len(got)}; v2 writer calls total {n}")


if __name__ == "__main__":
    main()
