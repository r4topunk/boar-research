# Disk policy — BOAR R&D (Mac mini + MacBook)

TL;DR: anything that can be rebuilt from git + a recorded source is deleted as soon as its line is closed. The disk alarm fires below 25 GiB free; the target is ≥ 40 GiB. Kiln runs the GC, and every deletion is logged.

```fish
# dry run (lists candidates by class, deletes nothing)
<on the mini> '<runner>/kiln/disk-gc.sh --dry-run'
# apply classes A+B (standing approval from r4to, 2026-10-02)
<on the mini> '<runner>/kiln/disk-gc.sh --apply A,B'
```

## Scope

- **In scope:** Mac mini `<runner>/**`; MacBook `<workspace>/builds`, `wt/` and the session scratchpads.
- **Never touched:** anything outside those paths, Docker (images, volumes, the `a database container` container), `blind/`, `rnd/veil/`, git repos' tracked files, or the phone. Phone deletions still need r4to's per-item OK.

## Classes

| Class | What | Rule | Approval |
|---|---|---|---|
| **A: closed lines** | Model weights, packs, or arm trees whose verdict is in `rnd/research/QUEUE.md` as FAIL / KILL / K-fired / NOT ADOPTED | Delete once the patch + sha256 (for arms) or the source URL + sha256 (for weights/data) is recorded in git | Standing (r4to 2026-10-02) |
| **B: reproducible build output** | `kiln/be-<sha>-<arm>` trees of adopted arms (patch committed), `app-<sha>*` trees of old engine commits, superseded APKs (keep the latest per variant), `e2e-out`, run scratch older than 7 days whose numbers are in a committed report | Delete | Standing |
| **C: shared caches** | `~/.gradle/caches`, `~/Library/pnpm`, `~/.npm`, Xcode DerivedData | Prune only when below the floor, since a rebuild costs time | Coordinator decides |
| **D: active** | Base tree `be-<current main>`, arms with open device steps (now: p7b, p8-sqlbatch), models in use (1.5B, 4B, bge-small, deep35 while the deep tier is open), current packs, `android/boar-app` | Keep | — |
| **E: unknown** | Anything Kiln can't map to a QUEUE line | List it and ask r4to | r4to |

## Process

1. **When:** Kiln runs the GC after each L2/L3 verdict, and whenever free space < 25 GiB.
2. **Before deleting:** check that the item is closed in QUEUE, and that its reproduction recipe (patch + sha, or URL + sha) is in git.
3. **Log every deletion** in `rnd/kiln/DISK-LOG.md`: path, size, class, the QUEUE line, how to restore.
4. **Recipes:** a model being deleted gets a line in `rnd/kiln/MODELS.md` (repo/URL, file, sha256) first.
