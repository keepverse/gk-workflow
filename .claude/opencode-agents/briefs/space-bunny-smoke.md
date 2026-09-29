# OpenCode CLI smoke test — Space Bunny Free

## Goal

Verify that the repository's headless OpenCode CLI runner can launch the owner-approved `opencode/space-bunny-free` model, access this worktree, and finish a read-only smoke test.

## Allowed paths

- `README.md`
- `AGENTS.md`
- `.git/HEAD`

## Off limits

Do not edit, create, delete, stage, commit, push, or branch anything. Do not touch product code, pipeline files, generated data, or any other lane's files.

## Definition of done

- Report the current branch and short HEAD SHA.
- Report the installed OpenCode version.
- Confirm that no repository files were changed.
- End with the runner's required `<<<REPORT {...} REPORT>>>` block.
- Stop after this one smoke test; do not investigate or implement anything else.

## Verification

- `git rev-parse --abbrev-ref HEAD`
- `git rev-parse --short HEAD`
- `C:\tools\opencode\opencode.exe --version`
- `git status --porcelain`
