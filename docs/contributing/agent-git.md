# Agent git policy

**The git gate was retired by the owner on 2026-09-19.** It had these parts: the `repo-git` MCP server,
`scripts/commit-tool/`, the `.githooks` commit-msg policy, the history check in CI, and the
Claude/Kilo/Cursor shell blockers. The friction outweighed the protection. It blocked prompts that only
mentioned `git commit`, stalled merges on other sessions' untracked files, and needed an MCP bridge for
every new agent runtime.

## What agents do now

1. **Plain git.** `git add <explicit paths>`, then `git commit -m "..."`. Merge with `git merge`.
2. **Commit as part of finishing a task**, without waiting to be asked. Make one logical change per
   commit, at each verified increment. Never amend; a correction is a new commit.
3. **Explicit paths, never `git add -A` / `git commit -a`.** Parallel sessions share the main tree, so a
   broad stage sweeps another stream's half-finished files.
4. **Never touch another session's dirty work.** Do not `stash`, `checkout` or `reset` around it.
5. **Push and PRs are explicit-ask only**, and never `--force`.
6. **No watermarks.** Commit messages and bodies carry no assistant or vendor names, `Co-authored-by`
   trailers, or "AI-generated" text. The author is the owner's own git identity.
7. **Never commit** secrets, game binaries, `dist/`, or machine-local paths (`H:\Games\...`).

These rules are now prose, not mechanism. Review catches violations. No hook enforces them.
