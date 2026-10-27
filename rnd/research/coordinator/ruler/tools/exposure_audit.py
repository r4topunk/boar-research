#!/usr/bin/env python3
"""CV5-EXPOSURE-AUDIT: enumerate every judged or generated run since 2026-10-06 outside blind/ and
rnd/veil, hash its id set, classify the set, and diff against EXPOSURES.md rows.
0 LLM, 0 judge. Criterion: ruler/CV5-criterion.md.

Text safety: item ids, judge model and createdAt are pulled from each raw line by regex; no line is
json-parsed and no question/answer/reference text is kept or printed. v0.4 ids come from
boar-eval/bench/v0.4/items.jsonl by the same id-only regex.

Usage: python3 exposure_audit.py [--json OUT.json] [--table OUT.md] [--since 2026-10-06]
"""
import collections, datetime, glob, hashlib, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
WALK = ['rnd', 'boar-eval/runs', 'boar-eval/reports', 'boar-eval/adapters', 'handoff', 'bench-app', 'deep']
SKIP_DIRS = {'blind', 'veil', 'node_modules', '.git', 'archive'}
ID_RE = re.compile(r'"(?:queryId|itemId|item_id|qid)"\s*:\s*"([^"]{1,80})"')
JM_RE = re.compile(r'"judgeModel"\s*:\s*"([^"]{1,80})"')
V01_PREFIX = re.compile(r'^(dng|food|lan-(cmp|exp|hlt|ref|rsn)|trv|vit-(cry|hlt|hum|sci|trv))-\d')
V01_ALLOWED_EXTRA = re.compile(r'^(dng|food|lan|trv|vit)-')


def ids_v04():
    p = os.path.join(ROOT, 'boar-eval/bench/v0.4/items.jsonl')
    out = set()
    for line in open(p):
        m = re.search(r'"id"\s*:\s*"([^"]+)"', line)
        if m:
            out.add(m.group(1))
    return out


def classify_id(i, v04):
    if i in v04 or re.match(r'^c[wx]-\d{3}$', i):
        return 'v0.4'
    if i.startswith('vpara-'):
        return 'V-para'
    if i.startswith('v02-'):
        return 'v0.2'
    if i.startswith('st-qa-cooking-se') or i.startswith('st-qa-money-se'):
        return 'selftest-cm'
    if i.startswith('st-safepack'):
        return 'safepack'
    if i.startswith('st-'):
        return 'selftest'
    if V01_PREFIX.match(i):
        return 'v0.1'
    if re.match(r'^ls\d', i):
        return 'longsession'
    if i.startswith('exp-'):
        return 'rivalset'
    return 'other:' + re.sub(r'[-_]?\d.*$', '', i)[:16]


HELDOUT = {'v0.4', 'V-para', 'v0.2'}


def set_label(counter):
    keys = set(counter)
    if keys <= {'v0.1', 'selftest-cm'} and 'selftest-cm' in keys and 'v0.1' in keys:
        return 'MAIN (v0.1 + cooking/money SE)'
    if keys <= {'selftest', 'selftest-cm'}:
        return 'self-tests'
    if len(keys) == 1:
        return next(iter(keys))
    return '+'.join(sorted(keys))


def kind_of(name):
    n = name.lower()
    if 'judgment' in n:
        return 'judge'
    if 'traces' in n or n == 'rows.jsonl' or 'answers' in n:
        return 'generate'
    return None


def arm_of(rel):
    parts = rel.split('/')
    if 'arms' in parts:
        k = parts.index('arms')
        return parts[k + 1]
    if parts[0] == 'boar-eval' and parts[1] == 'runs':
        return '/'.join(parts[2:4])
    if 'ruler' in parts:
        k = parts.index('ruler')
        return 'ruler/' + parts[k + 1]
    return '/'.join(parts[:3])


def run_stem(name):
    return re.sub(r'\.(judgments|traces)[^/]*$|\.jsonl$', '', name)


def walk(since):
    for top in WALK:
        base = os.path.join(ROOT, top)
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn if d not in SKIP_DIRS and not d.endswith('.shards')]
            if '/rnd/veil' in dp or '/blind' in dp:
                continue
            for f in fn:
                if not f.endswith('.jsonl'):
                    continue
                k = kind_of(f)
                if not k:
                    continue
                p = os.path.join(dp, f)
                mt = datetime.datetime.fromtimestamp(os.path.getmtime(p))
                if mt.date() < since:
                    continue
                yield p, k, mt


def scan(since):
    v04 = ids_v04()
    runs = []
    for p, k, mt in walk(since):
        ids, models, nrows = [], collections.Counter(), 0
        with open(p, errors='replace') as fh:
            for line in fh:
                m = ID_RE.search(line)
                if not m:
                    continue
                nrows += 1
                ids.append(m.group(1))
                if k == 'judge':
                    jm = JM_RE.search(line)
                    models[jm.group(1) if jm else 'unknown'] += 1
        if not ids:
            continue
        uid = sorted(set(ids))
        cls = collections.Counter(classify_id(i, v04) for i in uid)
        rel = os.path.relpath(p, ROOT)
        runs.append(dict(path=rel, arm=arm_of(rel), run=run_stem(os.path.basename(p)), kind=k, date=mt.strftime('%Y-%m-%d'),
                         n_ids=len(uid), rows=nrows, set=set_label(cls), classes=dict(cls),
                         idset_sha=hashlib.sha256('\n'.join(uid).encode()).hexdigest()[:12],
                         judge=dict(models), v04_ids=sorted(i for i in uid if classify_id(i, v04) == 'v0.4')))
    return runs


def ledger_rows():
    rows = []
    for line in open(os.path.join(ROOT, 'rnd/research/coordinator/EXPOSURES.md')):
        if line.startswith('|') and not line.startswith('|---'):
            rows.append(line)
    return rows


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


SET_KEYS = {'V-para': ['V-para', 'v-para', 'vpara'], 'v0.2': ['bench-v02', 'v0.2'], 'v0.4': ['v0.4'],
            'v0.1': ['v0.1'], 'MAIN (v0.1 + cooking/money SE)': ['main 97', 'main97', 'v0.1'], 'self-tests': ['selftest', 'self-test', 'cand80'],
            'longsession': ['longsession'], 'rivalset': ['rivalset'], 'safepack': ['safepack']}


def matched(arm, setname, rows):
    a = norm(arm.split('/')[-1])
    keys = SET_KEYS.get(setname, [setname.lower()])
    hits = []
    for r in rows:
        rl = r.lower()
        if a and a in norm(r) and any(k in rl for k in keys):
            hits.append(r[:80])
    return hits


def tool_field_audit():
    """Which v0.4 fields do ruler tools read? grep only (code is ours)."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'rnd/research/coordinator/ruler/tools/*.py'))):
        src = open(f).read()
        if 'items.jsonl' not in src or os.path.basename(f) == 'exposure_audit.py':
            continue
        fields = sorted(set(re.findall(r"""\[['"]([a-zA-Z_]+)['"]\]|\.get\(['"]([a-zA-Z_]+)['"]""", src)) and
                        {a or b for a, b in re.findall(r"""\[['"]([a-zA-Z_]+)['"]\]|\.get\(['"]([a-zA-Z_]+)['"]""", src)})
        out[os.path.basename(f)] = dict(mentions_v04='v0.4' in src, fields=fields)
    return out


def main():
    args = sys.argv[1:]
    since = datetime.date.fromisoformat(args[args.index('--since') + 1]) if '--since' in args else datetime.date(2026, 10, 6)
    runs = scan(since)
    rows = ledger_rows()
    groups = collections.OrderedDict()
    for r in sorted(runs, key=lambda x: (x['set'] not in HELDOUT, x['arm'], x['date'])):
        key = (r['arm'], r['set'])
        g = groups.setdefault(key, dict(arm=r['arm'], set=r['set'], heldout=r['set'] in HELDOUT or any(c in HELDOUT for c in r['classes']),
                                        dates=set(), gen_runs=0, judge_files=0, judge_calls=collections.Counter(), idsets=set(), n_ids_max=0, paths=[]))
        g['dates'].add(r['date'])
        g['idsets'].add(r['idset_sha'])
        g['n_ids_max'] = max(g['n_ids_max'], r['n_ids'])
        if r['kind'] == 'generate':
            g['gen_runs'] += 1
        else:
            g['judge_files'] += 1
            for m, c in r['judge'].items():
                g['judge_calls'][m] += c
        if len(g['paths']) < 3:
            g['paths'].append(r['path'])
    out = []
    for (arm, st), g in groups.items():
        hits = matched(arm, st, rows)
        out.append(dict(arm=arm, set=st, heldout=g['heldout'], dates=sorted(g['dates']), gen_runs=g['gen_runs'], judge_files=g['judge_files'],
                        judge_calls=dict(g['judge_calls']), idset_shas=sorted(g['idsets']), n_ids_max=g['n_ids_max'], example_paths=g['paths'],
                        ledger_rows=len(hits), ledger_match=hits[:2]))
    v04_runs = [r for r in runs if r['v04_ids']]
    summary = dict(files=len(runs), groups=len(out), heldout_groups=sum(1 for o in out if o['heldout']),
                   heldout_unlogged=[(o['arm'], o['set']) for o in out if o['heldout'] and not o['ledger_rows']],
                   dev_unlogged=sum(1 for o in out if not o['heldout'] and not o['ledger_rows']),
                   v04_run_files=[r['path'] for r in v04_runs], tool_fields=tool_field_audit())
    per_set = collections.Counter()
    for o in out:
        if o['heldout'] and not o['ledger_rows']:
            per_set[o['set']] += 1
    summary['heldout_unlogged_per_set'] = dict(per_set)
    summary['kill'] = bool(v04_runs) or any(v >= 3 for v in per_set.values())
    if '--json' in args:
        json.dump(dict(criterion='ruler/CV5-criterion.md', since=str(since), summary=summary, groups=out,
                       runs=[{k: v for k, v in r.items()} for r in runs]), open(args[args.index('--json') + 1], 'w'), indent=1)
    if '--table' in args:
        with open(args[args.index('--table') + 1], 'w') as f:
            f.write('| arm | set | held-out | dates | gen files | judge files | judge calls (rows) | id-set sha(s) | max ids | ledger rows |\n|---|---|---|---|---|---|---|---|---|---|\n')
            for o in out:
                jc = ', '.join('%s %d' % (m.replace('claude-', ''), c) for m, c in sorted(o['judge_calls'].items()))
                f.write('| %s | %s | %s | %s | %d | %d | %s | %s | %d | %d |\n' % (
                    o['arm'], o['set'], 'yes' if o['heldout'] else '', ' '.join(d[5:] for d in o['dates']), o['gen_runs'], o['judge_files'], jc or '-',
                    ' '.join(o['idset_shas'][:3]) + (' +%d' % (len(o['idset_shas']) - 3) if len(o['idset_shas']) > 3 else ''), o['n_ids_max'], o['ledger_rows']))
    if '--proposed' in args:
        per_arm = collections.OrderedDict()
        for o in out:
            if o['ledger_rows']:
                continue
            pa = per_arm.setdefault(o['arm'], dict(sets=set(), dates=set(), gen=0, jf=0, calls=collections.Counter(), heldout=False))
            pa['sets'].add(o['set']); pa['dates'].update(o['dates']); pa['gen'] += o['gen_runs']; pa['jf'] += o['judge_files']
            pa['heldout'] |= o['heldout']
            for m, c in o['judge_calls'].items():
                pa['calls'][m] += c
        with open(args[args.index('--proposed') + 1], 'w') as f:
            f.write('| date | set | event/arm | kind | items/seeds | judge | who saw what | status after | source |\n|---|---|---|---|---|---|---|---|---|\n')
            for arm, pa in sorted(per_arm.items(), key=lambda kv: (not kv[1]['heldout'], min(kv[1]['dates']), kv[0])):
                ds = sorted(pa['dates']); dr = ds[0][5:] + ('..' + ds[-1][5:] if ds[-1] != ds[0] else '')
                kind = ' + '.join(k for k, v in (('generate', pa['gen']), ('judge', pa['jf'])) if v)
                calls = ', '.join('%s %d rows' % (m.replace('claude-', ''), c) for m, c in sorted(pa['calls'].items())) or 'none'
                f.write('| %s | %s | %s (CV5 audit backfill) | %s | %d generation files, %d judgment files | %s | script/agent outputs outside blind/; ids+counts in this audit | %s | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; %s |\n' % (
                    dr, '; '.join(sorted(pa['sets'])), arm, kind, pa['gen'], pa['jf'], calls,
                    'CHECK (held-out ids outside blind/)' if pa['heldout'] else 'dev (unchanged)', 'arms/' + arm if '/' not in arm else arm))
    print(json.dumps({k: v for k, v in summary.items() if k != 'tool_fields'}, indent=1)[:4000])
    print(json.dumps(summary['tool_fields'], indent=1))


if __name__ == '__main__':
    main()
