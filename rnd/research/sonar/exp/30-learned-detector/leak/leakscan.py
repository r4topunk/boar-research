import json,sys
CR=('Ethereum','Bitcoin','ethereum.org','ERC','EIP','Tornado','Consensus')
for f in sys.argv[1:]:
    n=nc=0
    for l in open(f):
        t=json.loads(l); n+=1
        sh=[str(s) for s in (t['answer'].get('shown') or [])]
        cr=[s for s in sh if not s.startswith('Wikivoyage')]
        rc=t['route']['reasonCodes']; health=any('health' in r for r in rc)
        g=[r for r in rc if r.startswith(('grounding','instant:off','task:'))]
        if cr: nc+=1
        print(f"{t['itemId']} {'H' if health else '-'} decl={int(t['answer']['declined'])} crypto={len(cr)} {[s[:28] for s in cr][:2]} {g[:4]} | {t['question'][:45]} -> {t['answer']['text'][:60]!r}".replace('\n',' '))
    print(f'== {f}: {nc}/{n} items show non-Wikivoyage sources\n')
