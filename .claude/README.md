# .claude — local assistant setup for this repo

Everything in this folder (and the root `CLAUDE.md` / `AGENTS.md`) is **tracked assistant config** — keep committed paths portable (`${workspaceFolder}` or repo-relative, never a drive letter). This guide explains what is installed and how to use it in any Claude Code session.

## What loads automatically each session

| File | Role |
|---|---|
| `CLAUDE.md` (repo root) | Auto-loaded by Claude Code at session start. First line `@AGENTS.md` imports the full contributor rules (plain-git commits, hard boundaries, style), then adds repo quick context: which architecture docs to read, which guard scripts to run. |
| `AGENTS.md` (repo root) | The actual rules document (cross-vendor format). Edit **this** file when rules change — `CLAUDE.md` just imports it. |
| `.claude/skills/*` | Project-level skills, auto-discovered at session start. |
| `.claude/agents/*` | Subagent definitions (`subagent_type`), auto-discovered at session start. |

Nothing to do to activate any of this — just start `claude` in the repo. If skills don't appear, restart the session (discovery happens once at startup).

## The installed skills (addyosmani/agent-skills)

Generic engineering-workflow skills — process, not repo knowledge. Invoke one by typing `/<name>`, or just describe a matching task and the agent picks them up.

| Phase | Skills |
|---|---|
| Define | `interview-me`, `idea-refine`, `spec-driven-development` |
| Plan | `planning-and-task-breakdown` |
| Build | `incremental-implementation`, `test-driven-development`, `context-engineering`, `source-driven-development`, `doubt-driven-development`, `frontend-ui-engineering`, `api-and-interface-design` |
| Verify | `browser-testing-with-devtools`, `debugging-and-error-recovery` |
| Review | `code-review-and-quality`, `code-simplification`, `security-and-hardening`, `performance-optimization` |
| Ship | `git-workflow-and-versioning`, `ci-cd-and-automation`, `deprecation-and-migration`, `documentation-and-adrs`, `observability-and-instrumentation`, `shipping-and-launch` |
| Meta | `using-agent-skills` (start here — explains how the set fits together) |

Useful combos for this repo:

- New feature: `/spec-driven-development` → `/planning-and-task-breakdown` → `/test-driven-development`
- Before handing work back: `/code-review-and-quality` or `/code-simplification`
- Web FE work: `/frontend-ui-engineering`, `/browser-testing-with-devtools`
- Note: `git-workflow-and-versioning` and `shipping-and-launch` follow the repo's git policy — plain git with explicit paths, push and PRs only when the owner asks ([docs/contributing/agent-git.md](../docs/contributing/agent-git.md)).

## Layout

```
.claude/
  README.md            ← this guide
  skills/              ← installed copies + repo skills (auto-discovered)   [tracked]
  agents/              ← subagent definitions (auto-discovered)            [tracked]
  commands/            ← slash commands                                    [tracked]
  vendor/agent-skills/ ← upstream git clone (for updates)                  [gitignored]
  worktrees/           ← session worktrees                                 [gitignored]
```

## Local modifications (re-apply after every update)

The vendored skills assume **one active stream** per repo: they default specs to `SPEC.md` and plans to `tasks/plan.md` / `tasks/todo.md`. This repo runs several programs at once, so those slots are always occupied by *somebody*, and a naive save destroys another stream's unreviewed work.

Patched locally on 2026-08-21:

| File | Change |
|---|---|
| `skills/spec-driven-development/SKILL.md` | Phase 0 gains a "Parallel initiatives in one repo" rule (read the target first, fall back to prefixed paths, project rules win, say where things landed); the Phase 2 output convention notes the same fallback |
| `skills/planning-and-task-breakdown/SKILL.md` | Task List Target gains a "Parallel initiatives" bullet; the verification checklist asks which paths were used |
| `skills/spec-driven-development/SKILL.md` | **(2026-08-23)** Phase 1 also requires the spec to name which numbers are tunable, their config file and their units (`tunables-ssot.md`) |
| `skills/spec-driven-development/SKILL.md` | **(2026-08-23)** Phase 1 also requires numeric width + overflow behaviour to be stated in the spec, citing `CLAUDE.md`'s measured thresholds |
| `skills/spec-driven-development/SKILL.md` | **(2026-08-23)** Phase 1 opens with a "Project reading gate first" step — satisfy `docs/DESIGN-GATE.md` before writing spec content, verify against code not comments, and state any checklist box you cannot tick |
| `commands/spec.md`, `commands/plan.md`, `commands/build.md` | stop hardcoding the single-stream paths; `/build auto` must ask which program it is building and must not sweep other streams' uncommitted work into a commit |
| `commands/plan.md`, `commands/spec.md`, both SKILLs | **(2026-08-24)** the prefixed pair is **unconditional**. The earlier patch left it as *"save to `tasks/plan.md` unless occupied"*, so every session read two files to re-derive the same answer. Now: always `tasks/<program>-plan.md` / `tasks/<program>-todo.md`, always `docs/architecture/<program>-map.md` / `<program>/spec-<module-id>.md`; `SPEC.md` and the bare pair are **not defaults and not fallbacks** — do not read them, never write to them |
| `commands/build.md` | header note on the repo's commit policy — **(2026-09-19)** plain git, one task per commit, explicit paths, `verify-change.ps1` for verification. It said "git hands-off: hand the owner a message" until the git gate was retired |
| `agents/code-reviewer.md`, `agents/security-auditor.md`, `agents/test-engineer.md` | **(2026-09-19)** copied from `vendor/agent-skills/agents/` so `/ship`'s parallel fan-out resolves its three `subagent_type`s; local edits: each file's broken relative link to upstream `docs/agents.md` becomes plain text, and the frontmatter gains `tools: Read, Grep, Glob, Bash` (a reviewer never edits the code it reviews) and `model: inherit` (the charter rule checks every agent's model). Re-copy after a vendor update, then re-apply both |
| `skills/planning-and-task-breakdown/SKILL.md`, `commands/plan.md` | **(2026-09-05)** new "Gates vs. checkpoints" section: a pre-work gate that blocks starting a phase must protect a genuinely irreversible action, name who resolves it, and state a default if unanswered — otherwise ship behind a reversible/tunable default and track it as a non-blocking follow-up. Added the checklist items to match. Incident: `base-defense`'s plan froze on two gates that weren't irreversible (a cross-program bug report, and a design-doc approval that had already happened a day before the plan was written and only looked blocked because the map document hadn't been re-read against `decisions.md`) |

**The authoritative copy of the convention lives in `AGENTS.md`** ("Parallel programs — where specs, plans, and tasks live"), because a vendor update force-overwrites `.claude/skills/` and never touches `AGENTS.md`. If a vendor update wipes the patches above, the rule still holds — the skills just stop reminding you about it.

`skills-lock.json` hashes will not match for the two patched skills. That drift is expected; do not "fix" it by reverting the patches.

## Updating the skills

```powershell
git -C .claude/vendor/agent-skills pull
Copy-Item -Recurse -Force .claude/vendor/agent-skills/skills/* .claude/skills/
```

Then restart the Claude Code session — **and re-apply the local modifications above**, since the copy is a force-overwrite.

## Repo-specific skills written here

| Skill | Command | What it is |
|---|---|---|
| `idea-ui` | `/idea-ui` | Menu/FE module idea phase — recipe+fold+themes, bug→module map. Durable: `docs/architecture/idea-ui-phase.md` |
| `idea-phase` | `/idea` | RPG-system idea phase (not menus) — durable ideals under `docs/architecture/*-ideal.md` |
| `live-lawn-quick-start` | — | Cold-start a LIVE lawn for debug proves |
| `local-web-review` | `/review-web` | Start the local server so the owner can review the web UI |
| `seedsmith-design` | `/seed-design` | The design domain under `/idea` and `/spec` for any generation feature — the six generation laws, the reading gate, the game-design questions, and the AI-native contract rules |
| `seedsmith-passivetree-repair` | `/passivetree-repair` | Closed-loop investigate/repair/prove for the SeedSmith PassiveTree pipeline and corpus. Also under `.agents/skills/seedsmith-passivetree-repair/` |
| `html-design-implementation` | — | Port approved `docs/design/*.html` drafts into production FE with structural + visual fidelity (structure breakdown → contract → side-by-side gate). Durable rules: `docs/architecture/html-design-implementation.md`. Also under `.agents/skills/html-design-implementation/` |
| `creative-mode` | `/creative` | **(2026-09-19)** A creative program: the owner is the customer and the agent is the hired creative project manager. One intake interview (brief, charter, landing branch, creative game install, content generation), then one or more invented features carried from idea to the landing branch with no human — a written filter and rubric, independent `creative-gate` agents and screenshot gates stand in for the owner. Durable policy: `docs/contributing/creative-mode.md` |

Create `.claude/skills/<name>/SKILL.md` (frontmatter: `name`, `description`; body: the instructions), and a matching `.claude/commands/<name>.md` if it deserves a slash command.

## Repo subagents

| Agent | Used by | What it is |
|---|---|---|
| `build-gate` | `/build full`, `/creative` | Independent, read-only verifier for one build task; PASS/FAIL |
| `creative-gate` | `/creative` | Independent, adversarial, read-only gate for one audit phase of a creative program (slate, ideal, spec, plan, review, visual screenshots); PASS/FAIL |
| `code-reviewer`, `security-auditor`, `test-engineer` | `/ship` | The three parallel ship reviewers, copied from the vendored agent-skills (see the modifications table) |

## Where durable knowledge lives

`.claude/` is tracked now — `.gitignore` excludes only `vendor/`, `worktrees/`, `settings.local.json` and the `cmdc-agents/` runtime state — but a skill is still read only by the assistant runtime that loads it, and each runtime keeps its own copy (`.agents/skills/`, `.commandcode/skills/`), which drifts unless edited together.

**Therefore: durable knowledge goes in committed `docs/`, and the skill is the procedure that loads it.** `seedsmith-design` is the worked example — its two knowledge halves live in `docs/research/game-design/` and `docs/research/ai-native-generation/`, both committed, and the SKILL.md is a reading gate plus a refusal list. `creative-mode` follows the same split: the policy is `docs/contributing/creative-mode.md`, the skill is the procedure. Never let a fact exist only inside `.claude/`. When you edit a skill that has a mirror copy, edit the mirror in the same change.

## Reinstalling from scratch (new machine)

```powershell
git clone --depth 1 https://github.com/addyosmani/agent-skills.git .claude/vendor/agent-skills
Copy-Item -Recurse -Force .claude/vendor/agent-skills/skills/* .claude/skills/
```

`CLAUDE.md` and `AGENTS.md` are tracked, so a fresh clone has them (ask the agent to regenerate `CLAUDE.md` if needed — it's a thin pointer file; `AGENTS.md` holds the real rules).
