# PR-1 split: engine branch + wiring branch (2026-10-15)

Worktree: <workspace>/wt/pr1 (upstream/main = 8fdb665f). Nothing pushed.

| Branch | Tip | Content |
|---|---|---|
| pr/cut7-engine | 3686c453 | 13 cut 7 commits + 8882b175 (test reconcile) + 08b5f623 (= de3d97ac) + 3686c453 (= 570e0716) |
| pr/cut7-wiring | 6643aa9f | pr/cut7-engine + 8a1e7f8e (= a1d75389) + 6643aa9f (= 8b117738) |

Old tip 570e0716 (history before the split) has a tree identical to pr/cut7-wiring (`git diff 570e0716 pr/cut7-wiring` empty).

## Checks
- de3d97ac / 570e0716 touch only src/inference, src/routing (+ tests); no src/ui-android, settings.ts or locales.
- `git diff upstream/main..pr/cut7-engine --name-only | grep -E 'src/ui-android|settings.ts|locales'` -> empty.
- `git diff 570e0716 pr/cut7-engine -- src/routing src/rag src/inference` -> empty, so the identity run done on 570e0716 applies to the engine branch (no new generation run).
- pr/cut7-engine: `npx tsc --noEmit` clean; `npx vitest run` 117 files, 1369 tests passed.
- pr/cut7-wiring: tsc clean; `npx vitest run src/ui-android/chat` 2 files, 28 tests passed.

## Push commands (coordinator)
```
cd <workspace>/wt/pr1
git push --force-with-lease origin pr/cut7-engine
git push origin pr/cut7-wiring
```
(Check the remote name with `git remote -v`; the engine branch was rewritten, hence the force-with-lease.)
