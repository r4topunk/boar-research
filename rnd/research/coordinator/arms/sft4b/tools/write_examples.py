"""SFT4B stage 0, step 3: Haiku 5.5 writes one (question, target answer) per pool candidate.

Writer = `claude -p --model claude-haiku-5-5 --effort low` on the Claude Code CLI login (same isolation as boar-eval
claude-cli.mjs: empty temp cwd, no tools, no settings sources, no MCP, no session persistence, API-key env stripped,
inherits CLAUDE_CONFIG_DIR), JSON schema output, 5 candidates per call, parallelism 4, one cache file per batch
(runs/writer/<split>-<round>-<k>.json; resumable: cached batches are never re-sent). Every call (ok or failed) is
appended to runs/writer/calls.jsonl.
The writer sees each chunk lettered [A]/[B] (title + "section: text", the engine's pre-compression body) and cites by
letter; filter_jev.py maps letters to the rendered prompt's [n] after compression.
Round >= 2 (candidates whose round-1 example failed filter_jev; --ids-from) adds RETRY_NOTE (one near-verbatim sentence).
Usage: python3 -I write_examples.py <split: train|holdout> [--round N] [--ids-from file] [--limit N]
Output: data/raw-<split>[-rN].jsonl"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_prompt import PackDB, chunk_input  # noqa: E402

ARM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WDIR = f"{ARM}/runs/writer"; BATCH = 5; PAR = 4
STRIP = re.compile(r"^(ANTHROPIC_API_KEY|ANTHROPIC_AUTH_TOKEN|ANTHROPIC_BASE_URL|AI_GATEWAY_API_KEY|VERCEL_AI_GATEWAY|OPENAI_API_KEY|CLAUDE_CODE_(SESSION_ID|CHILD_SESSION|MESSAGING_SOCKET|MESSAGING_TOKEN|ENTRYPOINT|SESSION_ATTENDED|USE_BEDROCK|USE_VERTEX))$")

SYSTEM = """You write supervised training examples for a small offline assistant ("Boar") that answers a user's question from retrieved reference passages and cites them by number.

For EACH candidate you get one or two passages, lettered [A] and [B] (title line, then the passage text). Write:
1. "question": ONE question a real user might type, in natural everyday English, that is fully answered by a specific fact (a value, name, date, cause, step, recommendation or explanation) stated explicitly in the passage text.
   - Self-contained: never mention "the passage", "the article", "the post", "the answer", "according to"; the user has not seen the text.
   - Reuse the key content words the passage itself uses for that fact (the system matches question words to sentences).
   - Do not ask about the passage's title alone, about usernames, votes, dates of posting, or anything not stated in the text.
   - For Stack Exchange posts (a question followed by answers), ask what the asker wanted to know, phrased freshly, and answer with what the answers say. If the text holds only the asker's question and no answer to it, ask instead about a concrete fact the asker states or another fact the text states clearly.
2. "answer": the ideal reply, at most 60 words, 1-3 short sentences, plain prose, no preamble, no lists, no hedging filler.
   - State the fact directly in the first sentence, as an expert would; never refer to "the writer", "the post", "the asker", "the passage", "the source says" or what the text does not contain.
   - Use ONLY information stated in the passages: every claim, number and name in the answer must be in the passage text. No outside knowledge, no extra advice.
   - Cite the passage you used with its letter in square brackets, placed before the sentence's final period, e.g. "... about 65% of exports [A]." Cite [B] only for a fact taken from [B].
   - Be extractive: build the answer from the fact sentence's own wording (trim it, address the user as "you"), and do not add connecting reasoning ("because", "so", "which means"), consequences, generalisations or advice that the passage does not state in those words. A single sentence is a good answer.
   - Keep to ONE fact (or two closely linked facts) taken from at most two sentences of the passage, in the passage's own words (close paraphrase or short quote). Every sentence of the answer ends with a citation.
   - The assistant will see only the first sentence of each passage plus the few sentences that share the most words with the question, so the question must share distinctive words with the sentence(s) holding the fact.
3. "fact_quote": the exact sentence (verbatim, copied from the passage) that contains the fact.

Return one item per candidate id, in the same order."""

SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "id": {"type": "string"}, "question": {"type": "string"}, "answer": {"type": "string"}, "fact_quote": {"type": "string"}},
    "required": ["id", "question", "answer", "fact_quote"]}}}, "required": ["items"]}


def passage_text(pack, cid):
    """[title]\\n[section: text] as the engine builds the body before compression (via render_core's rule, re-done here for the writer)."""
    ci = chunk_input(pack, cid)
    text = ci["text"].encode("utf-16-le")
    body = text[2 * ci["start"]:2 * ci["end"]].decode("utf-16-le", "ignore").strip()
    # section path: same heading rule as wikiPack.sectionAt (writer context only; the prompt itself is rendered by the engine)
    head = text[:2 * ci["start"]].decode("utf-16-le", "ignore")
    path = []
    for m in re.finditer(r"^(#{1,6})\s+(.*)$", head, re.M):
        lvl = len(m.group(1)); path = path[:lvl - 1] + [""] * max(0, lvl - 1 - len(path)); path.append(m.group(2).strip())
    sec = " > ".join(x for x in path[1:] if x)
    return ci["packTitle"], (f"{sec}: {body}" if sec else body)


def call(prompt):
    cwd = tempfile.mkdtemp(prefix="sft4b-writer-")
    env = {k: v for k, v in os.environ.items() if not STRIP.match(k)}
    argv = ["claude", "-p", prompt, "--model", "claude-haiku-5-5", "--effort", "low", "--system-prompt", SYSTEM, "--tools", "",
            "--setting-sources", "", "--strict-mcp-config", "--no-session-persistence", "--json-schema", json.dumps(SCHEMA),
            "--output-format", "json"]
    t = time.time()
    try:
        p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=300)
        out = json.loads(p.stdout) if p.stdout.strip().startswith("{") else {"is_error": True, "result": (p.stderr or p.stdout)[-500:]}
    except Exception as e:  # timeout etc.
        out = {"is_error": True, "result": str(e)[:300]}
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    return out, time.time() - t


RETRY_NOTE = ("A previous example for these candidates failed a strict check (an answer claim not stated in the text the assistant "
              "sees, or an off-target answer). This time pick the single most clearly stated fact, ask a question that reuses that "
              "sentence's key words, and answer with ONE near-verbatim sentence from it.\n\n")


def build_prompt(cands, retry=False):
    parts = []
    for c in cands:
        s = [f"### candidate id: {c['cid']}"]
        for letter, ch in zip("AB", c["chunk_ids"]):
            t, b = passage_text(c["pack"], ch)
            s.append(f"[{letter}] {t}\n{b}")
        parts.append("\n\n".join(s))
    return (RETRY_NOTE if retry else "") + f"Write one example for each of these {len(cands)} candidates.\n\n" + "\n\n".join(parts)


def run_batch(key, cands, prompt):
    f = f"{WDIR}/{key}.json"
    if os.path.exists(f): return json.load(open(f)), False
    for attempt in range(2):
        out, wall = call(prompt)
        rec = {"at": time.strftime("%FT%T"), "batch": key, "attempt": attempt, "ok": not out.get("is_error") and bool(out.get("structured_output")),
               "wall_s": round(wall, 1), "cost_list_usd": out.get("total_cost_usd"), "usage": out.get("usage", {}).get("output_tokens")}
        with open(f"{WDIR}/calls.jsonl", "a") as fh: fh.write(json.dumps(rec) + "\n")
        if rec["ok"]:
            res = {"items": out["structured_output"]["items"], "cands": cands}
            json.dump(res, open(f, "w")); return res, True
        if re.search(r"rate.?limit|usage limit|429|overloaded", str(out.get("result", "")), re.I):
            raise SystemExit(f" [usage detail removed].get('result'))[:200]}")
    return None, True


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("split"); ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--ids-from"); ap.add_argument("--limit", type=int)
    a = ap.parse_args(); os.makedirs(WDIR, exist_ok=True)
    pool = [json.loads(l) for l in open(f"{ARM}/data/{'pool' if a.split == 'train' else 'holdout-pool'}.jsonl")]
    if a.split == "holdout" and os.path.exists(f"{ARM}/data/holdout-pool-extra.jsonl"):  # replacements (disjoint_check --extra-holdout)
        pool += [json.loads(l) for l in open(f"{ARM}/data/holdout-pool-extra.jsonl")]
    if a.ids_from:
        keep = set(open(a.ids_from).read().split()); pool = [r for r in pool if f"{r['pack']}:{r['article_id']}" in keep]
    if a.limit: pool = pool[:a.limit]
    for r in pool: r["cid"] = f"{r['pack']}:{r['article_id']}"
    batches = [(f"{a.split}-r{a.round}-{k:04d}", pool[i:i + BATCH]) for k, i in enumerate(range(0, len(pool), BATCH))]
    batches = [(k, c, None if os.path.exists(f"{WDIR}/{k}.json") else build_prompt(c, a.round > 1)) for k, c in batches]  # sqlite in this thread
    sent = 0; got = []
    with ThreadPoolExecutor(PAR) as ex:
        for res, new in ex.map(lambda kb: run_batch(*kb), batches):
            sent += new
            if not res: continue
            by = {it["id"]: it for it in res["items"]}
            for c in res["cands"]:
                it = by.get(c["cid"])
                if it: got.append({**{k: c[k] for k in ("split", "pack", "article_id", "title", "chunk_ids")}, "round": a.round,
                                   "question": it["question"].strip(), "answer_letters": it["answer"].strip(), "fact_quote": it["fact_quote"]})
    sfx = "" if a.round == 1 else f"-r{a.round}"
    with open(f"{ARM}/data/raw-{a.split}{sfx}.jsonl", "w") as f:
        for g in got: f.write(json.dumps(g) + "\n")
    calls = [json.loads(l) for l in open(f"{WDIR}/calls.jsonl")]
    print(f"{a.split} r{a.round}: candidates {len(pool)} batches {len(batches)} (new {sent}) examples {len(got)}; "
          f"writer calls total {len(calls)} (failed {sum(not c['ok'] for c in calls)})")


if __name__ == "__main__":
    main()
