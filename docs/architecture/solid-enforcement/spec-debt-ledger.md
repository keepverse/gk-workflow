# Spec: `debt-ledger`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 0** · depends on:
`enforcement-registry`.

## Objective

The owner asked for **one file** that tracks debt, in the words `stub-register.md` opens with:
*"a own file to track debt and remove stub"*. The ruling *"everything SOLID, one program"* adds the
missing half. The repo's SOLID-violating **shapes** have no row anywhere today. They are spread across
an ideal doc (`CommanderId`), a class-system decision (G3/`atk`), a map section (god files), and this
program's inventory (test pollution in `gk-core/data/tuning/`, the commit-policy red).

This module makes `docs/architecture/stub-register.md` that one ledger. It does **not** create a second
register: two debt files is the exact defect a debt file exists to prevent (the O in SOLID, applied to
documentation: extend the existing register, don't fork it).

**Division of labour with `enforcement-registry`:** the registry records **guards** (what stops a
class of violation). The ledger records **instances** (a specific violation in the tree right now, and
the module that removes it). A guard module usually clears ledger rows as its backlog, and the
registry row and the ledger row point at the same module id.

## Design

### A fourth `kind`: `solid`

The ledger's `kind` column is a closed vocabulary `{stub, dark, unowned}`, and
`StubRegisterTests.Every_row_declares_a_kind_from_the_closed_vocabulary` pins it. It is correct to pin
it, and adding a member is a reviewed change. The test's own comment records the precedent:
`unowned` was added on 2026-09-17 when a finding fitted neither existing kind.

| kind | Definition | Disposition |
|---|---|---|
| **solid** | **A shape that violates a SOLID invariant and is known, measured and unfixed.** It usually works, and that is precisely why it stays: nothing fails. | Registered here with the `solid-enforcement` module that removes it. `waits-on` names that module. Never "someday" |

`solid` is not `dark`: a dark feature is unreached and simply needs wiring. A `solid` row is reached
and working, and its **shape** is the defect.

### Rows this module adds

<!-- citations-historical: scripts/commit-tool/ (including policy.json, check_history.py) was deleted 2026-09-19 when the git gate was retired; agents now use plain git with explicit paths, docs/contributing/agent-git.md -->


Every figure below was measured on 2026-09-18.

| id | kind | what | where | waits-on | owner | ships-on-it |
|---|---|---|---|---|---|---|
| `SR-19` | solid | `progression.bonus.atk` is a second attack channel beside `combat.power.*`; Might/Ferocity pay into both (class-system G3) | `gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatChannels.cs:8`, `gk-core/data/tuning/aptitudes.v8.json` | `retire-atk` | solid-enforcement | yes: the standalone sim applies it (`SimEngine.cs:247,313`); lawn and battle ignore it |
| ~~`SR-20`~~ | solid | **CLOSED by `commander-identity` (SE4.1–SE4.3, commit `1588875d`, 2026-09-19).** `CommanderId` was a closed two-member enum for what the owner ruled is a population (*"a commander literally a unique creature"*). It is deleted: the faction meaning is `EmpireId`, the unit meaning is `CommanderRef` (both open value types), and display name / allocation scope key / empire / default come from the authored registry `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json` through `ICommanderDirectory`. A third commander is a registry row, not a code change (the Open/Closed test). Persisted strings are unchanged, so no data migrated; a creature-commander arrives as a new row (`empire-progression`) | `gk-core/src/FusionRpg.Core/Commanders/EmpireId.cs` | nothing — closed | solid-enforcement | no — closed; the flag guard `guard-open-identity` (I1/I2) is SE4.4's |
| `SR-21` | solid | Test output committed into the balance surface: 4 `loopwarntest*.v{1,2}.json` written by `ResidualFitLoopTests` | `data/tuning/loopwarntest13c4c662.v1.json` | `tuning-immutability` | solid-enforcement | no, but they are copied into every test and tool `bin/` |
| `SR-22` | solid | Guard `commit-policy` red on 5 GitHub web-merge commits, so it cannot gate | `scripts/commit-tool/policy.json` | `commit-policy-green` | solid-enforcement | no |
| `SR-23` | solid | 8 C# files over 1,500 lines, 5 non-test TSX over 600 (single responsibility) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` (4,163 lines) | `srp-file-budget` | solid-enforcement | no |
| `SR-24` | solid | The legacy identity shape: an **empire is a `players` row**, and Zomboss is a second player row found by name (`EnsureZombossPlayer`) and shared by every save — so save A's and save B's Zomboss are the same row. Keyed by `(SaveId, EmpireId)` after the fix | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossDeploy.cs:25-29` | `save-identity` | solid-enforcement | yes: an AI-empire mint, its levels and its specimens land on one global row today (spec-save-identity.md D1/D5) |

### Phase 1 and 2 residuals — recorded, not ticked

The map records these, and this module writes them into the ledger's **Hand-off** section. They are
*not* rows: neither is debt this program can remove, and a row would falsely promise it.

- **Phase 1, `actor-hub-and-combat-power-solid-fixing`:** the one open item is *"Owner accepts program
  close — genuinely owner-only, cannot be self-closed"*. This program cannot close it. It surfaces it
  at its own final checkpoint.
- **Phase 2, `solid-remediation` T4.4 S7:** deferred by the owner on 2026-09-17 into
  `species-progression`'s level-up-grants sub-program. It is scheduled, not stalled.

### The append rule, extended

`stub-register.md`'s existing **append rule** (every module appends as it runs) is extended with one
sentence: *"A `solid` row is closed by the module named in `waits-on`, in that module's last commit.
The row is struck through (`~~SR-nn~~`), never deleted, and its `waits-on` cell gains the closing
SHA."* Strike-through keeps the trail, and the existing `SR-17` row already uses exactly this form.

## Commands

```powershell
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~StubRegisterTests"
.\scripts\verify-change.ps1 -Paths @('docs/architecture/stub-register.md','gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs') -Session <id>
```

## Project structure

| Path | Change |
|---|---|
| `docs/architecture/stub-register.md` | `solid` kind in the distinction table; rows SR-19..SR-23; residuals in Hand-off; one sentence in the append rule |
| `gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs` | `allowed` gains `"solid"`, with the reason written beside the pin; failure message lists all four |
| `gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs` | **new fact:** every `solid` row's `waits-on` is a module id in `solid-enforcement-map.md`, or the row is struck through with a SHA |

## Code style

The new fact follows the file's existing shape exactly:

```csharp
[Fact]
public void Every_open_solid_row_waits_on_a_module_of_the_enforcement_program()
{
    // A `solid` row is a known SOLID-violating shape; "waits on someday" is how such shapes become
    // permanent. Its waits-on must be a real module id, or the row must be closed (struck + SHA).
    var modules = EnforcementMap.ModuleIds(RepoRoot());
    foreach (var cells in Rows().Where(c => c[1] == "solid" && !c[0].StartsWith("~~")))
        Assert.True(modules.Contains(cells[4].Trim('`')),
            $"{cells[0]}: waits-on '{cells[4]}' is not a solid-enforcement module id");
}
```

## Testing strategy

- The kind-vocabulary pin changes from 3 to 4 members. This is a reviewed change to a closed
  vocabulary, not a bumped reading, and the comment beside it says so.
- The new fact gets a falsifier: an in-memory row whose `waits-on` names a nonexistent module must
  fail.
- `EnforcementMap.ModuleIds` is the **same** parser `enforcement-registry`'s R3 uses, extracted into
  one helper file in Guard.Tests. Two parsers of one table would be the drift this program exists to
  stop.

## Boundaries

- **Always:** append a row the moment a module finds a new SOLID-shaped instance it will not fix
  itself.
- **Ask first:** a fifth `kind`.
- **Never:** delete a closed row. Never create a second debt file. Never write a row whose `waits-on`
  is not a module.

## Success criteria

- [ ] `solid` is a documented kind, and the pin is updated with its reason.
- [ ] SR-19..SR-23 are present, each with all six fields and a real `where`.
- [ ] Both residuals are in the Hand-off section, worded as owner items.
- [ ] `StubRegisterTests` green, including the new fact and its falsifier.

## Self-audit — the debate

**Objection: "A new kind is scope creep on another program's file."** `solid-remediation`, which
created this file, is complete: 96/1, and the 1 is owner-deferred. The owner's ruling puts SOLID
debt in one program, and the file's own charter is "track debt". Adding a kind through the reviewed
path its test demands is what that test is for.

**Objection: "The enforcement registry already names backlog modules. The ledger duplicates it."**
It covers a different set. `SR-20` (`CommanderId`) and `SR-23` (god files) have *no guard at all
yet*, so no registry row can point at them. The ledger is the only place an instance with no guard
can live. Where both exist, they agree by construction: both name the same module id, and both are
checked against the same map parser.

**Objection: "IDs `SR-19+` continue a sequence whose `SR-17` was closed and `SR-18` is `creditEmpire`.
Isn't numbering fragile?"** Ids are append-only and never reused, which is the file's own rule. The
build step reads the current maximum id rather than trusting this spec, because another module may
append first.

## Gaps found and closed while writing

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


- **First draft listed rows with guessed line counts.** Replaced with the measured figures
  (`RpgStore.cs` 4,163 lines, `CommanderId.cs:20`, the loopwarn filenames).
- **The first draft ticked phase 1's close item "as recorded".** Wrong: the item says it cannot be
  self-closed. It is now a Hand-off note and nothing is ticked.
- **Id collision risk:** this module and `retire-atk` could both append in wave 1. Rule added: ids
  come from the current file maximum at commit time, never from this spec's table. The table shows
  the *intended* rows; its numbers are illustrative.
