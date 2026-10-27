# Frozen-criterion pins that do not verify, and why

TL;DR: `python3 tools/verify-criteria.py` checks every `*criterion*.sha256` / `*rule*.sha256` pin under `rnd/` (the last line of each file; whole file, or the text through `END FROZEN`). The pins below do not verify on the released bytes. None of them changes a verdict: the criterion text was frozen before its run in the private record; what differs is redaction or an old record defect. For redacted files, `docs/REDACTION-HASHES.tsv` gives the original and the released whole-file sha256.

| pin file | target | original whole-file sha256 of the target (private) | reason |
|---|---|---|---|
| `rnd/research/coordinator/arms/followup/FOLLOWUP-R2-criterion.sha256` | `rnd/research/coordinator/arms/followup/FOLLOWUP-R2-criterion.md` | `e28d65636c7ee00ec6290dad5dfd5f8f20201c0173f0c6fdd2b90b8fb390bb48` | pre-existing record defect: the pin did not match the private file either |
| `rnd/research/coordinator/arms/lossmap/LOSSMAP-criterion.sha256` | `rnd/research/coordinator/arms/lossmap/LOSSMAP-criterion.md` | `61d6047363cf9f1b7b4a766ef7781a92c3cb032284efc55585f72f29f4d06f7d` | the criterion text was redacted (names, paths or usage lines) and the pin is a partial or earlier-version hash; the original whole-file sha256 is in `docs/REDACTION-HASHES.tsv` |
| `rnd/research/coordinator/arms/healthgap/HEALTHGAP-rule-v1.1.sha256` | `rnd/research/coordinator/arms/healthgap/HEALTHGAP-rule-v1.1.md` | `3cddebd8208fa8fd938b01810cc8a28b333291a513abbeeb01c1e0670b1244d2` | partial pin (through `END FROZEN`) of the private original; redaction changed a path and a hash prefix inside the frozen part |
| `rnd/research/coordinator/arms/lite5/LITE5-criterion.v1.sha256` | `rnd/research/coordinator/arms/lite5/LITE5-criterion.v1.md` | `7fa005dab3bebd09d7ed6b627c336eeac766e758ccbbcd2c982fc52078b686a7` | pins version 1 of the criterion; the file was later revised and then redacted, so v1 bytes are not in the record |

Pins whose target file is not in this release (excluded, or a name mismatch in the record):

- `rnd/research/coordinator/ruler/RULER-SPEC-v1-r3.sha256` -> `rnd/research/coordinator/ruler/RULER-SPEC-v1-r3-2026-10-21.md`
- `rnd/research/coordinator/ruler/RULER-SPEC-v1-r4.sha256` -> `rnd/research/coordinator/ruler/RULER-SPEC-v1-r4-2026-10-21.md`
- `rnd/research/coordinator/arms/deepread/DEEPREAD-criterion.sha256` -> `rnd/research/coordinator/arms/deepread/FACTS-criterion.md`

`rnd/research/coordinator/BAR-TABLE.sha256` keeps one line per historical version of the table; only the last line is the current pin (earlier lines are earlier versions, see `RULE-CHANGES.md`).
