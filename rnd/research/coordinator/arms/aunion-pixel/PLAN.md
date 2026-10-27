# AUNION-PIXEL / PK-5: resume steps (pending a coordinator decision; PK5-criterion.md gate failed at step 1, 83.5 pct < 95 pct)

Phone state now: A-union installed (files/corpus: 6 packs; files/poi/world-places.sqlite), shas verified 03:3x. Merged file: <workspace>/shared-data/packs/persona-a-union-merged/boar-aunion-merged.sqlite (sha 7e86674b...).
Only if the coordinator overrides the gate (new frozen criterion first, committed):
```
export PATH=$HOME/Library/Android/sdk/platform-tools:$PATH; P=team.sopa.boarbench; B=<workspace>/handoff/pixel8-2026-10-20/bench
adb exec-out run-as $P sh -c 'ls -l files/corpus files/poi'                                   # before
adb shell am force-stop $P
adb shell run-as $P sh -c 'mkdir -p files/corpus-off && mv files/corpus/boar-*.sqlite files/corpus-off/'
printf '%s corpus/boar-aunion-merged.sqlite\n' <workspace>/shared-data/packs/persona-a-union-merged/boar-aunion-merged.sqlite > $B/merged.kit.txt
bash <workspace>/bench-app/scripts/push-kit.sh $B/merged.kit.txt; bash <workspace>/bench-app/scripts/push-kit.sh $B/merged.kit.txt   # rerun until "= ... (already" (flush race)
python3 -c "import json;r=json.load(open('$B/requests/aunion10-a.request.json'));r['requestId']='merged10-a';json.dump(r,open('$B/requests/merged10-a.request.json','w'),indent=1)"
python3 <workspace>/rnd/research/coordinator/arms/batchret/phone/thermal_gate.py merged10-a 310
cd $B && python3 boar_bench.py run merged10-a
python3 <workspace>/rnd/research/coordinator/arms/aunion-pixel/summarize_aunion.py <workspace>/shared-data/packs/persona-a-union-merged results/merged10-a results/aunion10-a
# restore
adb shell am force-stop $P
adb shell run-as $P sh -c 'rm files/corpus/boar-aunion-merged.sqlite && mv files/corpus-off/boar-*.sqlite files/corpus/ && rmdir files/corpus-off'
adb exec-out run-as $P sh -c 'sha256sum files/corpus/* files/poi/*; ls -l files/corpus files/poi'   # compare with shared-data/packs/persona-a-union/SHA256SUMS
```
