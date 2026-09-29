# CS-F1 — the layer-1b regression was red on its own content root, not on the ledger

Lane `cs-f1` (session `creature-seed-csf1`, branch `cmdc/cs-f1`, worktree
`.claude/worktrees/cmdc-cs-f1`), 2026-09-22. Row: `tasks/creature-seed-todo.md` CS-F1.
Rule under test: `docs/architecture/species-progression/spec-species-mod-ledger.md` Behaviour 1 —
"**No row means no 1b.** An empire that never fuses has no ledger row for any species." (unchanged:
reading it was how the row's premise was ruled out).

## Root cause, by `file:line` — the fixture, not the row and not the value

Pre-fix `gk-core/tests/FusionRpg.Data.Tests/SpeciesModLedgerTests.cs:98-102` resolved the seed root with a private
walk: `Path.GetFullPath(Path.Combine(<this file's own directory>, "..", "..", ".."))`. The file sits
directly in `gk-core/tests/FusionRpg.Data.Tests`, so three levels up is the repo root's **parent**, not the repo
root. `SeedImportRunner.FindUp(..., "data", "seed")` (`gk-core/src/FusionRpg.Data/Seed/SeedImportRunner.cs:76-87`)
then walked `D:\Works\source → D:\Works → D:\`, found nothing, and `RunSelfHealing` returned
`SeedTreeNotFound` (`:137-141`).

**Neither side the row named was wrong.** No layer-1b row exists for a never-fused save and none is
written, and no sentinel is stored in any row — the sentinel is a *boot status*, answered correctly and
loudly (`docs/architecture/effect-atom/spec-player-content-boot.md:65-73`: an absent import must be loud
and non-fatal) for a directory that holds no seed tree. The defect was the directory.

Why the same code passed in a lane worktree and failed at the integration head — `FindUp` keeps walking
*above* the wrong answer:

| test dir | old private walk `..\..\..` | `data\seed` there? | shared resolver `Get-ContentRoot` | `data\seed` there? |
|---|---|---|---|---|
| `<worktrees>/cmdc-cs-f1/tests/FusionRpg.Data.Tests` | `<worktrees>` | **no** | `<worktrees>/cmdc-cs-f1` | yes |
| `<repo>/tests/FusionRpg.Data.Tests` (main checkout) | `D:\Works\source` | **no** | `<repo>` | yes |

So a worktree run reached the **main checkout's** `gk-data/packs/fusion/data/seed` (passing, and silently reading another
tree), while the main checkout — the integration head the waiter ran — had nothing above it and failed.

## Fix — at the responsible layer: the repo's shared resolver

`RepoRoot()` deleted; the boot receives `FusionRpg.TestSupport.ContentRoot.Path`
(`gk-core/tests/Shared/KeepverseRoots.cs`, compiled into every `*.Tests` project by `Directory.Build.props:19-22`;
contract: `tasks/keepverse-split-plan.md` "Resolver contract"). A private relative walk is
depth-dependent — that is exactly how it got the wrong depth — and the shared resolver starts from the
test binary, so it finds *this* checkout and honours `KEEPVERSE_CONTENT_ROOT`. The anti-vacuity check is
strengthened in the same commit: `Assert.NotEqual(SeedTreeNotFound, …)` also accepted `Failed`, which is
equally vacuous, so it is now `Assert.True(boot.Ok, …)` (measured status at HEAD: `Imported`).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The row's own Verify line | `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --filter "FullyQualifiedName~After_a_real_boot_a_save_that_never_fused_has_no_layer_1b_rows"` | **Passed! — Failed 0, Passed 1, Total 1, 324 ms** | `gk-core/tests/FusionRpg.Data.Tests/SpeciesModLedgerTests.cs` |
| Whole Data project | `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet` | **Passed! — Failed 0, Passed 1850, Total 1850, 10 m 7 s** | — |
| Guards | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | **GUARDS OK — 21 guard(s) run, 0 red** | — |
| The defect, re-measured as arithmetic | `pwsh -NoProfile -Command ". ./scripts/lib/KeepverseRoots.ps1; <table above, both layouts>"` | old walk → a dir with **no** `gk-data/packs/fusion/data/seed` in **both** layouts; `Get-ContentRoot` → the repo root in both, `gk-data/packs/fusion/data/seed` present | `scripts/lib/KeepverseRoots.ps1` |
| Boundary | `.\scripts\verify-change.ps1 -Paths gk-core/tests/FusionRpg.Data.Tests/SpeciesModLedgerTests.cs -Session creature-seed-csf1` | see commit body | — |

## NOT proved

- The **fixed** test has not been executed from the main checkout (`D:\Works\source\...`); that tree
  belongs to the manager's CC8 gate. The layout is covered by the resolver table, not by a run.
- The strengthened `boot.Ok` assert was measured green (`Imported`); no planted failed boot was run to
  watch it go red — its red branch is by construction, not by measurement.
- The manager's `1 failed, 1780 passed` was not re-run at the head it was taken at. The count is
  reconciled arithmetically: the default profile (`test-fast.ps1 -AllDefault`, `Category!=DiskSemantics&
  Category!=Heavy`, Release) reads **1784** at this head, and `tasks/empire-progression-ledger.jsonl:482`
  records Data **1781** at the EP4 close, so the reading predates the head it is attributed to.
- `SeedImportRunner`'s own content-root discovery is untouched (see finding CS-F1-a).

## Findings routed (filed in `tasks/creature-seed-todo.md`, owner named — the fence excludes their files)

- **CS-F1-a** — `gk-core/src/FusionRpg.Data/Seed/SeedImportRunner.cs:126-148` has no Keepverse content-root
  awareness (`KEEPVERSE_CONTENT_ROOT` / `gk-data/packs/<pack>`) although every test and every script
  resolves through the shared contract. **Owner: `keepverse-split`** (content-root owner), caller
  `content-stack`. Not fixed here: changing the production boot path needs that program's ruling.
- **CS-F1-b** — no guard forbids a private repo-root walk in a test; `KeepverseRootsTests` only tests the
  resolver. **Owner: `keepverse-split`**, guard would live outside this fence (`gk-core/tests/FusionRpg.Guard.Tests/**`).
