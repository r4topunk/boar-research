#!/usr/bin/env python3
"""exp-31 (A) gap probes: what the post author-class content exists in each pack, independent of the bench items. Read-only.

1. Title probes (humanities, cryptography, countries): present? chars, sections; in kit A (crypto pack's enwiki subset,
   bundled corpus), wiki-vital5 (lead only) and boar-wiki-en-top100k (Mac mini, full text).
2. Term scan of the whole crypto pack (post-quantum signature vocabulary, the post author-blog topics).
3. Wikivoyage section coverage (travel: Get in / Get around / Respect / Stay safe / Climate; visa + altitude mentions;
   vegan mentions in Eat sections).
Usage: python3 probe.py > probe.out.txt
"""
import json, re, sqlite3, subprocess, collections, compression.zstd as zstd
B = "<workspace>"
cry = sqlite3.connect(f"file:{B}/shared-data/crypto/boar-crypto.sqlite?mode=ro", uri=True)
voy = sqlite3.connect(f"file:{B}/shared-data/packs/boar-wikivoyage-en.sqlite?mode=ro", uri=True)
v5 = sqlite3.connect(f"file:{B}/shared-data/packs/wiki-vital5.sqlite?mode=ro", uri=True)
corp = set()
for f in ("corpus.json", "corpus-standard.json", "corpus-full.json"):
    corp |= {d["title"].lower() for d in json.loads(subprocess.check_output(["git", "-C", f"{B}/boar-app", "show", f"0cfd4a77:assets/corpus/{f}"]))}

def all_articles(db):
    """yield (title, source, text) for every article of a format-2 pack."""
    cache = {}
    for aid, src, title, b, o, l in db.execute("SELECT id, source, title, block_id, off, len FROM articles ORDER BY block_id"):
        if b not in cache:
            cache.clear(); cache[b] = zstd.decompress(db.execute("SELECT zdata FROM blocks WHERE id = ?", (b,)).fetchone()[0])
        yield title, src, cache[b][o:o + l].decode("utf-8", "replace")

HUM = ["Mozi", "Mohism", "Confucius", "Confucianism", "Mencius", "Xunzi", "Laozi", "Tao Te Ching", "Zhuangzi (book)", "Han Fei",
       "Legalism (Chinese philosophy)", "Hundred Schools of Thought", "Neo-Confucianism", "Zhu Xi", "Wang Yangming", "Chinese philosophy",
       "Harm principle", "On Liberty", "Invisible hand", "The Wealth of Nations", "Utilitarianism", "Categorical imperative", "Stoicism"]
CRY = ["Post-quantum cryptography", "Lamport signature", "Hash-based cryptography", "Lattice-based cryptography", "Shor's algorithm",
       "NIST Post-Quantum Cryptography Standardization", "SPHINCS+", "Kyber", "Merkle signature scheme", "NTRU", "McEliece cryptosystem",
       "Elliptic Curve Digital Signature Algorithm", "Quantum computing", "Grover's algorithm", "Zero-knowledge proof", "Quadratic funding",
       "The DAO", "Tornado Cash", "Terra (blockchain)", "Ethereum", "Vitalik Buterin"]
countries = [l.split("\t")[4] for l in open(f"{B}/shared-data/poi/countryInfo.txt", encoding="utf-8") if not l.startswith("#") and l.strip()]
remote_titles = HUM + CRY + countries + ["Demographics of Japan", "Culture of Japan", "History of Japan", "Geography of Japan", "Economy of Japan"]
remote = json.loads(subprocess.run(["ssh", "-o", "BatchMode=yes", "MINI_HOST",
                                    "/opt/homebrew/bin/python3 /tmp/sonar31-f2text.py <runner>/shared-data/packs/boar-wiki-en-top100k.sqlite"],
                                   input=json.dumps(remote_titles), capture_output=True, text=True, check=True).stdout)
cry_titles = {t.lower() for (t,) in cry.execute("SELECT title FROM articles")}
def v5len(t):
    r = v5.execute("SELECT SUM(LENGTH(body)) FROM chunks WHERE title = ? COLLATE NOCASE", (t,)).fetchone()[0]
    return r or 0
def row(t):
    r = remote.get(t)
    return (f"{t:45s} kitA={'crypto-pack' if t.lower() in cry_titles else 'corpus' if t.lower() in corp else '-':11s} "
            f"vital5={v5len(t):5d}ch  top100k={(str(r['len']) + 'ch ' + str(len(r['sections'])) + ' sections') if r else '-'}")

print("## 1a humanities titles"); [print(row(t)) for t in HUM]
print("\n## 1b cryptography titles"); [print(row(t)) for t in CRY]
print("\n## 1c Japan article sections in top100k:", remote["Japan"]["sections"] if remote.get("Japan") else None)
for t in ["Demographics of Japan", "Culture of Japan", "History of Japan", "Geography of Japan", "Economy of Japan"]: print(row(t))
cv5 = sum(1 for c in countries if v5len(c)); ctop = [c for c in countries if remote.get(c)]
print(f"\n## 1d countries/territories (geonames countryInfo, n={len(countries)}): in vital5 (lead) {cv5}; full text in top100k {len(ctop)}; "
      f"top100k median chars {sorted(remote[c]['len'] for c in ctop)[len(ctop)//2] if ctop else 0}; missing from top100k: "
      f"{[c for c in countries if not remote.get(c)][:60]}")

print("\n## 2 crypto pack: articles containing term (whole-pack scan)")
TERMS = ["post-quantum", "quantum-resistant", "quantum resistant", "SPHINCS", "Dilithium", "ML-DSA", "SLH-DSA", "FIPS 204", "FIPS 205",
         "Falcon", "Lamport", "Winternitz", "XMSS", "hash-based signature", "lattice", "Shor", "quantum emergency", "STARK",
         "d/acc", "defensive accelerationism", "Privacy Pools", "association set", "quadratic funding", "Glamsterdam", "FOCIL",
         "history expiry", "EIP-4444", "PeerDAS", "MAX_EFFECTIVE_BALANCE"]
hits = collections.defaultdict(list); src_n = collections.Counter(); n = 0
for title, src, text in all_articles(cry):
    n += 1; src_n[src] += 1; low = text.lower()
    for t in TERMS:
        if t.lower() in low: hits[t].append(title)
print(f"articles scanned {n}, by source id {dict(src_n)}")
for t in TERMS: print(f"  {t!r:28s} {len(hits[t]):4d}  e.g. {hits[t][:4]}")

print("\n## 3 Wikivoyage: section coverage over all guides")
sec = collections.Counter(); nv = 0; visa = alt = vegan_eat = 0; lens = []
for title, src, text in all_articles(voy):
    nv += 1; lens.append(len(text)); heads = {l[3:].strip() for l in text.splitlines() if l.startswith("## ")}
    for h in ("Get in", "Get around", "Respect", "Stay safe", "Stay healthy", "Climate", "Understand", "Eat", "Talk", "Connect"):
        if h in heads or (h == "Climate" and re.search(r"^#+ Climate", text, re.M)): sec[h] += 1
    low = text.lower(); visa += "visa" in low; alt += "altitude sickness" in low or "acute mountain sickness" in low
    m = re.search(r"^## Eat\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    vegan_eat += bool(m and re.search(r"vegan|vegetarian", m.group(1), re.I))
print(f"guides {nv}; median chars {sorted(lens)[nv//2]}; with section: {dict(sec)}; mention 'visa' {visa}; altitude sickness {alt}; "
      f"Eat section mentions vegan/vegetarian {vegan_eat}")
for t in ["Japan", "Tokyo", "Berlin", "Pai", "Brazil", "Lisbon", "Altitude sickness", "Via Francigena", "Visas", "Travel to high altitude"]:
    r = voy.execute("SELECT len FROM articles WHERE title = ? COLLATE NOCASE", (t,)).fetchone()
    print(f"  Wikivoyage {t!r}: {r[0] if r else '-'}")
