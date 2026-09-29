# Binding rules for opencode lanes (injected into every segment prompt)

- Your workspace is the worktree you were started in. Work ONLY inside it.
  Never write outside it, never touch pipeline files, CI, guards, or hooks.
- Commit nothing, push nothing, create no branches. Leave the tree dirty; the
  orchestrator harvests and commits.
- RPG layer only: no game-binary edits, no ad-hoc Unity stat writes. Combat
  writes go through `EntityStatWriter`; HP deltas through the Funnel.
  `ActorHub` is the sole compose gate — never add another composer.
- SQL only inside `FusionRpg.Data`. Generated data (`gk-data/packs/fusion/data/seed/items/**`,
  `gk-data/packs/fusion/data/seed/actions/**`, `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/atoms/generated/**`)
  is never hand-edited. Tuning numbers go in `gk-core/data/tuning`, not code.
- Integer magnitudes are `long` with `checked` arithmetic. No hard
  progression caps. Tests assert contracts, never population counts.
- Foreground commands only; never start background shell tasks.
- If a rule blocks you, write BLOCKED: <what, why> and continue with other
  eligible work. Never probe the guard, the runner, or your agent directory.
- End your last message with the <<<REPORT>>> block from the brief. Evidence
  shows exact commands copied from your command line. A claim without a
  command you ran is not evidence.
