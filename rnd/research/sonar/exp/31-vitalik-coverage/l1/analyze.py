#!/usr/bin/env python3
"""exp-31 probe analysis: raw/pre titles and facet terms found in the EXACT pre-answer passage text (--event-source-text)."""
import json, re, sys
FACETS = {
 "p-jp-01": {"capital Tokyo": r"tokyo", "population": r"popul", "government": r"emperor|constitutional monarch|diet\b|parliament", "history": r"shogun|meiji|edo|world war", "geography": r"island|archipelago|mountain", "economy": r"econom|gdp", "culture": r"cultur|shinto|buddh"},
 "p-ke-02": {"Nairobi": r"nairobi", "1963": r"1963", "Swahili": r"swahili"},
 "p-pq-03": {"ML-DSA/Dilithium": r"ml-dsa|dilithium|fips 204", "SLH-DSA/SPHINCS+": r"slh-dsa|sphincs|fips 205", "Falcon/FN-DSA": r"falcon|fn-dsa"},
 "p-pq-04": {"ML-DSA": r"ml-dsa", "SLH-DSA": r"slh-dsa", "lattice": r"lattice", "hash-based": r"hash-based|hash based"},
 "p-pq-05": {"SPHINCS": r"sphincs", "hash": r"hash", "quantum": r"quantum|shor|grover"},
 "p-pq-06": {"hard fork": r"hard.fork", "STARK/ZK/seed": r"stark|zero-knowledge|\bzk|seed|preimage"},
 "p-cn-07": {"Xunzi": r"xunzi|xun zi", "Mencius": r"mencius|mengzi", "nature bad": r"evil|bad|wicked", "nature good": r"\bgood"},
 "p-cn-08": {"Han Fei/Shang Yang": r"han fei|shang yang|li si", "law (fa)": r"\blaw|\bfa\b", "reward/punishment": r"punish|reward"},
 "p-tv-09": {"visa": r"visa", "Brazil": r"brazil", "Japan": r"japan"},
 "p-tv-10": {"Patagonia": r"patagonia", "season months": r"december|january|february|march|summer|spring|autumn"},
 "p-tv-11": {"Japan": r"japan", "etiquette": r"bow|shoes|chopstick|tipping|etiquette|respect"},
 "p-tv-12": {"Puno": r"puno", "bus/train": r"\bbus|train|perurail", "altitude": r"altitude|soroche|3,8\d\d|3\.8 ?km|elevation"},
}
for run in sys.argv[1:]:
    print(f"\n=== {run}")
    for l in open(run):
        t = json.loads(l); ev = [e for e in t["events"] if e.get("type") == "sources"]; pre = ev[-1]["sources"] if ev else []
        txt = "\n".join(s.get("text", "") for s in pre).lower()
        f = FACETS[t["itemId"]]; got = [k for k, rx in f.items() if re.search(rx, txt)]
        codes = [c for c in t["route"]["reasonCodes"] if c.startswith(("context:", "grounding:"))]
        print(f"{t['itemId']} task={t['route']['task']} declined={t['answer']['declined']}\n   raw={[s['title'] for s in t['retrieval']['raw']]}\n   pre={[s['title'] for s in pre]}"
              f"\n   facets in pre text {len(got)}/{len(f)}: {got}  {codes}\n   answer: {t['answer']['text'][:220]!r}")
