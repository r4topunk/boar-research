#!/bin/bash
# DENSECHUNK-ST2 Opus L2 chain: wait for a running st2_opus_l2.sh, re-run it (resumes / skips judged packs), aggregate, append the "Opus L2" section.
# Usage: nohup tools/st2_opus_finish.sh > runs/judge/opus_finish.log 2>&1 < /dev/null &
D=<workspace>/rnd/research/coordinator/arms/densechunk-st
while pgrep -f st2_opus_l2.sh > /dev/null; do sleep 30; done
$D/tools/st2_opus_l2.sh >> $D/runs/judge/opus_l2.log 2>&1
python3 -I $D/tools/st2_opus_agg.py > $D/aggregates/st2-l2-opus.json.tmp || { echo "AGG FAILED (fail-closed; see stderr)"; exit 1; }
mv $D/aggregates/st2-l2-opus.json.tmp $D/aggregates/st2-l2-opus.json
python3 -I - $D/aggregates/st2-l2-opus.json >> $D/DENSECHUNK-ST2.md <<'PY'
import json, sys; d = json.load(open(sys.argv[1])); f = lambda x: f"{x['d_raw']:+.3f} ({x['d_raw_ci'][0]:+.3f}…{x['d_raw_ci'][1]:+.3f})"
P = d["pooled"]; a = d["haiku_vs_opus"]
print(f"\n## Opus L2 (auto-written by tools/st2_opus_finish.sh; judge.v1 claude-opus-5-5, N=4, both orders, 720 calls, same traces as L1; aggregates/st2-l2-opus.json)")
print(f"Pooled 180: raw OFF {P['OFF']['raw']} → ON {P['ON']['raw']}, **paired Δ {f(P['ON_minus_OFF'])}**; above_min {P['OFF']['above_min']} → {P['ON']['above_min']}, Δ {P['ON_minus_OFF']['d_above_min']:+.3f} {P['ON_minus_OFF']['d_above_min_ci']}; better/worse {P['ON_minus_OFF']['items_better_worse']}; win/tie/loss OFF {P['OFF']['win_tie_loss']} ON {P['ON']['win_tie_loss']}.")
print(f"Declared split: topic (n {d['topic']['ON_minus_OFF']['n']}) Δ {f(d['topic']['ON_minus_OFF'])}; SE (n {d['SE']['ON_minus_OFF']['n']}) Δ {f(d['SE']['ON_minus_OFF'])}. Haiku L1 same ids: pooled {f(P['haiku_ON_minus_OFF'])}.")
print("Per pack (Opus): " + "; ".join(f"{p['pack']} {p['OFF']['raw']}→{p['ON']['raw']} Δ{p['ON_minus_OFF']['d_raw']:+.3f}" for p in d["packs"]) + ".")
print(f"Haiku vs Opus: same winner OFF {a['OFF']['winner_same']}/180, ON {a['ON']['winner_same']}/180; ratio Opus/Haiku OFF {a['OFF']['ratio_opus']}/{a['OFF']['ratio_haiku']}, ON {a['ON']['ratio_opus']}/{a['ON']['ratio_haiku']}; per-item score r {a['OFF']['r_boar_score']}/{a['ON']['r_boar_score']}; per-item Δ r {a['item_delta_r']}, sign agree {a['item_delta_sign_agree']}/180.")
print(f"**Verdict (criterion rule on the Opus pooled Δ): {d['verdict']}.** Fail-closed checks passed (180 ids × 2 orders × 2 arms; floor_metrics --strict per pack × arm).")
PY
echo "FINISH-DONE $(date '+%F %T') verdict=$(python3 -c "import json;print(json.load(open('$D/aggregates/st2-l2-opus.json'))['verdict'])")"
