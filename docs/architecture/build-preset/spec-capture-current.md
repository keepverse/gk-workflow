# Spec: `capture-current`

**Program:** [`build-preset`](../build-preset-map.md) · **Wave B** · depends on: `preset-store`,
`item-loadout-apply`.
**Status:** spec, not reviewed, no build authorized.

## Objective

The Vision line's point is that a lean is *"something you keep, not five independent clicks"*
(`docs/guide/the-loops.md:55`). Assembling a preset by picking five references is itself five clicks.
Capture is the one click: **"Save what I have now as Fire lean."** It reads the current patron, bound
set, skill loadout, gear and aptitude allocations, writes the aptitude and gear parts into their **own**
libraries (map D1), and saves a build preset that references them.

Capture writes library rows only. It changes nothing an actor fights with, and it spends nothing.

## Design

### Request

`POST /api/build-presets/capture` `{ playerId, name, pieces?: { patron?, field?, skills?, aptitudeTargets?, gearTargets? } }`

Omitted `pieces` means: patron, field, skills, the commander's aptitudes and gear, and aptitudes and gear
for every fielded specimen. The player can narrow it; capture never guesses beyond that default.

### What each piece captures

| Piece | Read | Written |
|---|---|---|
| `patron` | `GetPatron(playerId)` | a `patron` row; skipped with `capture.patron.none` when there is no patron |
| `field` | the bound contracts, **excluding wardens** (a warden is never a choice, and the field diff ignores it, `spec-piece-appliers.md`) | `field` rows |
| `skills` | `GetLoadout(player scope)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loadouts.cs:87`) | `skills` rows; skipped with `capture.skills.auto` when there is no stored loadout, because an auto-equipped set is recomputed every read (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loadouts.cs:110-121`) and freezing it would be a choice the player never made |
| `aptitudes` per target | the explicit allocation for that scope (`LoadAllocation`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs:120`) | see below |
| `gear` per target | current assignments: `ListAssignments(specimenId)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:744`) or, for the commander, `ListPlayerItemAssignments` (`:808`) | a new item loadout, entries mapped back by `LoadoutReport`'s ref-kind function (`rolled` → `item`, `stock` → `stock`); skipped with `capture.gear.empty` when nothing is worn |

### Aptitudes: reference the active preset when it still describes the build

1. If the scope has an active preset binding (`GetAptitudePresetActive`,
   `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:280`) **and** materializing that preset at
   the current budget yields the current allocation exactly, reference that preset. No new row.
2. Otherwise create a `player` aptitude preset from the allocation with
   `AptitudePresetCapture.FromAllocation` (new, Core, pure): each row's `targetPermille` is its share of
   the **spent** points, largest remainder so the rows sum to exactly 1000 (the library's own sum rule,
   `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:196-199`). Caps stay null.
3. An empty allocation is skipped with `capture.aptitudes.empty`. There is nothing to keep, and the
   scope's default (`empire-progression` `default-build`) already applies when nothing explicit exists.

**Capture keeps the lean, not the exact points.** A preset is a share of a budget; the library cannot say
"leave these points unspent", because its rows must sum to 1000. So re-applying a captured preset at the
same budget spends any points the player had left unspent, in the same proportions, and at a higher level
it grows with the budget. That is the Vision's "fire lean", and it is what an aptitude preset already
means. A player who wants exact caps sets them in the aptitude preset console after capture.

**Not a third favour-to-points function.** `empire-progression` D3 forbids a new distribution-to-points
function. `FromAllocation` goes the other way (points to shares); points are still produced only by
`AptitudePresetMaterialize.Materialize` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetMaterialize.cs:57`).

### One transaction

All capture writes are library rows in Data with no runtime side effects, so, unlike apply, capture
**is** one transaction: `RpgStore.CaptureBuildPreset(...)` (new) runs the reads and the writes under one
lock and one transaction. It calls transaction-scoped cores of the existing writers, extracted so the
public methods stay thin wrappers with unchanged behaviour:

| Writer | Core extracted (new) | Public method, unchanged |
|---|---|---|
| aptitude preset save | `SaveAptitudePresetUnlocked(db, tx, …)` | `SaveAptitudePreset` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:184`) |
| item loadout save | `SaveLoadoutUnlocked(db, tx, …)` | `SaveLoadout` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:431`) |
| build preset save | `SaveBuildPresetUnlocked(db, tx, …)` | `preset-store`'s save |

If any library's soft max refuses (`presets.softMax` for aptitude presets, `build-preset.softMax`), the
whole capture refuses by that library's name and writes nothing. No orphan aptitude preset or item loadout
can be left behind.

Generated names are deterministic and readable: `"{preset name} · {target label}"` for the aptitude and
gear rows, so the player can find them in those libraries.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudePresetCapture"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~BuildPresetCapture|FullyQualifiedName~AptitudePreset|FullyQualifiedName~Armoury"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetCapture"
python gk-core/scripts/guard-dal.py
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetCapture.cs` (new) | `FromAllocation`, pure |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs` | `CaptureBuildPreset` (new) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs`, `RpgStore.Items.cs` | transaction-scoped cores extracted |
| `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs` | `POST /capture` |
| `gk-core/tests/FusionRpg.Core.Stats.Tests/Stats/AptitudePresetCaptureTests.cs` (new), `tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetCaptureTests.cs` (new) | below |

## Code style

```csharp
public static class AptitudePresetCapture
{
    /// Points → shares of the spent total, largest remainder, rows sum to exactly 1000.
    /// long throughout; ×1000 before ÷spent, divide once (CLAUDE.md numeric rules 2 and 5).
    public static IReadOnlyList<AptitudePresetRowSpec> FromAllocation(IReadOnlyDictionary<string, long> points)
    {
        var spent = checked(points.Values.Sum());
        if (spent <= 0) return [];
        …
    }
}
```

## Testing strategy

1. **Shares sum to 1000** for any non-empty allocation, including a single aptitude and many tied ones;
   ties break by aptitude id so the result is deterministic.
2. **Round trip at the same budget, all points spent.** `Materialize(FromAllocation(a), budget)` differs
   from `a` per row by no more than the permille resolution, asserted as the bound `⌈budget / 1000⌉ + 1`
   computed from the budget under test, never a literal.
3. **Active preset reused.** When the active binding still materializes to the current allocation, no new
   aptitude preset row is written and the piece references the active one.
4. **Capture then apply restores.** Capture, change patron, field, skills, gear and aptitudes by hand,
   apply the captured preset: each layer reads back equal to the captured state through its own route
   (the lean equality for aptitudes, per test 2).
5. **Atomic.** With the aptitude library at its soft max, capture refuses and no item loadout, aptitude
   preset or build preset row exists afterwards.
6. **Skips are named.** No patron, auto-equip skills, empty gear, empty allocation: each piece is skipped
   with its code, and the response lists the skips.
7. **Wardens excluded** from the captured field.

## Boundaries

- **Always:** write aptitude and gear parts into their own libraries; one transaction; name every skip.
- **Ask first:** capturing exact points (caps) by default instead of the lean.
- **Never:** freeze an auto-equipped skill set; write a layer an actor fights with; spend anything.

## Tunables

**None new.** The soft maxima are the libraries' own (`aptitude-presets.v1.json` `softMaxPresets`,
`build-preset.v1.json` `softMaxBuildPresets`).

## ActorHub gate

**Not applicable.** Capture reads layer inputs and writes library rows; no actor number changes.

## Integer widths

`long` points and permille, `checked` sums, multiply by 1000 before dividing by `spent`, divide once.
A per-row product `points × 1000` stays far inside `long` at any reachable `Θ` (CLAUDE.md range table).

## Seedsmith / generator

**None.** Player-owned runtime rows.

## Success criteria

- [ ] One-click capture produces a build preset whose apply restores the captured build.
- [ ] Aptitude and gear parts land in their own libraries; the active aptitude preset is reused when it
      still fits.
- [ ] Capture is atomic across the three libraries.
- [ ] `verify-change.ps1` green.

## Open questions

None.

## Self-audit — the debate

- **"Capturing the lean instead of the points changes the build on re-apply."** Only the points the
  player left unspent, and only at the same budget; that is what a preset in this library already means.
  Capturing exact caps by default would make a captured preset stop growing with level, which defeats
  "something you keep".
- **"Capture could just store the raw allocation in the build preset."** That is a second aptitude
  library (map D1).
- **"Why is capture transactional when apply is not?"** Capture touches only Data-owned library rows with
  no runtime side effects, so one transaction costs nothing and removes orphans. Apply crosses Server
  services with injector pushes; forcing one transaction there would need a second implementation of four
  gates.
