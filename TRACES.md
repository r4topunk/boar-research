# Run traces (Hugging Face)

The raw run data of every experiment (answer traces, judge requests and judgments, retrieval replays: the `.jsonl` files, about 1.06 GB) is published as a separate dataset so that this repository stays light:

**https://huggingface.co/datasets/r4topunk/boar-traces**

The dataset keeps the exact same paths as this repository. A file listed in [`TRACES.tsv`](TRACES.tsv) at `rnd/research/coordinator/arms/<arm>/...` lives at the same path in the dataset, with the sha256 given there.

Fetch the traces of one experiment next to its report and tools:

```bash
pip install -U huggingface_hub
hf download r4topunk/boar-traces --repo-type dataset \
  --include "rnd/research/coordinator/arms/headpass-st/**" --local-dir .
```

Fetch everything: drop `--include`. Verify: `python3 tools/verify-traces.py` checks every downloaded file against `TRACES.tsv`.

**v1.1 (2026-10-27):** the dataset now also holds the raw runs of the retired held-out sets, under `rnd/heldout/<set>/` (bench-v02, vitalik-para1 = V-para, health-fresh1-3, chat-v3, meta-fresh1, localgate, veil-lane), and the 160 files that v1.0 had removed (original paths under `rnd/research/` and `rnd/kiln/`). Fetch one set: `hf download r4topunk/boar-traces --repo-type dataset --include "rnd/heldout/vitalik-para1/**" --local-dir .`. Map and licences: `rnd/heldout/README.md`.

**Content note.** The health, crisis and medical-emergency sets (`health-fresh*`, `chat-v3` safety items, `veil-lane` crisis and hm rounds, `bench-v02` danger/health items, three V-para items) are safety evaluation probes with model answers: AI-reviewed, not clinically reviewed; if you are in crisis, contact local emergency services.

Still not in the dataset: the app maintainer's data, private correspondence, spend ledgers, prompt-hash gateway caches, credentials, unlicensed competitor question sets (`docs/EXCLUDED.md`).
