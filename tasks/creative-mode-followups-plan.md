# Creative mode follow-ups — plan

Leftovers from the creative-mode merge (`02a538b3`) and its pre-merge audit. Each task is one commit on the
worktree branch `worktree-creative-mode-followups-20260919`, merged into `features/mega-merge` last. Session record: `tasks/sessions/creative-mode-followups-20260919.json`.

1. **Citation audit knows deliberate out-of-repo files.** Since the merge, `verify-change.ps1` runs
   `audit-doc-citations.py --strict` on every changed Markdown file. `CLAUDE.md`,
   `.claude/README.md` and `.claude/skills/project-manager/SKILL.md` cite four files that are real
   but outside git on purpose: `skills-lock.json` and `.claude/settings.local.json` (gitignored), and
   `cmdc_agent.py` / `allowed-models.json` (the user-level `cmdc-subagent` skill). Extend EXEMPT 1's
   closed basename set, with a reason per name. Verify: the three docs pass `--strict`.
2. **Class-system regen tests build their own tools.** `regen-class-system-baselines.ps1` runs
   `gk-core/tools/CombatSim` and `gk-forge/tools/DominanceBaseline` with `dotnet run --no-build` (Debug). Nothing
   guarantees a Debug build exists: a fresh worktree fails, and CI builds those tools only in Release
   (via Core.Tests). Follow the cold-process precedent: Guard.Tests takes a non-assembly
   `ProjectReference` to both tools, and the script takes `-Configuration`, which the test passes
   from its own build. Verify: `ClassSystemBaselineRegenTests` green in a tree with no tool builds.
3. **Stale `deploy-play.ps1:N` citations in `docs/`.** Re-point each to the current line
   (AtomImporter call, MelonLoader game-dir default, guard runner); rewrite the one finding whose
   claim was corrected on 2026-09-15 (deploy-play no longer runs the suite by default).
   `tasks/**` evidence fragments and old todos record history and are left as written.
4. **Cleanup.** Remove the merged `creative-mode-20260919-1d38` worktree (the branch stays, its
   record references it), close this session's record.
