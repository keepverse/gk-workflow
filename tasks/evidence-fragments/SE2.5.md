# SE2.5 — `pvz-write-surface`: extend `guard-single-writer` (W2/W3)

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| Comment stripping; per-writer field lists measured after `retire-atk` | Python scratch scan of the 4 allowed files, comment-stripped | `EntityStatWriter.cs` 23 (matches spec exactly); `ZombieCombatFields.cs` 2 (`theHealth`,`theMaxHealth`, both bridge versions agree); `UniqueBoundLoadout.cs` 0 (grants only through Funnel, measured -- retire-atk already removed its atk write); `EntityPositionWriter.cs` 4 (`thePlantColumn`,`thePlantRow`,`theZombieRow`,`transform.position`) | scripts/guard-single-writer.ps1 |
| Five retired fields refused everywhere (W3), including inside an allowed file | `dotnet test --filter "FullyQualifiedName~PvzWriteSurfaceGuardTests"` | **15/15 pass**: an uncommented `p.attackDamage =` inside a file NAMED `EntityStatWriter.cs` now fails W3 (the exact gap W1 never covered); the commented line still passes | gk-core/tests/FusionRpg.Guard.Tests/PvzWriteSurfaceGuardTests.cs |
| Falsifier: an uncommented `p.attackDamage` fails; a new unpinned field fails (W2); `==` never flagged | same run | `z.theZombieType =` fails W2 by name; `UniqueBoundLoadout`'s empty list catches any direct field write; `z.theSpeed == x` passes | scripts/guard-single-writer.ps1 |
| Stays ONE guard, gating; no new registry row | `run-guards.ps1 -Tier ci`; read registry | **16/16 CI guards green**; `pr-rpg-layer-only` already lists `single-writer` (spec's own cited id `claude-rpg-layer-only` was informal naming for this real row) -- no invariant edit needed | gk-core/scripts/enforcement-registry.v1.json |
| Real tree passes | `powershell scripts/guard-single-writer.ps1` | `SINGLE-WRITER GUARD OK` (extended message) | — |
