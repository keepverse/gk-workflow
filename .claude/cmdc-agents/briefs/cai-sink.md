# Task: the injector/lawn half of `combat-ai` CAI1.12 (`resolvable-here`), handed off by the combat-ai lane

Program: `tasks/combat-ai-plan.md` / `tasks/combat-ai-todo.md`, row **CAI1.12** (its remaining
acceptance lines) plus the errata the combat-ai lane filed. Read the row, then
`docs/architecture/combat-ai/spec-resolvable-here.md` (or the module spec the row names) and the
combat-ai lane's own evidence fragment `tasks/evidence-fragments/CAI1.12.md` before writing anything —
it records exactly what was built (battle half, complete) and what is left.

**First action:** check whether the integration branch is already an ancestor of your HEAD (`git merge-base --is-ancestor features/mega-merge HEAD`) and merge it with `git merge --no-ff features/mega-merge` if not. Your base is the combat-ai lane's branch, which already carries `IDeclaresExecution`, its battle dispatch-table test and CAI1.13/CAI1.14.

## What is left (the combat-ai lane was fenced out of these files — you are not)

1. **Move `IDeclaresExecution` to its spec'd home.** It currently lives in
   `gk-core/src/FusionRpg.Core/Actions/ResolvableHere.cs` only because `gk-core/src/FusionRpg.Core/Effects/EffectModels.cs`
   was outside that lane's fence. Move the interface to the contract file the spec names, keep the
   battle call sites compiling, and leave no second copy behind.
2. **The injector declaration.** `gk-fusion/src/FusionRpg.Injector/Effects/InjectorEffectActionSink.cs` is the
   **live host's** effect-action sink; it must declare the opcodes it executes, so the per-place
   allowlist is built from the sink and never from a profile row. Prove it the way the battle half is
   proved: a source-scan test that the declaration equals the sink's own dispatch table, so the two
   cannot drift.
3. **The lawn half of the source-scan contract.** `The_lawn_sinks_declared_allowlist_matches_every_EffectActions_constant_its_dispatch_references`
   was **not run** by the combat-ai lane; build it.
4. **Tick only the CAI1.12 acceptance lines you actually close**, with an evidence fragment under
   `tasks/evidence-fragments/`, and leave one line pointing at the battle half (already green) instead
   of restating it. Do not touch CAI1.13/CAI1.14's rows. The `No_file_under_data_tuning_names_an_opcode`
   acceptance was ruled **erratum granted** — the substituted
   `No_file_under_data_tuning_authors_a_place_allowlist` stands; do not re-open it.

## Rules that bind this work

- One logical change per commit: code + tests + evidence + ledger + the ticked todo line together.
- **Do not move a battle golden.** If a hash moves, stop and report it as a blocker: this change
  declares what executes, it does not change what executes.
- A defect outside your fence: `file:line`, the cause you read, a row in the OWNING program's todo in
  the same commit — never a sentence in your report alone.
- Foreground commands only; never end a turn waiting on your own background job.
- `verify-change.ps1` needs `tasks/sessions/cai-sink.json`; write it before your first verification run.

## Verification

> **Runner note:** the runner takes the *first code span of each bullet in this section* as a
> verification command and runs it **verbatim** — a placeholder like `<every changed path>` is never
> substituted, so it is run as written and fails with a shell error. Each bullet below is therefore a
> real, substitution-free command; run the full `verify-change.ps1` yourself with your real changed
> paths and report the **numbers printed**, never the exit code alone (TVB-F3).

Boundary check -- run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then report the numbers printed:

```powershell
./scripts/verify-change.ps1 -Paths <paths you changed> -Session cai-sink
```
- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ResolvableHere|FullyQualifiedName~BattleGolden|FullyQualifiedName~Dominance|Category=BalanceGuard"`
- `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ResolvableHere"`
- `python gk-core/scripts/guard-battle-responsibility.py`
- `pwsh -NoProfile -File scripts/guard-actor-hub.ps1`
- `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`
- If you touch the injector: `$env:FUSIONRPG_ML_GAMEDIR = "<MelonLoader 3.9 pack>"; $env:FUSIONRPG_GAME_PROFILE = "pvzrh-3.9"; dotnet build gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj -c Release` must succeed (the injector is not built by CI).

On `user-mapped section open`, run `dotnet build-server shutdown` and retry.
