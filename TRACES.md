# Run traces (Hugging Face)

The raw run data of every experiment (answer traces, judge requests and judgments, retrieval replays: the `.jsonl` files, about 825 MB) is published as a separate dataset so that this repository stays light:

**https://huggingface.co/datasets/r4topunk/boar-traces**

The dataset keeps the exact same paths as this repository. A file listed in [`TRACES.tsv`](TRACES.tsv) at `rnd/research/coordinator/arms/<arm>/...` lives at the same path in the dataset, with the sha256 given there.

Fetch the traces of one experiment next to its report and tools:

```bash
pip install -U huggingface_hub
hf download r4topunk/boar-traces --repo-type dataset \
  --include "rnd/research/coordinator/arms/headpass-st/**" --local-dir .
```

Fetch everything: drop `--include`. Verify: `python3 tools/verify-traces.py` checks every downloaded file against `TRACES.tsv`.

What is not in the dataset either: traces and judgments that embed held-out item text (removed before publication; see `docs/EXCLUDED.md`).
