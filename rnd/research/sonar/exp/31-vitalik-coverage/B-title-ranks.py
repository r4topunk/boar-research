import json,urllib.request,urllib.parse,bisect
titles=["Mozi","Mohism","Mozi (book)","Mencius","Jian'ai","Post-quantum cryptography","ML-KEM","ML-DSA","SPHINCS+","Lamport signature","Hash-based cryptography","Lattice-based cryptography","Falcon (signature scheme)","Japan","Tourism in Japan","Rail transport in Japan","Japan Rail Pass","Climate of Japan","Etiquette in Japan","Visa policy of Japan","Visa requirements for United States citizens","Visa requirements for Brazilian citizens","Schengen Area","Veganism","Altitude sickness","Inca Trail to Machu Picchu","Trans-Siberian Railway","Quadratic funding","Vitalik Buterin","Ethereum","Proof of stake","Zero-knowledge proof","Kazakhstan","Bhutan","Visa policy of China","Tipping","Shinkansen"]
ids={}
for i in range(0,len(titles),40):
  q=urllib.parse.urlencode({"action":"query","titles":"|".join(titles[i:i+40]),"redirects":1,"format":"json"})
  r=urllib.request.Request("https://en.wikipedia.org/w/api.php?"+q,headers={"User-Agent":"boar-research/0.1 (offline-research-bench)"})
  d=json.load(urllib.request.urlopen(r))["query"]
  norm={x["from"]:x["to"] for x in d.get("normalized",[])+d.get("redirects",[])}
  for p in d["pages"].values():
    ids[p["title"]]=int(p.get("pageid",-1))
pv={}
for l in open("<workspace>/shared-data/dumps/pageviews-en-20250815.tsv"):
  a,b=l.split("\t");pv[int(a)]=int(b)
vs=sorted(pv.values(),reverse=True); neg=[-v for v in vs]
for t in titles:
  tt=t
  pid=ids.get(tt)
  if pid is None:
    # find via redirect: look for matching
    pid=next((v for k,v in ids.items() if k.lower()==t.lower()),-1)
  v=pv.get(pid,0); rank=bisect.bisect_left(neg,-v)+1 if v else None
  print(f"{t}\tpid={pid}\tviews={v}\trank={rank}")
