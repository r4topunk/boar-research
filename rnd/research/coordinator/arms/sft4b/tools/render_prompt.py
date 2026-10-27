"""SFT4B stage 0, step 2: render the cut-7 engine's exact 4B prompt for (question, pack chunks).

Python side reads the pack (article text + chunk UTF-16 offsets); tools/render_core.mts runs the engine's own
sectionAt / packHitToChunk shape / isSubstantive / compressContext (budget 1200) / assembleChatMessages (succinct persona).
Library use: render([{id, question, chunks: [(pack, chunk_id), ...]}]) -> list of {id, messages, kept, ...}.
Validation: python3 -I render_prompt.py --validate  -> replays the 15 SEEDGEN B1 prompts (qa-health-se, cut 7, dumped by the
adapter) from the same items' raw chunk ids (densechunk-st OFF retrieval log) and kept set (B1 traces), and compares
the full messages byte for byte (system incl. the passage block, and user). Writes aggregates/render-validate.json."""
import json, os, subprocess, sqlite3, sys
import zstandard

BOAR = "<workspace>"
ARM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREE = f"{BOAR}/kiln-local/be-0cfd4a77-cut7"
TSX = f"{TREE}/be/node_modules/tsx/dist/cli.mjs"
CORE = f"{ARM}/tools/render_core.mts"
DIRS = [f"{BOAR}/shared-data/packs/{w}" for w in ("wave3", "wave1", "wave2")] + [f"{BOAR}/shared-data/packs"]


class PackDB:
    _open = {}

    @classmethod
    def get(cls, name):
        if name not in cls._open: cls._open[name] = cls(name)
        return cls._open[name]

    def __init__(self, name):
        path = next(os.path.join(d, name + ".sqlite") for d in DIRS if os.path.exists(os.path.join(d, name + ".sqlite")))
        self.db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        self.dz = zstandard.ZstdDecompressor(); self.blk = (None, None)

    def article(self, aid):
        t, s, b, o, l = self.db.execute("SELECT title, source, block_id, off, len FROM articles WHERE id=?", (aid,)).fetchone()
        if self.blk[0] != b:
            z = self.db.execute("SELECT zdata FROM blocks WHERE id=?", (b,)).fetchone()[0]
            self.blk = (b, self.dz.decompress(z, max_output_size=1 << 27))
        return t, s, self.blk[1][o:o + l].decode("utf-8")

    def chunk(self, cid):
        aid, st, en = self.db.execute("SELECT article_id, start, end FROM chunks WHERE id=?", (cid,)).fetchone()
        t, s, text = self.article(aid)
        return {"packTitle": t, "source": s, "text": text, "start": st, "end": en, "article_id": aid}


def chunk_input(pack, cid):
    c = PackDB.get(pack).chunk(cid)
    return {"chunkId": f"pack:{pack}:{cid}", "packTitle": c["packTitle"], "source": c["source"], "text": c["text"], "start": c["start"], "end": c["end"]}


def chunk_plain(pack, cid):
    """The chunk's raw text (no section prefix), for the writer."""
    c = PackDB.get(pack).chunk(cid)
    b = c["text"].encode("utf-16-le")
    return b[2 * c["start"]:2 * c["end"]].decode("utf-16-le", "ignore").strip()


def render_raw(lines):
    p = subprocess.run(["node", TSX, CORE], input="".join(json.dumps(l) + "\n" for l in lines), capture_output=True, text=True, cwd=TREE)
    if p.returncode: raise RuntimeError(p.stderr[-2000:])
    return [json.loads(x) for x in p.stdout.splitlines() if x.strip()]


def render(items):
    lines = [{"id": it["id"], "question": it["question"], "chunks": [chunk_input(p, c) for p, c in it["chunks"]]} for it in items]
    return render_raw(lines)


def validate():
    sg = f"{ARM}/../seedgen/runs"
    prompts = [json.loads(l) for l in open(f"{sg}/B1.prompts.jsonl")]
    traces = {d["itemId"]: d for d in map(json.loads, open(f"{sg}/B1.traces.jsonl"))}
    raws = {}
    for l in open(f"{ARM}/../densechunk-st/runs/st-qa-health-se.jsonl"):
        d = json.loads(l)
        if d["mode"] == "off" and d["id"] not in raws: raws[d["id"]] = d
    lines, keep_titles = [], {}
    for pr in prompts:
        i = pr["itemId"]; d = raws[i]
        ch = []
        for x in d["raw"]:
            pack, cid = x["chunkId"].split(":")[1].replace("local-", ""), int(x["chunkId"].rsplit(":", 1)[1])
            ci = chunk_input(pack, cid); ci["chunkId"] = x["chunkId"]; ch.append(ci)
        lines.append({"id": i, "question": traces[i]["question"], "chunks": ch})
        keep_titles[i] = traces[i]["answer"]["shown"]
    # pass 1: compression order of the chunk ids; pass 2: keep only those whose title the B1 trace shows (engine's kept set)
    first = {o["id"]: o for o in render_raw(lines)}
    lines2 = []
    for l in lines:
        i = l["id"]; o = first[i]
        titles = keep_titles[i]
        allowed = []
        bytitle = {}
        for c in l["chunks"]:
            t = "Wikivoyage: " + c["packTitle"] if c["source"] == 1 else c["packTitle"]  # B1 raw: qa-health-se (src 9 -> enwiki, bare) + wikivoyage
            bytitle.setdefault(c["chunkId"], t)
        for cid in o["kept"]:
            if bytitle.get(cid) in titles: allowed.append(cid)
        lines2.append(dict(l, keep=allowed))
    final = {o["id"]: o for o in render_raw(lines2)}
    rows, match_full, match_ctx, match_user = [], 0, 0, 0
    for pr in prompts:
        i = pr["itemId"]; o = final[i]
        a_sys, a_user = pr["messages"][0]["content"], pr["messages"][1]["content"]
        b_sys, b_user = o["messages"][0]["content"], o["messages"][1]["content"]
        ctx = lambda s: s.split("\n\nContext:\n", 1)[1] if "\n\nContext:\n" in s else ""
        fs, cs, us = (a_sys == b_sys and a_user == b_user), ctx(a_sys) == ctx(b_sys), a_user == b_user
        match_full += fs; match_ctx += cs; match_user += us
        row = {"id": i, "no_source_item": len(o["kept"]) == 0, "full_identical": fs, "passage_block_identical": cs, "user_identical": us, "n_msgs_match": len(pr["messages"]) == len(o["messages"])}
        if not fs:
            k = next((j for j in range(min(len(a_sys), len(b_sys))) if a_sys[j] != b_sys[j]), min(len(a_sys), len(b_sys)))
            row["first_diff_at"] = k; row["engine"] = a_sys[max(0, k - 60):k + 120]; row["ours"] = b_sys[max(0, k - 60):k + 120]
        rows.append(row)
    agg = {"n": len(prompts), "full_identical": match_full, "passage_block_identical": match_ctx, "user_identical": match_user, "rows": rows}
    os.makedirs(f"{ARM}/aggregates", exist_ok=True)
    json.dump(agg, open(f"{ARM}/aggregates/render-validate.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in agg.items() if k != "rows"}))
    for r in rows:
        if not r["full_identical"]: print(json.dumps(r)[:600])


if __name__ == "__main__":
    if "--validate" in sys.argv: validate()
