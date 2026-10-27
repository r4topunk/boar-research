import json, sys
for f in sys.argv[1:]:
    for l in open(f):
        t = json.loads(l); a = t["answer"]; r = t["route"]; tm = t["timing"]
        rc = [c for c in r["reasonCodes"] if not c.startswith(("generate:", "offer-deep"))]
        txt = a["text"].replace("\n", " ")
        print(f'## {t["itemId"]} tier={r["tier"]} task={r["task"]} out={tm.get("outputTokens")} pt={tm.get("promptTokens")} declined={a["declined"]} shown={a["shown"]}')
        print("   rc:", " ".join(rc)); print("   A:", txt[:150], "...|END:", txt[-60:])
