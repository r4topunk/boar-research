import json,sys
for l in open(sys.argv[1]):
    t=json.loads(l); ti=t['timing']; h=[e for e in t['events'] if e.get('kind')=='history']
    print(t['itemId'], 'err' if t['error'] else 'ok', 'pt',ti.get('promptTokens'),'ms',round(ti.get('totalMs') or 0),'hist',h[0]['turns'] if h else 0, t['route']['task'], '|', t['answer']['text'][:110].replace(chr(10),' '))
