import json,sys
S=sys.argv[1]
P={json.loads(l)['id']:json.loads(l) for l in open('probes.jsonl')}
for l in open(f'{S}/replay/tf.traces.jsonl'):
  r=json.loads(l); p=P[r['itemId']]; rc=r['route']['reasonCodes']
  a=(r.get('answer') or {}).get('text','') if isinstance(r.get('answer'),dict) else ''
  route='places' if 'task:places' in rc else 'travel' if any('travel-distance' in c for c in rc) else ('model' if 'Stub' in a else 'other:'+','.join(c for c in rc if c.startswith('answer:'))[:40])
  ok='OK' if route==p['expect'] else 'XX'
  print(ok, p['id'], '|', p['question'][:52], '| ->', route, [c for c in rc if c.startswith(('places:','diet','near'))][:4], '|', a.split('\n')[0][:120] if route!='model' else '')
