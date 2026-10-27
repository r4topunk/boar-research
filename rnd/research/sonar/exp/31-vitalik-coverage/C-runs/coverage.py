import sqlite3, math, json, glob, os, collections
T="<workspace>/shared-data/poi/geofabrik/work/tiles"
G=sqlite3.connect("<workspace>/shared-data/poi/world-places-tiles.sqlite")
idx={r[0]:r for r in G.execute("select id,size_bytes,pois,vegan from tiles")}
def tid(la,lo):
    la=math.floor(la); lo=math.floor(lo)
    return f"t-{'N' if la>=0 else 'S'}{abs(la):02d}{'E' if lo>=0 else 'W'}{abs(lo):03d}"
def tiles_for(lat,lon,km):
    dLat=km/111.195; dLon=dLat/max(0.01,math.cos(math.radians(lat)))
    s=set()
    for la in range(math.floor(lat-dLat), math.floor(lat+dLat)+1):
        for lo in range(math.floor(lon-dLon), math.floor(lon+dLon)+1):
            s.add(tid(la,lo))
    return sorted(s)
def dist(a,b,c,d):
    r=math.pi/180; h=math.sin((c-a)*r/2)**2+math.cos(a*r)*math.cos(c*r)*math.sin((d-b)*r/2)**2
    return 2*6371000*math.asin(min(1,math.sqrt(h)))
def resolve(name):
    return G.execute("select p.name,p.lat,p.lon,p.country,p.population from names n join places p on p.id=n.place_id where n.name=? collate nocase order by p.population desc limit 1",(name,)).fetchone()
cities=["Berlin","Rome","Tokyo","Lisbon","São Paulo","Mexico City","Bangkok","New York City","London","Chiang Mai","Kathmandu","Nairobi","Qujing"]
FOOD=("restaurant","cafe","fast_food","food_court","bar","pub","biergarten","ice_cream","bakery","deli","confectionery","pastry","listing")
out=[]
for c in cities:
    r=resolve(c)
    if not r: out.append({"city":c,"resolved":None}); continue
    name,lat,lon,cc,pop=r
    ts=tiles_for(lat,lon,15)
    present=[t for t in ts if os.path.exists(f"{T}/{t}.sqlite")]
    size=sum(idx[t][1] for t in present if t in idx)
    stats={}
    for R in (3000,10000,25000):
        tot=veg=vonly=vyes=vlim=vcuis=vegt=doubt=0; cats=collections.Counter(); restaurant_v=0
        for t in present:
            db=sqlite3.connect(f"{T}/{t}.sqlite")
            for (la,lo,cat,cu,v,vg,dc,dcf,approx,src) in db.execute("select lat,lon,category,cuisine,vegan,vegetarian,diet_check,diet_check_for,approx,source from pois where category in (%s)"%",".join("?"*len(FOOD)),FOOD):
                if dist(lat,lon,la,lo)>R: continue
                tot+=1
                if v and v!="no":
                    veg+=1; cats[cat]+=1
                    if v=="only": vonly+=1
                    elif v=="yes": vyes+=1
                    elif v=="limited": vlim+=1
                    if cu and "vegan" in cu.split(";"): vcuis+=1
                    if dc is not None and dcf=="vegan" and dc<0.35: doubt+=1
                    if cat=="restaurant": restaurant_v+=1
                if vg and vg!="no": vegt+=1
        stats[R]=dict(food=tot,vegan=veg,only=vonly,yes=vyes,limited=vlim,cuisine_vegan=vcuis,doubtful=doubt,vegetarian=vegt,vegan_restaurants=restaurant_v,vegan_by_cat=dict(cats.most_common(6)))
    out.append({"city":c,"resolved":name,"cc":cc,"pop":pop,"lat":lat,"lon":lon,"tiles15km":ts,"tilesPresent":len(present),"tilesMB":round(size/1e6,1),"stats":stats})
print(json.dumps(out,ensure_ascii=False,indent=1))
