# Stage 1a (0 LLM): title presence in wiki-vital5 and the essential corpus.
import json, sqlite3
B="<workspace>"; T=B+"/kiln-local/be-0cfd4a77-cut7-litepacks/assets/corpus/"
ANCH={"b1":[["Natural selection","Charles Darwin","Alfred Russel Wallace","On the Origin of Species"]],
"b2":[["Vaccine","Vaccination","Smallpox vaccine","MRNA vaccine","Smallpox"],["Immune system","Adaptive immune system","Immunity (medicine)"]],
"b3":[["Photosynthesis","Calvin cycle","Light-dependent reactions"]],"b4":[["French Revolution"],["Industrial Revolution"]],
"b5":[["Fall of the Western Roman Empire","Western Roman Empire","Decline of the Roman Empire"]],"b6":[["Black hole","Event horizon","Stellar black hole"]],
"b7":[["Napoleon","Napoleon Bonaparte","Napoleonic Wars"]],"b8":[["Antimicrobial resistance","Antibiotic resistance"]],"b9":[["Canberra","Australian Capital Territory"]],
"b10":[["Great Wall of China"]],"b11":[["Polar bear"],["Grizzly bear","Brown bear"]],"b12":[["Brazil","Economy of Brazil"],["Russia","Economy of Russia"]],
"b13":[["Mosquito","Mosquito-borne disease"]],"b14":[["Physical exercise","Exercise","Physical activity","Physical fitness"]],"b15":[["Kyoto","History of Kyoto"]],
"b16":[["Mount Kilimanjaro","Kilimanjaro"]],"b17":[["Berlin Wall","Fall of the Berlin Wall"]],"b18":[["Cheetah"]],
"b19":[["AC power plugs and sockets","Mains electricity by country","Emergency telephone number"]],
"b20":[["Japan","Demographics of Japan","Aging of Japan"],["Germany","Demographics of Germany"],["Population density","Population ageing"]],
"b21":[["Dengue fever","Dengue virus","Dengue"]]}
sug=json.load(open("in/suggestions.json")); EXP={s["key"]:s["expect"] for s in sug["sources"]}
db=sqlite3.connect(B+"/shared-data/packs/wiki-vital5.sqlite")
vt={}; 
for (t,n) in db.execute("select lower(title),count(*) from chunks group by lower(title)"): vt[t]=n
ct=set()
for f in ["corpus","corpus-standard","corpus-full"]:
    for a in json.load(open(T+f+".json")): ct.add(a["title"].lower())
topics=json.load(open("in/topics.json")); out=[]
for r in topics:
    k=r["key"]; groups=[[t] for t in EXP[k]] if k in EXP else ANCH[k]
    tit={t:{"vital5_chunks":vt.get(t.lower(),0),"corpus":t.lower() in ct} for g in groups for t in g}
    gok=[any(tit[t]["vital5_chunks"] or tit[t]["corpus"] for t in g) for g in groups]
    present = any(gok) if k in EXP else all(gok)
    out.append(dict(key=k,kind="expect" if k in EXP else "anchor",groups=groups,titles=tit,groups_ok=gok,present=present,
       vital5_only=(any(tit[t]["vital5_chunks"] for g in groups for t in g) if k in EXP else all(any(tit[t]["vital5_chunks"] for t in g) for g in groups))))
json.dump(out,open("aggregates/titles.json","w"),indent=1)
for o in out: print(o["key"],o["present"],"vital5:",o["vital5_only"],{t:(v["vital5_chunks"],v["corpus"]) for t,v in o["titles"].items() if v["vital5_chunks"] or v["corpus"]})
