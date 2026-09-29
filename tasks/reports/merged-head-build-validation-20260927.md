# Merged-head build validation — 2026-09-27

## What was asked

Nothing had validated `features/mega-merge` as a whole. Every lane's GREEN was true only at
its own SHA, and the merged head is hundreds of commits ahead of `main`.

## The obstacle, and how far it actually reaches

`dotnet build FusionRpg.slnx` fails on this machine with:

```
error FUSIONRPG0002: Cell pvzrh-3.8.1 x BepInEx was pointed at a pack that is not this
cell's ... gameAssembly/Assembly-CSharp fingerprints did not match game-profiles.json
```

That is an **environment** refusal, not a code defect: `FUSIONRPG_GAME_DIR`,
`FUSIONRPG_GAME_POOL` and `FUSIONRPG_GAME_SOURCE` are all unset, and this machine has no
game pack. The gate is per-cell and `Directory.Build.targets:74` fires only for the injector
hosts and the launcher.

**So the refusal blocks 5 of 80 projects, not the build.** Measured, not assumed: 75 of the
80 projects in `FusionRpg.slnx` need no game pack.

| Needs a game pack | Does not |
|---|---|
| `gk-fusion/src/FusionRpg.Injector.BepInEx` | the other **75** projects |
| `gk-fusion/src/FusionRpg.Injector.MelonLoader` | |
| `gk-fusion/src/FusionRpg.Injector.MelonLoader.39` | |
| `gk-fusion/src/FusionRpg.Launcher` | |
| `gk-fusion/tests/FusionRpg.Launcher.Tests` | |

## The measurement

Every non-game project built individually at HEAD:

```
building 75 non-game projects at HEAD 3a1f4c81e
BUILD OK : 75 / 75
```

**The merged head compiles.** 75/75, zero errors. That is the first whole-tree build
evidence this branch has had, and it retires the "is it even green" question for everything
except the injector/launcher cell.

## What is still unproven, stated plainly

1. **The 5 game-pack projects have never been compiled here** — no pack on this machine.
   They are also the projects most likely to break on a merge, because the injector is where
   Harmony patches and Unity interop live.
2. **No test suite was run against the merged head in this pass.** This is a *build*
   validation: the 75 projects compile. `post_merge_check.py`
   (`.claude/cmdc-agents/scripts/`) is the gate that also runs the Guard suite and the touched
   test projects, and it is unrun against this head.
3. `main` is still far behind, so "the merged head is green" and "main is shippable" remain
   two different claims. Only the first is supported by this measurement.

## The two guard failures that were NOT environmental

While measuring, the 2 pre-existing `VerificationBoundaryWorkflowTests` failures turned out to
be a real defect and are now fixed (in `6f479d091`). They hardcoded `README.md` as "a path
with no owner", and `README.md` later joined the `docs-and-assistant-config` group — so the
planner correctly returned a scope plan and both tests went red against correct behaviour.
The tests now derive an unmapped path from the registry itself.

A further 2 failures in the same class are **machine contention, not defects**:
`guard-verification-boundaries.py` takes **75.2 s** measured alone, and those tests spawn it
under load on a busy machine, so they cross the test's timeout. The guard itself prints
`VERIFICATION BOUNDARY GUARD OK`.

## Incidental finding: a stale tool name in the guide

`AGENTS.md` and the manager tooling table both name the merged-head gate with a `.ps1`
extension. No such file exists — it is
[post_merge_check.py](../.claude/cmdc-agents/scripts/post_merge_check.py). This report's own
citation audit caught it (`D1 ... no tracked file with this name`, 1 HIGH), which is the audit
working as designed. **Not fixed here**: `AGENTS.md` is inside
`mega-merge-program-manager-20260925-f78e`'s declared paths, and the ps1-ban program is
porting tooling to Python concurrently, so the correct target name may still be moving.

## How to reproduce

```powershell
$sln   = Get-Content FusionRpg.slnx -Raw
$all   = [regex]::Matches($sln, 'Path="([^"]*\.csproj)"') | ForEach-Object { $_.Groups[1].Value }
$game  = @('gk-fusion/src/FusionRpg.Injector.BepInEx/FusionRpg.Injector.BepInEx.csproj',
           'gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj',
           'gk-fusion/src/FusionRpg.Injector.MelonLoader.39/FusionRpg.Injector.MelonLoader.39.csproj',
           'gk-fusion/src/FusionRpg.Launcher/FusionRpg.Launcher.csproj',
           'gk-fusion/tests/FusionRpg.Launcher.Tests/FusionRpg.Launcher.Tests.csproj')
$nonGame = $all | Where-Object { $game -notcontains $_ }
foreach ($p in $nonGame) { dotnet build $p -c Debug -v q --nologo }
```

This is a **build** gate, not a release gate. It says the merged head compiles; it does not
say it is correct, tested, or shippable.
