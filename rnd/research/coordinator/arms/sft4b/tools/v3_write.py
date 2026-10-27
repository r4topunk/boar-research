"""SFT4B v3 step 3: targets by Haiku 5.5 (claude -p, write_examples.call isolation; 5 per call, parallelism 4, cached per batch in
runs/writer-v3/<split>-r<N>-<k>.json, every call in runs/writer-v3/calls.jsonl).
The writer sees the question + the context block exactly as the 4B sees it (runs/v3/contexts.jsonl) + which passages hold the
answer. gold-present: 40-60 words, fact + one supporting detail, cite every passage used ("... [2]." engine style, cut-7
answers), two-gold: one fact/detail from EACH gold passage, both cited. gold-absent: the engine's own uncited-answer line
(context.ts uncitedPreface, the opening of 73 cut-7 self-test answers) + a brief general answer, no citation, nothing from the
passages; `covered` = true if a passage does answer (dropped).
Round >= 2 = examples in data/retry-v3-<split>.txt (from v3_filter.py) with a retry note.
Usage: python3 -I v3_write.py <train|holdout> [--round N] [--limit N]  -> data/raw-v3-<split>-r<N>.jsonl"""
import argparse, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zstd_shim  # noqa: E402,F401
import write_examples as W  # noqa: E402

ARM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WDIR = f"{ARM}/runs/writer-v3"; BATCH = 5; PAR = 4
NOSRC = "This answer is not from an offline source on this phone; check it before relying on it."

SYSTEM = f"""You write the ideal reply of a small offline research assistant ("Boar") for supervised training. For EACH candidate you get the user's question, the numbered context passages exactly as the assistant sees them ([1] ... [6]; most of them are retrieval distractors), and a TASK line saying which passage(s) hold the answer.

General rules for "answer":
- 40 to 60 words (aim for 45-55; count them: an answer under 40 or over 60 words is rejected), 2-3 sentences of plain prose, no preamble, no lists, no headings.
- Speak directly to the user; never say "the passage", "the post", "the context", "the source says", "according to".

TASK "answer passages: [n]" (one passage):
- Sentence 1: the direct answer, in passage [n]'s own wording (close paraphrase or short quote). Sentence 2 (and 3 if needed): ONE supporting detail copied almost verbatim from a nearby sentence of [n].
- Use ONLY passage [n]. Never take anything from the other passages, even if related.
- The supporting detail must be about the same topic as the question (a reason, condition, number, example or next step), not an unrelated fact that happens to sit in the passage.

TASK "answer passages: [a] and [b]" (two parts of the same article):
- Use BOTH: the answer from one and a supporting detail from the other that is about the same topic as the question, and cite each where used, e.g. "... sentence [a]. ... sentence [b]." Use nothing from any other passage.

For both tasks: faithfulness is checked strictly, claim by claim. Every claim, number and name must be stated in the cited passage text. Do not join facts with reasoning the passage does not state ("so", "because", "which means"), do not generalise, do not add advice. Cite by number in square brackets before each sentence's final period, e.g. "... about 65% of exports [2]." Every sentence ends with a citation.

TASK "no passage answers this":
- Start with exactly this sentence: "{NOSRC}"
- Then 2 short sentences that actually answer the question from general knowledge: give the best-established answer directly (if a specific number or date is uncertain, give the approximate value and say in a few words that it is approximate). Do not tell the user to check other sources (the opening line already does). No citations, no [n], and do not use or mention any detail from the passages.
- (For the answer-passage tasks always set "covered" to false.) Set "covered" to true only if, contrary to the TASK line, one of the passages clearly does answer the question; otherwise false.

Return one item per candidate id, in the same order."""
RETRY = ("A previous answer for these candidates failed a strict check (a claim not stated in the cited passages, a detail taken "
         "from a distractor passage, off-target, or wrong length). Stay closer to the answer passages' own wording; keep 40-60 words.\n\n")
SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "id": {"type": "string"}, "answer": {"type": "string"}, "covered": {"type": "boolean"}}, "required": ["id", "answer", "covered"]}}},
    "required": ["items"]}


def task_line(c):
    if c["mode"] == "absent": return "TASK: no passage answers this"
    g = [f"[{p}]" for p in c["gold_pos"]]
    return "TASK: answer passages: " + " and ".join(g)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("split"); ap.add_argument("--round", type=int, default=1); ap.add_argument("--limit", type=int)
    a = ap.parse_args(); os.makedirs(WDIR, exist_ok=True)
    cands = [c for c in map(json.loads, open(f"{ARM}/runs/v3/contexts.jsonl")) if c["split"] == a.split]
    if a.round > 1:
        retry = set(open(f"{ARM}/data/retry-v3-{a.split}.txt").read().split()); cands = [c for c in cands if c["xid"] in retry]
    if a.limit: cands = cands[:a.limit]
    batches = []
    for k, i in enumerate(range(0, len(cands), BATCH)):
        cs = cands[i:i + BATCH]
        body = "\n\n".join(f"### candidate id: {c['xid']}\nQuestion: {c['question']}\n{task_line(c)}\n\nContext:\n{c['passages']}" for c in cs)
        batches.append((f"{a.split}-r{a.round}-{k:04d}", cs, (RETRY if a.round > 1 else "") + f"Write the answer for each of these {len(cs)} candidates.\n\n" + body))

    def run(key, cs, prompt):
        f = f"{WDIR}/{key}.json"
        if os.path.exists(f):
            res = json.load(open(f))
            if res["ids"] == [c["xid"] for c in cs]: return res, 0
        for att in range(2):
            W.SYSTEM, W.SCHEMA = SYSTEM, SCHEMA
            out, wall = W.call(prompt)
            ok = not out.get("is_error") and bool(out.get("structured_output"))
            with open(f"{WDIR}/calls.jsonl", "a") as fh:
                fh.write(json.dumps({"at": time.strftime("%FT%T"), "batch": key, "attempt": att, "ok": ok, "wall_s": round(wall, 1),
                                     "cost_list_usd": out.get("total_cost_usd")}) + "\n")
            if ok:
                res = {"items": out["structured_output"]["items"], "ids": [c["xid"] for c in cs]}
                json.dump(res, open(f, "w")); return res, 1
            if re.search(r"rate.?limit|usage limit|429|overloaded", str(out.get("result", "")), re.I):
                raise SystemExit(f" [usage detail removed]")
        return None, 1

    got, new = [], 0
    with ThreadPoolExecutor(PAR) as ex:
        for (key, cs, _), (res, n) in zip(batches, ex.map(lambda b: run(*b), batches)):
            new += n
            if not res: continue
            by = {it["id"]: it for it in res["items"]}
            for c in cs:
                if c["xid"] in by:
                    got.append({**c, "round": a.round, "answer": by[c["xid"]]["answer"].strip(), "covered": bool(by[c["xid"]].get("covered"))})
    with open(f"{ARM}/data/raw-v3-{a.split}-r{a.round}.jsonl", "w") as f:
        for g in got: f.write(json.dumps(g) + "\n")
    n = sum(1 for _ in open(f"{WDIR}/calls.jsonl"))
    print(f"v3 {a.split} r{a.round}: candidates {len(cands)} batches {len(batches)} (new calls {new}) answers {len(got)}; v3 writer calls total {n}")


if __name__ == "__main__":
    main()
