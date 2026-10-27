"""Oracle sources for v0.1 EN items (Anvil, dev): every Wikipedia article the item's reference_sources / the Opus+web reference
cite / gold/sources.json name, plus non-Wikipedia reference URLs (best-effort HTML -> text). Cached in cache/. Writes
articles.jsonl: {id, url, title, kind: wiki|web, text}. Stdlib only."""
import json, re, os, hashlib, urllib.request, urllib.parse, html, time, sys
B = "<workspace>/boar-eval/bench/v0.1/"
H = os.path.dirname(os.path.abspath(__file__))
refs = {json.loads(l)["id"]: json.loads(l) for l in open(B + "refs/refs.jsonl")}
qs = {json.loads(l)["id"]: json.loads(l) for l in open(B + "questions.public.jsonl")}
gold = json.load(open(B + "gold/sources.json"))
ids = open(H + "/../outofkit/v01-en-ids.txt").read().strip().split(",")
UA = {"User-Agent": "boar-research/0.1 (offline-research-bench)"}
def get(url):
    f = os.path.join(H, "cache", hashlib.sha256(url.encode()).hexdigest()[:24])
    if os.path.exists(f): return open(f).read()
    for a in range(3):
        try:
            t = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "replace"); break
        except Exception as e:
            t = ""; time.sleep(2 * (a + 1))
    open(f, "w").write(t); time.sleep(0.3); return t
def wiki(title):
    u = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "prop": "extracts", "explaintext": 1, "redirects": 1, "format": "json", "titles": title})
    try:
        pages = json.loads(get(u))["query"]["pages"]
        p = next(iter(pages.values())); return p.get("title", title), p.get("extract", "") or ""
    except Exception: return title, ""
def web(url):
    t = get(url)
    t = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?i)<(br|/p|/h\d|/li|/div)[^>]*>", "\n", t); t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t); t = re.sub(r"[ \t]+", " ", t); t = re.sub(r"\n\s*\n+", "\n\n", t)
    return t.strip()
out = open(H + "/articles.jsonl", "w"); n = 0
for i in ids:
    blob = json.dumps(refs[i].get("sources")) + json.dumps(qs[i].get("reference_sources")) + json.dumps(refs[i].get("answer"))
    titles = {urllib.parse.unquote(w).replace("_", " ") for w in re.findall(r"en\.wikipedia\.org/wiki/([^\s\"\)\]#?,]+)", blob)}
    titles |= set(gold.get(i, []) if isinstance(gold.get(i), list) else [])
    urls = {u for u in re.findall(r"https?://[^\s\"\)\]]+", json.dumps(qs[i].get("reference_sources")) + json.dumps(refs[i].get("sources"))) if "wikipedia.org" not in u}
    for t in sorted(titles):
        tt, text = wiki(t)
        if len(text) > 200: out.write(json.dumps({"id": i, "url": "https://en.wikipedia.org/wiki/" + tt.replace(" ", "_"), "title": tt, "kind": "wiki", "text": text}) + "\n"); n += 1
    for u in sorted(urls)[:4]:
        text = web(u)
        if len(text) > 300: out.write(json.dumps({"id": i, "url": u, "title": u.split("//")[1][:80], "kind": "web", "text": text[:60000]}) + "\n"); n += 1
    print(i, len(titles), "wiki", len(urls), "web", flush=True)
print("articles", n)
