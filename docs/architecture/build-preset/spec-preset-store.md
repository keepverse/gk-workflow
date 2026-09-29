# Spec: `preset-store`

**Program:** [`build-preset`](../build-preset-map.md) · **Wave A** · depends on: nothing inside the
program; **built after** `empire-progression` `commander-roster` and `solid-enforcement`
`commander-identity` / `save-identity`, because its target column stores their actor-reference grammar.
**Status:** spec, not reviewed, no build authorized.

## Objective

A player can name a lean ("Fire lean") and keep it. The store holds that name and a list of
**references**: which creature is patron, which creatures are fielded, which aptitude preset goes on
which scope, which item loadout goes on which actor, which skills are equipped. It never copies what the
references point at (map D1). It re-checks every reference on read, so a salvaged loadout or a retired
patron shows as a visible hole, never as a quietly shorter preset.

## Design

### Tables (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs`, new)

```sql
CREATE TABLE IF NOT EXISTS rpg_build_preset (
  preset_id   TEXT    NOT NULL PRIMARY KEY,
  save_id     INTEGER NOT NULL,
  empire_id   TEXT    NOT NULL,          -- always HumanEmpireOf(save) today; see "Identity" below
  name        TEXT    NOT NULL,
  created_utc TEXT    NOT NULL,
  revision    INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_rpg_build_preset_empire ON rpg_build_preset(save_id, empire_id);

CREATE TABLE IF NOT EXISTS rpg_build_preset_piece (
  preset_id  TEXT    NOT NULL,
  piece_kind TEXT    NOT NULL,           -- BuildPresetPieceKind id
  target_ref TEXT    NOT NULL DEFAULT '', -- who the piece is applied to; '' for player-wide pieces
  ordinal    INTEGER NOT NULL DEFAULT 0,  -- position inside a multi-row piece (field members, skill slots)
  ref_id     TEXT    NOT NULL,            -- what the piece points at
  PRIMARY KEY (preset_id, piece_kind, target_ref, ordinal)
);
```

The header mirrors `rpg_aptitude_preset` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:58-65`)
and `rpg_item_loadout` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:131-138`): one library discipline,
three libraries. Schema is ensured in the same `Ensure…SchemaUnlocked` pattern those use.

### The closed piece vocabulary (`gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetPieceKind.cs`, new)

| Kind | `target_ref` | `ref_id` | Rows | Points at |
|---|---|---|---|---|
| `patron` | `''` | specimen `instance_id` | 0–1 | `rpg_patron` target (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs:17`) |
| `field` | `''` | specimen `instance_id` | 0 or ≥1, ordinal 0..n-1, unique ids | the contract-bound set (map D3) |
| `aptitudes` | `{scope}:{scopeKey}` with scope ∈ `commander`, `unique`, `species` (the activate gate's own scope words, `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs:287-293`) | `rpg_aptitude_preset.preset_id` | one per target | the aptitude preset library |
| `gear` | the equip target id (specimen `instance_id` or commander stable id, `gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:300-325`) | `rpg_item_loadout.loadout_id` | one per target | the item loadout library |
| `skills` | the loadout owner (`player` today: the only HTTP scope, `gk-core/src/FusionRpg.Server/LoadoutEndpoints.cs:74`) | action id | ordinal 0..n-1 | `rpg_actor_loadout` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loadouts.cs:41`) |

Closed in code, five members, pinned by a membership test **because it is a declared vocabulary**: a
sixth kind is a reviewed change (map D2). The ids are persisted strings, parsed through one `TryParse`;
an unknown stored id reads as a `Missing` piece, never an exception and never a dropped row.

### Save-time rules (structural; refused by name, nothing written)

| Rule | Reason code |
|---|---|
| At least one piece | `build-preset.empty` |
| At most one `patron` row | `build-preset.patron.multiple` |
| `field` ids unique, ordinals contiguous | `build-preset.field.shape` |
| If both `patron` and `field` are present, the patron is a field member, because the patron gate refuses an unbound creature (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs:38-40`) and the field piece would release it | `build-preset.patron.outside-field` |
| `aptitudes` target scope is one of the three words | `build-preset.aptitudes.scope` |
| `skills` ordinals contiguous | `build-preset.skills.shape` |
| Name non-empty; soft max on create | `build-preset.name.missing`, `build-preset.softMax` |

Save-time rules are **shape only**. Whether a reference is still valid, whether capacity allows the field,
whether a skill is held: those are the gates' questions, asked at preview. A preset that was valid when
saved and is not today is still readable.

### Validate on read

`GetBuildPresetValidated(presetId, playerId)` returns every piece row with a state:

| Kind | `Present` when |
|---|---|
| `patron`, `field` | the specimen is owned by this player and not `Retired` |
| `aptitudes` | the aptitude preset exists and is owned by this player; for `unique:{id}` the specimen is owned; for `species:{id}` the species is known |
| `gear` | the item loadout exists and is owned by this player; the target resolves |
| `skills` | the action exists or is a known aura id, the same held test the loadout route uses (`gk-core/src/FusionRpg.Server/LoadoutEndpoints.cs:60-63`) |

`Missing` carries a reason. **Every stored row comes back**, the armoury rule
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:474-488`).

### Delete

Deletes the header and its pieces in one transaction. **Never cascades** into the aptitude preset or item
loadout it references: those belong to their own libraries, and a player may keep one in two build
presets. Deleting a referenced aptitude preset or item loadout is allowed; the build preset then reads
that piece as `Missing`.

### Routes (`gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs`, new)

| Method | Route | Serves |
|---|---|---|
| GET | `/api/build-presets/{playerId}` | list with validated pieces |
| POST | `/api/build-presets` | create (soft max) |
| PUT | `/api/build-presets/{presetId}` | replace pieces, bump `revision` |
| DELETE | `/api/build-presets/{presetId}?playerId=` | delete |

Preview and apply are `apply-orchestrator`'s; capture is `capture-current`'s.

### Identity after `save-identity` (R3)

This table is new after `solid-enforcement` `save-identity`, so it follows that spec's rules from its
first build rather than being migrated later:

- **The column is `save_id`**: *"New and rebuilt tables name the column `save_id`"*
  (`docs/architecture/solid-enforcement/spec-save-identity.md:63-65`). On the wire the value is still the
  `playerId` the sibling routes take, which that spec keeps as the save id.
- **Empire-keyed from birth, human-only API.** A build preset is the human empire's build state, beside
  `rpg_aptitude_preset` and `rpg_item_loadout`, which that spec classifies Tier B
  (`docs/architecture/solid-enforcement/spec-save-identity.md:160,168`). Because the table is **new**, it
  carries `empire_id` from its first build (always `HumanEmpireOf(save)` today), so no migration is ever
  owed to widen it; this is `save-identity`'s cross-program sweep, mismatch 3, applied (strengthen pass
  2026-09-18). The store API still takes an `EmpireRef` and throws `EmpireScopeNotWidened` for any empire
  other than the save's human empire (`:135-139`): no AI empire applies presets. If one ever does, only the
  refusal is lifted; the key and the callers do not change.

That is why this module is built after `save-identity`, not before it.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildPreset"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~BuildPreset"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetEndpoints"
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-test-substrate.py
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetPieceKind.cs` (new) | enum + ids + `TryParse` |
| `gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetShape.cs` (new) | pure save-time rules above |
| `gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetTuning.cs` (new) | record, loader, hub (the `AptitudePresetTuning` pattern, `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetTuning.cs:8-37`) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs` (new) | tables, CRUD, validate-on-read. The only SQL |
| `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs` (new) | four routes |
| `gk-core/src/FusionRpg.Server/Program.cs` | load `build-preset.v1.json`, map routes (beside the aptitude-presets load, `gk-core/src/FusionRpg.Server/Program.cs:251`) |
| `gk-core/data/tuning/build-preset.v1.json` (new) | below |
| `gk-core/tests/FusionRpg.Core.Tests/BuildPresets/*`, `gk-core/tests/FusionRpg.Data.Tests/BuildPresets/*`, `gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs` (new) | below |

## Code style

```csharp
public enum BuildPresetPieceKind { Patron, Field, Aptitudes, Gear, Skills }

public static class BuildPresetPieceKinds
{
    public static string Id(BuildPresetPieceKind k) => k switch
    {
        BuildPresetPieceKind.Patron => "patron", BuildPresetPieceKind.Field => "field",
        BuildPresetPieceKind.Aptitudes => "aptitudes", BuildPresetPieceKind.Gear => "gear",
        BuildPresetPieceKind.Skills => "skills",
        _ => throw new ArgumentOutOfRangeException(nameof(k)),
    };
    public static bool TryParse(string? id, out BuildPresetPieceKind kind) { … }
}
```

## Testing strategy

Tests run on the in-memory store (`docs/contributing/testing-standard.md`).

1. **Closed vocabulary.** `BuildPresetPieceKind` has exactly five members and every id round-trips.
   Pinned because it is a declared vocabulary; the test comment says so.
2. **Shape rules.** Each save-time rule refuses by its code and writes nothing.
3. **Round trip.** Save then read returns every piece in ordinal order; piece save order in the request
   does not change the stored result.
4. **Validate on read.** Retire the patron, delete the referenced aptitude preset, delete the item
   loadout, retire a field member: each piece reads `Missing` with its reason, and the row count read
   equals the row count saved.
5. **No cascade.** Deleting a build preset leaves the referenced aptitude preset and item loadout intact.
6. **Soft max.** Create refuses at `softMaxBuildPresets` read from the loaded tuning, never a literal.
7. **Owner checks.** Another save's preset id refuses update and delete; a non-human `EmpireRef`
   throws `EmpireScopeNotWidened`.

## Boundaries

- **Always:** store references only; return every row on read; SQL only in `RpgStore.BuildPresets.cs`.
- **Ask first:** a sixth piece kind; storing a value (shares, item rows) instead of a reference.
- **Never:** cascade a delete into another library; validate a gate's rule (price, capacity, held)
  at save time.

## Tunables

`gk-core/data/tuning/build-preset.v1.json` (new). The first version of a new domain is authored with the
module; every later change is `v{n+1}` through `gk-core/tools/tuning/publish.py` (tunables-ssot T4).

```json
{
  "schemaVersion": 1,
  "version": 1,
  "_meta": { "owner": "docs/architecture/build-preset/spec-preset-store.md",
             "note": "softMaxBuildPresets is a soft refusal on create, same discipline as aptitude-presets softMaxPresets — not a progression ceiling." },
  "softMaxBuildPresets": 32
}
```

- `softMaxBuildPresets`: `long`, presets per player, ≥ 1. A missing key is a load rejection naming it
  (T5). 32 matches `softMaxPresets` in `gk-core/data/tuning/aptitude-presets.v1.json`, the sibling library's
  shipped value; a balance pass changes it here.
- **Not a cap in the §11 sense:** it bounds a player's list length, not a magnitude, and the comment in
  code says so.

## ActorHub gate

**Not applicable.** The store holds references; nothing here reaches an actor number.

## Integer widths

`revision` and `ordinal` are SQLite integers read as `long`. No magnitudes.

## Seedsmith / generator

**None.** Player-authored runtime rows; there is no seed shape or corpus.

## Success criteria

- [ ] Two tables, four routes, the closed five-kind vocabulary.
- [ ] Save-time shape rules refuse by name; validate-on-read never drops a row.
- [ ] `build-preset.v1.json` loads; a missing key rejects.
- [ ] `guard-dal.py` and `verify-change.ps1` green.

## Open questions

None.

## Self-audit — the debate

- **"One generic piece table is an EAV smell."** The alternative is five tables for five shapes that are
  all *(target, ordinal, reference)*. The shape is genuinely the same, the kind is a closed enum, and the
  validator is per kind. A new kind is a reviewed enum change either way.
- **"Store the aptitude shares inline so a preset is self-contained."** That is a second aptitude
  library with its own sum-to-1000 validation and soft max, drifting from the first (map D1). A preset
  that survives its aptitude preset's deletion is exactly the kind of silent divergence the armoury's
  validate-on-read rule exists to prevent.
- **"Refuse the save when a reference is already invalid."** Then a preset that was fine yesterday
  becomes unsavable after an unrelated salvage. Shape is checked at save; validity is shown on read and
  enforced at preview, where it matters.
