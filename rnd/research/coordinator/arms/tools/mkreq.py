import json,sys
# usage: mkreq.py name arm items.jsonl(id,question) > out
name,arm,src=sys.argv[1:4]
for l in open(src):
    r=json.loads(l)
    print(json.dumps({"protocol":"1.0.0","runId":name,"item":{"id":r["id"],"question":r.get("question") or r.get("text"),"lang":"en"},
      "config":{"commit":"0cfd4a77","arm":arm,"modelId":"qwen3-4b-instruct-2507-q4km","settings":{"quickFirst":True,"alwaysComplete":False},
      "kit":[{"id":"boar-crypto","sha256":"ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb"},{"id":"boar-wikivoyage-en","sha256":"ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e"}],
      "device":{"platform":"android","ramGb":12.0},"seed":42},"seed":42}))
