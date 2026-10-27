#!/bin/bash
# RC1-LABS: run the v2.0.0-rc1 Labs tool slot on the 51 CV5 questions (0 LLM, MacBook).
set -euo pipefail
B=<workspace>; ARM=$B/rnd/research/coordinator/arms/native-parity; W=$ARM/work/labs; TAG=v2.0.0-rc1
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
GRADLE=$(ls -d $HOME/.gradle/wrapper/dists/gradle-8.14.3-bin/*/gradle-8.14.3)/bin/gradle
rm -rf $W && mkdir -p $W/tag
git -C $B/boar-app archive $TAG android-native/engine/src/main/java android-native/app/src/labs/plugins/facts/res/raw android-native/app/src/labs/plugins/distance/res/raw | tar -x -C $W/tag
export ENGINE_SRC=$W/tag/android-native/engine/src/main/java BUILD_DIR=$W/build
cd $ARM/tools/harness-labs && $GRADLE -q --no-daemon installDist
FACTS=$W/tag/android-native/app/src/labs/plugins/facts/res/raw/lab_facts_facts_v1.json
CITIES=$W/tag/android-native/app/src/labs/plugins/distance/res/raw/lab_distance_world_cities_v1.json
shasum -a 256 $FACTS $CITIES
$W/build/install/rc1-labs-harness/bin/rc1-labs-harness --questions $ARM/work/questions-cv5-51.jsonl --facts $FACTS --cities $CITIES --out $ARM/runs/rc1-labs-tools.jsonl
