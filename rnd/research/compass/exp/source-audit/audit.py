# Offline audit: which pack chunks would trip the bench's safety forbid rules (v0.3, same negation logic) if quoted?
# A rule only applies to chunks that mention its topic (topic gate below). Read-only over local packs.
import json, re, sys, sqlite3, collections
import compression.zstd as zstd
sys.path.insert(0, "<workspace>/rnd/bench/safety"); import safety_check as sc
S = sc.load(version="v0.3")
TOPIC = {"hypo": r"hypotherm|hipoterm", "snake": r"snake|serpent|cobra|viper|rattlesnake", "burn": r"\bburn|scald|queimad", "nose": r"nose ?bleed|nosebleed|epistaxis|nariz",
         "quake": r"earthquake|terremoto", "jelly": r"jellyfish|man-o'-war|água-viva|agua-viva", "frost": r"frostbit|frostnip|congelament", "altitude": r"altitude|mountain sickness|\bAMS\b|HAPE|HACE",
         "water": r"drinking water|boil(ing)? (the )?water|purif|disinfect", "heat": r"heat ?stroke|hyperthermia|insola"}
forbid = [rid for rid, m in S["meta"].items() if m.get("type", "forbid") == "forbid"]
def run(path, label, limit_titles=None):
    db = sqlite3.connect(path); srcs = json.loads(dict(db.execute("select key, value from meta").fetchall()).get("sources", "{}"))
    blocks = {}
    def block(i):
        if i not in blocks:
            if len(blocks) > 64: blocks.clear()
            blocks[i] = zstd.decompress(db.execute("select zdata from blocks where id=?", (i,)).fetchone()[0])
        return blocks[i]
    hits = []; n = 0
    for aid, src, title, bid, off, ln in db.execute("select id, source, title, block_id, off, len from articles order by block_id"):
        text = block(bid)[off:off + ln].decode("utf8", "replace")
        if not any(re.search(p, text, re.I) for p in TOPIC.values()): continue
        n += 1
        for st, en in db.execute("select start, end from chunks where article_id=?", (aid,)):
            ch = text[st:en]
            rules = [r for r in forbid if re.search(TOPIC[r.split("-")[0]], ch, re.I)]
            if not rules: continue
            for h in sc.check(ch, rules, S):
                hits.append({"pack": label, "source": src, "title": title, "rule": h["rule"], "match": h["match"], "sentence": h["sentence"]})
    print(f"{label}: articles mentioning a topic {n}; hits {len(hits)}")
    return hits
H = run("<workspace>/shared-data/preparedness-v3/boar-preparedness.sqlite", "preparedness")
H += run("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", "wikivoyage")
json.dump(H, open("hits.json", "w"), ensure_ascii=False, indent=0)
for pack in ("preparedness", "wikivoyage"):
    c = collections.Counter(h["rule"] for h in H if h["pack"] == pack); print(pack, dict(c.most_common()))
