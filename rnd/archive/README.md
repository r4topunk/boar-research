# Archive of unpushed boar-app work (2026-10-03)

Our experiment branches and worktrees live in the boar-app fork, which is PUBLIC (r4topunk/boar-app). We don't push them there. They are archived in this private repo instead.

- `boar-app-wip.bundle`: every worktree HEAD that is not on a remote, stored as `refs/archive/<worktree>`. To restore: `git -C boar-app fetch /path/to/boar-app-wip.bundle 'refs/archive/*:refs/archive/*'`.
- `wt-dirty/<name>.patch` + `.base` + `.untracked.tgz`: uncommitted changes of each dirty worktree (diff against its HEAD, base sha, untracked files < 2 MB, no node_modules).
- `bench-app.bundle`: the full BOAR Bench repo (no remote yet). To restore: `git clone bench-app.bundle bench-app`.

Refresh: rerun the archive script in rnd/research/QUEUE.md (2026-10-03 entry), or ask the coordinator.
