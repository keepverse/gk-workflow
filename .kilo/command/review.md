---
description: "Review the current changes — correctness, readability, architecture, security, performance"
---

Load the `code-review-and-quality` skill with the skill tool.

Review the current changes (staged or recent commits) across all five axes:

1. **Correctness** — Does it match the spec? Edge cases handled? Tests adequate?
2. **Readability** — Clear names? Straightforward logic? Well-organized?
3. **Architecture** — Follows existing patterns? Clean boundaries? Right abstraction level?
4. **Security** — Input validated? Secrets safe? Auth checked? (Use `security-and-hardening` skill)
5. **Performance** — No N+1 queries? No unbounded ops? (Use `performance-optimization` skill)

Categorize findings as Critical, Important, or Suggestion.
Output a structured review with specific file:line references and fix recommendations.

Modes: `/review uncommitted` (staged/unstaged/untracked), `/review unpushed` (commits ahead of upstream), `/review branch` (vs base branch). In an Agent Manager managed worktree, `/review worktree` reviews all of its changes regardless of commit status. Default to `uncommitted` when no mode is given. `$ARGUMENTS` selects the mode.
