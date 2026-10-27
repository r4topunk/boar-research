#!/usr/bin/env python3
"""exp-08b: before/after on vitalik58 (exp-06 harness, P2 config).

Usage: python3 compare.py BEFORE.jsonl AFTER.jsonl [label_before label_after]
Prints a markdown block: summary table, changed items, verdict.

FAIL (rule from the request) = any increase in declines or in answers without shown sources,
or any item that showed a source before and shows none after.
"""
import json, statistics, sys


def load(p):
    return {r["id"]: r for r in map(json.loads, open(p))}


def declined(r):
    return bool((r.get("flags") or {}).get("declined"))


def weak(r):
    return bool((r.get("flags") or {}).get("weak_sources"))


def shown(r):
    return [s["title"] for s in r.get("shownSources") or []]


def pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))]


def summary(rows):
    rs = list(rows.values())
    tiers = {}
    for r in rs:
        tiers[str(r.get("tier"))] = tiers.get(str(r.get("tier")), 0) + 1
    rec = [r.get("receipt") or {} for r in rs]
    return {
        "n": len(rs),
        "errors": sum(1 for r in rs if r.get("error")),
        "declined": sum(map(declined, rs)),
        "weak": sum(map(weak, rs)),
        "noshown": sum(1 for r in rs if not shown(r)),
        "tiers": dict(sorted(tiers.items())),
        "ttft50": pct([x.get("ttftMs") for x in rec], 0.5),
        "ttft95": pct([x.get("ttftMs") for x in rec], 0.95),
        "tot50": pct([x.get("totalMs") for x in rec], 0.5),
        "tot95": pct([x.get("totalMs") for x in rec], 0.95),
        "ret50": pct([x.get("retrievalMs") for x in rec], 0.5),
    }


def fmt_ms(v):
    return "—" if v is None else f"{v / 1000:.1f} s"


def codes(r):
    return sorted(set(r.get("reasonCodes") or []))


def main():
    a, b = load(sys.argv[1]), load(sys.argv[2])
    la = sys.argv[3] if len(sys.argv) > 3 else "before"
    lb = sys.argv[4] if len(sys.argv) > 4 else "after"
    ids = [i for i in a if i in b]
    sa, sb = summary({i: a[i] for i in ids}), summary({i: b[i] for i in ids})
    out = []
    out.append(f"| | {la} | {lb} |\n|---|---|---|")
    out.append(f"| items (shared) | {sa['n']} | {sb['n']} |")
    out.append(f"| errors | {sa['errors']} | {sb['errors']} |")
    out.append(f"| declined | {sa['declined']}/{sa['n']} | {sb['declined']}/{sb['n']} |")
    out.append(f"| weak_sources | {sa['weak']}/{sa['n']} | {sb['weak']}/{sb['n']} |")
    out.append(f"| no shown sources | {sa['noshown']}/{sa['n']} | {sb['noshown']}/{sb['n']} |")
    out.append(f"| tier | {sa['tiers']} | {sb['tiers']} |")
    out.append(f"| TTFT p50 / p95 (desktop) | {fmt_ms(sa['ttft50'])} / {fmt_ms(sa['ttft95'])} | {fmt_ms(sb['ttft50'])} / {fmt_ms(sb['ttft95'])} |")
    out.append(f"| total p50 / p95 (desktop) | {fmt_ms(sa['tot50'])} / {fmt_ms(sa['tot95'])} | {fmt_ms(sb['tot50'])} / {fmt_ms(sb['tot95'])} |")
    out.append(f"| retrieval p50 (desktop) | {fmt_ms(sa['ret50'])} | {fmt_ms(sb['ret50'])} |")

    worse, better, other = [], [], []
    for i in ids:
        x, y = a[i], b[i]
        ch = []
        if declined(x) != declined(y):
            ch.append(f"declined {declined(x)}→{declined(y)}")
        if bool(shown(x)) != bool(shown(y)):
            ch.append(f"shown {len(shown(x))}→{len(shown(y))}")
        elif set(shown(x)) != set(shown(y)):
            ch.append(f"shown titles changed ({len(shown(x))}→{len(shown(y))})")
        if x.get("tier") != y.get("tier"):
            ch.append(f"tier {x.get('tier')}→{y.get('tier')}")
        if not ch:
            continue
        line = (f"| `{i}` | {'; '.join(ch)} | {', '.join(codes(x)) or '—'} | {', '.join(codes(y)) or '—'} | "
                f"{' · '.join(shown(x)) or '—'} | {' · '.join(shown(y)) or '—'} |")
        is_worse = (not declined(x) and declined(y)) or (shown(x) and not shown(y))
        is_better = (declined(x) and not declined(y)) or (not shown(x) and shown(y))
        (worse if is_worse else better if is_better else other).append(line)

    hdr = f"| id | change | codes {la} | codes {lb} | shown {la} | shown {lb} |\n|---|---|---|---|---|---|"
    for name, lst in (("Worse", worse), ("Better", better), ("Other changes (same decline/source status)", other)):
        out.append(f"\n**{name}: {len(lst)}**\n")
        if lst:
            out.append(hdr)
            out.extend(lst)

    lost_source = sum(1 for i in ids if shown(a[i]) and not shown(b[i]))
    fail = sb["declined"] > sa["declined"] or sb["noshown"] > sa["noshown"] or lost_source > 0 or sb["errors"] > 0
    out.append(f"\n**Rule check:** declined {sa['declined']}→{sb['declined']} · no shown sources {sa['noshown']}→{sb['noshown']} · "
               f"items that lost their shown source: {lost_source} · errors {sb['errors']} → **{'FAIL' if fail else 'PASS'}**")
    print("\n".join(out))


if __name__ == "__main__":
    main()
